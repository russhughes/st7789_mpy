"""
hello_128.py

    Writes "Hello!" in random colors at random locations on a
    128x128 st7735 Display.
"""

import random
from machine import Pin, SPI
import st7789

import vga1_bold_16x32 as font

COLSTART = const(0)
ROWSTART = const(1)

def main():
    tft = st7789.ST7789(
        SPI(1, baudrate=30000000, sck=Pin(19), mosi=Pin(18)),
        128,
        128,
        reset=Pin(4, Pin.OUT),
        cs=Pin(13, Pin.OUT),
        dc=Pin(12, Pin.OUT),
        backlight=Pin(15, Pin.OUT),
        color_order=st7789.BGR,
        rotation=0)

    tft.init()
    tft.inversion_mode(False)

    offsets = [(2, 1), (1, 2), (2, 3), (3, 2)]

    while True:
        for rotation in range(4):
            tft.rotation(rotation)
            tft.offset(offsets[rotation][COLSTART], offsets[rotation][ROWSTART])

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
                        random.getrandbits(8))
                )


main()
