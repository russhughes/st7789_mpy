"""

Adafruit 1.47" 320x172 Round Rectangle Color IPS TFT Display - Product ID: 5393

    Assumes the following pin use, modify code below for your configuration:
        sck: 18,  mosi: 19, reset: 23, cs: 5, dc: 16, backlight: 4

    NOTE: Reduce the SPI baudrate below 26.7MHz unless you are using my compiled firmware or you modify
    the spi_device_interface_config_t devcfg.flags setting in the micropython/ports/esp machine_hw_spi.c
    file to include the SPI_DEVICE_NO_DUMMY flag.

    for example change line 262 in micropython/ports/esp32/machine_hw_spi.c from this:

        .flags = self->firstbit == MICROPY_PY_MACHINE_SPI_LSB ? SPI_DEVICE_TXBIT_LSBFIRST | SPI_DEVICE_RXBIT_LSBFIRST : 0,

    to this:

        .flags = self->firstbit == MICROPY_PY_MACHINE_SPI_LSB ? SPI_DEVICE_TXBIT_LSBFIRST | SPI_DEVICE_RXBIT_LSBFIRST : 0 | SPI_DEVICE_NO_DUMMY,

    Recompile and flash the firmware and you can use the 40MHz speed.
"""


"""
    Adafruit 1.47" 320x172 Round Rectangle Color IPS TFT Display - Product ID: 5393
"""

from machine import Pin, SPI
import st7789

TFA = 40
BFA = 40

custom_rotations = [
    (0x00, 172, 320, 34, 0),
    (0x60, 320, 172, 0, 34),
    (0xc0, 172, 320, 34, 0),
    (0xa0, 320, 172, 0, 34),
]

def config(rotation=0, buffer_size=0, options=0):
    return st7789.ST7789(
        SPI(2, baudrate=40000000, sck=Pin(18), mosi=Pin(19), miso=None),
        172,
        320,
        reset=Pin(23, Pin.OUT),
        cs=Pin(5, Pin.OUT),
        dc=Pin(16, Pin.OUT),
        backlight=Pin(4, Pin.OUT),
        rotations=custom_rotations,
        rotation=rotation,
        options=options,
        buffer_size= buffer_size)
