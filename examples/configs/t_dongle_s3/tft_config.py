""" LilyGo T-DONGLE-S3 80x160 ST7735 display """

from machine import freq, Pin, SPI
import st7789

# start in second gear
freq(240000000)

TFA = 1
BFA = 1

def config(rotation=0, buffer_size=0, options=0):
    """Configure the T-DONGLE-S3 display using a custom_init and
    custom_rotations since the display is st7735.

    The custom_init is a list of commands to send to the display during the init() metehod.
    The list contains tuples with a bytes object, optionally followed by a delay specified in ms.
    The first byte of the bytes object contains the command to send optionally followed by data bytes.
    """

    custom_init = [
        (b'\x01', 150),
        (b'\x11', 255),
        (b'\xb1\x01\x2c\x2d',),
        (b'\xb2\x01\x2c\x2d',),
        (b'\xb3\x01\x2c\x2d\x01\x2c\x2d',),
        (b'\xb4\x07',),
        (b'\xc0\xa2\x02\x84',),
        (b'\xc1\xc5',),
        (b'\xc2\x0a\x00',),
        (b'\xc3\x8a\x2a',),
        (b'\xc4\x8a\xee',),
        (b'\xc5\x0e',),
        (b'\x21',),
        (b'\x36\x08',),
        (b'\x3a\x05',),
        (b'\x2a\x00\x01\x00\x7f',),
        (b'\x2b\x00\x01\x00\x9f',),
        (b'\xe0\x02\x1c\x07\x12\x37\x32\x29\x2d\x29\x25\x2b\x39\x00\x01\x03\x10',),
        (b'\xe1\x03\x1d\x07\x06\x2e\x2c\x29\x2d\x2e\x2e\x37\x3f\x00\x00\x02\x10',),
        (b'\x13', 10),
        (b'\x29', 100),
    ]

    custom_rotations = [
        (0x08,  80, 160, 26,  1),
        (0x68, 160,  80,  1, 26),
        (0xc8,  80, 160, 26,  1),
        (0xa8, 160,  80,  1, 26)
    ]

    return st7789.ST7789(
        SPI(2, baudrate=60000000, sck=Pin(5), mosi=Pin(3), miso=None),
        80,
        160,
        reset=Pin(1, Pin.OUT),
        cs=Pin(4, Pin.OUT),
        dc=Pin(2, Pin.OUT),
        custom_init=custom_init,
        rotations=custom_rotations,
        color_order=st7789.BGR,
        rotation=rotation,
        options=options,
        buffer_size=buffer_size)
