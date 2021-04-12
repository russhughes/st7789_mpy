"""
chango.py

     Test for font2bitmap converter for a ST7789 display
    connected to a Raspberry Pi Pico.

    Pico Pin   Display
    =========  =======
    14 (GP10)  BL
    15 (GP11)  RST
    16 (GP12)  DC
    17 (GP13)  CS
    18 (GND)   GND
    19 (GP14)  CLK
    20 (GP15)  DIN
"""

from machine import Pin, SPI
import st7789

import chango_16 as font_16
import chango_32 as font_32
import chango_64 as font_64


def main():

    spi = SPI(1, baudrate=40000000, sck=Pin(14), mosi=Pin(15))
    tft = st7789.ST7789(
        spi,
        240,
        320,
        reset=Pin(11, Pin.OUT),
        cs=Pin(13, Pin.OUT),
        dc=Pin(12, Pin.OUT),
        backlight=Pin(10, Pin.OUT),
        rotation=3)

    # enable display and clear screen
    tft.init()
    tft.fill(st7789.BLACK)

    row = 0

    tft.write(font_16, "abcdefghijklmnopqrstuvwxyz", 0, row)
    row += font_16.HEIGHT

    tft.write(font_32, "abcdefghijklm", 0, row)
    row += font_32.HEIGHT

    tft.write(font_32, "nopqrstuvwxy", 0, row)
    row += font_32.HEIGHT

    tft.write(font_64, "abcdef", 0, row)
    row += font_64.HEIGHT

    tft.write(font_64, "ghijkl", 0, row)
    row += font_64.HEIGHT


main()
