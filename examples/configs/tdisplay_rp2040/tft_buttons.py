
# input pins for tdisplay_rp2040

from machine import Pin

class Buttons():
    def __init__(self):
        self.name = "tdisplay_rp2040"
        self.left = Pin(6,Pin.IN,Pin.PULL_UP)      # joystick left
        self.right = Pin(7,Pin.IN,Pin.PULL_UP)     # joystick right
