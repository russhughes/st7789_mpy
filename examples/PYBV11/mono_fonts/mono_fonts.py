"""
mono_fonts.py for monofont2bitmap converter and bitmap method.
"""

import time
from pyb import Pin, SPI
import st7789

import inconsolata_16 as font_16
import inconsolata_32 as font_32
import inconsolata_64 as font_64


def main():
    fast = False

    def display_font(font):
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

    tft = st7789.ST7789(
        SPI(1, SPI.MASTER, baudrate=42000000, prescaler=2),
        240,
        320,
        reset=Pin('X3', Pin.OUT),
        cs=Pin('X5', Pin.OUT),
        dc=Pin('X4', Pin.OUT),
        backlight=Pin('X2', Pin.OUT),
        rotation=3)

    tft.init()
    tft.fill(st7789.BLUE)

    while True:
        for font in [font_16, font_32, font_64]:
            display_font(font)

        fast = not fast


main()
