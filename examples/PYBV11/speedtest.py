"""
speedtest.py

    Speed test writing text on a ST7789 TFT display connected to a pyboard1.1.
"""

from pyb import Pin, SPI
import st7789 as st7789
import utime

import vga1_8x16 as font


def main():

    spi = SPI(1, SPI.MASTER, baudrate=42000000, prescaler=2)
    print(spi)

    # configure display
    tft = st7789.ST7789(
        spi, 240, 320,
        reset=Pin('X3', Pin.OUT),
        cs=Pin('X5', Pin.OUT),
        dc=Pin('X4', Pin.OUT),
        backlight=Pin('X2', Pin.OUT),
        rotation=3)

    tft.init()
    tft.fill(st7789.BLACK)

    start = utime.ticks_ms()
    tft.text(font, "MicroPython MicroPython MicroPython", 0, 0,  st7789.WHITE)
    tft.text(font, "MicroPython MicroPython MicroPython", 0, 32, st7789.RED)
    tft.text(font, "MicroPython MicroPython MicroPython", 0, 64, st7789.GREEN)
    tft.text(font, "MicroPython MicroPython MicroPython", 0, 96, st7789.BLUE)
    tft.text(font, "MicroPython MicroPython MicroPython", 0, 128,  st7789.WHITE)
    tft.text(font, "MicroPython MicroPython MicroPython", 0, 160, st7789.RED)
    tft.text(font, "MicroPython MicroPython MicroPython", 0, 192, st7789.GREEN)
    tft.text(font, "MicroPython MicroPython MicroPython", 0, 224, st7789.BLUE)

    print("time:", utime.ticks_ms() - start, "ms")


main()
