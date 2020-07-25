"""
watch_hello.py

    Writes "Hello!" in random colors at random locations on a
    LILYGO® TTGO T-Watch 2020.

    https://youtu.be/Bwq39tuMoY4

"""
import time
import random
from machine import Pin, SPI
import axp202c
import st7789

# Choose a font

# import vga1_8x8 as font
# import vga2_8x8 as font

# import vga1_8x16 as font
# import vga2_8x16 as font

# import vga1_16x16 as font
# import vga1_bold_16x16 as font
# import vga2_16x16 as font
# import vga2_bold_16x16 as font

# import vga1_16x32 as font
# import vga1_bold_16x32 as font
# import vga2_16x32 as font
import vga2_bold_16x32 as font

def wheel(pos):
    pos = 255 - (pos % 255)
    if pos < 85:
        return st7789.color565(255 - pos * 3, 0, pos * 3)

    if pos < 170:
        pos -= 85
        return st7789.color565(0, pos * 3, 255 - pos * 3)

    pos -= 170
    return st7789.color565(pos * 3, 255 - pos * 3, 0)

def random_color():
    return st7789.color565(
        random.getrandbits(8),
        random.getrandbits(8),
        random.getrandbits(8))

def main():
    try:
        # Turn power on display power
        axp = axp202c.PMU()
        axp.enablePower(axp202c.AXP202_LDO2)

        # initalize spi port
        spi = SPI(
            2,
            baudrate=32000000,
            polarity=1,
            phase=0,
            bits=8,
            firstbit=0,
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
        tft.fill(st7789.BLACK)
        time.sleep(2)

        while True:
            # say Hello! and show off some colors
            tft.fill(st7789.BLUE)
            tft.text(font, "Hello!", 76, 96, st7789.WHITE, st7789.BLUE)
            time.sleep(1)
            tft.fill(0)
            for _ in range(2):
                for i in range(256):
                    j = i % 64
                    tft.rect(68-j, 96-j, j*2+104, j*2+32, wheel(i))
                    tft.text(font, "Hello!", 76, 96, wheel(i))

            time.sleep(1)

            # display some random letters
            tft.fill(0)
            col_max = tft.width() - font.WIDTH
            row_max = tft.height() - font.HEIGHT

            for i in range(5):
                for c in range(0, 255):
                    tft.text(
                        font,
                        c,
                        random.randint(0, col_max),
                        random.randint(0, row_max),
                        random_color())
                    time.sleep(0.005)

            time.sleep(1)

            # write hello! randomly on display running through each rotation
            for rotation in range(9):
                tft.fill(0)
                tft.rotation(rotation%4+2)
                col_max = tft.width() - font.WIDTH*6
                row_max = tft.height() - font.HEIGHT

                for _ in range(250):
                    tft.text(
                        font,
                        "Hello!",
                        random.randint(0, col_max),
                        random.randint(0, row_max),
                        random_color(),
                        random_color())

    finally:
        # shutdown spi
        spi.deinit()
        # turn off display power
        axp.disablePower(axp202c.AXP202_LDO2)

main()
