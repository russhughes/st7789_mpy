"""
cfg_helper.py

    Utility to help with determining colstarts, rowstarts, color_order and inversion settings for
    for a display.

    Set the `HEIGHT` and `WIDTH` constants to the physical size of your display or use the {Cc} keys
    to set the number of columns and the {Rr} keys to set the number of rows for your display.

    The program starts by filling the display with RED and draws a WHITE rectangle around the
    perimeter.

    - If the display background is RED, the color configuration is correct.
    - If the display background is BLUE, toggle the color_order from RGB to BGR using the {Oo} keys.
    - If the display background is YELLOW, toggle the inversion from False to True using the {Ii}
      keys.
    - If the display background is CYAN, toggle both the color_order from RGB to BGR using the {Oo}
      keys and toggle the inversion from False to True using the {Ii} keys.

    Once you have a display with a RED background you can step through RED, GREEN and BLUE
    backgrounds using the {Bb} keys.

    Use the {Yy}, {Xx}, {Vv}, {Ll} and {Hh} keys to toggle the MADCTL_MY, MADCTL_MX, MADCTL_MV,
    MADCTL_ML and MADCTL_ML bits of the MADCTL register.

    The MADCTL_MY bit sets the Page Address Order.
    The MADCTL_MX bit sets the Column Address Order
    The MADCTL_MV bit sets the Page/Column Order
    The MADCTL_ML bit sets the Line Address Order
    The MADCTL_MH bit sets the Display Data Latch Order

    Observe the edges of the display, there should be a 1 pixel wide rectangle outlining the
    display. If one of the lines are not showing or you see random pixels on the outside of the
    white rectangle your display requires a colstart and/or rowstart offset. Some displays have a
    frame buffer memory larger than the physical LCD or LED matrix. In these cases the driver must
    be configured with the position of the first physical column and row pixels relative to the
    frame buffer.  Each rotation setting of the display may require different colstart and rowstart
    values.

    Use the 'W' and 'S' keys to increase or decrease the rowstart values by 10.
    Use the 'w' and 's' keys to increase or decrease the rowstart values by 1.

    Use the 'A' and 'D' keys to increase or decrease the colstart values by 10.
    Use the 'a' and 'd' keys to increase or decrease the colstart values by 1.

    Use the '+' and '-' keys to change the displays rotation.
    Use the '0' key to reset the rotation, the colstart and rowstart values to 0.

    Once you have determined the colstart and rowstart values for the rotations you are going to
    use, press the {Pp} key to print the current configuration values. You can use these values to
    support a display that does not work with the default values.
"""

# pylint: disable=import-error
import sys
from machine import Pin, SPI
import vga1_8x8 as font
import st7789

# Set your display configuration

# TTGO T-Display st7789 135x250 display
# BAUDRATE = 30000000
# COLUMNS = 135
# ROWS = 240
# SCK_PIN = 18
# MOSI_PIN = 19
# RESET_PIN = 23
# CS_PIN = 5
# DC_PIN = 16
# BACKLIGHT_PIN = 4

# Generic st7735 128x128 OR 128X160 display
BAUDRATE = 30000000
COLUMNS = 128
ROWS = 128
SCK_PIN = 18
MOSI_PIN = 19
RESET_PIN = 4
CS_PIN = 13
DC_PIN = 12
BACKLIGHT_PIN = 15

# Waveshare Pico LCD 2 display
# 320×240 ST7789VW
# https://www.waveshare.com/wiki/Pico-LCD-2
# BAUDRATE = 30000000
# COLUMNS = 320
# ROWS = 240
# SCK_PIN = 10
# MOSI_PIN = 11
# RESET_PIN = 12
# CS_PIN = 9
# DC_PIN = 8
# BACKLIGHT_PIN = 13

# madctl register bits
MADCTL_MY = 0x80   # Page Address Order
MADCTL_MX = 0x40   # Column Address Order
MADCTL_MV = 0x20   # Page/Column Order
MADCTL_ML = 0x10   # Line Address Order
MADCTL_MH = 0x04   # Display Data Latch Order
MADCTL_RGB = 0x08  # RGB or BGR color mode

# constants for table access
COLSTART = 0
ROWSTART = 1
NAME = 0
VAL = 1
KEYS = 0
FUNC = 1
ARGS = 2

COLORS = [['Red', st7789.RED],['Green', st7789.GREEN], ['Blue', st7789.BLUE]]
ORDERS = [['st7789.RGB', st7789.RGB], ['st7789.BGR', st7789.BGR]]
INVERSIONS = [['False', False], ['True', True]]

