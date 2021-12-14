'''
toasters.py - Flying Toasters(ish) for Raspberry Pi PICO with Waveshare Pico LCD 2 Display Module.

    Uses spritesheet from CircuitPython_Flying_Toasters pendant project
    https://learn.adafruit.com/circuitpython-sprite-animation-pendant-mario-clouds-flying-toasters

    Convert spritesheet bmp to tft.bitmap() method compatible python module using:
        python3 ./sprites2bitmap.py toasters.bmp 64 64 4 > toast_bitmaps.py

'''

import gc
import time
import random
from machine import Pin, SPI
import st7789
import toast_bitmaps

TOASTER_FRAMES = [0, 1, 2, 3]
TOAST_FRAMES = [4]

class rect():
    '''rectangle class'''

    def __init__(self, col, row, width, height):
        '''create new rectangle'''
        self.col = col
        self.row = row
        self.width = width
        self.height = height

    def __add__(self, other):
        '''add two rectangles'''
        return rect(
            self.col + other.col,
            self.row + other.row,
            self.width + other.width,
            self.height + other.height)

def collide(rect_a, rect_b):
    '''return true if two rectangles overlap'''
    return (rect_a.col + rect_a.width >= rect_b.col
            and rect_a.col <= rect_b.col + rect_b.width
            and rect_a.row + rect_a.height >= rect_b.row
            and rect_a.row <= rect_b.row + rect_b.height)

def collision(sprites):
    ''''return true if any sprites overlap'''
    return any(collide(a.location, b.location) for a, b in zip(sprites[::], sprites[1::]))

def random_start(tft, sprites, bitmaps):
    '''return new location along the top or right of the screen that does not overlap any sprites'''
    while True:
        if random.getrandbits(2) > 1:
            row = 0
            col = random.randint(bitmaps.WIDTH, tft.width()-bitmaps.WIDTH)
        else:
            col = tft.width() - bitmaps.WIDTH
            row = random.randint(bitmaps.HEIGHT, tft.height()-bitmaps.HEIGHT)

        new_location = rect(col, row, bitmaps.WIDTH, bitmaps.HEIGHT)
        if not any(collide(new_location, sprite.location) for sprite in sprites):
            return new_location

def main():

    class toast():
        '''
        toast class to keep track of toaster and toast sprites
        '''
        def __init__(self, sprites, bitmaps, frames):
            '''create new sprite in random location that does not overlap other sprites'''
            self.id = len(sprites)
            self.bitmaps = bitmaps
            self.frames = frames
            self.steps = len(frames)
            self.location = random_start(tft, sprites, bitmaps)
            self.last = self.location
            self.step = random.randint(0, self.steps)
            self.direction = rect(-random.randint(2, 5), 1, 0, 0)
            self.prev_direction = self.direction
            self.iceberg = 0

        def clear(self):
            '''clear above and behind sprite'''
            tft.fill_rect(
                self.location.col, self.location.row-1, self.location.width, self.direction.row+1,
                st7789.BLACK)

            tft.fill_rect(
                self.location.col+self.bitmaps.WIDTH+self.direction.col, self.location.row,
                -self.direction.col, self.location.height, st7789.BLACK)

        def erase(self):
            '''erase last postion of sprite'''
            tft.fill_rect(
                self.last.col, self.last.row, self.last.width, self.last.height, st7789.BLACK)

        def move(self, sprites):
            '''step frame and move sprite'''
            if self.steps:
                self.step = (self.step + 1) % self.steps

            self.last = self.location
            new_location = self.location + self.direction

            # if new location collides with another sprite, change direction down for 16 frames
            if any(collide(new_location, sprite.location) for sprite in sprites if self.id != sprite.id):
                self.iceberg = 16
                self.direction = rect(-1, 2, 0, 0)
                new_location = self.location + self.direction

            self.location = new_location

            # if new location touches edge of screen, erase then set new start location
            if new_location.col <= 0 or new_location.row > tft.height() - self.location.height:
                self.erase()
                self.direction = rect(-random.randint(2, 5), 1, 0, 0)
                self.location = random_start(tft, sprites, self.bitmaps)

            # Track post collision direction change
            if self.iceberg:
                self.iceberg -= 1
                if self.iceberg == 1:
                    self.direction = self.prev_direction

        def draw(self):
            '''draw current frame of sprite at it's location'''
            tft.bitmap(self.bitmaps, self.location.col, self.location.row, self.frames[self.step])


    # configure spi interface
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
        rotation=1,
        buffer_size=64*64*2)

    # init and clear screen
    tft.init()
    tft.fill(st7789.BLACK)

    # create toast spites and set animation frames
    sprites = []
    sprites.append(toast(sprites, toast_bitmaps, TOAST_FRAMES))
    sprites.append(toast(sprites, toast_bitmaps, TOASTER_FRAMES))
    sprites.append(toast(sprites, toast_bitmaps, TOASTER_FRAMES))

    # move and draw sprites
    while True:
        for sprite in sprites:

            sprite.clear()
            sprite.move(sprites)
            sprite.draw()

        gc.collect()
        time.sleep(0.01)

main()
