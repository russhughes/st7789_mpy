"""
logo.py

    Draw different sized png MicroPython logos to test the png decoder and clipping. 
    Copy the png logo files to the same directory as this file.

    The MicroPython logo is copyright George Robotics Ltd.
"""

import gc
from time import sleep, ticks_ms
import st7789
import tft_config

LOGOS = (
    (128, 128),
    (160, 128),
    (160, 80),
    (240, 135),
    (240, 240),
    (240, 320),
    (480, 320),
    (320, 170),
    (320, 240),
    (64, 64),
    (80, 160),
)

gc.collect()
tft = tft_config.config(0, buffer_size=32768)

def main():
    '''
    Decode and draw png on display
    '''

    tft.init()

    for width, height in LOGOS:
        tft.fill(st7789.BLACK)
        png_file_name = f'logo-{width}x{height}.png'
        start = ticks_ms()
        tft.png(png_file_name, 0, 0)
        print(f'Displaying {png_file_name} took {ticks_ms() - start}ms')
        sleep(2)


main()
