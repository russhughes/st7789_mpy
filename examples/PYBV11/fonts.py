"""
fonts.py

    Pages through all characters of four fonts on on a ST7789 TFT display
    connected to a pyboard1.1.
"""

import utime
import random
from pyb import Pin, SPI
import st7789

import vga1_8x8 as font1
import vga1_8x16 as font2
import vga1_bold_16x16 as font3
import vga1_bold_16x32 as font4


def main():
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

    while True:
        for font in (font1, font2, font3, font4):
            tft.fill(st7789.BLUE)
            line = 0
            col = 0
            for char in range(font.FIRST, font.LAST):
                tft.text(font, chr(char), col, line, st7789.WHITE, st7789.BLUE)
                col += font.WIDTH
                if col > tft.width() - font.WIDTH:
                    col = 0
                    line += font.HEIGHT

                    if line > tft.height()-font.HEIGHT:
                        utime.sleep(3)
                        tft.fill(st7789.BLUE)
                        line = 0
                        col = 0

            utime.sleep(3)


main()
