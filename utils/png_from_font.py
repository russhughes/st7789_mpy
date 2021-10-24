#!/usr/bin/env python

"""
Imports all the python font files from the specified -input-directory (-i) and
creates png samples of each font in the specified -output-directory (-o).

Example:
    png_from_font.py font_directory png_directory

Requires argparse, importlib and pypng
"""

import os
import importlib
import png
import argparse

def create_png(font_file_name, png_file_name):

        module_spec = importlib.util.spec_from_file_location('font', font_file_name)
        font = importlib.util.module_from_spec(module_spec)
        module_spec.loader.exec_module(font)
        char_count = font.LAST - font.FIRST
        column_count = 16
        row_count = (char_count // column_count)

        with open(png_file_name, 'wb') as png_file:
            image = png.Writer((16+2) * font.WIDTH, (row_count+3) * font.HEIGHT, bitdepth=1)
            image_data = [[0 for j in range((16+2) * font.WIDTH)] for i in range((row_count+3)* font.HEIGHT)]
            for chart_row in range(row_count+2):
                for chart_col in range(16):
                    chart_idx = chart_row * 16 + chart_col
                    for char_line in range(font.HEIGHT):
                        for char_byte in range(font.WIDTH//8):
                            ch_idx = chart_idx * font.HEIGHT * font.WIDTH//8 + char_byte + char_line * font.WIDTH//8
                            print(chart_idx, char_count)
                            if (chart_idx <= char_count):
                                data = font.FONT[ch_idx]
                            else:
                                data = 0

                            for bit in range(8):
                                png_row = (chart_row+1)*font.HEIGHT+char_line
                                png_col = (chart_col+1)*font.WIDTH+char_byte*8+bit
                                if data & 1 << 7-bit:
                                    image_data[png_row][png_col] = 1
                                else:
                                    image_data[png_row][png_col] = 0

            print("Creating", png_file_name)
            image.write(png_file, image_data)

def main():
    parser = argparse.ArgumentParser(
        description='Convert 8bit font-bin.bin font files in bin_directory to python in font_directory.')
    parser.add_argument(
        'font_directory', help='directory containing python font files. (input)')
    parser.add_argument(
        'png_directory', help='directory to contain binary font files. (output)')
    args = parser.parse_args()

    for file_name in os.listdir(args.font_directory):
        if file_name.endswith('.py'):
            font_file_name = args.font_directory+'/'+file_name
            png_file_name = args.png_directory+'/'+os.path.splitext(file_name)[0]+'.png'
            create_png(font_file_name, png_file_name)

main()
