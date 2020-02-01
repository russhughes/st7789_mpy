"""
ttgo_fonts.py

    Pages through all characters of four fonts on the LILYGO® TTGO T-Display.

    https://www.youtube.com/watch?v=2cnAhEucPD4

"""
import utime
import random
from machine import Pin, SPI
import st7789

# Choose fonts

import vga1_8x8 as font1
#import vga2_8x8 as font1

import vga1_8x16 as font2
#import vga2_8x16 as font2

# import vga1_16x16 as font3
import vga1_bold_16x16 as font3
# import vga2_16x16 as font3
#import vga2_bold_16x16 as font3

# import vga1_16x32 as font4
import vga1_bold_16x32 as font4
# import vga2_16x32 as font4
#import vga2_bold_16x32 as font4

def main():
    tft = st7789.ST7789(
        SPI(2, baudrate=30000000, polarity=1, phase=1, sck=Pin(18), mosi=Pin(19)),
        135,
        240,
        reset=Pin(23, Pin.OUT),
        cs=Pin(5, Pin.OUT),
        dc=Pin(16, Pin.OUT),
        backlight=Pin(4, Pin.OUT),
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
