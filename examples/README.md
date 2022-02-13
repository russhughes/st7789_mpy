# Example Programs


## bitarray.py

    An example using map_bitarray_to_rgb565 to draw sprites


## bitmap_fonts.py

    Cycles through all characters of four bitmap fonts on the display

## chango.py

    Proportional font test for font2bitmap converter.


## clock.py

    Displays a clock over a background image on the display.

    The buttons on the module can be used to set the time.

    Background images courtesy of the NASA image and video gallery available at
    https://images.nasa.gov/

    The Font is Copyright 2018 The Pacifico Project Authors (https://github.com/googlefonts/Pacifico)
    This Font Software is licensed under the SIL Open Font License, Version 1.1.
    This license is copied below, and is also available with a FAQ at:
    http://scripts.sil.org/OFL


## feathers.py

    Smoothly scroll rainbow-colored mirrored random curves across the display.


## hello.py

    Writes "Hello!" in random colors at random locations on the display.


## hershey.py

    Demo program that draws greetings on display cycling thru hershey fonts and colors.

## jpg.py

    Draw a full screen jpg using the slower but less memory intensive method of blitting
    each Minimum Coded Unit (MCU) block. Usually 8×8pixels but can be other multiples of 8.

    bigbuckbunny.jpg (c) copyright 2008, Blender Foundation / www.bigbuckbunny.org


### mono_fonts.py
    mono_fonts.py test for monofont2bitmap converter and bitmap method. This is the older method of
    converting monofonts to bitmaps.  See the newer method in prop_fonts/chango.py that works with
    mono and proportional fonts using the write method.


## noto_fonts.py

    Writes the names of three Noto fonts centered on the display
    using the font. The fonts were converted from True Type fonts using
    the font2bitmap utility.


## paint.py

    A very simple paint program for the TTGO T-Watch-2020
    using the adafruit_focaltouch driver modified for micropython by franz
    schaefer from https://gitlab.com/mooond/t-watch2020-esp32-with-micropython
    See the lib directory for the focaltouch and axp202c drivers.

    https://www.youtube.com/watch?v=O_lDBnvH1Sw


## proverbs.py

    Displays what I hope are chinese proverbs in simplified chinese to test UTF-8 font support.

## roids.py

    Asteroids style game demo using polygons.


## scroll.py

    Smoothly scroll all characters of a font up the display.
    Fonts heights must be even multiples of the screen height (i.e. 8 or 16 pixels high).


## tbbunny.py

    Reads, decodes and displays movie frames from individual JPG's stored on a SD Card. See https://github.com/russhughes/TinyBigBuckBunny for JPG's.


## tiny_toasters.py

    Flying Tiny Toasters for smaller displays (like the ST7735)

    Uses spritesheet from CircuitPython_Flying_Toasters pendant project
    https://learn.adafruit.com/circuitpython-sprite-animation-pendant-mario-clouds-flying-toasters

    Convert spritesheet bmp to tft.bitmap() method compatible python module using:
        python3 ./sprites2bitmap.py ttoasters.bmp 32 32 4 > ttoast_bitmaps.py


## toasters.py

    Flying Toasters

    Uses spritesheet from CircuitPython_Flying_Toasters pendant project
    https://learn.adafruit.com/circuitpython-sprite-animation-pendant-mario-clouds-flying-toasters

    Convert spritesheet bmp to tft.bitmap() method compatible python module using:
        python3 ./sprites2bitmap.py toasters.bmp 64 64 4 > toast_bitmaps.py


## toasters_jpg.py

    An example using a jpg sprite map to draw sprites on T-Display.  This is an older version of the
    toasters.py and tiny_toasters example.  It uses the jpg_decode() method to grab a bitmap of each
    sprite from the toaster.jpg sprite sheet.

    Youtube video: https://youtu.be/0uWsjKQmCpU

    spritesheet from CircuitPython_Flying_Toasters
    https://learn.adafruit.com/circuitpython-sprite-animation-pendant-mario-clouds-flying-toasters


## watch.py

    Analog Watch Display using jpg for the face and filled polygons for the hands
    Requires face_{width}x{height}.jpg in the same directory as this script. See the create_face.py
    script for creating a face image for a given sized display.

    Previous version video: https://youtu.be/NItKb6umMc4


# Utility Programs

## cfg_helper.py

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
