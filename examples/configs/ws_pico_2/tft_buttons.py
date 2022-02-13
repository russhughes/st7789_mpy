# input pins for ws_pico_2

from machine import Pin

class Buttons():
    def __init__(self):
        self.left = Pin(2, Pin.IN, Pin.PULL_UP)      # Top Left
        self.right = Pin(3, Pin.IN, Pin.PULL_UP)     # Top Right
        self.fire = Pin(15, Pin.IN, Pin.PULL_UP)     # Bottom Left
        self.thrust = Pin(17, Pin.IN, Pin.PULL_UP)   # Bottom Right
        self.hyper = 0                               # No hyper button on ws_pico_2
