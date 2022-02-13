# input pins for ws_pico_114 v1 with four buttons

from machine import Pin

class Buttons():
    def __init__(self):
        self.left = Pin(2,Pin.IN,Pin.PULL_UP)        # KEY 2
        self.right = Pin(15,Pin.IN,Pin.PULL_UP)      # KEY 0
        self.thrust = Pin(3,Pin.IN,Pin.PULL_UP)      # KEY 3
        self.hyper = None                            # None
        self.fire = Pin(17 ,Pin.IN,Pin.PULL_UP)      # KEY 1
