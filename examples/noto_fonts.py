"""
noto_fonts Writes the names of three Noto fonts centered on the display
    using the font. The fonts were converted from True Type fonts using
    the font2bitmap utility.
"""

from machine import Pin, SPI
import st7789

# Select a config module for your display
## import esp32_7735_128 as Driver          # Not suitable due to resolution
## import esp32_7735_160 as Driver          # Not suitable due to resolution
import esp32_st7789 as Driver
## import pybv11_st7789 as Driver
## import tdisplay as Driver
## import twatch_2020_v2 as Driver
## import ws_pico_114 as Driver
## import ws_pico_13 as Driver
## import ws_pico_2 as Driver

tft = Driver.config(1, buffer_size=16*32*2)

import NotoSans_32 as noto_sans
import NotoSerif_32 as noto_serif
import NotoSansMono_32 as noto_mono


def center(font, s, row, color=st7789.WHITE):
    screen = tft.width()                     # get screen width
    width = tft.write_len(font, s)           # get the width of the string
    if width and width < screen:             # if the string < display
        col = tft.width() // 2 - width // 2  # find the column to center
    else:                                    # otherwise
        col = 0                              # left justify

    tft.write(font, s, col, row, color)      # and write the string


def main():
    # init display
    tft.init()
    tft.fill(st7789.BLACK)

    # center the name of the first font, using the font
    row = 16
    center(noto_sans, "NotoSans", row, st7789.RED)
    row += noto_sans.HEIGHT

    # center the name of the second font, using the font
    center(noto_serif, "NotoSerif", row, st7789.GREEN)
    row += noto_serif.HEIGHT

    # center the name of the third font, using the font
    center(noto_mono, "NotoSansMono", row, st7789.BLUE)
    row += noto_mono.HEIGHT


main()
