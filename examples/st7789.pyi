"""
Copyright (c) 2020, 2021 Russ Hughes
This file incorporates work covered by the following copyright and
permission notice and is licensed under the same terms:
The MIT License (MIT)
Copyright (c) 2019 Ivan Belokobylskiy
Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
The driver is based on devbis' st7789py_mpy module from
https://github.com/devbis/st7789py_mpy.
This driver adds support for:
- 320x240, 240x240 and 135x240 pixel displays
- Display rotation
- Hardware based scrolling
- Drawing text using 8 and 16 bit wide bitmap fonts with heights that are
  multiples of 8.  Included are 12 bitmap fonts derived from classic pc
  BIOS text mode fonts.
- Drawing text using converted TrueType fonts.
- Drawing converted bitmaps
"""
import ustruct as struct
from typing import Final


# commands
ST7789_NOP: Final[int] = ...
ST7789_SWRESET: Final[int] = ...
ST7789_RDDID: Final[int] = ...
ST7789_RDDST: Final[int] = ...

ST7789_SLPIN: Final[int] = ...
ST7789_SLPOUT: Final[int] = ...
ST7789_PTLON: Final[int] = ...
ST7789_NORON: Final[int] = ...

ST7789_INVOFF: Final[int] = ...
ST7789_INVON: Final[int] = ...
ST7789_DISPOFF: Final[int] = ...
ST7789_DISPON: Final[int] = ...
ST7789_CASET: Final[int] = ...
ST7789_RASET: Final[int] = ...
ST7789_RAMWR: Final[int] = ...
ST7789_RAMRD: Final[int] = ...

ST7789_PTLAR: Final[int] = ...
ST7789_VSCRDEF: Final[int] = ...
ST7789_COLMOD: Final[int] = ...
ST7789_MADCTL: Final[int] = ...
ST7789_VSCSAD: Final[int] = ...

ST7789_MADCTL_MY: Final[int] = ...
ST7789_MADCTL_MX: Final[int] = ...
ST7789_MADCTL_MV: Final[int] = ...
ST7789_MADCTL_ML: Final[int] = ...
ST7789_MADCTL_BGR: Final[int] = ...
ST7789_MADCTL_MH: Final[int] = ...
ST7789_MADCTL_RGB: Final[int] = ...

ST7789_RDID1: Final[int] = ...
ST7789_RDID2: Final[int] = ...
ST7789_RDID3: Final[int] = ...
ST7789_RDID4: Final[int] = ...

COLOR_MODE_65K: Final[int] = ...
COLOR_MODE_262K: Final[int] = ...
COLOR_MODE_12BIT: Final[int] = ...
COLOR_MODE_16BIT: Final[int] = ...
COLOR_MODE_18BIT: Final[int] = ...
COLOR_MODE_16M: Final[int] = ...

# Color definitions
BLACK: Final[int] = ...
BLUE: Final[int] = ...
RED: Final[int] = ...
GREEN: Final[int] = ...
CYAN: Final[int] = ...
MAGENTA: Final[int] = ...
YELLOW: Final[int] = ...
WHITE: Final[int] = ...

_ENCODE_PIXEL: Final[str] = ...
_ENCODE_POS: Final[str] = ...
_DECODE_PIXEL: Final[str] = ...

_BUFFER_SIZE: Final[int] = ...

_BIT7: Final[int] = ...
_BIT6: Final[int] = ...
_BIT5: Final[int] = ...
_BIT4: Final[int] = ...
_BIT3: Final[int] = ...
_BIT2: Final[int] = ...
_BIT1: Final[int] = ...
_BIT0: Final[int] = ...

WIDTH_320: list[tuple[int, int, int, int]]
"""
Rotation tables (width, height, xstart, ystart)[rotation % 4]
"""

WIDTH_240: list[tuple[int, int, int, int]]
"""
Rotation tables (width, height, xstart, ystart)[rotation % 4]
"""

WIDTH_135: list[tuple[int, int, int, int]]
"""
Rotation tables (width, height, xstart, ystart)[rotation % 4]
"""

