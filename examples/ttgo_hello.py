"""
ttgo_hello.py

    Writes "Hello!" in random colors at random locations on a
    LILYGO® TTGO T-Display.

    https://www.youtube.com/watch?v=atBa0BYPAAc

"""
import random
from machine import Pin, SPI
import st7789

# Choose a font

# from fonts import vga1_8x8 as font
# from fonts import vga2_8x8 as font

# from fonts import vga1_8x16 as font
# from fonts import vga2_8x16 as font

# from fonts import vga1_16x16 as font
# from fonts import vga1_bold_16x16 as font
# from fonts import vga2_16x16 as font
# from fonts import vga2_bold_16x16 as font

# from fonts import vga1_16x32 as font
# from fonts import vga1_bold_16x32 as font
# from fonts import vga2_16x32 as font
from fonts import vga2_bold_16x32 as font

def main():
    tft = st7789.ST7789(
        SPI(2, baudrate=30000000, polarity=1, phase=1, sck=Pin(18), mosi=Pin(19)),
        135,
        240,
        reset=Pin(23, Pin.OUT),
        cs=Pin(5, Pin.OUT),
        dc=Pin(16, Pin.OUT),
        backlight=Pin(4, Pin.OUT),
        rotation=3)

    tft.init()

    while True:
        for rotation in range(4):
            tft.rotation(rotation)
            tft.fill(0)
            col_max = tft.width() - font.WIDTH*6
            row_max = tft.height() - font.HEIGHT

            for _ in range(250):
                tft.text(
                    font,
                    "Hello!",
                    random.randint(0, col_max),
                    random.randint(0, row_max),
                    st7789.color565(
                        random.getrandbits(8),
                        random.getrandbits(8),
                        random.getrandbits(8)),
                    st7789.color565(
                        random.getrandbits(8),
                        random.getrandbits(8),
                        random.getrandbits(8))
                )

main()
