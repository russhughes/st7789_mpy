"""ESP32 Box Lite with ST7789 240x320 display"""

from machine import Pin, SPI
import st7789

TFA = 0
BFA = 0

def config(rotation=0, buffer_size=0, options=0):
    return st7789.ST7789(
        SPI(1, baudrate=40000000, sck=Pin(7), mosi=Pin(6)),
        240,
        320,
        reset=Pin(48, Pin.OUT),
        cs=Pin(5, Pin.OUT),
        dc=Pin(4, Pin.OUT),
        backlight=Pin(45, Pin.OUT),
        rotation=rotation,
        options=options,
        buffer_size=buffer_size)
