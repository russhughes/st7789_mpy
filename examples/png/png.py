"""
bigbuckbunny.py

    Draw a full screen png

    bigbuckbunny.png (c) copyright 2008, Blender Foundation / www.bigbuckbunny.org
"""

import st7789
import tft_config

tft = tft_config.config(0, buffer_size=4096)

def main():
    '''
    Decode and draw png on display
    '''

    tft.init()
    png_file_name = f'bigbuckbunny-{tft.width()}x{tft.height()}.png'
    print(f'Displaying {png_file_name}')
    tft.png(png_file_name, 0, 0)


main()
