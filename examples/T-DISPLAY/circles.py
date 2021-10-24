"""
circles.py

    Draw circles in random colors at random locations on a
    LILYGO® TTGO T-Display.

"""
import random
from machine import Pin, SPI
import st7789

def main():
    tft = st7789.ST7789(
        SPI(1, baudrate=30000000, sck=Pin(18), mosi=Pin(19)),
        135,
        240,
        reset=Pin(23, Pin.OUT),
        cs=Pin(5, Pin.OUT),
        dc=Pin(16, Pin.OUT),
        backlight=Pin(4, Pin.OUT),
        rotation=3)

    tft.init()

    radius_max = 25

    while True:
        for rotation in range(4):
            tft.rotation(rotation)
            tft.fill(0)
            col_max = tft.width() - radius_max
            row_max = tft.height() - radius_max

            for _ in range(128):

                tft.fill_circle(
                    random.randint(0, col_max),
                    random.randint(0, row_max),
                    random.randint(0, radius_max),
                    st7789.color565(
                        random.getrandbits(8),
                        random.getrandbits(8),
                        random.getrandbits(8)))

                tft.circle(
                    random.randint(0, col_max),
                    random.randint(0, row_max),
                    random.randint(0, radius_max),
                    st7789.color565(
                        random.getrandbits(8),
                        random.getrandbits(8),
                        random.getrandbits(8)))


main()
