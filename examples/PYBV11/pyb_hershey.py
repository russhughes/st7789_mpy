'''
pyb_hershey.py

    Demo program for a ST7789 TFT display connected to a pyboard1.1 that draws
    greetings on the display cycling thru hershey fonts and colors.

'''

import utime
import random
import sys
from pyb import SPI, Pin
import st7789

# Load several frozen fonts from flash

import gotheng
import greeks
import italicc
import italiccs
import meteo
import romanc
import romancs
import romand
import romanp
import romans
import romant
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
    gotheng, greeks, italicc, italiccs, meteo, romanc, romancs,
    romand, romanp, romans, romant, scriptc, scripts])

GREETINGS = cycle([
    "bonjour", "buenas noches", "buenos dias",
    "good day", "good morning", "hey",
    "hi-ya", "hi", "how are you", "how goes it",
    "howdy-do", "howdy", "shalom", "welcome",
    "what's happening", "what's up" ])

def main():
    '''
    Draw greetings on display cycling thru hershey fonts and colors
    '''
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
    tft.fill(st7789.BLACK)
    width = tft.width()
    row = 0

    while True:
        row += 32
        color = next(COLORS)
        tft.fill_rect(0, row-16, width, 32, st7789.BLACK)
        tft.draw(next(FONTS), next(GREETINGS), 0, row, color)

        if row > 192:
            row = 0

        utime.sleep(0.25)


main()
