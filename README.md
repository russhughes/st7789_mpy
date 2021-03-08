# ST7789 Driver for MicroPython

This driver is based on [devbis' st7789_mpy driver.](https://github.com/devbis/st7789_mpy)
I modified the original driver for one of my projects to add:

- Display Rotation
- Scrolling
- Drawing text using 8 and 16 bit wide bitmap fonts
- Drawing text using Hershey vector fonts
- Drawing JPG's, including a SLOW mode to draw jpg's larger than available ram
  using the TJpgDec - Tiny JPEG Decompressor R0.01d. from
  http://elm-chan.org/fsw/tjpgd/00index.html

Included are 12 bitmap fonts derived from classic pc text mode fonts, 26
Hershey vector fonts and several example programs for different devices. The
driver supports 135x240, 240x240 and 240x320 displays.

## Pre-compiled firmware files

The firmware directory contains pre-compiled firmware for various devices with
the st7789 C driver and frozen python font files. See the README.md file in the
fonts folder for more information on the font files.

### firmware/GENERIC (Generic ESP32 devices)

File         | Details
------------ | ----------------------------------------------------------
firmware.bin | MicroPython v1.14 compiled with ESP IDF v4

### firmware/GENERIC_SPIRAM (Generic ESP32 devices with SPI Ram)

File         | Details
------------ | ----------------------------------------------------------
firmware.bin | MicroPython v1.14 compiled with ESP IDF v4

### firmware/PYBV11 (Pyboard v1.1.)

File         | Details
------------ | ----------------------------------------------------------
firmware.dfu | MicroPython v1.14 compiled with ESP IDF v4

### firmware/T-DISPLAY (LILYGO® TTGO T-Display)

File         | Details
------------ | ----------------------------------------------------------
firmware.bin | MicroPython v1.14 compiled with ESP IDF v4

### firmware/TWATCH-2020 (T-Watch-2020)

Includes frozen axp202c driver from https://github.com/lewisxhe/AXP202X_Libraries

File          | Details
------------- | ----------------------------------------------------------
firmware.bin  | MicroPython v1.14 compiled with ESP IDF v4 with frozen focaltouch and axp202c modules

## Modules

Module             | Source
------------------ | -----------------------------------------------------------
axp202c            | https://github.com/lewisxhe/AXP202X_Libraries
focaltouch         | https://gitlab.com/mooond/t-watch2020-esp32-with-micropython


## Video Examples

Example               | Video
--------------------- | -----------------------------------------------------------
PYBV11 hello.py       | https://youtu.be/OtcERmad5ps
PYBV11 scroll.py      | https://youtu.be/ro13rvaLKAc
T-DISPLAY fonts.py    | https://youtu.be/2cnAhEucPD4
T-DISPLAY hello.py    | https://youtu.be/z41Du4GDMSY
T-DISPLAY scroll.py   | https://youtu.be/GQa-RzHLBak
TWATCH-2020 draw.py   | https://youtu.be/O_lDBnvH1Sw
TWATCH-2020 hello.py  | https://youtu.be/Bwq39tuMoY4
TWATCH-2020 bitmap.py | https://youtu.be/DgYzgnAW2d8


This is a work in progress.

## Thanks go out to:

- https://github.com/devbis for the original driver this is based on.
- https://github.com/hklang10 for letting me know of the new mp_raise_ValueError().
- https://github.com/aleggon for finding the correct offsets for a 240x240 display and discovering issues compiling for STM32 based boards.

-- Russ

## Overview

This is a driver for MicroPython to handle cheap displays
based on ST7789 chip.

<p align="center">
  <img src="https://raw.githubusercontent.com/russhughes/st7789_mpy/master/docs/ST7789.jpg" alt="ST7789 display photo"/>
</p>

It supports 240x240, 135x240 and 240x320 displays.

It is written in pure C. If you are using an ESP32 or pyboard1.1 you can use
one of the provided firmware files, otherwise you will have to build the
firmware from source. Only ESP8266, ESP32 and STM32 processors are supported
for now.


## Building instruction

Prepare build tools as described in the manual. You should follow the
instruction for building MicroPython and ensure that you can build the
firmware without this display module.

Clone this module alongside the MPY sources:

    $ git clone https://github.com/russhughes/st7789_mpy.git


for stm32 (PYBV11):

    $ cd micropython/ports/stm32

for ESP32:

    $ cd micropython/ports/esp32

And then compile the module with specified USER_C_MODULES dir

    $ make -DMODULE_ST7789_ENABLED=1 USER_C_MODULES=../../../st7789_mpy/ all


If you have other user modules, copy the st7789_driver/st7789 to
the user modules directory

Upload the resulting firmware to your MCU as usual with esptool.py
(See
[MicroPython docs](http://docs.micropython.org/en/latest/esp8266/tutorial/intro.html#deploying-the-firmware)
for more info)


## Working examples

This module was tested on ESP32 and the STM32 based pyboard v1.1.

You have to provide `machine.SPI` object and at least two pins for RESET and
DC pins on the screen for the display object.

For ESP32 modules you have to provide specific pins for SPI.
Unfortunately, I was unable to run this display on SPI(1) interface.
For machine.SPI(2) == VSPI you have to use

- CLK: Pin(18)
- MOSI: Pin(23)

Other SPI pins are not used.


    # ESP32

    import machine
    import st7789
    spi = machine.SPI(2, baudrate=40000000, polarity=1, sck=machine.Pin(18), mosi=machine.Pin(23))
    display = st7789.ST7789(spi, 240, 240, reset=machine.Pin(4, machine.Pin.OUT), dc=machine.Pin(2, machine.Pin.OUT))
    display.init()


I couldn't run the display on an SPI with baudrate higher than 40MHZ

## Methods

- `st7789.ST7789(spi, width, height, reset, dc, cs, backlight, rotation, buffer_size)`

    required args:

        `spi` spi device
        `width` display width
        `height` display height

    optional args:

        `reset` reset pin
        `dc` dc pin
        `cs` cs pin
        `backlight` backlight pin
        `rotation` 0-0 degrees, 1-90 degrees, 2-180 degrees, 3-270 degrees
        `buffer_size` 0= buffer dynamically allocated and freed as needed.

    If buffer_size is specified it must be large enough to contain the largest
    bitmap and/or JPG used (Rows * Columns *2 bytes).

This driver supports only 16bit colors in RGB565 notation.

- `ST7789.fill(color)`

  Fill the entire display with the specified color.

- `ST7789.pixel(x, y, color)`

  Set the specified pixel to the given color.

- `ST7789.line(x0, y0, x1, y1, color)`

  Draws a single line with the provided `color` from (`x0`, `y0`) to
  (`x1`, `y1`).

- `ST7789.hline(x, y, length, color)`

  Draws a single horizontal line with the provided `color` and `length`
  in pixels. Along with `vline`, this is a fast version with reduced
  number of SPI calls.

- `ST7789.vline(x, y, length, color)`

  Draws a single horizontal line with the provided `color` and `length`
  in pixels.

- `ST7789.rect(x, y, width, height, color)`

  Draws a rectangle from (`x`, `y`) with corresponding dimensions

- `ST7789.fill_rect(x, y, width, height, color)`

  Fill a rectangle starting from (`x`, `y`) coordinates

- `ST7789.blit_buffer(buffer, x, y, width, height)`

  Copy bytes() or bytearray() content to the screen internal memory.
  Note: every color requires 2 bytes in the array

- `ST7789.text(font, s, x, y[, fg, bg])`

  Write text to the display using the specified bitmap font with the
  coordinates as the upper-left corner of the text. The foreground and
  background colors of the text can be set by the optional arguments fg and bg,
  otherwise the foreground color defaults to `WHITE` and the background color
  defaults to `BLACK`.  See the README.md in the fonts directory for example
  fonts.

- `ST7789.draw(vector_font, s, x, y[, fg, bg])`

  Draw text to the display using the specified hershey vector font with the coordinates
  as the lower-left corner of the text. The foreground and background colors of
  the text can be set by the optional arguments fg and bg, otherwise the
  foreground color defaults to `WHITE` and the background color defaults to
  `BLACK`.  See the README.md in the fonts directory for example fonts and the
  utils directory for a font conversion program.

- `ST7789.jpg(jpg_filename, x, y [, method])`

  Draw JPG file on the display at the given x and y coordinates as the upper left corner of
  the image. There memory required to decode and display a JPG can be considerable as a full
  screen 320x240 JPG would require at least 3100 bytes for the working area + 320x240x2 bytes
  of ram to buffer the image. Jpg images that would require a buffer larger than available memory
  can be drawn by passing `SLOW` for method. The `SLOW` method will draw the image a piece at a time using the Minimum Coded Unit (MCU, typically 8x8) of the image.

- `ST7789.bitmap(bitmap, x , y)`

  Draw bitmap using the specified x, y coordinates as the upper-left corner of
  the of the bitmap.  See the imgtobitmap.py file in the utils folder for a
  python utility to create compatible bitmaps from image files using the
  Pillow Python Imaging Library.

- `ST7789.width()`

  Returns the current logical width of the display. (ie a 135x240 display
  rotated 90 degrees is 240 pixels wide)

- `ST7789.height()`

  Returns the current logical height of the display. (ie a 135x240 display
  rotated 90 degrees is 135 pixels high)

- `ST7789.rotation(r)`

  Set the rotates the logical display in a clockwise direction. 0-Portrait
  (0 degrees), 1-Landscape (90 degrees), 2-Inverse Portrait (180 degrees),
  3-Inverse Landscape (270 degrees)

- `ST7789.offset(x_start, y_start)` The memory in the ST7789 controller is
  configured for a 240x320 display. When using a smaller display like a
  240x240 or 135x240 an offset needs to added to the x and y parameters so
  that the pixels are written to the memory area that corresponds to the
  visible display.  The offsets may need to be adjusted when rotating the
  display.

  For example the TTGO-TDisplay is 135x240 and uses the following offsets.
  | Rotation | x_start | y_start |
  |----------|---------|---------|
  | 0        | 52      | 40      |
  | 1        | 40      | 53      |
  | 2        | 53      | 40      |
  | 3        | 40      | 52      |

  When the rotation method is called the driver will adjust the offsets for a
  135x240 or 240x240 display. Your display may require using different offset
  values, if so, use the `offset` method after `rotation` to set the offset
  values.

  The values needed for particular display may not be documented and may
  require some experimentation to determine the correct values. One technique
  is to draw a box the same size as the display and then make small changes
  to the offsets until the display looks correct.


The module exposes predefined colors:
  `BLACK`, `BLUE`, `RED`, `GREEN`, `CYAN`, `MAGENTA`, `YELLOW`, and `WHITE`


## Helper functions

- `color565(r, g, b)`

  Pack a color into 2-bytes rgb565 format

- `map_bitarray_to_rgb565(bitarray, buffer, width, color=WHITE, bg_color=BLACK)`

  Convert a bitarray to the rgb565 color buffer which is suitable for blitting.
  Bit 1 in bitarray is a pixel with `color` and 0 - with `bg_color`.

  This is a helper with a good performance to print text with a high
  resolution font. You can use an awesome tool
  https://github.com/peterhinch/micropython-font-to-py
  to generate a bitmap fonts from .ttf and use them as a frozen bytecode from
  the ROM memory.

## Performance

For the comparison I used an excellent library for Arduino
that can handle this screen.

https://github.com/ananevilya/Arduino-ST7789-Library/

Also, I used my slow driver for this screen, written in pure python.

https://github.com/devbis/st7789py_mpy/

I used these modules to draw a line from 0,0 to 239,239
The table represents the time in milliseconds for each case

|         | Arduino-ST7789 | st7789py_mpy | st7789_mpy    |
|---------|----------------|--------------|---------------|
| ESP8266 | 26             | 450          | 12            |
| ESP32   | 23             | 450          | 47            |


As you can see, the ESP32 module draws a line 4 times slower than
the older ESP8266 module.
