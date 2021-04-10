'''
jpg.py

    Randomly draw a jpg using the fast method

    The alien.jpg is from the Erik Flowers Weather Icons available from
    https://github.com/erikflowers/weather-icons and is licensed under
    SIL OFL 1.1

    It was was converted from the wi-alien.svg icon using
    ImageMagick's convert utility:

    convert wi-alien.svg -type TrueColor alien.jpg
'''

import gc
import random
from machine import Pin, SPI
import st7789

gc.enable()
gc.collect()


def main():
    '''
    Decode and draw jpg on display
    '''
    try:
        spi = SPI(1, baudrate=30000000, sck=Pin(18), mosi=Pin(19))

        tft = st7789.ST7789(
            spi,
            135,
            240,
            reset=Pin(23, Pin.OUT),
            cs=Pin(5, Pin.OUT),
            dc=Pin(16, Pin.OUT),
            backlight=Pin(4, Pin.OUT),
            rotation=3,
            buffer_size = 30*30*2)

        # enable display and clear screen
        tft.init()

        # display jpg in random locations
        while True:
            tft.rotation(random.randint(0, 4))
            tft.jpg(
                "alien.jpg",
                random.randint(0, tft.width() - 30),
                random.randint(0, tft.height() - 30),
                st7789.FAST)

    finally:
        # shutdown spi
        spi.deinit()


main()
