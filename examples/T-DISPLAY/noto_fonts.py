"""
noto_fonts Writes the names of three Noto fonts centered on the display 
    using the font. The fonts were converted from True Type fonts using 
    the font2bitmap utility.
"""

from machine import Pin, SPI
import st7789

import NotoSans_32 as noto_sans
import NotoSerif_32 as noto_serif
import NotoSansMono_32 as noto_mono


def main():

    def center(font, s, row, color=st7789.WHITE):
        screen = tft.width()                     # get screen width
        width = tft.write_len(font, s)           # get the width of the string
        if width and width < screen:             # if the string < display
            col = tft.width() // 2 - width // 2  # find the column to center
        else:                                    # otherwise
            col = 0                              # left justify

        tft.write(font, s, col, row, color)      # and write the string

    try:
        # initialize the SPI
        spi = SPI(1, baudrate=30000000, sck=Pin(18), mosi=Pin(19))

        # confgure the display
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

    finally:
        # shutdown spi
        if 'spi' in locals():
            spi.deinit()


main()
