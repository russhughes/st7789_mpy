"""
mono_fonts.py test for monofont2bitmap converter and bitmap method. This is the older method of
converting monofonts to bitmaps.  See the newer method in prop_fonts/chango.py that works with
mono and proportional fonts using the write method.
"""

import time
import gc
from machine import Pin, SPI
import st7789

import time
from machine import Pin, SPI
import st7789

import inconsolata_16 as font_16
import inconsolata_32 as font_32
import inconsolata_64 as font_64

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

tft = Driver.config(1, buffer_size=66*32*2)

def display_font(font, fast):
    tft.fill(st7789.BLUE)
    column = 0
    row = 0
    for char in font.MAP:
        tft.bitmap(font, column, row, font.MAP.index(char))
        column += font.WIDTH
        if column >= tft.width() - font.WIDTH:
            row += font.HEIGHT
            column = 0

            if row > tft.height() - font.HEIGHT:
                row = 0

        if not fast:
            time.sleep(0.05)


def main():
    fast = False

    tft.init()

    while True:
        for font in [font_16, font_32, font_64]:
            display_font(font, fast)

        fast = not fast


main()
