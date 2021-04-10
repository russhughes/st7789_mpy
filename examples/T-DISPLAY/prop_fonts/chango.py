"""
chango.py test for font2bitmap converter.
"""

from machine import Pin, SPI
import st7789

import chango_16 as font_16
import chango_32 as font_32
import chango_64 as font_64


def main():

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
        tft.fill(st7789.BLACK)

        row = 0
        tft.write(font_16, "abcdefghijklmnopqrst", 0, row)
        row += font_16.HEIGHT

        tft.write(font_32, "abcdefghij", 0, row)
        row += font_32.HEIGHT

        tft.write(font_64, "abcd", 0, row)
        row += font_64.HEIGHT

    finally:
        # shutdown spi
        if 'spi' in locals():
            spi.deinit()


main()
