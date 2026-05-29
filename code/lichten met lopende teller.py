from machine import Pin, I2C
import time

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
# VERKEERSCYCLUS
# ============================================================

def intersection_cycle():

    global state

    # ========================================================
    # STATE 0 -> Alles rood
    # ========================================================
    if state == 0:

        for light in [main1_straight, main1_left,
                      main2_straight, main2_left,
                      side1_1, side1_2]:
            light.red_on()

        next_state(1)

    # ========================================================
    # STATE 1 -> 2 sec wachten
    # ========================================================
    elif state == 1:

        if state_time_passed(2000):

            main1_straight.green_on()
            main2_straight.green_on()

            side1_1voet.green_on()
            side1_2voet.green_on()

            side2_1voet.green_on()
            side2_2voet.green_on()

            next_state(2)

    # ========================================================
    # STATE 2 -> Hoofdweg groen
    # ========================================================
    elif state == 2:

        # HIER kan je inductiesensoren lezen
        # zonder blokkering

        if state_time_passed(6000):

            main1_straight.orange_on()
            main2_straight.orange_on()

            side1_1voet.red_on()
            side1_2voet.red_on()

            side2_1voet.red_on()
            side2_2voet.red_on()

            next_state(3)

    # ========================================================
    # STATE 3 -> Oranje hoofdweg
    # ========================================================
    elif state == 3:

        if state_time_passed(2000):

            main1_straight.red_on()
            main2_straight.red_on()

            next_state(4)

    # ========================================================
    # STATE 4 -> Alles rood
    # ========================================================
    elif state == 4:

        if state_time_passed(2000):

            main1_left.green_on()
            main2_left.green_on()

            next_state(5)

    # ========================================================
    # STATE 5 -> Linksaf groen
    # ========================================================
    elif state == 5:

        if state_time_passed(4000):

            main1_left.orange_on()
            main2_left.orange_on()

            next_state(6)

    # ========================================================
    # STATE 6 -> Linksaf oranje
    # ========================================================
    elif state == 6:

        if state_time_passed(2000):

            main1_left.red_on()
            main2_left.red_on()

            next_state(7)

    # ========================================================
    # STATE 7 -> Zijstraat groen
    # ========================================================
    elif state == 7:

        side1_1.green_on()
        side1_2.green_on()

        next_state(8)

    # ========================================================
    # STATE 8 -> Wachten
    # ========================================================
    elif state == 8:

        if state_time_passed(5000):

            side1_1.orange_on()
            side1_2.orange_on()

            next_state(9)

    # ========================================================
    # STATE 9 -> Zijstraat oranje
    # ========================================================
    elif state == 9:

        if state_time_passed(2000):

            side1_1.red_on()
            side1_2.red_on()

            next_state(0)