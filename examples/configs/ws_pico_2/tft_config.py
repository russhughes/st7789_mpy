"""Waveshare Pico LCD 2 inch display"""

from machine import Pin, SPI
import st7789

TFA = 0	 # top free area when scrolling
BFA = 0	 # bottom free area when scrolling

def config(rotation=0, buffer_size=0, options=0):
    return st7789.ST7789(
        SPI(1, baudrate=62500000, sck=Pin(10), mosi=Pin(11)),
        240,
        320,
        reset=Pin(12, Pin.OUT),
        cs=Pin(9, Pin.OUT),
        dc=Pin(8, Pin.OUT),
        backlight=Pin(13, Pin.OUT),
        rotation=rotation,
        options=options,
        buffer_size=buffer_size)
