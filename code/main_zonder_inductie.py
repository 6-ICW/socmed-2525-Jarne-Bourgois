from machine import Pin, I2C
import time

# ============================================================
# I2C setup
# ============================================================
i2c0 = I2C(0, scl=Pin(22), sda=Pin(21), freq=100000)
i2c1 = I2C(1, scl=Pin(18), sda=Pin(19), freq=100000)

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

state = 0
state_start = time.ticks_ms()

# ============================================================
# STATE TIMER
# ============================================================

def state_time_passed(ms):
    return time.ticks_diff(time.ticks_ms(), state_start) >= ms

def next_state(new_state):
    global state, state_start
    state = new_state
    state_start = time.ticks_ms()



# ============================================================
# TRAFFIC LIGHT CLASS
# ============================================================
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
        self.off()
        set_led(self.i2c, self.bus_id , self.red, True)

    def green_on(self):
        self.off()
        set_led(self.i2c, self.bus_id , self.green, True)

    def orange_on(self):
        self.off()
        set_led(self.i2c, self.bus_id , self.orange, True)

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

  
def intersection_cycle():

    global state

    # ========================================================
    # STATE 0 -> All red
    # ========================================================
    if state == 0:

        for light in [main1_straight, main1_left,
                      main2_straight, main2_left,
                      side1_1, side1_2]:
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

        # HERE you can read induction sensors
        # without blocking

        if state_time_passed(6000):

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
# SEQUENCE
# ============================================================

# ============================================================
# START
# ============================================================
print("I2C scan:", i2c0.scan())
print("I2C scan:", i2c1.scan())

mcp_init(i2c0)
mcp_init(i2c1)

# bus

# Main road 1
main1_straight = TrafficLight(i2c0,0,0, 1, 2)
main1_left     = TrafficLight(i2c0,0,3, 4, 5)

# Side road pedestrian lights 1
side1_1_ped = PedestrianLight(i2c0,0,6,7) # pedestrian light only has red and green
side1_2_ped = PedestrianLight(i2c0,0,14,15) 

# Main road 2
main2_straight = TrafficLight(i2c0,0,8, 9, 10)
main2_left     = TrafficLight(i2c0,0,11, 12, 13)

# Side roads
side1_1 = TrafficLight(i2c1,1,0, 1, 2)
side1_2 = TrafficLight(i2c1,1,3, 4, 5)

# Side road pedestrian lights 2
side2_1_ped = PedestrianLight(i2c1,1,6,7) 
side2_2_ped = PedestrianLight(i2c1,1,8,9)
                        
# Railroad lights
                       
side1_railroad = RailroadLight(i2c1,1,10,11,12)
side2_railroad = RailroadLight(i2c1,1,13,14,15)
                        
# ============================================================
# LOOP
# ============================================================
while True:
    # if statement for railroad crossing button
    # new function will be used for railroad lights and barrier
    intersection_cycle()
    
    time.sleep_ms(10)
