"""
fonts.py

    Cycles through all characters of four bitmap fonts on the
    LILYGO® TTGO T-Watch-2020

"""

import utime
from machine import Pin, SPI
import st7789
import axp202c

import vga1_8x8 as font1
import vga1_8x16 as font2
import vga1_bold_16x16 as font3
import vga1_bold_16x32 as font4


def main():
    try:
        # Turn on display backlight
        axp = axp202c.PMU()
        axp.enablePower(axp202c.AXP202_LDO2)

        # initialize display spi port
        spi = SPI(
            1,
            baudrate=32000000,
            sck=Pin(18),
            mosi=Pin(19))

        # configure display
        tft = st7789.ST7789(
            spi,
            240,
            240,
            cs=Pin(5, Pin.OUT),
            dc=Pin(27, Pin.OUT),
            backlight=Pin(12, Pin.OUT),
            rotation=2)

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

    finally:
        # shutdown spi
        spi.deinit()

        # turn off display backlight
        axp.disablePower(axp202c.AXP202_LDO2)


main()
