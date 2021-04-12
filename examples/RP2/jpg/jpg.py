'''
jpg.py

    Draw a full screen jpg using the slower but less memory intensive method
    of blitting each Minimum Coded Unit (MCU) block. Usually 8×8 pixels but can
    be other multiples of 8.

    ST7789 display connected to a Raspberry Pi Pico.

    Pico Pin   Display
    =========  =======
    14 (GP10)  BL
    15 (GP11)  RST
    16 (GP12)  DC
    17 (GP13)  CS
    18 (GND)   GND
    19 (GP14)  CLK
    20 (GP15)  DIN

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
    spi = SPI(1, baudrate=40000000, sck=Pin(14), mosi=Pin(15))
    tft = st7789.ST7789(
        spi,
        240,
        320,
        reset=Pin(11, Pin.OUT),
        cs=Pin(13, Pin.OUT),
        dc=Pin(12, Pin.OUT),
        backlight=Pin(10, Pin.OUT),
        rotation=3)

    # enable display and clear screen
    tft.init()

    # display jpg
    tft.jpg("bigbuckbunny.jpg", 0, 0, st7789.SLOW)


main()
