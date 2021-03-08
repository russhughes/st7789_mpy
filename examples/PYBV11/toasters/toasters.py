'''
toasters.py

    An example using bitmap to draw sprites on a ST7789 TFT display
    connected to a pyboard1.1.

    spritesheet from CircuitPython_Flying_Toasters
    https://learn.adafruit.com/circuitpython-sprite-animation-pendant-mario-clouds-flying-toasters
'''

import time
import random
from pyb import SPI, Pin
import st7789
import t1,t2,t3,t4,t5

TOASTERS = [t1, t2, t3, t4]
TOAST = [t5]


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
            self.x = 320-64

        self.step += 1
        self.step %= self.steps
        self.x -= self.speed

def main():
    '''
    Draw and move sprite
    '''
    try:
        spi = SPI(1, SPI.MASTER, baudrate=42000000, prescaler=2)

        # initialize display
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

        # create toast spites in random positions
        sprites = [
            toast(TOASTERS, 320-64, 0),
            toast(TOAST, 320-64*2, 80),
            toast(TOASTERS, 320-64*4, 160)
        ]

        # move and draw sprites
        while True:
            for man in sprites:
                bitmap = man.sprites[man.step]
                tft.fill_rect(
                    man.x+bitmap.WIDTH-man.speed,
                    man.y,
                    man.speed,
                    bitmap.HEIGHT,
                    st7789.BLACK)

                man.move()

                if man.x > 0:
                    tft.bitmap(bitmap, man.x, man.y)
                else:
                    tft.fill_rect(
                        0,
                        man.y,
                        bitmap.WIDTH,
                        bitmap.HEIGHT,
                        st7789.BLACK)

            time.sleep(0.05)

    finally:
        # shutdown spi
        spi.deinit()


main()
