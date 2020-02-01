"""
ttgo_hello.py

    Writes "Hello!" in random colors at random locations on a
    LILYGO® TTGO T-Display ESP32 WiFi&Bluetooth Module

    https://www.youtube.com/watch?v=-spQgQPzGO0

"""

import random
from machine import Pin, SPI
import st7789 as st7789
import time
import utime

from fonts import vga2_8x16 as font

def main():

    tft = st7789.ST7789(
        SPI(2, baudrate=30000000, polarity=1, phase=1, sck=Pin(18), mosi=Pin(19)),
        135,
        240,
        reset=Pin(23, Pin.OUT),
        cs=Pin(5, Pin.OUT),
        dc=Pin(16, Pin.OUT),
        backlight=Pin(4, Pin.OUT),
        rotation=3)

    tft.init()
    tft.fill(st7789.BLACK)

    start = utime.ticks_ms()
    tft.text(font, "MicroPython", 0, 0,  st7789.WHITE)
    tft.text(font, "MicroPython", 0, 32, st7789.RED)
    tft.text(font, "MicroPython", 0, 64, st7789.GREEN)
    tft.text(font, "MicroPython", 0, 96, st7789.BLUE)
    print("time:", utime.ticks_ms()- start, "ms")

main()
