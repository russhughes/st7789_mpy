'''
jpg.py

    Draw a full screen jpg using the slower but less memory intensive method of blitting
    each Minimum Coded Unit (MCU) block. Usually 8×8pixels but can be other multiples of 8.

    bigbuckbunny.jpg (c) copyright 2008, Blender Foundation / www.bigbuckbunny.org
'''

import gc
import time
import random
from pyb import SPI, Pin
import st7789

gc.enable()
gc.collect()


def main():
    '''
    Decode and draw jpg on display
    '''
    try:
        spi = SPI(1, SPI.MASTER, baudrate=42000000, prescaler=2)

        # initialize display
        tft = st7789.ST7789(
            spi,
            240,
            320,
            reset=Pin('X3', Pin.OUT),
            cs=Pin('X5', Pin.OUT),
            dc=Pin('X4', Pin.OUT),
            backlight=Pin('X2', Pin.OUT),
            rotation=3)

        # enable display and clear screen
        tft.init()

        # display jpg
        tft.jpg("bigbuckbunny.jpg", 0, 0, st7789.SLOW)

    finally:
        # shutdown spi
        spi.deinit()


main()
