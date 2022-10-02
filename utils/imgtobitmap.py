#!python3
'''
    Convert image file to python module for use with blit_bitmap.

    Usage imgtobitmap image_file bits_per_pixel >image.py
'''

import sys
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
        'bits_per_pixel',
        type=int,
        choices=range(1, 9),
        default=1,
        metavar='bits_per_pixel',
        help='The number of bits to use per pixel (1..8)')

    args = parser.parse_args()
    bits = args.bits_per_pixel
    colors_requested = 1 << bits
    img = Image.open(args.image_file)
    img = img.convert("P", palette=Image.Palette.ADAPTIVE, colors=colors_requested)
    palette = img.getpalette()  # Make copy of palette colors
    palette_colors = len(palette) // 3
    bits_required = palette_colors.bit_length()
    if (bits_required < bits):
        print(f'\nNOTE: Quantization reduced colors to {palette_colors} from the {colors_requested} '
        f'requested, reconverting using {bits_required} bit per pixel could save memory.\n''', file=sys.stderr)

    # For all the colors in the palette
    colors = []

    for color in range(palette_colors):

        # get rgb values and convert to 565
        color565 = (
            ((palette[color*3] & 0xF8) << 8)
            | ((palette[color*3+1] & 0xFC) << 3)
            | ((palette[color*3+2] & 0xF8) >> 3))

        # swap bytes in 565
        color = ((color565 & 0xff) << 8) + ((color565 & 0xff00) >> 8)

        # append byte swapped 565 color to colors
        colors.append(f'{color:04x}')

    image_bitstring = ''
    max_colors = 1 << bits

    # Run through the image and create a string with the ascii binary
    # representation of the color of each pixel.
    for y in range(img.height):
        for x in range(img.width):
            pixel = img.getpixel((x, y))
            color = pixel
            bstring = ''.join(
                '1' if (color & (1 << bit - 1)) else '0'
                for bit in range(bits, 0, -1)
            )

            image_bitstring += bstring

    bitmap_bits = len(image_bitstring)

    # Create python source with image parameters
    print(f'HEIGHT = {img.height}')
    print(f'WIDTH = {img.width}')
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
