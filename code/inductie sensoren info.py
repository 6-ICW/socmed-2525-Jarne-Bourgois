from machine import Pin
import time


# Sensor inputs

# sensor1 = Pin(34,Pin.IN,Pin.PULL_UP)
# sensor2 = Pin(35,Pin.IN,Pin.PULL_UP)
# sensor3 = Pin(36,Pin.IN,Pin.PULL_UP)

class InductionSensor:
    def __init__(self,pin):
        self.sensor = Pin(pin,Pin.IN,Pin.PULL_UP)
    
    def detected(self):
        return self.sensor.value() == 0

main_road_sensor = InductionSensor(32)
# extra info voor poorten
# veilige poorten zijn
# 32 , 33 , 25 , 26 , 27 , 14 , 16 , 17
# testen met multi meter dat signaal van optocoupler zeker 3,3 v is anders spannings deler gebruiken

while true:
    if sensor1.value() == 0: # 0 is als hij iets detecteerd 1 is als hij nieks detecteert
        print("auto is er")