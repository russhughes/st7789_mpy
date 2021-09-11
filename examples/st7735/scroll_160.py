"""
scroll.py

    Smoothly scroll all characters of a font a 128x160 st7735 Display.
    Fonts heights must be even multiples of the screen height
    (i.e. 8 or 16 pixels high).
"""

import utime
from machine import Pin, SPI
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
        SPI(1, baudrate=30000000, sck=Pin(19), mosi=Pin(18)),
        128,
        160,
        reset=Pin(4, Pin.OUT),
        cs=Pin(13, Pin.OUT),
        dc=Pin(12, Pin.OUT),
        backlight=Pin(15, Pin.OUT),
        color_order=st7789.RGB,
        rotation=0)

    tft.init()
    tft.inversion_mode(False)

    colors = cycle([0xe000, 0xece0, 0xe7e0, 0x5e0, 0x00d3, 0x7030])
    foreground = next(colors)
    background = st7789.BLACK

    tft.fill(background)
    utime.sleep(1)

    height = tft.height()
    width = tft.width()
    last_line = height - font.HEIGHT

    tfa = 0        # top free area
    tfb = 0        # bottom free area
    #tft.vscrdef(tfa, height, tfb)

    scroll = 0
    character = font.FIRST

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
                16,
                line,
                foreground,
                background)

            # write character using a integer (could be > 0x7f)
            tft.text(
                font,
                character,
                90,
                line,
                foreground,
                background)

            # change color for next line
            foreground = next(colors)

            # next character with rollover at 256
            character += 1
            if character > font.LAST:
                character = font.FIRST

        # scroll the screen up 1 row
        tft.vscsad(scroll+tfa)
        scroll += 1
        scroll %= height

        utime.sleep(0.01)


main()