def show_help():
    """Display help for keys"""
    print('\n\nKeys:')
    print('+ Next rotation')
    print('- Previous rotation')
    print('W -10 rowstart, w -1 rowstart')
    print('A -10 colstart, a -1 colstart')
    print('S +10 rowstart, s +1 rowstart')
    print('D +10 colstart, d +1 colstart')
    print('O, o toggle MADCTL_RGB Change color_order')
    print('Y, y Toggle MADCTL_MY Page Address Order')
    print('X, x Toggle MADCTL_MX Column Address Order')
    print('V, v Toggle MADCTL_MV Page/Column Order ')
    print('L, l Toggle MADCTL_ML Line Address Order')
    print('H, h Toggle MADCTL_MH Display Data Latch Order')
    print('C, c Set Columns')
    print('R, r Set Rows')
    print('I, i Toggle inversion')
    print('B, b Change background')
    print('P, p Print current settings')
    print('?    Show Help\n')

class CfgHelper():
    """cfg_helper class implements the cfg_helper"""
    def __init__(self, spi, columns, rows):
        self.spi = spi
        self.rows = rows
        self.columns = columns
        self.rotation = 0
        self.order = 0
        self.color = 0
        self.inversion = 0
        self.madctl = 0
        self.change = True
        self.init_required = False
        self.starts = [[0, 0], [0, 0], [0, 0], [0, 0]]
        self.tft = self.init_display()

    def init_display(self):
        """initialize the display"""
        tft = st7789.ST7789(
            self.spi,
            self.columns,
            self.rows,
            reset=Pin(RESET_PIN, Pin.OUT),
            cs=Pin(CS_PIN, Pin.OUT),
            dc=Pin(DC_PIN, Pin.OUT),
            backlight=Pin(BACKLIGHT_PIN, Pin.OUT),
            color_order=ORDERS[self.order][VAL],
            rotation=self.rotation)

        tft.init()
        self.madctl = tft.madctl()
        self.init_required = False
        return tft

    def center(self, line, text):
        """center text on line"""
        col = (self.columns >> 1) - (len(text) * font.WIDTH >> 1)
        self.tft.text(
            font,
            text,
            col,
            line,
            st7789.WHITE,
            COLORS[self.color][VAL])

    def decode_madctl(self):
        """decode madctl bit values"""
        bits = [bit[NAME] for bit in [
            ("MY", MADCTL_MY),
            ("MX", MADCTL_MX),
            ("MV", MADCTL_MV),
            ("ML", MADCTL_ML),
            ("RGB", MADCTL_RGB),
            ("MH", MADCTL_MH)] if bit[VAL] & self.madctl]

        return " ".join(bits)

    def change_rowstart(self, value):
        """change the rowstart for the current rotation"""
        self.starts[self.rotation][ROWSTART] += value
        self.starts[self.rotation][ROWSTART] %= self.rows

    def change_colstart(self, value):
        """change the colstart for the current rotation"""
        self.starts[self.rotation][COLSTART] += value
        self.starts[self.rotation][COLSTART] %= self.columns

    def change_rotation(self, value):
        """change the current display rotation"""
        self.rotation += value
        self.rotation %= 4
        self.tft.rotation(self.rotation)
        self.columns = self.tft.width()
        self.rows = self.tft.height()

    def print_settings(self):
        """Print the current settings"""
        print("\n\nCurrent settings:")
        print(f'rotation = {self.rotation}')
        print(f'madctl = 0x{self.madctl:02x} ({self.decode_madctl()})')
        print(f'inversion_mode({INVERSIONS[self.inversion][NAME]})')
        print(f'color_order = {ORDERS[self.order][NAME]}')
        for index, offset in enumerate(self.starts):
            print(f'for rotation {index} use offset({offset[COLSTART]}, {offset[ROWSTART]})')
        print()

    def toggle_inversion(self):
        """Toggle the inversion setting"""
        self.inversion += 1
        self.inversion %= len(INVERSIONS)
        print(f'inversion({INVERSIONS[self.inversion][NAME]})')

    def change_background(self, value):
        """Change background color"""
        self.color += value
        self.color %= len(COLORS)
        print(f'background = {COLORS[self.color][NAME]}')

    def toggle_madctl_bit(self, name, bit):
        """Toggle the MADCTL bit"""
        self.madctl ^= bit
        self.tft.madctl(self.madctl)
        if self.madctl & bit:
            print(f'{name} Set')
        else:
            print(f'{name} Cleared')

        # datasheet says if RGB bit is set the color_mode is BGR
        self.order = 1 if self.madctl & MADCTL_RGB else 0

    def set_rows(self):
        """Set the display rows (height)"""
        rows_entered = int(input("Enter Rows (0-Cancel) ?"))
        if  rows_entered != 0:
            self.rows = rows_entered
            self.init_required = True

    def set_columns(self):
        """Set the display columns (width)"""
        cols_entered = int(input("Enter Columns (0-Cancel) ?"))
        if  cols_entered != 0:
            self.columns = cols_entered
            self.init_required = True

    def reset_rotations(self):
        """Reset the colstarts and rowstarts for all rotations"""
        self.starts = [[0, 0], [0, 0], [0, 0], [0, 0]]
        self.rotation = 0
        self.init_required = True

    def update_display(self):
        """fill display with current background color"""
        self.tft.fill(COLORS[self.color][VAL])

        # show current settings on display
        self.center(font.HEIGHT, f'Rot {self.rotation}')
        self.center(font.HEIGHT*3, COLORS[self.color][NAME])
        self.center(font.HEIGHT*5, f'MADCTL 0x{self.madctl:02x}')
        self.center(font.HEIGHT*6, self.decode_madctl())
        self.center(font.HEIGHT*8, f'colstart {self.starts[self.rotation][COLSTART]}')
        self.center(font.HEIGHT*9, f'rowstart {self.starts[self.rotation][ROWSTART]}')
        self.center(font.HEIGHT*11,"inversion")
        self.center(font.HEIGHT*12, f'{INVERSIONS[self.inversion][NAME]}')

        # draw white rectangle around the perimeter of the display
        self.tft.rect(0, 0, self.columns, self.rows, st7789.WHITE)
        print('? for help: ', end='')

    def menu(self):
        """handle menu"""
        menu_items = [
            ({'W'},      self.change_rowstart,    (-10,)),
            ({'w'},      self.change_rowstart,    (-1,)),
            ({'S'},      self.change_rowstart,    (10,)),
            ({'s'},      self.change_rowstart,    (1,)),
            ({'A'},      self.change_colstart,    (-10,)),
            ({'a'},      self.change_colstart,    (-1,)),
            ({'D'},      self.change_colstart,    (10,)),
            ({'d'},      self.change_colstart,    (1,)),
            ({'+'},      self.change_rotation,    (1,)),
            ({'-'},      self.change_rotation,    (-1,)),
            ({'P', 'p'}, self.print_settings,     ()),
            ({'I', 'i'}, self.toggle_inversion,   ()),
            ({'B'},      self.change_background,  (1,)),
            ({'b'},      self.change_background,  (-1,)),
            ({'O', 'o'}, self.toggle_madctl_bit,  ("MADCTL_RGB", MADCTL_RGB)),
            ({'Y', 'y'}, self.toggle_madctl_bit,  ("MADCTL_MY",  MADCTL_MY)),
            ({'X', 'x'}, self.toggle_madctl_bit,  ("MADCTL_MX",  MADCTL_MX)),
            ({'V', 'v'}, self.toggle_madctl_bit,  ("MADCTL_MV",  MADCTL_MV)),
            ({'L', 'l'}, self.toggle_madctl_bit,  ("MADCTL_ML",  MADCTL_ML)),
            ({'H', 'h'}, self.toggle_madctl_bit,  ("MADCTL_MH",  MADCTL_MH)),
            ({'R', 'r'}, self.set_rows,           ()),
            ({'C', 'c'}, self.set_columns,        ()),
            ({'0'},      self.reset_rotations,    ()),
            ({'?'},      show_help,               ())]

        while True:
            if self.change:
                # init the display if last change requires it.
                if self.init_required:
                    self.tft = self.init_display()

                # set current colstart and rowstart for this rotation
                self.tft.offset(
                    self.starts[self.rotation][COLSTART],
                    self.starts[self.rotation][ROWSTART])

                # set current inversion mode
                self.tft.inversion_mode(INVERSIONS[self.inversion][VAL])

                # show the current settings on the display
                self.update_display()

            # get user keypress
            key_pressed = sys.stdin.read(1)
            self.change = False

            for menu_item in menu_items:
                if key_pressed in menu_item[KEYS]:
                    print(key_pressed)
                    _, action, args = menu_item
                    action(*args)
                    self.change = True

def main():
    """init display and process menu"""

    # init the SPI port for the display
    display_spi = SPI(1, baudrate=BAUDRATE, sck=Pin(SCK_PIN), mosi=Pin(MOSI_PIN))
    cfg = CfgHelper(display_spi, COLUMNS, ROWS)
    show_help()
    while True:
        cfg.menu()

main()
