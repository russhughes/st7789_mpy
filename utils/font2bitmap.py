#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Needs freetype-py>=1.0

# Font handling classes are from Dan Bader blog post on using freetype
# http://dbader.org/blog/monochrome-font-rendering-with-freetype-and-python
#
# Modified by Russ Hughes, Mar 2021 to write bitmap modules compatible with
# the MicroPython ili9342c driver at https://github.com/russhughes/ili9342c_mpy
# and the st7789 driver at https://github.com/russhughes/st7789_mpy.
#
# The Negative glyph.left fix is from peterhinch's font conversion program
# https://github.com/peterhinch/micropython-font-to-py
# https://github.com/peterhinch/micropython-font-to-py/issues/21
# Handle negative glyph.left correctly (capital J),
# also glyph.width > advance (capital K and R).
#

# The MIT License (MIT)
#
# Copyright (c) 2013 Daniel Bader (http://dbader.org)
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.


import sys
import shlex
import argparse
import bisect
import freetype


def to_int(string):
    """ Return integer value from a hex or decimal string"""
    return int(string, base=16) if string.startswith("0x") else int(string)


def get_chars(string):
    """ Return string comprised of given characters or range(s) of characters"""
    return ''.join(chr(b) for a in [
            (lambda sub: range(sub[0], sub[-1] + 1))
            (list(map(to_int, ele.split('-'))))
            for ele in string.split(',')] for b in a)


def wrap_str(string, items_per_line=32):
    """ Return a string wrapped to items_per_line with special care for escape characters"""
    length = len(string)
    lines = []
    i = 0
    end = 0
    while length > end:
        end = min(i + items_per_line, length)
        if string[end - 1] == '\\':
            end -= 2
        lines.append(string[i : end])
        i = end
    return "(\n    '" + "'\n    '".join(lines) + "'\n)"


def wrap_bytes(lst, items_per_line=16):
    """Return a string of items wrapped to items_per_line"""
    lines = [
        "".join(f'\\x{x:02x}' for x in lst[i : i + items_per_line])
        for i in range(0, len(lst), items_per_line)
    ]
    return "    b'" + "'\\\n    b'".join(lines) + "'"


def wrap_longs(lst, items_per_line=16):
    """Return a string of longs wrapped to items_per_line"""
    lines = [
        "".join(f'\\x{x:02x}' for x in lst[i : i + items_per_line])
        for i in range(0, len(lst), items_per_line)
    ]
    return "    b'" + "'\\\n    b'".join(lines) + "'"


class Bitmap():
    """
    A 2D bitmap image represented as a list of byte values. Each byte indicates
    the state of a single pixel in the bitmap. A value of 0 indicates that the
    pixel is `off` and any other value indicates that it is `on`.
    """
    def __init__(self, width, height, pixels=None):
        self.width = int(width)
        self.height = int(height)
        self.pixels = pixels or bytearray(width * height)

    def __repr__(self):
        """Return a string representation of the bitmap's pixels."""
        rows = ''
        for y in range(self.height):
            for x in range(self.width):
                rows += '#' if self.pixels[y * self.width + x] else '.'
            rows += '\n'
        return rows

    def bit_string(self):
        """Return a binary string representation of the bitmap's pixels."""
        bits = ''
        for y in range(self.height):
            for x in range(self.width):
                bits += '1' if self.pixels[y * self.width + x] else '0'
        return bits

    def bitblt(self, src, x, y):
        """Copy all pixels from `src` into this bitmap"""
        srcpixel = 0
        dstpixel = y * self.width + x
        row_offset = self.width - src.width

        for _ in range(src.height):
            for _ in range(src.width):
                # Perform an OR operation on the destination pixel and the
                # source pixel because glyph bitmaps may overlap if character
                # kerning is applied, e.g. in the string "AVA", the "A" and "V"
                # glyphs must be rendered with overlapping bounding boxes.
                self.pixels[dstpixel] = (
                    self.pixels[dstpixel] or src.pixels[srcpixel])
                srcpixel += 1
                dstpixel += 1
            dstpixel += row_offset


