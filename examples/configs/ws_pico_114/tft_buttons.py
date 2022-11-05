# input pins for ws_pico_114 v1 with four buttons

from machine import Pin

class Buttons():
    def __init__(self):
        self.name = "ws_pico_114"
        self.key0 = Pin(15,Pin.IN,Pin.PULL_UP)  # KEY 0
        self.key1 = Pin(17 ,Pin.IN,Pin.PULL_UP) # KEY 1
        self.key2 = Pin(2,Pin.IN,Pin.PULL_UP)   # KEY 2
        self.key3 = Pin(3,Pin.IN,Pin.PULL_UP)   # KEY 3

        # for roids.py
        self.left = self.key2                   # KEY 2
        self.right = self.key0                  # KEY 0
        self.thrust = self.key3                 # KEY 3
        self.hyper = None                       # None
        self.fire = self.key1                   # KEY 1
