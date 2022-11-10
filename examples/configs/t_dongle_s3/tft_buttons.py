# input pin for esp32 T-DONGLE-S3 module

from machine import Pin

class Buttons():
    def __init__(self):
        self.name = "t-dongle-s3"
        self.button = Pin(0, Pin.IN)
