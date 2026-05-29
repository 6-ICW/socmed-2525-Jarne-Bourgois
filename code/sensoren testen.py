from machine import Pin
import time

# ============================================================
# SENSOR CLASS
# ============================================================

class InductionSensor:
    def __init__(self, pin, name):
        self.sensor = Pin(pin, Pin.IN, Pin.PULL_UP)
        self.name = name

    def detected(self):
        return self.sensor.value() == 0

# ============================================================
# SENSORS (zelfde poorten als jouw hoofdcode)
# ============================================================

main_road_sensor1_1 = InductionSensor(32, "Main road sensor 1_1")
main_road_sensor1_2 = InductionSensor(33, "Main road sensor 1_2")
main_road_sensor2_1 = InductionSensor(25, "Main road sensor 2_1")
main_road_sensor2_2 = InductionSensor(26, "Main road sensor 2_2")

side_road_sensor1_1 = InductionSensor(27, "Side road sensor 1_1")
side_road_sensor1_2 = InductionSensor(14, "Side road sensor 1_2")
side_road_sensor2_1 = InductionSensor(16, "Side road sensor 2_1")
side_road_sensor2_2 = InductionSensor(17, "Side road sensor 2_2")

sensors = [
    main_road_sensor1_1,
    main_road_sensor1_2,
    main_road_sensor2_1,
    main_road_sensor2_2,
    side_road_sensor1_1,
    side_road_sensor1_2,
    side_road_sensor2_1,
    side_road_sensor2_2
]

# ============================================================
# LOOP
# ============================================================

print("Sensor test gestart...")

while True:
    for sensor in sensors:
        if sensor.detected():
            print(sensor.name, "GEDETECTEERD")

    time.sleep_ms(100)