from machine import Pin, I2C
import time

# ============================================================
# I2C setup
# ============================================================
i2c = I2C(
    0,
    scl=Pin(22),
    sda=Pin(21),
    freq=100000   # iets trager = stabieler
)

# ============================================================
# MCP23017 adres (meestal 0x20)
# ============================================================
MCP_ADDR = 0x20

# Registers
IODIRA = 0x00
IODIRB = 0x01
GPIOA  = 0x12
GPIOB  = 0x13

# ============================================================
# Init MCP (alles OUTPUT)
# ============================================================
def mcp_init():
    i2c.writeto_mem(MCP_ADDR, IODIRA, b'\x00')
    i2c.writeto_mem(MCP_ADDR, IODIRB, b'\x00')

# ============================================================
# State bijhouden (belangrijk!)
# ============================================================
stateA = 0
stateB = 0

# ============================================================
# LED control (0 t.e.m. 15)
# ============================================================
def set_led(led_number, value):
    global stateA, stateB

    if led_number < 8:
        # Bank A
        if value:
            stateA |= (1 << led_number)
        else:
            stateA &= ~(1 << led_number)

        i2c.writeto_mem(MCP_ADDR, GPIOA, bytes([stateA]))

    else:
        # Bank B
        pin = led_number - 8

        if value:
            stateB |= (1 << pin)
        else:
            stateB &= ~(1 << pin)

        i2c.writeto_mem(MCP_ADDR, GPIOB, bytes([stateB]))

# ============================================================
# START
# ============================================================
print("I2C scan:", i2c.scan())

mcp_init()

# ============================================================
# TEST: loopje
# ============================================================
while True:
    for i in range(16):
        set_led(i, True)
        time.sleep(0.1)
        set_led(i, False)