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

def mcp_init():
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

        i2c.writeto_mem(MCP_ADDR, GPIOA, bytes([stateA[bus_id]))

    else:
        pin = led_number - 8

        if value:
            stateB[bus_id] |= (1 << pin)
        else:
            stateB[bus_id] &= ~(1 << pin)

        i2c.writeto_mem(MCP_ADDR, GPIOB, bytes([stateB[bus_id]]))

# ============================================================
# STOPLICHT CLASS
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

  
  
class Spoorlicht:
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

    # --- Alles rood ---
    for light in [main1_straight, main1_left,
                  main2_straight, main2_left,
                  side1, side2]:
        light.red_on()
    time.sleep(2)

    # --- Hoofdstraat rechtdoor groen ---
    main1_straight.green_on()
    main2_straight.green_on()

    main1_left.red_on()
    main2_left.red_on()
    side1.red_on()
    side2.red_on()
                        
    side1_1voet.green_on()
    side1_2voet.green_on()
                        
    side2_1voet.green_on() 
    side2_2voet.green_on()                    
                        

    time.sleep(6)

    # --- Hoofdstraat geel ---
    main1_straight.orange_on()
    main2_straight.orange_on()
                        
     
    side1_1voet.red_on()
    side1_2voet.red_on()  
     
    side2_1voet.red_on() 
    side2_2voet.red_on() 
     
    time.sleep(2)

    # --- Alles rood ---
    for light in [main1_straight, main2_straight]:
        light.red_on()
    time.sleep(2)

    # --- Linksaf groen ---
    main1_left.green_on()
    main2_left.green_on()

    time.sleep(4)

    # --- Linksaf geel ---
    main1_left.orange_on()
    main2_left.orange_on()
    time.sleep(2)

    # --- Alles rood ---
    main1_left.red_on()
    main2_left.red_on()
    time.sleep(2)

    # --- Zijstraten groen ---
    side1.green_on()
    side2.green_on()

    time.sleep(5)

    # --- Zijstraten geel ---
    side1.orange_on()
    side2.orange_on()
    time.sleep(2)

    # --- Terug naar rood ---
    side1.red_on()
    side2.red_on()
    time.sleep(2)
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

# Hoofdstraat 1
main1_straight = TrafficLight(i2c0,0,0, 1, 2)
main1_left     = TrafficLight(i2c0,0,3, 4, 5)

#zijstraat voet1
side1_1voet = TrafficLight(i2c0,0,6,20,7) # poort 20 bestaat niet maar is een opvuller want word niet gebruikt 
side1_2voet = TrafficLight(i2c0,0,14,20,15) # voetgangerlicht heeft enkel rood en groen

# Hoofdstraat 2
main2_straight = TrafficLight(i2c0,0,8, 9, 10)
main2_left     = TrafficLight(i2c0,0,11, 12, 13)

# Zijstraten
side1_1 = TrafficLight(i2c1,1,0, 1, 2)
side1_2 = TrafficLight(i2c1,1,3, 4, 5)

#zijstraat voet2
side2_1voet = TrafficLight(i2c1,1,6,20,7) 
side2_2voet = TrafficLight(i2c1,1,8,20,9)
                        
# spoorlichten
                       
side1_spoor = Spoorlicht(i2c1,1,10,11,12)
side2_spoor = Spoorlicht(i2c1,1,13,14,15)
                        
# ============================================================
# LOOP
# ============================================================
while True:
    #hier if statement met knop voor treinspoor oversteek
    # nieuwe functie zal gebruikt worden voor spoorlichten en slagboom
    intersection_cycle()
    