class Glyph():
    def __init__(self, pixels, width, height, top, left, advance_width):
        self.bitmap = Bitmap(width, height, pixels)

        # The glyph bitmap's top-side bearing, i.e. the vertical distance from
        # the baseline to the bitmap's top-most scanline.
        self.top = top
        self.left = left
        # Ascent and descent determine how many pixels the glyph extends
        # above or below the baseline.
        self.descent = max(0, self.height - self.top)
        self.ascent = max(0, max(self.top, self.height) - self.descent)

        # The advance width determines where to place the next character
        # horizontally, that is, how many pixels we move to the right to draw
        # the next glyph.
        self.advance_width = advance_width

    @property
    def width(self):
        return self.bitmap.width

    @property
    def height(self):
        return self.bitmap.height

    @staticmethod
    def from_glyphslot(slot):
        """Construct and return a Glyph object from a FreeType GlyphSlot."""
        pixels = Glyph.unpack_mono_bitmap(slot.bitmap)
        width, height = slot.bitmap.width, slot.bitmap.rows
        top = slot.bitmap_top
        left = slot.bitmap_left

        # The advance width is given in FreeType's 26.6 fixed point format,
        # which means that the pixel values are multiples of 64.
        advance_width = slot.advance.x // 64

        return Glyph(pixels, width, height, top, left, advance_width)

    @staticmethod
    def unpack_mono_bitmap(bitmap):
        """
        Unpack a freetype FT_LOAD_TARGET_MONO glyph bitmap into a bytearray
        where each pixel is represented by a single byte.
        """
        # Allocate a bytearray of sufficient size to hold the glyph bitmap.
        data = bytearray(bitmap.rows * bitmap.width)

        # Iterate over every byte in the glyph bitmap. Note that we're not
        # iterating over every pixel in the resulting unpacked bitmap --
        # we're iterating over the packed bytes in the input bitmap.
        for y in range(bitmap.rows):
            for byte_index in range(bitmap.pitch):

                # Read the byte that contains the packed pixel data.
                byte_value = bitmap.buffer[y * bitmap.pitch + byte_index]

                # We've processed this many bits (=pixels) so far. This
                # determines where we'll read the next batch of pixels from.
                num_bits_done = byte_index * 8

                # Pre-compute where to write the pixels that we're going
                # to unpack from the current byte in the glyph bitmap.
                rowstart = y * bitmap.width + byte_index * 8

                # Iterate over every bit (=pixel) that's still a part of the
                # output bitmap. Sometimes we're only unpacking a fraction of a
                # byte because glyphs may not always fit on a byte boundary. So
                # we make sure to stop if we unpack past the current row of
                # pixels.
                for bit_index in range(min(8, bitmap.width - num_bits_done)):

                    # Unpack the next pixel from the current glyph byte.
                    bit = byte_value & (1 << (7 - bit_index))

                    # Write the pixel to the output bytearray. We ensure that
                    # `off` pixels have a value of 0 and `on` pixels have a
                    # value of 1.
                    data[rowstart + bit_index] = 1 if bit else 0

        return data


