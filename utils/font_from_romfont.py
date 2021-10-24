#!/usr/bin/env python
"""
Convert fonts from the font-bin directory of spacerace's
https://github.com/spacerace/romfont repo.

Reads all romfont bin files from the specified -input-directory (-i) and writes
python font files to the specified -output-directory (-o).  Optionally limiting
characters included to -first-char (-f) thru -last-char (-l).

Example:

    font_from_romfont -i font-bin -o pyfont -f 32 -l 127

requires argparse
"""
import os
import re
import argparse

def convert_font(file_in, file_out, width, height, first=0x0, last=0xff):
    chunk_size = height
    with open(file_in, "rb") as bin_file:
        bin_file.seek(first * height)
        current = first
        with open(file_out, 'wt') as font_file:
            print(f'"""converted from {file_in} """', file=font_file)
            print(f'WIDTH = {width}', file=font_file)
            print(f'HEIGHT = {height}', file=font_file)
            print(f'FIRST = 0x{first:02x}', file=font_file)
            print(f'LAST = 0x{last:02x}', file=font_file)
            print('_FONT =\\\n', sep='', end='', file=font_file)
            for chunk in iter(lambda: bin_file.read(chunk_size), b''):
                print('b\'', sep='', end='', file=font_file)
                for data in chunk:
                    print(f'\\x{data:02x}', end='', file=font_file)
                print('\'\\', file=font_file)
                current += 1
                if current > last:
                    break

            print('', file=font_file)
            print('FONT = memoryview(_FONT)', file=font_file)

def auto_int(x):
    return int(x, 0)

def main():
    parser = argparse.ArgumentParser(
        description='Convert Romfont.bin font files in input to python in font_directory.')
    parser.add_argument('input', help='file or directory containing binary font file(s).')
    parser.add_argument('output', help='file or directory to contain python font file(s).')
    parser.add_argument('-f', '--first-char', type=auto_int, default=0x20)
    parser.add_argument('-l', '--last-char', type=auto_int, default=0x7f)
    args = parser.parse_args()

    file_re = re.compile(r'^(.*)(\d+)x(\d+)\.bin$')

    is_dir = os.path.isdir(args.input)
    bin_files = os.listdir(args.input) if is_dir else [args.input]
    for bin_file_name in bin_files:
        match = file_re.match(bin_file_name)
        if match:
            font_width = int(match.group(2))
            font_height = int(match.group(3))

            if is_dir:
                bin_file_name = args.input+'/'+bin_file_name

            if is_dir:
                font_file_name = (
                    args.font_directory + '/' +
                    match.group(1).rstrip('_').lower()+
                    f'_{font_width}x{font_height}.py')
            else:
                font_file_name = args.output

            print("converting", bin_file_name, 'to', font_file_name)

            convert_font(
                bin_file_name,
                font_file_name,
                font_width,
                font_height,
                args.first_char,
                args.last_char)

main()
