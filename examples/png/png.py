"""
bigbuckbunny.py

    Draw a full screen png

    bigbuckbunny.png (c) copyright 2008, Blender Foundation / www.bigbuckbunny.org
"""

import st7789
import tft_config

tft = tft_config.config(1, buffer_size=2048)

def main():
    '''
    Decode and draw png on display
    '''

    tft.init()
    tft.png(f'bigbuckbunny-{tft.width()}x{tft.height()}.png', 0, 0)


main()
