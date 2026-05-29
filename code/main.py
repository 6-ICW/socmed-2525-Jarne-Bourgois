from machine import Pin, I2C,PWM
import time

# ============================================================
# I2C setup
# ============================================================

i2c0 = I2C(0, scl=Pin(22), sda=Pin(21), freq=100000) # I²C 1
i2c1 = I2C(1, scl=Pin(18), sda=Pin(19), freq=100000) # I²C 2

MCP_ADDR = 0x20

IODIRA = 0x00
IODIRB = 0x01
GPIOA  = 0x12
GPIOB  = 0x13

def mcp_init(i2c):
    i2c.writeto_mem(MCP_ADDR, IODIRA, b'\x00')
    i2c.writeto_mem(MCP_ADDR, IODIRB, b'\x00')

stateA = {0:0,1:0}
stateB = {0:0,1:0}

# LED function used to control ports on the I²C expander
# You provide:
# - which I²C bus (0 or 1)
# - which bus_id (0 or 1 = A or B)
# - which LED number (0-15)
# - value True or False (on or off)

def set_led(i2c,bus_id,led_number, value):
    global stateA, stateB

    if led_number < 8:
        if value:
            stateA[bus_id] |= (1 << led_number)
        else:
            stateA[bus_id] &= ~(1 << led_number)

        i2c.writeto_mem(MCP_ADDR, GPIOA, bytes([stateA[bus_id]]))

    else:
        pin = led_number - 8

        if value:
            stateB[bus_id] |= (1 << pin)
        else:
            stateB[bus_id] &= ~(1 << pin)

        i2c.writeto_mem(MCP_ADDR, GPIOB, bytes([stateB[bus_id]]))

# ============================================================
# VARIABLES
# ============================================================

# Current traffic state 
state = 0
state_start = time.ticks_ms()

# Railroad crossing variables
railroad_active = False
railroad_state = 0
railroad_timer = time.ticks_ms()
flash_timer = time.ticks_ms()
flash_state = False
train_requested = False

# ============================================================
# STATE TIMER
# ============================================================

# Calculates elapsed time for traffic cycle
def state_time_passed(ms):
    return time.ticks_diff(time.ticks_ms(), state_start) >= ms

# When the next traffic phase starts,
# reset the start time
def next_state(new_state):
    global state, state_start
    state = new_state
    state_start = time.ticks_ms()

# Same principle as above but for railroad crossing
def next_railroad_state(new_state):
    global railroad_state, railroad_timer

    railroad_state = new_state
    railroad_timer = time.ticks_ms()

# Calculates elapsed time for railroad cycle
def railroad_time_passed(ms):
    return time.ticks_diff(time.ticks_ms(), railroad_timer) >= ms

# ============================================================
# TRAFFIC LIGHT CLASS
# ============================================================

# For each traffic light you provide:
# - which I²C bus
# - which MCP bus (0 or 1)
# - which ports are red, orange and green
class TrafficLight:
    def __init__(self,i2c,bus_id, red, orange, green):
        self.i2c = i2c
        self.bus_id = bus_id                
        self.red = red
        self.orange = orange
        self.green = green

    def off(self):
        set_led(self.i2c, self.bus_id , self.red, False)
        set_led(self.i2c, self.bus_id , self.orange, False)
        set_led(self.i2c, self.bus_id , self.green, False)

    def red_on(self):
        self.off() # Turns all lights of this traffic light off
        set_led(self.i2c, self.bus_id , self.red, True)

    def green_on(self):
        self.off()
        set_led(self.i2c, self.bus_id , self.green, True)

    def orange_on(self):
        self.off()
        set_led(self.i2c, self.bus_id , self.orange, True)

# Works the same way as TrafficLight
# but with only red and green lights
class PedestrianLight:
    def __init__(self, i2c, bus_id, red, green):
        self.i2c = i2c
        self.bus_id = bus_id
        self.red = red
        self.green = green

    def off(self):
        set_led(self.i2c, self.bus_id, self.red, False)
        set_led(self.i2c, self.bus_id, self.green, False)

    def red_on(self):
        self.off()
        set_led(self.i2c, self.bus_id, self.red, True)

    def green_on(self):
        self.off()
        set_led(self.i2c, self.bus_id, self.green, True)

