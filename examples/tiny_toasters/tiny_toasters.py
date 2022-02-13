"""
tiny_toasters.py - Flying Tiny Toasters for smaller displays (like the ST7735)

    Uses spritesheet from CircuitPython_Flying_Toasters pendant project
    https://learn.adafruit.com/circuitpython-sprite-animation-pendant-mario-clouds-flying-toasters

    Convert spritesheet bmp to tft.bitmap() method compatible python module using:
        python3 ./sprites2bitmap.py ttoasters.bmp 32 32 4 > ttoast_bitmaps.py

"""

import gc
import time
import random
import st7789
import tft_config
import ttoast_bitmaps as toast_bitmaps

TOASTER_FRAMES = [0, 1, 2, 3]
TOAST_FRAMES = [4]

def collide(a_col, a_row, a_width, a_height, b_col, b_row, b_width, b_height):
    '''return true if two rectangles overlap'''
    return (a_col + a_width >= b_col and a_col <= b_col + b_width
            and a_row + a_height >= b_row and a_row <= b_row + b_height)

def random_start(tft, sprites, bitmaps, num):
    '''
    Return a random location along the top or right of the screen, if that location would overlaps
    with another sprite return (0,0). This allows the other sprites to keep moving giving the next
    random_start a better chance to avoid a collision.

    '''
    # 50/50 chance to try along the top/right half or along the right/top half of the screen
    if random.getrandbits(1):
        row = 1
        col = random.randint(bitmaps.WIDTH//2, tft.width()-bitmaps.WIDTH)
    else:
        col = tft.width() - bitmaps.WIDTH
        row = random.randint(1, tft.height() // 2)

    if any(collide(
        col, row, bitmaps.WIDTH, bitmaps.HEIGHT,
        sprite.col, sprite.row, sprite.width, sprite.height)
        for sprite in sprites if num != sprite.num):

        col = 0
        row = 0

    return (col, row)

def main():

    class Toast():
        '''
        Toast class to keep track of toaster and toast sprites
        '''
        def __init__(self, sprites, bitmaps, frames):
            '''create new sprite in random location that does not overlap other sprites'''
            self.num = len(sprites)
            self.bitmaps = bitmaps
            self.frames = frames
            self.steps = len(frames)
            self.col, self.row  = random_start(tft, sprites, bitmaps, self.num)
            self.width = bitmaps.WIDTH
            self.height = bitmaps.HEIGHT
            self.last_col = self.col
            self.last_row = self.row
            self.step = random.randint(0, self.steps)
            self.dir_col = -random.randint(2, 5)
            self.dir_row = 2
            self.prev_dir_col = self.dir_col
            self.prev_dir_row = self.dir_row
            self.iceberg = 0

        def clear(self):
            '''clear above and behind sprite'''
            tft.fill_rect(
                self.col, self.row-1, self.width, self.dir_row+1,
                st7789.BLACK)

            tft.fill_rect(
                self.col+self.width+self.dir_col, self.row,
                -self.dir_col, self.height, st7789.BLACK)

        def erase(self):
            '''erase last postion of sprite'''
            tft.fill_rect(
                self.last_col, self.last_row, self.width, self.height, st7789.BLACK)

        def move(self, sprites):
            '''step frame and move sprite'''

            if self.steps:
                self.step = (self.step + 1) % self.steps

            self.last_col = self.col
            self.last_row = self.row
            new_col = self.col + self.dir_col
            new_row = self.row + self.dir_row

            # if new location collides with another sprite, change direction for 32 frames

            for sprite in sprites:
                if (
                    self.num != sprite.num
                    and collide(
                        new_col, new_row, self.width, self.height,
                        sprite.col, sprite.row, sprite.width, sprite.height,
                    )
                    and (self.col > sprite.col)):

                    self.iceberg = 32
                    self.dir_col = -1
                    self.dir_row = 3
                    new_col = self.col + self.dir_col
                    new_row = self.row + self.dir_row

            self.col = new_col
            self.row = new_row

            # if new location touches edge of screen, erase then set new start location
            if self.col <= 0 or self.row > tft.height() - self.height:
                self.erase()
                self.dir_col = -random.randint(2, 5)
                self.dir_row = 2
                self.col, self.row  = random_start(tft, sprites, self.bitmaps, self.num)

            # Track post collision direction change
            if self.iceberg:
                self.iceberg -= 1
                if self.iceberg == 1:
                    self.dir_col = self.prev_dir_col
                    self.dir_row = self.prev_dir_row

        def draw(self):
            '''if the location is not 0,0 draw current frame of sprite at it's location'''
            if self.col and self.row:
                tft.bitmap(self.bitmaps, self.col, self.row, self.frames[self.step])


    tft = tft_config.config(1, buffer_size=64*62*2)   # configure display driver

    # init and clear screen
    tft.init()
    tft.fill(st7789.BLACK)

    # create toast spites and set animation frames
    sprites = []
    sprites.append(Toast(sprites, toast_bitmaps, TOAST_FRAMES))
    sprites.append(Toast(sprites, toast_bitmaps, TOASTER_FRAMES))
    sprites.append(Toast(sprites, toast_bitmaps, TOASTER_FRAMES))

    # move and draw sprites

    while True:
        for sprite in sprites:
            sprite.clear()
            sprite.move(sprites)
            sprite.draw()

        gc.collect()
        time.sleep(0.05)

main()
