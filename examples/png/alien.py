'''
alien.py

    Randomly draw alien.png with alpha-channel masking

    The alien.png is from the Erik Flowers Weather Icons available from
    https://github.com/erikflowers/weather-icons and is licensed under
    SIL OFL 1.1

'''

import gc
import random
import tft_config
import st7789

gc.enable()
gc.collect()


def main():
    '''
    Decode and draw png on display
    '''

    tft = tft_config.config(1, buffer_size=30*2)

    # enable display and clear screen
    tft.init()

    # display png in random locations
    while True:
        tft.rotation(random.randint(0, 4))
        tft.png(
            "alien.png",
            random.randint(0, tft.width() - 63),
            random.randint(0, tft.height() - 63),
            True)


main()