# Works the same way as TrafficLight
class RailroadLight:
    def __init__(self,i2c,bus_id, red1, red2, orange):
        self.i2c = i2c
        self.bus_id = bus_id                
        self.red1 = red1
        self.red2 = red2
        self.orange = orange

    def off(self):
        set_led(self.i2c, self.bus_id , self.red1, False)
        set_led(self.i2c, self.bus_id , self.red2, False)
        set_led(self.i2c, self.bus_id , self.orange, False)

    def red_on(self):
        self.off()
        set_led(self.i2c, self.bus_id , self.red1, True)
        set_led(self.i2c, self.bus_id , self.red2, True)

    def orange_on(self):
        self.off()
        set_led(self.i2c, self.bus_id , self.orange, True)


class Servo:
    # Initialize servo motor with pin
    # and frequency 50Hz because our motors use that
    # PWM = Pulse Width Modulation
    def __init__(self, pin):
        self.pwm = PWM(Pin(pin), freq=50)

    def set_angle(self, angle):

        min_duty = 1638
        max_duty = 8192

        duty = int(min_duty + (max_duty - min_duty) * angle / 180)

        self.pwm.duty_u16(duty)



class InductionSensor:
     # Initialize sensor
    def __init__(self,pin):
        self.sensor = Pin(pin,Pin.IN,Pin.PULL_UP)
    
    def detected(self):
        return self.sensor.value() == 0

def railroad_crossing_cycle():
    # Because everything is in one file,
    # global variables can be used here
    global railroad_active
    global flash_timer
    global flash_state
    global train_requested
    
    # Check if a railroad crossing request is active
    # and if the train button is pressed

      if train_requested and railroad_active == False:
            train_requested = False
            railroad_active = True
            next_railroad_state(0)
    
    if railroad_active == False:
        return

    # Stop road traffic
    for light in [main1_straight, main1_left,    
                  main2_straight, main2_left    
                  ,side1_1_ped,side1_2_ped]:
        light.red_on()
    for light in[ side1_1, side1_2]:
        light.green_on()

    # Flashing railroad lights
    if time.ticks_diff(time.ticks_ms(), flash_timer) >= 500:

        flash_timer = time.ticks_ms()
        flash_state = not flash_state

        if flash_state:
            side1_railroad.red_on()
            side2_railroad.off()
        else:
            side1_railroad.off()
            side2_railroad.red_on()

    # STATE 0
    if railroad_state == 0:

        barrier1.set_angle(0)
        barrier2.set_angle(0)

        if railroad_time_passed(3000):
            next_railroad_state(1)

    # STATE 1
    elif railroad_state == 1:

        barrier1.set_angle(90)
        barrier2.set_angle(90)

        if railroad_time_passed(3000):
            next_railroad_state(2)

    # STATE 2
    elif railroad_state == 2:
        for light in [ side1_1,side1_2]:
            light.red_on()
        for light in [ side1_1_ped,side1_2_ped]:
            light.green_on()   
        if railroad_time_passed(8000):
            next_railroad_state(3)

    # STATE 3
    elif railroad_state == 3:

        barrier1.set_angle(0)
        barrier2.set_angle(0)

        if railroad_time_passed(3000):
            
            for light in [ side1_1_ped,side1_2_ped]:
                light.red_on()
            
            side1_railroad.off()
            side2_railroad.off()

            railroad_active = False

def check_train_request():
    global train_requested

    if train_button.value() == 0:
        train_requested = True

    
