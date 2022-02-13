"""
chango.py proportional font test for font2bitmap converter.
"""

import time
import gc
import st7789
import tft_config

tft = tft_config.config(1)

#
# Large fonts take alot of memory, they should be frozen in the
# firmaware or compiled using the mpy-cross compiler.
#

import chango_16 as font_16
import chango_32 as font_32
import chango_64 as font_64

gc.collect()

def display_font(font):

    tft.fill(st7789.BLUE)                       # clear the screen
    column = 0                                  # first column
    row = 0                                     # first row

    for char in font.MAP:                       # for each character in the font map
        width = tft.write_len(font, char)       # get the width of the character

        if column + width > tft.width():        # if the character will not fit on the current line
            row += font.HEIGHT                  # move to the next row
            column = 0                          # reset the column

            if row+font.HEIGHT > tft.height():  # if the row will not fit on the screen
                time.sleep(1)                   # pause for a second
                tft.fill(st7789.BLUE)           # clear the screen
                row = 0                         # reset the row

        tft.write(                              # write to the screen
            font,                               # in this font
            char,                               # the character
            column,                             # at this column
            row,                                # on this row
            st7789.WHITE,                       # in white
            st7789.BLUE)                        # with blue background

        column += width                         # move the column past the character

def main():
    tft.init()
    tft.fill(st7789.BLUE)

    for font in [font_16, font_32, font_64]:    # for each font
        display_font(font)                      # display the font characters
        time.sleep(1)                           # pause for a second


main()
