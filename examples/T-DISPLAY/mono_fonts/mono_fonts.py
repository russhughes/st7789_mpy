"""
mono_fonts.py for monofont2bitmap converter and bitmap method.
"""

import time
from machine import Pin, SPI
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
        SPI(1, baudrate=30000000, sck=Pin(18), mosi=Pin(19)),
        135,
        240,
        reset=Pin(23, Pin.OUT),
        cs=Pin(5, Pin.OUT),
        dc=Pin(16, Pin.OUT),
        backlight=Pin(4, Pin.OUT),
        rotation=3)

    tft.init()

    while True:
        for font in [font_16, font_32, font_64]:
            display_font(font)

        fast = not fast


main()
