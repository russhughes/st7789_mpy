"""
toasters_jpg.py

    An example using a jpg sprite map to draw sprites on T-Display.  This is an older version of the
    toasters.py and tiny_toasters example.  It uses the jpg_decode() method to grab a bitmap of each
    sprite from the toaster.jpg sprite sheet.

    youtube video: https://youtu.be/0uWsjKQmCpU

    spritesheet from CircuitPython_Flying_Toasters
    https://learn.adafruit.com/circuitpython-sprite-animation-pendant-mario-clouds-flying-toasters
"""

import time
import random
from machine import Pin, SPI
import st7789

#
# Select a config module for your display
#

# Not suitable for esp32_7735_128 due to resolution
# Not suitable for esp32_7735_160 due to resolution
# import tdisplay as Driver
# import twatch_2020_v2 as Driver
# import ws_pico_114 as Driver
# import ws_pico_13 as Driver
# import ws_pico_2 as Driver
import tdisplay_rp2040 as Driver

tft = Driver.config(0)

class toast():
    '''
    toast class to keep track of a sprites locaton and step
    '''

    def __init__(self, sprites, x, y):
        self.sprites = sprites
        self.steps = len(sprites)
        self.x = x
        self.y = y
        self.step = random.randint(0, self.steps-1)
        self.speed = random.randint(2, 5)

    def move(self):
        if self.x <= 0:
            self.speed = random.randint(2, 5)
            self.x = 135-64

        self.step += 1
        self.step %= self.steps
        self.x -= self.speed


def main():
    '''
    Draw and move sprite
    '''

    # enable display and clear screen
    tft.init()
    tft.fill(st7789.BLACK)

    width = 64
    height = 64

    # grab each sprite from the toaster.jpg sprite sheet
    t1, _, _ = tft.jpg_decode('toaster.jpg', 0, 0, width, height)
    t2, _, _ = tft.jpg_decode('toaster.jpg', width, 0, width, height)
    t3, _, _ = tft.jpg_decode('toaster.jpg', width*2, 0, width, height)
    t4, _, _ = tft.jpg_decode('toaster.jpg', 0, height, width, height)
    t5, _, _ = tft.jpg_decode('toaster.jpg', width, height, width, height)

    TOASTERS = [t1, t2, t3, t4]
    TOAST = [t5]

    sprites = [
        toast(TOASTERS, tft.width() - width, 0),
        toast(TOAST, tft.width() - width * 2, tft.height() // 3),
        toast(TOASTERS, tft.width() - width * 4, tft.height() // 3 * 2)
    ]

    # move and draw sprites
    while True:
        for man in sprites:
            bitmap = man.sprites[man.step]
            tft.fill_rect(
                man.x+width-man.speed,
                man.y,
                man.speed,
                height,
                st7789.BLACK)

            man.move()

            if man.x > 0:
                tft.blit_buffer(bitmap, man.x, man.y, width, height)
            else:
                tft.fill_rect(
                    0,
                    man.y,
                    width,
                    height,
                    st7789.BLACK)

        time.sleep(0.05)


main()
