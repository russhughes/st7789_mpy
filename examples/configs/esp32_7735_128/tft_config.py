"""Generic ESP32 with 128x128 7735 display"""

from machine import Pin, SPI
import st7789

TFA = 1
BFA = 3

def config(rotation=0, buffer_size=0, options=0):
    return st7789.ST7789(
        SPI(1, baudrate=30000000, sck=Pin(18), mosi=Pin(19)),
        128,
        128,
        reset=Pin(4, Pin.OUT),
        cs=Pin(13, Pin.OUT),
        dc=Pin(12, Pin.OUT),
        backlight=Pin(15, Pin.OUT),
        color_order=st7789.BGR,
        inversion=False,
        rotation=rotation,
        options=options,
        buffer_size=buffer_size)
