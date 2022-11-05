
# input pins for ws_pico_13

from machine import Pin

class Buttons():
    def __init__(self):
        self.name = "ws_pico_13"
        self.up = Pin(2,Pin.IN,Pin.PULL_UP)         # joystick up
        self.down = Pin(18,Pin.IN,Pin.PULL_UP)      # joystick down
        self.left = Pin(16,Pin.IN,Pin.PULL_UP)      # joystick left
        self.right = Pin(20,Pin.IN,Pin.PULL_UP)     # joystick right
        self.center = Pin(3,Pin.IN,Pin.PULL_UP)     # joystick center

        self.a = Pin(15,Pin.IN,Pin.PULL_UP)         # button A
        self.b = Pin(17,Pin.IN,Pin.PULL_UP)         # button B
        self.x = Pin(19,Pin.IN,Pin.PULL_UP)         # button X
        self.y = Pin(21,Pin.IN,Pin.PULL_UP)         # button Y

        # for roids.py

        self.thrust = self.center                   # joystick center
        self.hyper = self.a                         # button A
        self.fire = self.y                          # button Y
