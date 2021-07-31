'''
watch.py - Analog Watch Display
    Video: https://youtu.be/NItKb6umMc4
'''

import utime
import math
from machine import Pin, SPI
import axp202c
import st7789

def main():
    '''
    Draw analog watch face and update time
    '''
    try:
        # Turn power on display power
        axp = axp202c.PMU()
        axp.enablePower(axp202c.AXP202_LDO2)

        # initialize spi port
        spi = SPI(
            1,
            baudrate=32000000,
            sck=Pin(18, Pin.OUT),
            mosi=Pin(19, Pin.OUT))

        # configure display
        tft = st7789.ST7789(
            spi,
            240,
            240,
            cs=Pin(5, Pin.OUT),
            dc=Pin(27, Pin.OUT),
            backlight=Pin(12, Pin.OUT),
            rotation=2)

        # enable display
        tft.init()

        # draw the watch face background
        tft.jpg("face.jpg", 0, 0, st7789.SLOW)

        # define the polygons for the hour, minute and second hands
        # polygons must be closed convex polygons or bad things(tm) happen.

        second_poly = [
            (3, 1), (1, 3), (1, 72), (3, 75), (6, 72), (6, 3), (4, 1), (3, 1)]

        minute_poly = [
            (5, 1), (1, 8), (1, 72), (5, 75), (10, 72), (10, 8), (6, 1), (5, 1)]

        hour_poly = [
            (7, 1), (1, 8), (1, 62), (7, 65), (14, 62), (14, 8), (10, 1), (7, 1)]

        # constants for calculating hand angles.
        pi_div_6 = math.pi/6
        pi_div_30 = math.pi/30
        pi_div_360 = math.pi/360
        pi_div_1800 = math.pi/1800
        pi_div_2160 = math.pi/2160

        # initialize variables for the bounding rectangles for the
        # hour, minute and second hands. Calling bounding with True will
        # reset the bounds, calling with False will disable bounding

        tft.bounding(True)
        hour_bound = tft.bounding(True)
        minute_bound = tft.bounding(True)
        second_bound = tft.bounding(True)

        while True:
            # save the current time in seconds so we can determine when
            # when to update the display.
            last = utime.time()

            # get the current hour, minute and second
            _, _, _, hour, minute, second, _, _ = utime.localtime()

            # constrain hours to 12 hour time
            hour %= 12

            # calculate the angle of the hour hand in radians
            hour_ang = (
                (hour * pi_div_6) +
                (minute * pi_div_360) +
                (second * pi_div_2160))

            # calculate the angle of the minute hand in radians
            minute_ang = ((minute*pi_div_30)+(second*pi_div_1800))

            # calculate the angle of the second hand on radians
            second_ang = (second*pi_div_30)

            # erase the bounding area of the last drawn hour hand
            x1, y1, x2, y2 = hour_bound
            tft.fill_rect(x1, y1, x2-x1+1, y2-y1+1, st7789.WHITE)

            # erase the bounding area of the last drawn minute hand
            x1, y1, x2, y2 = minute_bound
            tft.fill_rect(x1, y1, x2-x1+1, y2-y1+1, st7789.WHITE)

            # erase the bounding area of the last drawn second hand
            x1, y1, x2, y2 = second_bound
            tft.fill_rect(x1, y1, x2-x1+1, y2-y1+1, st7789.WHITE)

            tft.bounding(True)      # clear bounding rectangle

            # draw and fill the hour hand polygon rotated to hour_ang
            tft.fill_polygon(
                hour_poly,
                112,                # 119-7 (half polygon_width)
                59,                 # 119-60 (polygon_height - tail)
                st7789.BLACK,
                hour_ang,
                7,                  # center of
                60)                 #   polygon rotaton

            # get the bounding rectangle of the hour_polygon as drawn and
            # reset the bounding box for the next polygon
            hour_bound = tft.bounding(True)

            # draw and fill the minute hand polygon rotated to minute_ang
            tft.fill_polygon(
                minute_poly,
                114,                # 119-5 (half polygon_width)
                49,                 # 119-70 (polygon_height - tail)
                st7789.BLACK,
                minute_ang,
                5,                  # center of
                70)                 #   polygon rotation

            # get the bounding rectangle of the minute_polygon as drawn and
            # reset the bounding box for the next polygon
            minute_bound = tft.bounding(True)

            # draw and fill the second hand polygon rotated to second_ang

            tft.fill_polygon(
                second_poly,
                116,                # 119-3 (half polygon_width)
                49,                 # 119-70 (polygon_height - tail)
                st7789.RED,
                second_ang,
                3,                  # center of
                70)                 #   polygon rotation

            # get the bounding rectangle of the second_polygon as drawn and
            # reset the bounding box for the next polygon
            second_bound = tft.bounding(True)

            # wait until the current second changes
            while last == utime.time():
                utime.sleep_ms(50)

    finally:
        # shutdown spi
        if 'spi' in locals():
            spi.deinit()


main()