class Font():
    def __init__(self, filename, width, height):
        self.face = freetype.Face(filename)
        self.face.set_pixel_sizes(width, height)

    def glyph_for_character(self, char):
        # Let FreeType load the glyph for the given character and tell it to
        # render a monochromatic bitmap representation.
        self.face.load_char(
            char, freetype.FT_LOAD_RENDER | freetype.FT_LOAD_TARGET_MONO)

        return Glyph.from_glyphslot(self.face.glyph)

    def render_character(self, char):
        glyph = self.glyph_for_character(char)
        return glyph.bitmap

    def text_dimensions(self, text):
        """
        Return (width, height, baseline) of `text` rendered in the current
        font.
        """
        width = 0
        max_ascent = 0
        max_descent = 0

        # For each character in the text string we get the glyph
        # and update the overall dimensions of the resulting bitmap.
        for char in text:
            glyph = self.glyph_for_character(char)
            max_ascent = max(max_ascent, glyph.ascent)
            max_descent = max(max_descent, glyph.descent)

            if glyph.left >= 0:
                char_width = int(
                    max(glyph.advance_width, glyph.width + glyph.left))
            else:
                char_width = int(
                    max(glyph.advance_width - glyph.left, glyph.width))

            width += char_width

        height = max_ascent + max_descent
        return (width, height, max_descent)

    def write_python(self, text, font_file):
        """
        Render the given `text` into a python bitmap module.
        """
        _, height, baseline = self.text_dimensions(text)

        bits = []
        widths = []
        offsets = []
        offset = 0

        for char in text:
            glyph = self.glyph_for_character(char)

            # Negative glyph.left fix from peterhinch
            # https://github.com/peterhinch/micropython-font-to-py
            #
            # https://github.com/peterhinch/micropython-font-to-py/issues/21
            # Handle negative glyph.left correctly (capital J),
            # also glyph.width > advance (capital K and R).

            if glyph.left >= 0:
                char_width = int(
                    max(glyph.advance_width, glyph.width + glyph.left))
                left = glyph.left
            else:
                char_width = int(
                    max(glyph.advance_width - glyph.left, glyph.width))
                left = 0

            # save the bit offset and width of the current glyph
            offsets.append(offset)
            widths.append(char_width)
            outbuffer = Bitmap(char_width, height)

            # The vertical drawing position should place the glyph
            # on the baseline as intended.
            y = height - glyph.ascent - baseline
            outbuffer.bitblt(glyph.bitmap, left, y)

            # convert bitmap to ascii bitmap string
            bit_string = outbuffer.bit_string()
            bits.append(bit_string)
            offset += len(bit_string)

        # join all the bitmap strings together
        bit_string = ''.join(bits)

        # escape backslash, quote and single quote characters for char_map
        text_escaped = text.replace('\\', '\\\\').replace('"', '\\"').replace("'", "\\'")
        char_map = wrap_str(text_escaped)

        cmd_line = " ".join(map(shlex.quote, sys.argv))
        max_width = max(widths)

        # write python module source
        print('# -*- coding: utf-8 -*-')
        print(f'# Converted from {font_file} using:')
        print(f'#     {cmd_line}')
        print()

        print(f'MAP = {char_map}\n')
        print('BPP = 1')
        print(f'HEIGHT = {height}')
        print(f'MAX_WIDTH = {max_width}')
        print('_WIDTHS = \\')
        print(wrap_bytes(widths))
        print()

        byte_offsets = bytearray()
        bytes_table = [0xff, 0xffff, 0xffffff, 0xffffffff]
        bytes_required = bisect.bisect_left(bytes_table, offset, 0, 3) + 1
        for offset in offsets:
            byte_offsets.extend(offset.to_bytes(bytes_required, 'big'))

        print(f'OFFSET_WIDTH = {bytes_required}')
        print('_OFFSETS = \\')
        print(wrap_longs(byte_offsets))
        print()

        print('_BITMAPS =\\')
        byte_values = [int(bit_string[i:i+8], 2) for i in range(0, len(bit_string), 8)]
        print(wrap_bytes(byte_values))
        print("\nWIDTHS = memoryview(_WIDTHS)")
        print("OFFSETS = memoryview(_OFFSETS)")
        print("BITMAPS = memoryview(_BITMAPS)")


def main():
    parser = argparse.ArgumentParser(
        prog='font2bitmap',
        description=('''
            Convert characters from a truetype font to a python bitmap for use
            with the bitmap method in the st7789 and ili9342 drivers.'''))

    parser.add_argument(
        'font_file',
        help='name of font file to convert.')

    parser.add_argument(
        'font_height',
        type=int,
        default=8,
        help='size of font to create bitmaps from.')

    parser.add_argument(
        '-width', '--font_width',
        type=int,
        default=None,
        help='width of font to create bitmaps from.')

    group = parser.add_argument_group(
        'character selection',
        'characters from the font to include in the bitmap.')

    excl = group.add_mutually_exclusive_group(required=True)
    excl.add_argument(
        '-c', '--characters',
        help='''integer or hex character values and/or ranges to include.
        For example: "65, 66, 67" or "32-127" or "0x30-0x39, 0x41-0x5a"''')

    excl.add_argument(
        '-s', '--string',
        help='''string of characters to include
        For example: "1234567890-."''')

    args = parser.parse_args()
    font_file = args.font_file
    height = args.font_height
    width = args.font_height if args.font_width is None else args.font_width
    characters = get_chars(args.characters) if args.string is None else args.string

    fnt = Font(font_file, width, height)
    fnt.write_python(characters, font_file)


main()
