"""
proverbs.py - Displays what I hope are chinese proverbs in simplified chinese to test UTF-8
    font support.
"""

import random
import math
import utime
from machine import Pin, SPI

import proverbs_font as font
import st7789

# Select a config module for your display
## import esp32_7735_128 as Driver
## import esp32_7735_160 as Driver
import esp32_st7789 as Driver
## import pybv11_st7789 as Driver
## import tdisplay as Driver
## import twatch_2020_v2 as Driver
## import ws_pico_114 as Driver
## import ws_pico_13 as Driver
## import ws_pico_2 as Driver

tft = Driver.config(1)

def color_wheel(WheelPos):
    """returns a 565 color from the given position of the color wheel"""
    WheelPos = (255 - WheelPos) % 255

    if WheelPos < 85:
        return st7789.color565(255 - WheelPos * 3, 0, WheelPos * 3)

    if WheelPos < 170:
        WheelPos -= 85
        return st7789.color565(0, WheelPos * 3, 255 - WheelPos * 3)

    WheelPos -= 170
    return st7789.color565(WheelPos * 3, 255 - WheelPos * 3, 0)

def main():

    proverbs = [
        "万事起头难",
        "熟能生巧",
        "冰冻三尺，非一日之寒",
        "三个臭皮匠，胜过诸葛亮",
        "今日事，今日毕",
        "师父领进门，修行在个人",
        "一口吃不成胖子",
        "欲速则不达",
        "百闻不如一见",
        "不入虎穴，焉得虎子"]

    # initialize display
    tft.init()
    line_height = font.HEIGHT+8
    half_height = tft.height() // 2
    half_width = tft.width() // 2
    wheel = 0

    tft.fill(st7789.BLACK)

    while True:
        for proverb in proverbs:
            proverb_lines = proverb.split('，')
            half_lines_height = len(proverb_lines) * line_height // 2

            tft.fill(st7789.BLACK)

            for count, proverb_line in enumerate(proverb_lines):
                half_length = tft.write_len(font, proverb_line) // 2

                tft.write(
                    font,
                    proverb_line,
                    half_width - half_length,
                    half_height - half_lines_height + count * line_height,
                    color_wheel(wheel))

            wheel = (wheel + 5) % 256

            # pause to slow down scrolling
            utime.sleep(5)


main()
