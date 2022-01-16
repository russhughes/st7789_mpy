"""
hello.py

    Writes "Hello!" in random colors at random locations on the display.
"""

import random
from machine import Pin, SPI
import utime
import st7789
import vga1_bold_16x32 as font

# Select a config module for your display
## import esp32_7735_128 as Driver
## import esp32_7735_160 as Driver
import esp32_st7789 as Driver
## import pybv11_st7789 as Driver
## import tdisplay as Driver
## import twatch_2020_v2 as Driver
## import ws_pico_114 as Driver
## import ws_pico_13 as Driver
## import ws_pico_2 as Driver

tft = Driver.config(0)

def center(text):
    length = len(text)
    tft.text(
        font,
        text,
        tft.width() // 2 - length // 2 * font.WIDTH,
        tft.height() // 2 - font.HEIGHT,
        st7789.WHITE,
        st7789.RED)

def main():
    tft.init()

    tft.fill(st7789.RED)
    center("Hello!")
    utime.sleep(2)
    tft.fill(st7789.BLACK)

    while True:
        for rotation in range(4):
            tft.rotation(rotation)
            tft.fill(0)
            col_max = tft.width() - font.WIDTH*6
            row_max = tft.height() - font.HEIGHT

            for _ in range(128):
                tft.text(
                    font,
                    "Hello!",
                    random.randint(0, col_max),
                    random.randint(0, row_max),
                    st7789.color565(
                        random.getrandbits(8),
                        random.getrandbits(8),
                        random.getrandbits(8)),
                    st7789.color565(
                        random.getrandbits(8),
                        random.getrandbits(8),
                        random.getrandbits(8)))


main()
