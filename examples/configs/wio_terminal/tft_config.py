"""Generic ESP32 with ST7789 240x320 display"""

from machine import Pin, SPI
import st7789

TFA = 0
BFA = 0

def config(rotation=0, buffer_size=0, options=0):
    return st7789.ST7789(
        SPI(7 , baudrate=14000000, sck=Pin("LCD_SCK"), mosi=Pin("LCD_MOSI")),
        240,
        320,
        reset=Pin("LCD_RESET", Pin.OUT),
        cs=Pin("LCD_CS", Pin.OUT),
        dc=Pin("LCD_D/C", Pin.OUT),
        backlight=Pin("LED_LCD", Pin.OUT),
        rotation=rotation,
        rotations= [(0x88, 240, 320, 0, 0),
                    (0xe8, 320, 240, 0, 0),
                    (0x48, 240, 320, 0, 0),
                    (0x28, 320, 240, 0, 0)],
        color_order=st7789.RGB,
        inversion=False,
        options=options,
        buffer_size=buffer_size)
