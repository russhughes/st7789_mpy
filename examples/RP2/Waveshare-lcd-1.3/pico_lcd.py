
from machine import Pin, SPI
import micropython
import time
import os
import st7789


def main():
    """Waveshare Pico LCD 1.3 demo modified to run using this driver"""
    micropython.kbd_intr(3)
    # configure spi interface
    spi = SPI(1, baudrate=31250000, sck=Pin(10), mosi=Pin(11))

    # initialize display
    tft = st7789.ST7789(
        spi,
        240,
        240,
        reset=Pin(12, Pin.OUT),
        cs=Pin(9, Pin.OUT),
        dc=Pin(8, Pin.OUT),
        backlight=Pin(13, Pin.OUT),
        rotation=1,
        buffer_size=64*64*2)

    # enable display and clear screen
    tft.init()
    tft.fill(st7789.WHITE)

    keyA = Pin(15, Pin.IN, Pin.PULL_UP)
    keyB = Pin(17, Pin.IN, Pin.PULL_UP)
    keyX = Pin(19, Pin.IN, Pin.PULL_UP)
    keyY = Pin(21, Pin.IN, Pin.PULL_UP)

    up = Pin(2, Pin.IN, Pin.PULL_UP)
    down = Pin(18, Pin.IN, Pin.PULL_UP)
    left = Pin(16, Pin.IN, Pin.PULL_UP)
    right = Pin(20, Pin.IN, Pin.PULL_UP)
    ctrl = Pin(3, Pin.IN, Pin.PULL_UP)

    while True:
        if keyA.value() == 0:
            tft.fill_rect(208, 15, 30, 30, st7789.RED)
            print("A")
        else:
            tft.fill_rect(208, 15, 30, 30, st7789.WHITE)
            tft.rect(208, 15, 30, 30, st7789.RED)

        if keyB.value() == 0:
            tft.fill_rect(208, 75, 30, 30, st7789.RED)
            print("B")
        else:
            tft.fill_rect(208, 75, 30, 30, st7789.WHITE)
            tft.rect(208, 75, 30, 30, st7789.RED)

        if keyX.value() == 0:
            tft.fill_rect(208, 135, 30, 30, st7789.RED)
            print("C")
        else:
            tft.fill_rect(208, 135, 30, 30, st7789.WHITE)
            tft.rect(208, 135, 30, 30, st7789.RED)

        if keyY.value() == 0:
            tft.fill_rect(208, 195, 30, 30, st7789.RED)
            print("D")
        else:
            tft.fill_rect(208, 195, 30, 30, st7789.WHITE)
            tft.rect(208, 195, 30, 30, st7789.RED)

        if up.value() == 0:
            tft.fill_rect(60, 60, 30, 30, st7789.RED)
            print("UP")
        else:
            tft.fill_rect(60, 60, 30, 30, st7789.WHITE)
            tft.rect(60, 60, 30, 30, st7789.RED)

        if down.value() == 0:
            tft.fill_rect(60, 150, 30, 30, st7789.RED)
            print("DOWM")
        else:
            tft.fill_rect(60, 150, 30, 30, st7789.WHITE)
            tft.rect(60, 150, 30, 30, st7789.RED)

        if left.value() == 0:
            tft.fill_rect(15, 105, 30, 30, st7789.RED)
            print("LEFT")
        else:
            tft.fill_rect(15, 105, 30, 30, st7789.WHITE)
            tft.rect(15, 105, 30, 30, st7789.RED)

        if right.value() == 0:
            tft.fill_rect(105, 105, 30, 30, st7789.RED)
            print("RIGHT")
        else:
            tft.fill_rect(105, 105, 30, 30, st7789.WHITE)
            tft.rect(105, 105, 30, 30, st7789.RED)

        if ctrl.value() == 0:
            tft.fill_rect(60, 105, 30, 30, st7789.RED)
            print("CTRL")
        else:
            tft.fill_rect(60, 105, 30, 30, st7789.WHITE)
            tft.rect(60, 105, 30, 30, st7789.RED)


main()
