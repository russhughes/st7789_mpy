"""
paint.py

    A very simple paint program for the TTGO T-Watch-2020
    using the adafruit_focaltouch driver modified for micropython by franz
    schaefer from https://gitlab.com/mooond/t-watch2020-esp32-with-micropython
    See the lib directory for the focaltouch and axp202c drivers.

    https://www.youtube.com/watch?v=O_lDBnvH1Sw

"""

from machine import Pin, SPI, SoftI2C
import axp202c
import st7789
import focaltouch
import vga1_8x8 as font

# color swatches
COLORS = [
    st7789.BLACK,
    st7789.BLUE,
    st7789.RED,
    st7789.GREEN,
    st7789.CYAN,
    st7789.MAGENTA,
    st7789.YELLOW,
    st7789.WHITE]


def main():
    '''
    Draw on screen using focaltouch sensor
    '''
    try:
        # Turn on display backlight
        axp = axp202c.PMU()
        axp.enablePower(axp202c.AXP202_LDO2)

        # initialize display spi port
        spi = SPI(
            1,
            baudrate=32000000,
            polarity=1,
            phase=0,
            bits=8,
            firstbit=0,
            sck=Pin(18, Pin.OUT),
            mosi=Pin(19, Pin.OUT))

        # configure display
        tft = st7789.ST7789(
            spi,
            240,
            240,
            cs=Pin(5, Pin.OUT),
            dc=Pin(27, Pin.OUT),
            backlight=Pin(12, Pin.OUT),
            rotation=2)

        # enable display and clear screen
        tft.init()
        tft.fill(st7789.BLACK)
        tft.text(font, "Draw", 104, 1, st7789.WHITE)

        # enable focaltouch touchscreen
        touch_i2c = SoftI2C(scl=Pin(32), sda=Pin(23))
        touch = focaltouch.FocalTouch(touch_i2c)

        color_index = 0
        color = 0
        # draw color swatches used to select color to draw
        for color_index, color in enumerate(COLORS):
            tft.fill_rect(color_index*30, 210, 30, 30, color)

        add_highlight(tft, color_index)
        while True:
            # can be up to two touches
            if touch.touched == 1:

                # get x and y points of the first touch
                p_x = touch.touches[0]['x']
                p_y = touch.touches[0]['y']

                # If point is in the lowest 30 rows of the screen
                # change color to swatch pressed.
                if p_y > 209:
                    # remove highlight from around previous color swatch
                    remove_highlight(tft, color_index, color)

                    # update new color
                    color_index = p_x//30
                    color = COLORS[color_index]

                    add_highlight(tft, color_index)
                else:
                    # draw the pixel - would be better with lines
                    tft.pixel(p_x, p_y, color)

    finally:
        # shutdown spi
        spi.deinit()

        # turn off display backlight
        axp.disablePower(axp202c.AXP202_LDO2)

def remove_highlight(tft, color_index, color):
    # remove highlight around previously selected color swatch
    tft.rect(color_index*30, 210, 30, 30, color)
    tft.rect(color_index*30+1, 211, 28, 28, color)
    tft.rect(color_index*30+2, 212, 26, 26, color)

def add_highlight(tft, color_index):
    # draw highlight around newly selected color swatch
    tft.rect(color_index*30, 210, 30, 30, st7789.WHITE)
    tft.rect(color_index*30+1, 211, 28, 28, st7789.BLACK)
    tft.rect(color_index*30+2, 212, 26, 26, st7789.BLACK)


main()
