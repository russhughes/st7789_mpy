'''
jpg.py

    Draw a full screen jpg using the slower but less memory intensive method of blitting
    each Minimum Coded Unit (MCU) block. Usually 8×8pixels but can be other multiples of 8.

    bigbuckbunny.jpg (c) copyright 2008, Blender Foundation / www.bigbuckbunny.org
'''

import gc
import random
from machine import Pin, SPI
import axp202c
import st7789

gc.enable()
gc.collect()


def main():
    '''
    Decode and draw jpg on display
    '''
    try:
        # Turn on display backlight
        axp = axp202c.PMU()
        axp.enablePower(axp202c.AXP202_LDO2)

        # initialize display spi port
        spi = SPI(
            2,
            baudrate=32000000,
            sck=Pin(18, Pin.OUT),
            mosi=Pin(19, Pin.OUT))

        # configure display
        tft = st7789.ST7789(
            spi,
            240,
            240,
            cs=Pin(5, Pin.OUT),
            dc=Pin(27, Pin.OUT),
            backlight=Pin(12, Pin.OUT),
            rotation=2)

        # enable display and clear screen
        tft.init()

        # display jpg
        tft.jpg("bigbuckbunny.jpg", 0, 0, st7789.SLOW)

    finally:
        # shutdown spi
        spi.deinit()


main()
