# input pins for my esp32 test breadboard

from machine import Pin

class Buttons():
    def __init__(self):
        self.left = 0
        self.right = 0
        self.hyper = 0
        self.thrust = 0
        self.fire = 0
