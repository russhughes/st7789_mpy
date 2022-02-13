# input pins for ws_pico_114 v2 witjh Joystick

from machine import Pin

class Buttons():
    def __init__(self):
        self.left = Pin(16,Pin.IN,Pin.PULL_UP)       # joystick left
        self.right = Pin(20,Pin.IN,Pin.PULL_UP)      # joystick right
        self.thrust = Pin(3,Pin.IN,Pin.PULL_UP)      # joystick center
        self.hyper = Pin(15,Pin.IN,Pin.PULL_UP)      # button A
        self.fire = Pin(17 ,Pin.IN,Pin.PULL_UP)      # button B