ROTATIONS: list[int]
"""
MADCTL ROTATIONS[rotation % 4]
"""


def color565(red: int, green: int = 0, blue: int = 0) -> int:
    """
    Convert red, green and blue values (0-255) into a 16-bit 565 encoding.
    """


def _encode_pos(x: int, y: int) -> bytes:
    """Encode a position into bytes."""


def _encode_pixel(color: int):
    """Encode a pixel color into bytes."""


class ST7789:
    """
    ST7789 driver class
    """
    def __init__(self, spi, width, height, dc=None, reset=None,
                 cs=None, backlight=None, rotations=None, rotation=0, color_order=None,
                 inversion=None, options=None, buffer_size=None):
        """
        Initialize display.
        Args:
        spi (spi): spi object **Required**
        width (int): display width **Required**
        height (int): display height **Required**
        dc (pin): dc pin **Required**
        reset (pin): reset pin
        cs (pin): cs pin
        backlight(pin): backlight pin
        rotations sets the orientation table.
            The orientation table is a list of tuples for each rotation that
            defines the MADCTL register, width, height, start_x, and start_y values.
        color_order set the color order used by the driver st7789.RGB
            and st7789.BGR are supported.
        inversion Sets the display color inversion mode if True,
            clears the display color inversion mode if false.
        rotation (int): display rotation
            - 0-Portrait
            - 1-Landscape
            - 2-Inverted Portrait
            - 3-Inverted Landscape
        buffer_size If a buffer_size is not specified a dynamically allocated
            buffer is created and freed as needed. If a buffer_size is specified
            it must be large enough to contain the largest bitmap, font character
            and/or decoded JPG image used (Rows * Columns * 2 bytes, 16bit
            colors in RGB565 notation). Dynamic allocation is slower and can
            cause heap fragmentation so garbage collection (GC) should be enabled.
        """

    def hard_reset(self):
        """
        Hard reset display.
        """


    def soft_reset(self):
        """
        Soft reset display.
        """

    def sleep_mode(self, value: bool):
        """
        Enable or disable display sleep mode.
        Args:
            value (bool): if True enable sleep mode. if False disable sleep mode
        """

    def inversion_mode(self, value: bool):
        """
        Enable or disable display inversion mode.
        Args:
            value (bool): if True enable inversion mode. if False disable
            inversion mode
        """

    def rotation(self, rotation: int):
        """
        Set display rotation.
        Args:
            rotation (int):
                - 0-Portrait
                - 1-Landscape
                - 2-Inverted Portrait
                - 3-Inverted Landscape
        """

    def vline(self, x: int, y: int, length: int, color: int):
        """
        Draw vertical line at the given location and color.
        Args:
            x (int): x coordinate
            y (int): y coordinate
            length (int): length of line
            color (int): 565 encoded color
        """

    def hline(self, x: int, y: int, length: int, color: int):
        """
        Draw horizontal line at the given location and color.
        Args:
            x (int): x coordinate
            y (int): y coordinate
            length (int): length of line
            color (int): 565 encoded color
        """

    def pixel(self, x: int, y: int, color: int):
        """
        Draw a pixel at the given location and color.
        Args:
            x (int): x coordinate
            y (int): y coordinate
            color (int): 565 encoded color
        """

    def blit_buffer(self, buffer: bytes, x: int, y: int, width: int, height: int):
        """
        Copy buffer to display at the given location.
        Args:
            buffer (bytes): Data to copy to display
            x (int): Top left corner x coordinate
            y (int): Top left corner y coordinate
            width (int): Width
            height (int): Height
        """

    def rect(self, x: int, y: int, w: int, h: int, color: int):
        """
        Draw a rectangle at the given location, size and color.
        Args:
            x (int): Top left corner x coordinate
            y (int): Top left corner y coordinate
            w (int): Width in pixels
            h (int): Height in pixels
            color (int): 565 encoded color
        """

    def fill_rect(self, x: int, y: int, width: int, height: int, color: int):
        """
        Draw a rectangle at the given location, size and filled with color.
        Args:
            x (int): Top left corner x coordinate
            y (int): Top left corner y coordinate
            width (int): Width in pixels
            height (int): Height in pixels
            color (int): 565 encoded color
        """

    def fill(self, color: int):
        """
        Fill the entire FrameBuffer with the specified color.
        Args:
            color (int): 565 encoded color
        """

    def line(self, x0: int, y0: int, x1: int, y1: int, color: int):
        """
        Draw a single pixel wide line starting at x0, y0 and ending at x1, y1.
        Args:
            x0 (int): Start point x coordinate
            y0 (int): Start point y coordinate
            x1 (int): End point x coordinate
            y1 (int): End point y coordinate
            color (int): 565 encoded color
        """

    def vscrdef(self, tfa: int, vsa: int, bfa: int):
        """
        Set Vertical Scrolling Definition.
        To scroll a 135x240 display these values should be 40, 240, 40.
        There are 40 lines above the display that are not shown followed by
        240 lines that are shown followed by 40 more lines that are not shown.
        You could write to these areas off display and scroll them into view by
        changing the TFA, VSA and BFA values.
        Args:
            tfa (int): Top Fixed Area
            vsa (int): Vertical Scrolling Area
            bfa (int): Bottom Fixed Area
        """

    def vscsad(self, vssa: int):
        """
        Set Vertical Scroll Start Address of RAM.
        Defines which line in the Frame Memory will be written as the first
        line after the last line of the Top Fixed Area on the display
        Example:
            for line in range(40, 280, 1):
                tft.vscsad(line)
                utime.sleep(0.01)
        Args:
            vssa (int): Vertical Scrolling Start Address
        """

    def text(self, font, text: str, x0: int, y0: int, color: int=WHITE, background: int=BLACK):
        """
        Draw text on display in specified font and colors. 8 and 16 bit wide
        fonts are supported.
        Args:
            font (module): font module to use.
            text (str): text to write
            x0 (int): column to start drawing at
            y0 (int): row to start drawing at
            color (int): 565 encoded color to use for characters
            background (int): 565 encoded color to use for background
        """

    def bitmap(self, bitmap, x: int, y: int, index: int=0):
        """
        Draw a bitmap on display at the specified column and row
        Args:
            bitmap (bitmap_module): The module containing the bitmap to draw
            x (int): column to start drawing at
            y (int): row to start drawing at
            index (int): Optional index of bitmap to draw from multiple bitmap
                module
        """

    # @micropython.native
    def write(self, font, string: str, x: int, y: int, fg: int=WHITE, bg: int=BLACK,
              background_tuple=None, fill_flag=None):
        """
        Write a string using a converted true-type font on the display starting
        at the specified column and row
        Args:
            font (font): The module containing the converted true-type font
            string (str): The string to write
            x (int): column to start writing
            y (int): row to start writing
            fg (int): foreground color, optional, defaults to WHITE
            bg (int): background color, optional, defaults to BLACK
            background_tuple: Transparency can be emulated by providing a
                background_tuple containing (bitmap_buffer, width, height).
                This is the same format used by the jpg_decode method.
                See examples/T-DISPLAY/clock/clock.py for an example.
            fill_flag:
        """

    def write_len(self, font, string: str):
        """
        Returns the width in pixels of the string if it was written with the
        specified font
        Args:
            font (font): The module containing the converted true-type font
            string (string): The string to measure
        """

    def madctl(self, value):
        """
        Returns the current value of the MADCTL register. Optionally sets the
        MADCTL register if a value is passed to the method.
        """

    def init(self):
        """
        Must be called to initalize the display.
        """

    def on(self):
        """
        Turn on the backlight pin if one was defined during init.
        """

    def off(self):
        """
        Turn off the backlight pin if one was defined during init.
        """

    def circle(self, x: int, y: int, r: int, color: int):
        """
        Draws a circle with radius r centered at the (x, y) coordinates in the given color.
        """

    def fill_circle(self, x: int, y: int, r: int, color: int):
        """
        Draws a filled circle with radius r centered at the (x, y) coordinates in the given color.
        """

    def draw(self, vector_font, s: str, x: int, y: int, fg: int=WHITE, scale: int=1.0):
        """
        Draw text to the display using the specified hershey vector font with
        the coordinates as the lower-left corner of the text. The foreground
        color of the text can be set by the optional argument fg, otherwise
        the foreground color defaults to WHITE. The size of the text can be
        scaled by specifying a scale value. The scale value must be larger
        than 0 and can be a floating point or an integer value. The scale value
        defaults to 1.0. See the README.md in the vector/fonts directory
        for example fonts and the utils directory for a font conversion program.
        """

    def draw_len(self, vector_font, s: str, scale: int=1.0):
        """
        Returns the width of the string in pixels if drawn with the specified font.
        """

    def jpg(self, jpg_filename: str, x: int, y: int, method=None):
        """
        Draw JPG file on the display at the given x and y coordinates as the
        upper left corner of the image. There memory required to decode and
        display a JPG can be considerable as a full screen 320x240 JPG would
        require at least 3100 bytes for the working area + 320 * 240 * 2 bytes
        of ram to buffer the image. Jpg images that would require a buffer
        larger than available memory can be drawn by passing SLOW for method.
        The SLOW method will draw the image a piece at a time using the Minimum
        Coded Unit (MCU, typically a multiple of 8x8) of the image.
        """

    def jpg_decode(self, jpg_filename: str, x: int, y: int, width: int, height: int):
        """
        Decode a jpg file and return it or a portion of it as a tuple composed
        of (buffer, width, height). The buffer is a color565 blit_buffer
        compatible byte array. The buffer will require width * height * 2 bytes of memory.

        If the optional x, y, width and height parameters are given the buffer
        will only contain the specified area of the image.
        See examples/T-DISPLAY/clock/clock.py
        examples/T-DISPLAY/toasters_jpg/toasters_jpg.py for examples.
        """

    def polygon_center(self, polygon: list[tuple[int, int]]):
        """
        Return the center of the polygon as an (x, y) tuple.
        The polygon should consist of a list of (x, y) tuples forming a closed convex polygon.
        """

    def fill_polygon(self, polygon: list[tuple[int, int]], x: int, y: int, color: int,
                     angle: int=0, center_x: int=0, center_y: int=0):
        """
        Draw a filled polygon at the x, y coordinates in the color given.
        The polygon may be rotated angle radians about the center_x and center_y point.
        The polygon should consist of a list of (x, y) tuples forming a closed convex polygon.
        """

    def polygon(self, polygon: list[tuple[int, int]], x: int, y: int, color: int,
                angle: int, center_x: int, center_y: int):
        """
        Draw a polygon at the x, y coordinates in the color given.
        The polygon may be rotated angle radians a bout the center_x and center_y point.
        The polygon should consist of a list of (x, y) tuples forming a closed convex polygon.

        See the T-Display roids.py for an example.
        """

    def bounding(self, status: bool, as_rect=False):
        """
        Bounding turns on and off tracking the area of the display that has been written to.
        Initially tracking is disabled, pass a True value to enable tracking and False to
        disable. Passing a True or False parameter will reset the current bounding rectangle
        to (display_width, display_height, 0, 0).

        Returns a four integer tuple containing (min_x, min_y, max_x, max_y)
        indicating the area of the display that has been written to since the last clearing.

        If as_rect parameter is True, the returned tuple will contain
        (min_x, min_y, width, height) values.
        """

    def width(self):
        """
        Returns the current logical width of the display.
        (ie a 135x240 display rotated 90 degrees is 240 pixels wide)
        """

    def height(self):
        """
        Returns the current logical height of the display.
        (ie a 135x240 display rotated 90 degrees is 135 pixels high)
        """

    def offset(self, x_start: int, y_start: int):
        """
        The memory in the ST7789 controller is configured for a 240x320 display.
        When using a smaller display like a 240x240 or 135x240 an offset needs
        to added to the x and y parameters so that the pixels are written to
        the memory area that corresponds to the visible display. The offsets
        may need to be adjusted when rotating the display.
        """