def intersection_cycle():
    # Traffic simulation is controlled using states
    global state

    # ========================================================
    # STATE 0 -> All red
    # ========================================================
    if state == 0:

        for light in [main1_straight, main1_left,
                      main2_straight, main2_left,
                      side1_1, side1_2,side1_1_ped,side1_2_ped,side2_1_ped,side2_2_ped]:
            light.red_on()

        next_state(1)

    # ========================================================
    # STATE 1 -> Wait 2 sec
    # ========================================================
    elif state == 1:

        if state_time_passed(2000):

            main1_straight.green_on()
            main2_straight.green_on()

            side1_1_ped.green_on()
            side1_2_ped.green_on()

            side2_1_ped.green_on()
            side2_2_ped.green_on()

            next_state(2)

    # ========================================================
    # STATE 2 -> Main road green
    # ========================================================
    elif state == 2:

        # Here you can read induction sensors
        # to detect waiting cars
        
        main_road_busy = (
            main_road_sensor1_1.detected() or
            main_road_sensor1_2.detected() or
            main_road_sensor2_1.detected() or
            main_road_sensor2_2.detected()
        )

        side_road_waiting = (
            side_road_sensor1_1.detected() or
            side_road_sensor1_2.detected() or
            side_road_sensor2_1.detected() or
            side_road_sensor2_2.detected()
        )
        if side_road_waiting:
           if main_road_busy:
               pass
           else:
                main1_straight.orange_on()
                main2_straight.orange_on()

                side1_1_ped.red_on()
                side1_2_ped.red_on()

                side2_1_ped.red_on()
                side2_2_ped.red_on()
                
                if state_time_passed(2000):
            
                    main1_straight.red_on()
                    main2_straight.red_on()

                    next_state(7)

        if state_time_passed(10000):

            main1_straight.orange_on()
            main2_straight.orange_on()

            side1_1_ped.red_on()
            side1_2_ped.red_on()

            side2_1_ped.red_on()
            side2_2_ped.red_on()

            next_state(3)

    # ========================================================
    # STATE 3 -> Main road orange
    # ========================================================
    elif state == 3:

        if state_time_passed(2000):

            main1_straight.red_on()
            main2_straight.red_on()

            next_state(4)

    # ========================================================
    # STATE 4 -> All red
    # ========================================================
    elif state == 4:

        if state_time_passed(2000):

            main1_left.green_on()
            main2_left.green_on()

            next_state(5)

    # ========================================================
    # STATE 5 -> Left turn green
    # ========================================================
    elif state == 5:

        if state_time_passed(4000):

            main1_left.orange_on()
            main2_left.orange_on()

            next_state(6)

    # ========================================================
    # STATE 6 -> Left turn orange
    # ========================================================
    elif state == 6:

        if state_time_passed(2000):

            main1_left.red_on()
            main2_left.red_on()

            next_state(7)

    # ========================================================
    # STATE 7 -> Side road green
    # ========================================================
    elif state == 7:
            
            side1_1.green_on()
            side1_2.green_on()

            next_state(8)

    # ========================================================
    # STATE 8 -> Waiting
    # ========================================================
    elif state == 8:

        if state_time_passed(5000):

            side1_1.orange_on()
            side1_2.orange_on()

            next_state(9)

    # ========================================================
    # STATE 9 -> Side road orange
    # ========================================================
    elif state == 9:

        if state_time_passed(2000):

            side1_1.red_on()
            side1_2.red_on()

            next_state(0)

# ============================================================
# START
# ============================================================

# Test if I²C devices are connected
print("I2C scan:", i2c0.scan())
print("I2C scan:", i2c1.scan())

# Initialize I²C expanders
mcp_init(i2c0)
mcp_init(i2c1)

# Connect all lights to the correct ports
# Main road 1
main1_straight = TrafficLight(i2c0,0,0, 1, 2)
main1_left     = TrafficLight(i2c0,0,3, 4, 5)

# Side road pedestrian lights 1
side1_1_ped = PedestrianLight(i2c0,0,6,7) # pedestrian light only has red and green
side1_2_ped = PedestrianLight(i2c0,0,14,15) 

# Main road 2
main2_straight = TrafficLight(i2c0,0,8, 9, 10)
main2_left     = TrafficLight(i2c0,0,11, 12, 13)

# Side road pedestrian lights 2
side2_1_ped = PedestrianLight(i2c1,1,6,7) 
side2_2_ped = PedestrianLight(i2c1,1,8,9)
                
# Side roads
side1_1 = TrafficLight(i2c1,1,0, 1, 2)
side1_2 = TrafficLight(i2c1,1,3, 4, 5)

        
# Railroad lights
                       
side1_railroad = RailroadLight(i2c1,1,10,11,12)
side2_railroad = RailroadLight(i2c1,1,13,14,15)
 
# Connect all sensors to a port
main_road_sensor1_1 = InductionSensor(32)
main_road_sensor1_2 = InductionSensor(33)
main_road_sensor2_1 = InductionSensor(25)
main_road_sensor2_2 = InductionSensor(26)

side_road_sensor1_1 = InductionSensor(27)
side_road_sensor1_2 = InductionSensor(14)
side_road_sensor2_1 = InductionSensor(16)
side_road_sensor2_2 = InductionSensor(17)

# This button simulates an incoming train
train_button = Pin(5, Pin.IN, Pin.PULL_UP)

# Assign ports to servo motors
barrier1 = Servo(23)
barrier2 = Servo(13)
 
# ============================================================
# LOOP
# ============================================================

# Main loop:
# First check railroad crossing,
# then continue normal traffic cycle
while True:
  
    check_train_request()
    
    railroad_crossing_cycle()

    if railroad_active == False:
        intersection_cycle()
    
    time.sleep_ms(10)