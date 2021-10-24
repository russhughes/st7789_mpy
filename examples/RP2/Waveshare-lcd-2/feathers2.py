"""
feathers2.py
    Smoothly scroll rainbow colored random curves across the front of a Waveshare Pico LCD 1.3
    Display Module using a Raspberry Pi PICO.

    Video: https://youtu.be/ZKrKsz7_CXo
"""

import random
import math
import utime
from machine import Pin, SPI
import st7789


def between(left, right, along):
    """returns a point along the curve from left to right"""
    d = (1 - math.cos(along * math.pi)) / 2
    return left * (1 - d) + right * d


def color_wheel(WheelPos):
    """returns a 565 color from the given position of the color wheel"""
    WheelPos = (255 - WheelPos) % 255

    if WheelPos < 85:
        return st7789.color565(255 - WheelPos * 3, 0, WheelPos * 3)

    if WheelPos < 170:
        WheelPos -= 85
        return st7789.color565(0, WheelPos * 3, 255 - WheelPos * 3)

    WheelPos -= 170
    return st7789.color565(WheelPos * 3, 255 - WheelPos * 3, 0)


def main():
    # configure spi interface
    spi = SPI(1, baudrate=31250000, sck=Pin(10), mosi=Pin(11))

    # initialize display
    tft = st7789.ST7789(
        spi,
        240,
        320,
        reset=Pin(12, Pin.OUT),
        cs=Pin(9, Pin.OUT),
        dc=Pin(8, Pin.OUT),
        backlight=Pin(13, Pin.OUT),
        rotation=1)

    # enable display and clear screen
    tft.init()

    height = tft.height()
    width = tft.width()

    tfa = 0        # top free area
    bfa = 0       # bottom free area

    scroll = 0
    wheel = 0

    tft.vscrdef(tfa, width, bfa)
    tft.vscsad(scroll+tfa)
    tft.fill(st7789.BLACK)

    h = (height >> 1) - 1       # half the height of the dislay
    interval = 50               # steps between new points
    increment = 1/interval      # increment per step
    counter = interval + 1      # step counter, overflow to start
    current_y = 0               # current_y value (right point)
    last_y = 0                  # last_y value (left point)

    x_offsets = []

    while True:
        # when the counter exceeds the interval, save current_y to last_y,
        # choose a new random value for current_y between 0 and 1/2 the
        # height of the display, choose a new random interval then reset
        # the counter to 0

        if counter > interval:
            offsets = random.randint(4, 32)
            x_offsets = [width//offsets*(x+1)-1 for x in range(offsets)]
            last_y = current_y
            current_y = random.randint(0, h)
            counter = 0
            interval = random.randint(10, 100)


        # clear the first column of the display and scroll it
        tft.vline(scroll, 0, height, st7789.BLACK)
        tft.vscsad(scroll)

        # get the next point between last_y and current_y
        tween = int(between(last_y, current_y, counter * increment))

        # draw mirrored pixels across the display at the offsets using the color_wheel effect
        for i, x_offset in enumerate(x_offsets):
            tft.pixel((scroll+x_offset) % width, h + tween, color_wheel(wheel+(i<<2)))
            tft.pixel((scroll+x_offset) % width, h - tween, color_wheel(wheel+(i<<2)))

        # increment scroll, counter, and wheel
        scroll += 1
        scroll %= width
        counter += 1
        wheel += 1
        wheel %= 256

        # pause to slow down scrolling
        utime.sleep(0.01)


main()
