"""
jpg.py

    Draw a full screen jpg using the slower but less memory intensive method of blitting
    each Minimum Coded Unit (MCU) block. Usually 8×8pixels but can be other multiples of 8.

    bigbuckbunny.jpg (c) copyright 2008, Blender Foundation / www.bigbuckbunny.org
"""

import random
import st7789
import tft_config

tft = tft_config.config(1)

def main():
    '''
    Decode and draw jpg on display
    '''

    tft.init()
    tft.jpg(f'bigbuckbunny-{tft.width()}x{tft.height()}.jpg', 0, 0, st7789.SLOW)


main()
