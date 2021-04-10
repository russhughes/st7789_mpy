'''
jpg.py

    Draw a full screen jpg using the slower but less memory intensive method
    of blitting each Minimum Coded Unit (MCU) block. Usually 8×8 pixels but can
    be other multiples of 8.

    bigbuckbunny.jpg (c) copyright 2008, Blender Foundation / www.bigbuckbunny.org
'''

import gc
from machine import Pin, SPI
import st7789

gc.enable()
gc.collect()


def main():
    '''
    Decode and draw jpg on display
    '''
    try:
        spi = SPI(1, baudrate=30000000, sck=Pin(18), mosi=Pin(19))

        tft = st7789.ST7789(
            spi,
            135,
            240,
            reset=Pin(23, Pin.OUT),
            cs=Pin(5, Pin.OUT),
            dc=Pin(16, Pin.OUT),
            backlight=Pin(4, Pin.OUT),
            rotation=3)

        # enable display and clear screen
        tft.init()

        # display jpg
        tft.jpg("bigbuckbunny.jpg", 0, 0, st7789.SLOW)

    finally:
        # shutdown spi
        spi.deinit()


main()
