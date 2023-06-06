"""
logo.py

    Draw a full screen png MicroPython logo. Copy the png logo file that
    matches the dimensions of your display to the same directory as this file.

    The MicroPython logo is copyright George Robotics Ltd.
"""

from time import sleep
import st7789
import tft_config

tft = tft_config.config(0)

def main():
    '''
    Decode and draw png on display
    '''

    tft.init()
    png_file_name = f'logo-{tft.width()}x{tft.height()}.png'
    print(f'Displaying {png_file_name}')
    tft.png(png_file_name, 0, 0)

main()
