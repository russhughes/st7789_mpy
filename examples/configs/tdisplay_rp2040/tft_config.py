"""TTGO T-Display RP2040 display"""

from machine import Pin, SPI
from time import sleep
import st7789

TFA = 40	# top free area when scrolling
BFA = 40	# bottom free area when scrolling

def config(rotation=0, buffer_size=0, options=0):

    Pin(22, Pin.OUT, value=1)

    spi = SPI(0,
        baudrate=62500000,
        polarity=0,
        phase=0,
        sck=Pin(2, Pin.OUT),
        mosi=Pin(3, Pin.OUT),
        miso=None)

    return st7789.ST7789(
        spi,
        135,
        240,
        cs=Pin(5, Pin.OUT),
        dc=Pin(1, Pin.OUT),
        reset=Pin(6, Pin.OUT),
        backlight=Pin(4, Pin.OUT),
        rotation=rotation,
        options=options,
        buffer_size=buffer_size)
