'''
bitarray.py

    An example using map_bitarray_to_rgb565 to draw sprites on a ST7789 TFT
    display connected to a pyboard V1.1.


    https://www.youtube.com/watch?v=DgYzgnAW2d8

'''

import time
import random
from pyb import SPI, Pin
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
        if self.x == 303:
            self.step = SPRITE_STEPS

        self.x %= 304


def main():
    '''
    Draw on screen using map_bitarray_to_rgb565
    '''
    try:
        # initialize display spi port
        spi = SPI(1, SPI.MASTER, baudrate=42000000, prescaler=2)

        # configure display
        tft = st7789.ST7789(
        spi,
        240,
        320,
        reset=Pin('X3', Pin.OUT),
        cs=Pin('X5', Pin.OUT),
        dc=Pin('X4', Pin.OUT),
        backlight=Pin('X2', Pin.OUT),
        rotation=3)

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
        spi.deinit()


main()
