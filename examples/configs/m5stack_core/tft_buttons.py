
# input pins for M5Stack Core buttons

from machine import Pin


class Buttons():
    def __init__(self):
        self.name = "m5stack_core"

        self.button_a = Pin(39, Pin.IN)  # button A
        self.button_b = Pin(38, Pin.IN)  # button B
        self.button_c = Pin(37, Pin.IN)  # button C

