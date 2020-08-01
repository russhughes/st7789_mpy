'''
watch_draw.py

    A very simple drawing program for the TTGO T-Watch-2020
    using the adafruit_focaltouch driver modified for micropython by franz
    schaefer from https://gitlab.com/mooond/t-watch2020-esp32-with-micropython

    https://www.youtube.com/watch?v=O_lDBnvH1Sw

'''

import machine
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
        spi = machine.SPI(
            2,
            baudrate=32000000,
            polarity=1,
            phase=0,
            bits=8,
            firstbit=0,
            sck=machine.Pin(18, machine.Pin.OUT),
            mosi=machine.Pin(19, machine.Pin.OUT))

        # configure display
        tft = st7789.ST7789(
            spi,
            240,
            240,
            cs=machine.Pin(5, machine.Pin.OUT),
            dc=machine.Pin(27, machine.Pin.OUT),
            backlight=machine.Pin(12, machine.Pin.OUT),
            rotation=2)

        # enable display and clear screen
        tft.init()
        tft.fill(st7789.BLACK)
        tft.text(font, "Draw", 104, 1, st7789.WHITE)

        # enable focaltouch touchscreen
        touch_i2c = machine.I2C(scl=machine.Pin(32), sda=machine.Pin(23))
        touch = focaltouch.FocalTouch(touch_i2c)

        color_index = 0
        color = 0
        # draw color swatches used to select color to draw
        for color_index, color in enumerate(COLORS):
            tft.fill_rect(color_index*30, 210, 30, 30, color)

        # draw box around currently selected color
        tft.rect(color_index*30, 210, 30, 30, st7789.WHITE)
        tft.rect(color_index*30+1, 211, 28, 28, st7789.BLACK)
        tft.rect(color_index*30+2, 212, 26, 26, st7789.BLACK)

        while True:
            # can be up to two touches
            if touch.touched == 1:

                # get x and y points of the first touch
                p_x = touch.touches[0]['x']
                p_y = touch.touches[0]['y']

                # If point is in the lowest 30 rows of the screen
                # change color to swatch pressed.
                if p_y > 209:
                    # remove box from around previous color swatch
                    tft.rect(color_index*30, 210, 30, 30, color)
                    tft.rect(color_index*30+1, 211, 28, 28, color)
                    tft.rect(color_index*30+2, 212, 26, 26, color)

                    # update new color
                    color_index = p_x//30
                    color = COLORS[color_index]

                    # draw box around newly selected color swatch
                    tft.rect(color_index*30, 210, 30, 30, st7789.WHITE)
                    tft.rect(color_index*30+1, 211, 28, 28, st7789.BLACK)
                    tft.rect(color_index*30+2, 212, 26, 26, st7789.BLACK)

                else:
                    # draw the pixel - would be better with lines
                    tft.pixel(p_x, p_y, color)

    finally:
        # shutdown i2c
        if 'touch_i2c' in locals():
            touch_i2c.deinit()

        # shutdown spi
        if 'spi' in locals():
            spi.deinit()

        # turn off display backlight
        axp.disablePower(axp202c.AXP202_LDO2)

main()
