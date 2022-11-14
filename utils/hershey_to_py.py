#!/usr/bin/env python3

"""
Convert Hershey font data to python module.

Usage: hershey_to_py.py <glyph_file> [map_file]

The glyph_file (hf) is the Hershey font data file. The map_file (hmp) is an optional file that maps
the Hershey font data to a character set.  The hershey_to_py.py script is compatible with the output
from my fork of LingDong's ttf2hershey python2 program available from my github repository at
https://github.com/russhughes/ttf2hershey.  Not all TrueType fonts can be converted. Some may
result in a font with out-of-order or missing characters.

A Hershey font file is a text file with the following format:

Optional header lines:

# WIDTH = 40        width of the font
# HEIGHT = 45       height of the font
# FIRST = 32        first character in the font
# LAST = 127        last character in the font

Comment lines start with a # and are ignored with the exception of the optional header lines.

Glyph data lines have the following format:

Bytes 1-5:  The character number
Bytes 6-8:  The number of vector pairs in the glyph
Bytes   9:  left hand position
Bytes  10:  right hand position
Bytes  11+: The vector data as a string of characters, 2 characters per vector.

Vector values are relative to the ascii value of 'R'. A value of " R" non-drawing move to operation.

Example:

   45  6JZLBXBXFLFLB

    Character number: 45 (ASCII '-')
    Number of vectors: 6
    Left hand position: J (ascii value 74 - 82 = -8)
    Right hand position: Z (ascii value 90 - 82 = 8)
    Vector data: LBXBXFLFLB

    The vector data is interpreted as follows:

        LB - Line to (-6, -16)
        XB - Line to (6, -16)
        XF - Line to (6, -12)
        LF - Line to (-6, -12)
        LB - Line to (-6, -16)


A Hershey Map file is a text file with the following format:

Comment lines start with a # and are ignored.

Map data lines have the following format:

Number of the first glyph to include in the font followed by space and the number of the last glyph
in the font.  If the last glyph is 0 then only the first glyph is included.

Example:

32 64
65 127

"""

import argparse
import re
from struct import pack


class HersheyFont:
    """
    Hershey font data
    """

    def __init__(self, width=40, height=45, first=32, last=127, glyphs=None):
        self.width = width
        self.height = height
        self.first = first
        self.last = last
        self.glyphs = glyphs or {}


class Glyph:
    """
    Glyph data

    """

    def __init__(self, num, vectors, count):
        self.num = num
        self.vectors = vectors
        self.count = count


def parse_line(keyword_dict, line):
    """
    Perform regex search against all defined regexes and
    return the key and match result from the first match.
    """
    for key, rx in keyword_dict.items():
        match = rx.search(line)
        if match:
            return key, match

    return None, None


HF_KEYWORDS = {
    'glyph': re.compile(r'^(?P<num>[0-9 ]{5})(?P<length>[0-9 ]{3})(?P<vectors>.*)$'),
    'width': re.compile(r'^# WIDTH = (?P<width>\d+)$'),
    'height': re.compile(r'^# HEIGHT = (?P<height>\d+)$'),
    'first': re.compile(r'^# FIRST = (?P<first>\d+)$'),
    'last': re.compile(r'^# LAST = (?P<last>\d+)$')}


def hershey_load(glyph_file_name, map_file_name=None):
    """
    Load Hershey font, optionally using a map file.
    """
    glyphs = {}
    font = []
    width = 40
    height = 45
    first = 32
    last = 127

    # Read the glyphs file
    with open(glyph_file_name, "r") as file:
        for line in file:
            key, glyph_data = parse_line(HF_KEYWORDS, line.rstrip())

            if key == 'glyph':
                num = int(glyph_data['num'])
                if map_file_name is None:
                    font.append(
                        Glyph(num, glyph_data['vectors'], int(glyph_data['length'])-1))
                else:
                    glyphs[num] = Glyph(
                        num, glyph_data['vectors'], int(glyph_data['length'])-1)

            elif key == 'width':
                width = int(glyph_data['width'])

            elif key == 'height':
                height = int(glyph_data['height'])

            elif key == 'first':
                first = int(glyph_data['first'])

            elif key == 'last':
                last = int(glyph_data['last'])

    # Read the map file if one was specified
    if map_file_name is not None:
        map_line = re.compile(r'(?P<begin>\d+)\s+(?P<end>\d+)$')
        with open(map_file_name, "r") as file:
            for line in file:
                if line[0] == '#':
                    continue

                match = map_line.search(line.rstrip())
                if match:
                    begin = int(match['begin'])
                    end = int(match['end'])
                    if end > 0:
                        font.extend(glyphs[glyph_num] for glyph_num in range(begin, end + 1))
                    else:
                        font.append(glyphs[begin])

    return HersheyFont(width, height, first, last, font)


def write_font(font):
    """
    Write _fronts.
    """
    font_data = bytes()
    for glyph in font.glyphs:
        count = glyph.count
        f_c = bytearray(count.to_bytes(1, byteorder='little'))
        f_v = bytearray(glyph.vectors, 'utf-8')
        font_data += f_c + f_v

    print("_font =\\")
    print("b'", sep='', end='')
    count = 0
    for byte in (font_data):
        print(f'\\x{byte:02x}', sep='', end='')
        count += 1
        if count == 15:
            print("'\\\nb'", sep='', end='')
            count = 0

    print("'")


def write_offsets(offsets):
    """
    Write the 16 bit integer table to the start of the vector data for each
    glyph in the font.
    """

    index_data = bytes()
    for offset in offsets:
        index_data += bytearray(pack('H', offset))

    print("\n_index =\\")
    print("b'", sep='', end='')

    for count, byte in enumerate(index_data):
        if count > 0 and count % 15 == 0:
            print("'\\\nb'",  sep='', end='')
        print(f'\\x{byte:02x}', sep='', end='')
    print("'")


def create_module(font):
    """
    Create python module from Hershey glyphs, optionally using a map file.
    """

    print(f"FIRST = {font.first}")
    print(f"LAST = {font.last}")
    print(f"WIDTH = {font.width}")
    print(f"HEIGHT = {font.height}\n")

    write_font(font)

    offsets = []
    offset = 0
    for glyph in font.glyphs:
        offsets.append(offset)
        offset += len(glyph.vectors) + 1

    write_offsets(offsets)

    print("\nFONT = memoryview(_font)")
    print("INDEX = memoryview(_index)\n")


parser = argparse.ArgumentParser(
    prog='hershey2py',
    description=('''
        Convert hershey format font to python module for use
        with the draw method in the st7789 and ili9342 drivers.'''))

parser.add_argument(
    'hershey_file',
    type=str,
    help='name of hershey font file to convert.')

parser.add_argument(
    'map_file',
    type=str,
    nargs='?',
    default=None,
    help='Hershey glyph map file.')

args = parser.parse_args()

font = hershey_load(args.hershey_file, args.map_file)
create_module(font)
