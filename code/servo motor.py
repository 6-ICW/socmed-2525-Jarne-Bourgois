from machine import Pin, PWM
import time

servo = PWM(Pin(15), freq=50)
button = Pin(14, Pin.IN, Pin.PULL_UP)

# Zet servo via microseconden (stabiel!)
def set_angle(angle):
    us = 500 + (angle / 180) * 2000  # 500–2500 µs
    duty = int(us / 20000 * 1023)   # 20ms periode (50Hz)
    servo.duty(duty)

def move_slow(start, end):
    step = 1 if end > start else -1
    for angle in range(start, end, step):
        set_angle(angle)
        time.sleep(0.015)

# START
current_angle = 0
set_angle(current_angle)

while True:
        time.sleep(5)

        move_slow(current_angle, 90)
        time.sleep(2)

        move_slow(90, 0)
        current_angle = 0

        time.sleep(0.3)