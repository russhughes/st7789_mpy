"""
jpg.py

    Draw a full screen jpg using the slower but less memory intensive method of blitting
    each Minimum Coded Unit (MCU) block. Usually 8×8pixels but can be other multiples of 8.

    bigbuckbunny.jpg (c) copyright 2008, Blender Foundation / www.bigbuckbunny.org
"""

import gc
import random
from machine import Pin, SPI
import st7789

# Select a config module for your display
## import esp32_7735_128 as Driver
## import esp32_7735_160 as Driver
import esp32_st7789 as Driver
## import pybv11_st7789 as Driver
## import tdisplay as Driver
## import twatch_2020_v2 as Driver
## import ws_pico_114 as Driver
## import ws_pico_13 as Driver
## import ws_pico_2 as Driver

tft = Driver.config(1)


def main():
    '''
    Decode and draw jpg on display
    '''

    tft.init()
    tft.jpg(f'bigbuckbunny-{tft.width()}x{tft.height()}.jpg', 0, 0, st7789.SLOW)


main()
