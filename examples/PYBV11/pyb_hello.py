"""
pyb_hello.py

    Writes "Hello!" in random colors at random locations on a
    on a ST7789 TFT display connected to a pyboard1.1.

    https://youtu.be/OtcERmad5ps
"""
import random, time
from pyb import SPI, Pin
import st7789

import vga1_bold_16x32 as font

def main():
    tft = st7789.ST7789(
        SPI(1, SPI.MASTER, baudrate=30000000, polarity=1, phase=0),
        240,
        320,
        reset=Pin('X3', Pin.OUT),
        cs=Pin('X5', Pin.OUT),
        dc=Pin('X4', Pin.OUT),
        backlight=Pin('X2', Pin.OUT),
        rotation=3)

    tft.init()

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
                        random.getrandbits(8))
                )

main()
