"""PYBOARD V1.1 with Generic 240x320 ST7789 display"""

from pyb import SPI, Pin
import st7789

TFA = 0
BFA = 0

def config(rotation=0, buffer_size=0, options=0):
    return st7789.ST7789(
        SPI(1, SPI.MASTER, baudrate=42000000, prescaler=2),
        240,
        320,
        reset=Pin('X3', Pin.OUT),
        cs=Pin('X5', Pin.OUT),
        dc=Pin('X4', Pin.OUT),
        backlight=Pin('X2', Pin.OUT),
        rotation=rotation,
        options=options,
        buffer_size=buffer_size)
