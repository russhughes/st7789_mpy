"""Generic ESP32 with 128x160 7735 display"""

from machine import Pin, SPI
import st7789

# Orientation Overrides for each rotation of the display counter-clockwise, with the ribbon
# cable at the top of the display.  0-Portrait (0 degrees), 1-Landscape (90 degrees), 2-Inverse
# Portrait (180 degrees), 3-Inverse Landscape (270 degrees)Portrait.
# (MADCTL Register Value, width, height, start_x, start_y)x

ORIENTATIONS = [
    (st7789.RGB,                          128, 160, 0, 0),
    (st7789.MADCTL_MX | st7789.MADCTL_MV, 160, 128, 0, 0),
    (st7789.MADCTL_MY | st7789.MADCTL_MX, 128, 160, 0, 0),
    (st7789.MADCTL_MY | st7789.MADCTL_MV, 160, 128, 0, 0),
]

TFA = 0
BFA = 0

def config(rotation=0, buffer_size=0, options=0):
    return st7789.ST7789(
        SPI(1, baudrate=20000000, sck=Pin(18), mosi=Pin(19)),
        128,
        160,
        reset=Pin(4, Pin.OUT),
        cs=Pin(13, Pin.OUT),
        dc=Pin(12, Pin.OUT),
        backlight=Pin(15, Pin.OUT),
        color_order=st7789.RGB,
        inversion=False,
        rotations=ORIENTATIONS,
        rotation=rotation,
        options=options,
        buffer_size=buffer_size)
