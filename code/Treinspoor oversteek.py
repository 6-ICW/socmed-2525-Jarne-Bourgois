from machine import Pin, PWM
import time

# ============================================================
# SERVO CLASS
# ============================================================
class Servo:
    def __init__(self, pin):
        self.pwm = PWM(Pin(pin), freq=50)

    def set_angle(self, angle):

        min_duty = 1638
        max_duty = 8192

        duty = int(min_duty + (max_duty - min_duty) * angle / 180)

        self.pwm.duty_u16(duty)

# ============================================================
# RAILROAD LIGHT CLASS
# ============================================================
class RailroadLight:
    def __init__(self, red1_pin, red2_pin):
        self.red1 = Pin(red1_pin, Pin.OUT)
        self.red2 = Pin(red2_pin, Pin.OUT)

    def off(self):
        self.red1.off()
        self.red2.off()

    def flash_1(self):
        self.red1.on()
        self.red2.off()

    def flash_2(self):
        self.red1.off()
        self.red2.on()

# ============================================================
# HARDWARE SETUP
# ============================================================
train_button = Pin(32, Pin.IN, Pin.PULL_UP)

barrier1 = Servo(25)
barrier2 = Servo(26)

railroad = RailroadLight(18, 19)

# ============================================================
# VARIABLES
# ============================================================
railroad_active = False
railroad_state = 0
railroad_timer = time.ticks_ms()
flash_timer = time.ticks_ms()
flash_state = False

# ============================================================
# HELPER FUNCTIONS
# ============================================================
def next_railroad_state(new_state):
    global railroad_state, railroad_timer

    railroad_state = new_state
    railroad_timer = time.ticks_ms()


def railroad_time_passed(ms):
    return time.ticks_diff(time.ticks_ms(), railroad_timer) >= ms

# ============================================================
# RAILROAD CROSSING LOGIC
# ============================================================
def railroad_crossing_cycle():

    global railroad_active
    global flash_timer
    global flash_state
            railroad_active = False