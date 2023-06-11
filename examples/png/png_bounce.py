"""
png_bounce.py

    Bounce a png around the display to test png decoder and visibility clipping.

"""

import gc
import random
import time
import tft_config
import st7789   

gc.enable()
gc.collect()

LOGO_WIDTH = 30
LOGO_HEIGHT = 30


def main():
    """
    Bounce a png around the display.
    """

    tft = tft_config.config(0, buffer_size=4096)

    # enable display and clear screen
    tft.init()
    tft.fill(st7789.BLACK)

    width = tft.width()
    height = tft.height()
    col = width // 2 - LOGO_WIDTH // 2
    row = height // 2 - LOGO_HEIGHT // 2
    xd = 3
    yd = 2

    ticks = 1000 // 45

    while True:
        last = time.ticks_ms()
        tft.png("alien.png", col, row)

        # Update the position to bounce the bitmap around the screen
        col += xd
        if col <= -LOGO_WIDTH - 1 or col > width:
            xd = -xd

        row += yd
        if row <= -LOGO_HEIGHT - 1 or row > height+1:
            yd = -yd

        if time.ticks_ms() - last < ticks:
            time.sleep_ms(ticks - (time.ticks_ms() - last))


main()
