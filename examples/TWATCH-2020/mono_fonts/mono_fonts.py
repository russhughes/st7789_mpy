"""
mono_fonts.py for monofont2bitmap converter and bitmap method.
"""

import time
from machine import Pin, SPI
import axp202c
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
            rotation=2,
            buffer_size=66*32*2)

        tft.init()

        while True:
            for font in [font_16, font_32, font_64]:
                display_font(font)

            fast = not fast

    finally:
        # shutdown spi
        spi.deinit()
        # turn off display power
        axp.disablePower(axp202c.AXP202_LDO2)


main()
