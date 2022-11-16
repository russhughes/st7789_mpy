"""M5Stack CORE2 ili9342 320x240 display"""

from machine import Pin, SPI, freq
import st7789
import axp202c

TFA = 0
BFA = 0


def config(rotation=0, buffer_size=0, options=0):
    """Configure the M5Stack CORE2 display using a custom_init and
        custom_rotations since the display is ili9342c. The custom_init is a
        list of commands to send to the display during the init() metehod. The
        list contains tuples with a bytes object, optionally followed by a
        delay specified in ms. The first byte of the bytes object contains the
        command to send optionally followed by data bytes.
    """
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
        (b'\x36\x00',),			         # madctl
        (b'\x21',),			             # inversion on
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

    custom_rotations = [
        (0x08, 320, 240, 0, 0),
        (0x68, 240, 320, 0, 0),
        (0xc8, 320, 240, 0, 0),
        (0xa8, 240, 320, 0, 0),
    ]

    # Set clock to 240MHz
    freq(240000000)

    axp = axp202c.PMU(address=0x34)
    axp.enablePower(axp202c.AXP192_LDO2)
    # Set backlight voltage
    axp.setDC3Voltage(3000)

    return st7789.ST7789(
        SPI(2, baudrate=24000000, sck=Pin(18), mosi=Pin(23)),
        320,
        240,
        cs=Pin(5, Pin.OUT),
        dc=Pin(15, Pin.OUT),
        custom_init=custom_init,
        rotations=custom_rotations,
        rotation=rotation,
        color_order=st7789.RGB,
        inversion=False,
        options=options,
        buffer_size=buffer_size)
