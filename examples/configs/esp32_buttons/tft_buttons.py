# input pins for my esp32 test breadboard

from machine import Pin

class Buttons():
    def __init__(self):
        self.left = Pin(32, Pin.IN)
        self.right = Pin(39, Pin.IN)
        self.hyper = Pin(38, Pin.IN)
        self.thrust = Pin(37, Pin.IN)
        self.fire = Pin(36, Pin.IN)
