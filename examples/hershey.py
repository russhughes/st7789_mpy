"""
hershey.py

    Demo program that draws greetings on display cycling thru hershey fonts and colors.

"""

import random
import utime
import st7789
import tft_config

tft = tft_config.config(0, options=st7789.WRAP_V)

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
    """return the next item in a list"""
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


# Create a cycle of colors
COLORS = cycle([0xe000, 0xece0, 0xe7e0, 0x5e0, 0x00d3, 0x7030])

# List Hershey fonts
FONT = [greeks, italicc, italiccs, meteo, romanc, romancs, romand, romanp, romans, scriptc, scripts]

# Create a cycle of tuples consisting of a FONT[] and the HEIGHT of the next FONT[] in the cycle
FONTS = cycle([
    (font, FONT[(i + 1) % len(FONT)].HEIGHT)
        for i, font in enumerate(FONT)])

# Greetings
GREETING = [
    "Ahoy", "Bonjour", "Bonsoir", "Buenos Dias", "Buenas tardes", "Buenas Noches", "Ciao", "Dude",
    "Good Morning", "Good Day", "Good Evening", "Hello", "Hey", "Hi", "Hiya", "Hola", "How Are You",
    "How Goes It", "Howdy", "How you doing", "Konnichiwa","Salut", "Shalom", "Welcome", "What's Up",
    'Yo!']

# Create a cycle of tuples consisting of a list of words from a GREETING, the number of spaces+1
# in the that GREETING, and the number of spaces+1 in the next GREETING of the cycle
GREETINGS = cycle([
    (greeting.split(), greeting.count(' ')+1, GREETING[(i + 1) % len(GREETING)].count(' ')+1)
        for i, greeting in enumerate(GREETING)])


def main():
    """Scroll greetings on the display cycling thru Hershey fonts and colors"""

    tft.init()
    tft.fill(st7789.BLACK)

    height = tft.height()
    width = tft.width()

    # Set up scrolling area
    tfa = tft_config.TFA
    bfa = tft_config.BFA
    tft.vscrdef(tfa, height, bfa)

    scroll = 0
    to_scroll = 0

    while True:

        # if we have scrolled high enough for the next greeting
        if to_scroll == 0:
            font = next(FONTS)                              # get the next font
            greeting = next(GREETINGS)                      # get the next greeting
            color = next(COLORS)                            # get the next color
            lines = greeting[2]                             # number of lines in the greeting
            to_scroll = lines * font[1] + 8                 # number of rows to scroll

            # draw each line of the greeting
            for i, word in enumerate(greeting[0][::-1]):
                word_len = tft.draw_len(font[0], word)                          # width in pixels
                col = 0 if word_len > width else (width//2 - word_len//2)       # column to center
                row = (scroll + height - ((i + 1) * font[0].HEIGHT) % height)   # row to draw
                tft.draw(font[0], word, col, row, color)                        # draw the word

        tft.fill_rect(0, scroll, width, 1, st7789.BLACK)    # clear the top line
        tft.vscsad(scroll+tfa)                              # scroll the display
        scroll = (scroll+1) % height                        # update the scroll position
        to_scroll -= 1                                      # update rows left to scroll
        utime.sleep(0.02)                                   # stop and smell the roses


main()
