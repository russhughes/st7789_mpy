'''
watch_bitarray.py

    An example using map_bitarray_to_rgb565 to draw sprites for
    the TTGO T-Watch-2020

    https://www.youtube.com/watch?v=DgYzgnAW2d8

'''

import time
import random
import machine
import axp202c
import st7789

SPRITES = 100

SPRITE_WIDTH = 16
SPRITE_HEIGHT = 16
SPRITE_STEPS = 3
SPRITE_BITMAPS = [
    bytearray([
        0b00000000, 0b00000000,
        0b00000001, 0b11110000,
        0b00000111, 0b11110000,
        0b00001111, 0b11100000,
        0b00001111, 0b11000000,
        0b00011111, 0b10000000,
        0b00011111, 0b00000000,
        0b00011110, 0b00000000,
        0b00011111, 0b00000000,
        0b00011111, 0b10000000,
        0b00001111, 0b11000000,
        0b00001111, 0b11100000,
        0b00000111, 0b11110000,
        0b00000001, 0b11110000,
        0b00000000, 0b00000000,
        0b00000000, 0b00000000]),

    bytearray([
        0b00000000, 0b00000000,
        0b00000011, 0b11100000,
        0b00001111, 0b11111000,
        0b00011111, 0b11111100,
        0b00011111, 0b11111100,
        0b00111111, 0b11110000,
        0b00111111, 0b10000000,
        0b00111100, 0b00000000,
        0b00111111, 0b10000000,
        0b00111111, 0b11110000,
        0b00011111, 0b11111100,
        0b00011111, 0b11111100,
        0b00001111, 0b11111000,
        0b00000011, 0b11100000,
        0b00000000, 0b00000000,
        0b00000000, 0b00000000]),

    bytearray([
        0b00000000, 0b00000000,
        0b00000111, 0b11000000,
        0b00011111, 0b11110000,
        0b00111111, 0b11111000,
        0b00111111, 0b11111000,
        0b01111111, 0b11111100,
        0b01111111, 0b11111100,
        0b01111111, 0b11111100,
        0b01111111, 0b11111100,
        0b01111111, 0b11111100,
        0b00111111, 0b11111000,
        0b00111111, 0b11111000,
        0b00011111, 0b11110000,
        0b00000111, 0b11000000,
        0b00000000, 0b00000000,
        0b00000000, 0b00000000]),

    bytearray([
        0b00000000, 0b00000000,
        0b00000000, 0b00000000,
        0b00000000, 0b00000000,
        0b00000000, 0b00000000,
        0b00000000, 0b00000000,
        0b00000000, 0b00000000,
        0b00000000, 0b00000000,
        0b00000000, 0b00000000,
        0b00000000, 0b00000000,
        0b00000000, 0b00000000,
        0b00000000, 0b00000000,
        0b00000000, 0b00000000,
        0b00000000, 0b00000000,
        0b00000000, 0b00000000,
        0b00000000, 0b00000000,
        0b00000000, 0b00000000])]


class pacman():
    '''
    pacman class to keep track of a sprites locaton and step
    '''
    def __init__(self, x, y, step):
        self.x = x
        self.y = y
        self.step = step

    def move(self):
        self.step += 1
        self.step %= SPRITE_STEPS
        self.x += 1
        if self.x == 223:
            self.step = SPRITE_STEPS

        self.x %= 224


def main():
    '''
    Draw on screen using map_bitarray_to_rgb565
    '''
    try:
        # Turn on display backlight
        axp = axp202c.PMU()
        axp.enablePower(axp202c.AXP202_LDO2)

        # initialize display spi port
        spi = machine.SoftSPI(
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
        sprite = bytearray(512)

        # create pacman spites in random positions
        sprites = []
        for man in range(SPRITES):
            sprites.append(
                pacman(
                    random.randint(0, tft.width()-SPRITE_WIDTH),
                    random.randint(0, tft.height()-SPRITE_HEIGHT),
                    random.randint(0, SPRITE_STEPS-1)
                )
            )

        # move and draw sprites
        while True:
            for man in sprites:
                # move the sprite
                man.move()

                # convert bitmap into rgb565 blitable buffer
                tft.map_bitarray_to_rgb565(
                    SPRITE_BITMAPS[man.step],
                    sprite,
                    SPRITE_WIDTH,
                    st7789.YELLOW,
                    st7789.BLACK)

                # blit the buffer to the display
                tft.blit_buffer(
                    sprite,
                    man.x,
                    man.y,
                    SPRITE_WIDTH,
                    SPRITE_HEIGHT)

            time.sleep(0.1)

    finally:
        # shutdown spi
        if 'spi' in locals():
            spi.deinit()

        # turn off display backlight
        axp.disablePower(axp202c.AXP202_LDO2)


main()
