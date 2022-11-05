# input pins for esp32 T-Display module

from machine import Pin

class Buttons():
    def __init__(self):
        self.name = "tdisplay_esp32"
        self.left = Pin(0, Pin.IN)
        self.right = Pin(35, Pin.IN)
