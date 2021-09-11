"""
cfg_helper.py

    Utility to help with determining colstarts, rowstarts, color_order and inversion settings for
    for a display.

    Set the `HEIGHT` and `WIDTH` constants to the physcial size of your display.

    The program starts by filling the display with RED and draws a WHITE rectangle around the perimeter.

    - If the display background is RED, the color configuration is correct.
    - If the display background is BLUE, toggle the color_order from RGB to BGR using the 'O' or 'o' keys.
    - If the display background is YELLOW, toggle the inversion from False to True using the 'I' or 'i' keys.
    - If the display background is CYAN, toggle both the color_order from RGB to BGR using the 'O' or 'o' keys and
    toggle the inversion from False to True using the 'I' or 'i' keys.

    Once you have a display with a RED background you can step through RED, GREEN and BLUE backgrounds using
    the 'C' or 'c' keys.

    Observe the edges of the display, there should be a 1 pixel wide rectangle outlining the display. If
    one of the lines are not showing or you see random pixels on the outside of the white rectangle your
    display requires a colstart and/or rowstart offset. Some displays have a frame buffer memory larger
    than the physical LCD or LED matrix. In these cases the driver must be configured with the position of
    the first physcial column and row pixels relative to the frame buffer.  Each rotation setting of the
    display may require different colstart and rowstart values.

    Use the 'w', 'a', 's' and 'd' keys to increase or decrease the colstart and rowstart values by 1.
    Use the 'W', 'A', 'S' and 'S' keys to increase or decrease the colstart and rowstart values by 10.
    Use the '+' and '-' keys to change the displays rotation.

    Once you have determined the colstart and rowstart values for the rotations you are going to use,
    press the 'P' or 'p' key to print the current configuration values.
"""

import sys
from machine import Pin, SPI

import st7789
import vga1_bold_16x16 as font

WIDTH = const(128)
HEIGHT = const(128)

COLSTART = const(0)
ROWSTART = const(1)
NAME = const(0)
VAL = const(1)

def show_help():
    print('\n\nKeys:')
    print('+ - Next rotation')
    print('- - Previous rotation')
    print('W - Decrease rowstart by 10')
    print('w - Decrease rowstart by 1')
    print('A - Decrease colstart by 10')
    print('a - Decrease colstart by 1')
    print('S - Increase rowstart by 10')
    print('s - Increase rowstart by 1')
    print('D - Increase colstart by 10')
    print('d - Increase colstart by 1')
    print('O, o - Change color_order')
    print('I, i - Toggle inversion')
    print('C, c - Change background')
    print('P, p - Print current settings')
    print('?, H, h - Show Help\n')


def main():
    starts = [[0, 0], [0, 0], [0, 0], [0, 0]]

    orders = [['st7789.RGB', st7789.RGB], ['st7789.BGR', st7789.BGR]]

    colors = [
        ['Red', st7789.RED],
        ['Green', st7789.GREEN],
        ['Blue', st7789.BLUE]
    ]
    inversions = [['False', False], ['True', True]]

    rotation = 0
    order = 0
    color = 0
    inversion = 0

    tft = st7789.ST7789(
        SPI(1, baudrate=30000000, sck=Pin(19), mosi=Pin(18)),
        WIDTH,
        HEIGHT,
        reset=Pin(4, Pin.OUT),
        cs=Pin(13, Pin.OUT),
        dc=Pin(12, Pin.OUT),
        backlight=Pin(15, Pin.OUT),
        color_order=orders[order][VAL],
        rotation=rotation)

    tft.init()
    tft.inversion_mode(0)

    show_help()
    change = True

    while True:
        if change:
            tft.inversion_mode(inversions[inversion][VAL])
            tft.rotation(rotation)
            tft.offset(starts[rotation][COLSTART], starts[rotation][ROWSTART])
            tft.fill(colors[color][VAL])

            print(f'for rotation {rotation} colstart is {starts[rotation][COLSTART]} rowstart is {starts[rotation][ROWSTART]}')

            tft.text(
                font,
                f'Rot: {rotation}',
                (tft.width() >> 1) - (font.WIDTH * 3),
                (tft.height() >> 1) - font.HEIGHT,
                st7789.WHITE,
                colors[color][VAL])

            tft.text(
                font,
                colors[color][NAME],
                (tft.width() >> 1) - (font.WIDTH * len(colors[color][NAME]) >> 1),
                (tft.height() >> 1),
                st7789.WHITE,
                colors[color][VAL])

            tft.rect(0, 0, tft.width(), tft.height(), st7789.WHITE)
            print('?,H,h for help: ', end='')

        change = True
        cmd = sys.stdin.read(1)

        if cmd == '+':
            rotation += 1
            rotation %= 4

        elif cmd == '-':
            rotation -= 1
            rotation %= 4

        elif cmd in ['?', 'H', 'h']:
            show_help()

        elif cmd == 'W':
            starts[rotation][ROWSTART] -= 10
            starts[rotation][ROWSTART] %= tft.height()

        elif cmd == 'w':
            starts[rotation][ROWSTART] -= 1
            starts[rotation][ROWSTART] %= tft.height()

        elif cmd == 'A':
            starts[rotation][COLSTART] -= 10
            starts[rotation][COLSTART] %= tft.width()

        elif cmd == 'a':
            starts[rotation][COLSTART] -= 1
            starts[rotation][COLSTART] %= tft.width()

        elif cmd == 'S':
            starts[rotation][ROWSTART] += 10
            starts[rotation][ROWSTART] %= tft.height()

        elif cmd == 's':
            starts[rotation][ROWSTART] += 1
            starts[rotation][ROWSTART] %= tft.height()

        elif cmd == 'D':
            starts[rotation][COLSTART] += 10
            starts[rotation][COLSTART] %= tft.width()

        elif cmd == 'd':
            starts[rotation][COLSTART] += 1
            starts[rotation][COLSTART] %= tft.width()

        elif cmd in ['P', 'p']:
            print("\n\nCurrent settings:")
            print(f'rotation = {rotation}')
            print(f'inversion_mode({inversions[inversion][NAME]})')
            print(f'color_order = {orders[order][NAME]}')
            for index, offset in enumerate(starts):
                print(f'for rotation {index} use offset({offset[COLSTART]}, {offset[ROWSTART]})')
            print()

        elif cmd in ['I', 'i']:
            inversion += 1
            inversion %= len(inversions)
            print(f'inversion({inversions[inversion][NAME]})')

        elif cmd in ['C', 'c']:
            color += 1
            color %= len(colors)

        elif cmd in ['O', 'o']:
            order += 1
            order %= len(orders)
            print(f'color_order = {orders[order][NAME]}')
            tft = st7789.ST7789(
                SPI(1, baudrate=30000000, sck=Pin(19), mosi=Pin(18)),
                WIDTH,
                HEIGHT,
                reset=Pin(4, Pin.OUT),
                cs=Pin(13, Pin.OUT),
                dc=Pin(12, Pin.OUT),
                backlight=Pin(15, Pin.OUT),
                color_order=orders[order][VAL],
                rotation=rotation)
        else:
            change = False


main()
