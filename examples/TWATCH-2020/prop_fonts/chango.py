"""
chango.py test for font2bitmap converter.
"""

import time
import gc
from machine import Pin, SPI
import axp202c
import st7789

import chango_16 as font_16
import chango_32 as font_32
import chango_64 as font_64

gc.collect()


def main():
    try:
        # Turn power on display power
        axp = axp202c.PMU()
        axp.enablePower(axp202c.AXP202_LDO2)

        # initialize spi port
        spi = SPI(
            1,
            baudrate=32000000,
            sck=Pin(18, Pin.OUT),
            mosi=Pin(19, Pin.OUT))

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
        tft.fill(st7789.BLUE)
        row = font_16.HEIGHT

        tft.write(font_16, "abcdefghijklmnopqrst", 0, row, st7789.WHITE, st7789.BLUE)
        row += font_16.HEIGHT

        tft.write(font_32, "abcdefghij", 0, row, st7789.WHITE, st7789.BLUE)
        row += font_32.HEIGHT

        tft.write(font_32, "klmnopqrs", 0, row, st7789.WHITE, st7789.BLUE)
        row += font_32.HEIGHT

        tft.write(font_32, "tuvwxyz", 0, row, st7789.WHITE, st7789.BLUE)
        row += font_32.HEIGHT

        tft.write(font_64, "abcd", 0, row, st7789.WHITE, st7789.BLUE)
        row += font_64.HEIGHT

    finally:
        # shutdown spi
        spi.deinit()
        # turn off display power
        # axp.disablePower(axp202c.AXP202_LDO2)


main()
