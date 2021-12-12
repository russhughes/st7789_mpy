#!/usr/bin/env python3

'''
    Convert a sprite sheet image to python a module for use with indexed bitmap method.
    Sprite sheet width and height should be a multiple of sprite width and height. There
    should be no extra pixels between sprites. All sprites will share the same palette.

    Usage:
        sprites2bitmap image_file spite_width sprite_height bits_per_pixel  >sprites.py

    MicroPython:
        import sprites
        ... tft config and init code ...
        tft.bitmap(sprites, x, y, index)

'''

from os import setpriority
from PIL import Image
import argparse

def main():

    parser = argparse.ArgumentParser(
        prog='imgtobitmap',
        description='Convert image file to python module for use with bitmap method.')

    parser.add_argument(
        'image_file',
        help='Name of file containing image to convert')

    parser.add_argument(
        'sprite_width',
        type=int,
        help='width of sprites in pixels')

    parser.add_argument(
        'sprite_height',
        type=int,
        help='height of sprites in pixels')

    parser.add_argument(
        'bits_per_pixel',
        type=int,
        choices=range(1, 9),
        default=1,
        metavar='bits_per_pixel',
        help='The number of bits to use per pixel (1..8)')

    args = parser.parse_args()

    bits = args.bits_per_pixel
    img = Image.open(args.image_file)
    img = img.convert("P", palette=Image.ADAPTIVE, colors=2**bits)
    palette = img.getpalette()  # Make copy of palette colors

    # For all the colors in the palette
    colors = []
    for color in range(1 << bits):

        # get rgb values and convert to 565
        color565 = (
            ((palette[color*3] & 0xF8) << 8) |
            ((palette[color*3+1] & 0xFC) << 3) |
            ((palette[color*3+2] & 0xF8) >> 3))

        # swap bytes in 565
        color = ((color565 & 0xff) << 8) + ((color565 & 0xff00) >> 8)

        # append byte swapped 565 color to colors
        colors.append(f'{color:04x}')

    image_bitstring = ''
    max_colors = 1 << bits
    bitmaps = 0
    # Run through the image and create a string with the ascii binary
    # representation of the color of each pixel.
    for y in range(0, img.height, args.sprite_height):
        for x in range(0, img.width, args.sprite_width):
            bitmaps += 1
            for yy in range(y, y + args.sprite_height):
                for xx in range(x, x + args.sprite_width):
                    pixel = img.getpixel((xx, yy))
                    color = pixel
                    image_bitstring += ''.join(
                        '1' if (color & (1 << bit - 1)) else '0' for bit in range(bits, 0, -1))

    bitmap_bits = len(image_bitstring)

    # Create python source with image parameters
    print(f'BITMAPS = {bitmaps}')
    print(f'HEIGHT = {args.sprite_height}')
    print(f'WIDTH = {args.sprite_width}')
    print(f'COLORS = {max_colors}')
    print(f'BITS = {bitmap_bits}')
    print(f'BPP = {bits}')
    print('PALETTE = [', sep='', end='')

    for color, rgb in enumerate(colors):
        if color:
            print(',', sep='', end='')
        print(f'0x{rgb}', sep='', end='')
    print("]")

    # Run though image bit string 8 bits at a time
    # and create python array source for memoryview

    print("_bitmap =\\", sep='')
    print("b'", sep='', end='')

    for i in range(0, bitmap_bits, 8):

        if i and i % (16*8) == 0:
            print("'\\\nb'", end='', sep='')

        value = image_bitstring[i:i+8]
        color = int(value, 2)
        print(f'\\x{color:02x}', sep='', end='')

    print("'\nBITMAP = memoryview(_bitmap)")


main()
