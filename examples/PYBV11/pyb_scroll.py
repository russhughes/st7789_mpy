"""
pyb_scroll.py

    Smoothly scroll all characters of a font up the screen. Fonts heights
    must be even multiples of the screen height (i.e. 8 or 16 pixels high).

    https://youtu.be/ro13rvaLKAc
"""

import utime
import random
from pyb import SPI, Pin
import st7789

import vga1_bold_16x16 as font

def cycle(p):
    try:
        len(p)
    except TypeError:
        cache = []
        for i in p:
            yield i
            cache.append(i)
        p = cache
    while p:
        yield from p

def main():
    tft = st7789.ST7789(
        SPI(1, SPI.MASTER, baudrate=30000000, polarity=1, phase=0),
        240,
        320,
        reset=Pin('X3', Pin.OUT),
        cs=Pin('X5', Pin.OUT),
        dc=Pin('X4', Pin.OUT),
        backlight=Pin('X2', Pin.OUT),
        rotation=0)

    colors = cycle([0xe000, 0xece0, 0xe7e0, 0x5e0, 0x00d3, 0x7030])
    foreground = next(colors)
    background = st7789.BLACK

    tft.init()
    tft.fill(background)
    utime.sleep(1)

    height = tft.height()
    width = tft.width()
    last_line = height - font.HEIGHT

    tfa = 0
    tfb = 0
    tft.vscrdef(tfa, height, tfb)

    scroll = 0
    character = 0

    while True:
        # clear top line before scrolling off display
        tft.fill_rect(0, scroll, width, 1, background)

        # Write new line when we have scrolled the height of a character
        if scroll % font.HEIGHT == 0:
            line = (scroll + last_line) % height

            # write character hex value as a string
            tft.text(
                font,
                'x{:02x}'.format(character),
                0,
                line,
                foreground,
                background)

            # write character using a integer (could be > 0x7f)
            tft.text(
                font,
                character,
                64,
                line,
                foreground,
                background)

            # write character+64 hex value as a string
            tft.text(
                font,
                'x{:02x}'.format(character+64),
                120,
                line,
                foreground,
                background)

            # write character+64 using a integer (could be > 0x7f)
            tft.text(
                font,
                character+64,
                184,
                line,
                foreground,
                background)

            # change color for next line
            foreground = next(colors)

            # next character with rollover at 256
            character += 1
            character %= 64

        tft.vscsad(scroll+tfa)
        scroll +=1
        scroll %= height

        utime.sleep(0.01)

main()
