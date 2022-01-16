"""Generic ESP32 with 128x128 7735 display"""

from machine import Pin, SPI
import st7789

# Orientation Overrides for each rotation of the display counter-clockwise, with the ribbon cable at
# the top of the display.  0-Portrait (0 degrees), 1-Landscape (90 degrees), 2-Inverse Portrait
# (180 degrees), 3-Inverse Landscape (270 degrees)Portrait.
# (MADCTL Register Value, width, height, start_x, start_y)x

ORIENTATIONS = [
    (0,                                   128, 128, 2, 1),
    (st7789.MADCTL_MX | st7789.MADCTL_MV, 128, 128, 1, 2),
    (st7789.MADCTL_MY | st7789.MADCTL_MX, 128, 128, 2, 3),
    (st7789.MADCTL_MY | st7789.MADCTL_MV, 128, 128, 3, 2),
]

TFA = 1
BFA = 3

def config(rotation=0, buffer_size=0, options=0):
    return st7789.ST7789(
        SPI(1, baudrate=30000000, sck=Pin(18), mosi=Pin(19)),
        128,
        128,
        reset=Pin(4, Pin.OUT),
        cs=Pin(13, Pin.OUT),
        dc=Pin(12, Pin.OUT),
        backlight=Pin(15, Pin.OUT),
        color_order=st7789.BGR,
        inversion=False,
        rotations=ORIENTATIONS,
        rotation=rotation,
        options=options,
        buffer_size=buffer_size)
