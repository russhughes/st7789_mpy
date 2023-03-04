"""ESP32 Box or Box Lite with ili9342c 320x240 display"""

from machine import Pin, SPI, freq
import st7789

TFA = 0
BFA = 0

def config(rotation=0, buffer_size=0, options=0):
    custom_init = [
        (b'\x01', 150),                  # soft reset
        (b'\x11', 255),	                 # exit sleep
        (b'\xCB\x39\x2C\x00\x34\x02',),  # power control A
        (b'\xCF\x00\xC1\x30',),		     # power control B
        (b'\xE8\x85\x00\x78',),		     # driver timing control A
        (b'\xEA\x00\x00',),			     # driver timing control B
        (b'\xED\x64\x03\x12\x81',),	     # power on sequence control
        (b'\xF7\x20',),			         # pump ratio control
        (b'\xC0\x23',),			         # power control,VRH[5:0]
        (b'\xC1\x10',),			         # Power control,SAP[2:0];BT[3:0]
        (b'\xC5\x3E\x28',),			     # vcm control
        (b'\xC7\x86',),			         # vcm control 2
        (b'\x3A\x55',),			         # pixel format
        (b'\x36\x08',),			         # madctl
        (b'\xB1\x00\x18',),			     # frameration control,normal mode full colours
        (b'\xB6\x08\x82\x27',),		     # display function control
        (b'\xF2\x00',),			         # 3gamma function disable
        (b'\x26\x01',),			         # gamma curve selected
        # set positive gamma correction
        (b'\xE0\x0F\x31\x2B\x0C\x0E\x08\x4E\xF1\x37\x07\x10\x03\x0E\x09\x00',),
        # set negative gamma correction
        (b'\xE1\x00\x0E\x14\x03\x11\x07\x31\xC1\x48\x08\x0F\x0C\x31\x36\x0F',),
        (b'\x29', 100),                  # display on
    ]

    # rotated 180 degrees -- scrolling demos need to be modified to
    # to scroll in the opposite direction.
    custom_rotations = [
        (0xc8, 320, 240, 0, 0),
        (0xa8, 240, 320, 0, 0),
        (0x08, 320, 240, 0, 0),
        (0x68, 240, 320, 0, 0),
    ]

    # upside down -- scrolling demos are scrolled in the correct direction.
    # custom_rotations = [
    #     (0x08, 320, 240, 0, 0),
    #     (0x68, 240, 320, 0, 0),
    #     (0xc8, 320, 240, 0, 0),
    #     (0xa8, 240, 320, 0, 0),
    # ]

    # Set clock to 240MHz
    freq(240000000)

    # To use baudrates above 26.6MHz you must use my firmware or modify the micropython
    # source code to increase the SPI baudrate limit by adding SPI_DEVICE_NO_DUMMY to the
    # .flag member of the spi_device_interface_config_t struct in the machine_hw_spi_init_internal.c
    # file.  Not doing so will cause the ESP32 to crash if you use a baudrate that is too high.

    return st7789.ST7789(
        SPI(1, baudrate=40000000, sck=Pin(7), mosi=Pin(6)),
        320,
        240,
        reset=Pin(48, Pin.OUT),
        cs=Pin(5, Pin.OUT),
        dc=Pin(4, Pin.OUT),
        backlight=Pin(45, Pin.OUT),
        custom_init=custom_init,
        rotations=custom_rotations,
        rotation=rotation,
        options=options,
        inversion=False,
        color_order=st7789.BGR,
        buffer_size=buffer_size)
