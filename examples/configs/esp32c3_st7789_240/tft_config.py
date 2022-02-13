"""Generic ESP32-C3 with ST7789 240x240 display"""

from machine import Pin, SPI
import st7789

TFA = 0
BFA = 80

def config(rotation=0, buffer_size=0, options=0):
    return st7789.ST7789(
        SPI(1, baudrate=80000000, polarity=1, sck=Pin(6), mosi=Pin(7)),
        240,
        240,
        reset=Pin(10, Pin.OUT),
        dc=Pin(4, Pin.OUT),
        rotation=rotation,
        options=options,
        buffer_size=buffer_size)
