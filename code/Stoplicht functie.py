from machine import Pin 
import time

#pins licht 1
R1 = Pin(27,Pin.OUT)
G1 = Pin(25,Pin.OUT)
GE1 = Pin(26,Pin.OUT)
# pins licht 2
R2 = Pin(4,Pin.OUT)
G2 = Pin(18,Pin.OUT)
GE2 = Pin(17,Pin.OUT)

#Lichten prio setten
G = 1
GE = 0
R = 0
A = 0
# laatste tijd gemeten
LTM = time.time()

while True:
    # timer van rood moet groen + geel zijn zodat verschillende kanten niet tegen elkaar rijden
    if time.time() - LTM >= 5 and G ==1:
        print("1")
        R1.value(0)
        G1.value(1)
        R2.value(1)
        GE2.value(0)
        LTM = time.time()
        G = 0
        GE = 1
    if time.time() - LTM >= 3 and GE == 1:
        print("2")
        G1.value(0)
        GE1.value(1)
        LTM = time.time()
        GE = 0
        R = 1
    if time.time() - LTM >= 2 and R == 1:
        print("3")
        GE1.value(0)
        R1.value(1)
        R2.value(0)
        G2.value(1)
        LTM = time.time()
        R = 0
        G = 1
        A = 1
    if time.time() - LTM >= 3 and A == 1:
        print("4")
        G2.value(0)
        GE2.value(1)
        LTM = time.time()
        A = 0
    time.sleep(0.1)
    
    
