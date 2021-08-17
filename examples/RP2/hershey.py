'''
hershey.py

    Demo program that draws greetings on a ST7789 display
    connected to a Raspberry Pi Pico cycling  thru hershey
    fonts and colors.

    Pico Pin   Display
    =========  =======
    14 (GP10)  BL
    15 (GP11)  RST
    16 (GP12)  DC
    17 (GP13)  CS
    18 (GND)   GND
    19 (GP14)  CLK
    20 (GP15)  DIN
'''

import utime
from machine import Pin, SPI
import st7789

# Load several frozen fonts from flash

import greeks
import italicc
import italiccs
import meteo
import romanc
import romancs
import romand
import romanp
import romans
import scriptc
import scripts


def cycle(p):
    '''
    return the next item in a list
    '''
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


COLORS = cycle([0xe000, 0xece0, 0xe7e0, 0x5e0, 0x00d3, 0x7030])

FONTS = cycle([
    greeks, italicc, italiccs, meteo, romanc, romancs,
    romand, romanp, romans, scriptc, scripts])

GREETINGS = cycle([
    "bonjour", "buenas noches", "buenos dias",
    "good day", "good morning", "hey",
    "hi-ya", "hi", "how are you", "how goes it",
    "howdy-do", "howdy", "shalom", "welcome",
    "what's happening", "what's up"])


def main():
    '''
    Draw greetings on display cycling thru hershey fonts and colors
    '''
    # configure display
    spi = SPI(1, baudrate=31250000, sck=Pin(14), mosi=Pin(15))
    tft = st7789.ST7789(
        spi,
        240,
        320,
        reset=Pin(11, Pin.OUT),
        cs=Pin(13, Pin.OUT),
        dc=Pin(12, Pin.OUT),
        backlight=Pin(10, Pin.OUT),
        rotation=3)

    tft.init()
    tft.fill(st7789.BLACK)
    width = tft.width()

    while True:
        for line in range(1, 7):
            row = line * 32
            color = next(COLORS)
            tft.fill_rect(0, row-16, width, 38, st7789.BLACK)
            tft.draw(next(FONTS), next(GREETINGS), 0, row, color)
            utime.sleep(0.25)


main()
