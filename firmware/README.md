
The esp32 directory contains a firmware.bin file with MicroPython
v1.12-464-gcae77daf0 compiled using ESP IDF v3 with the st7789 C driver and
the frozen python font files for generic ESP32 boards.

The pybv11 directory contains a firmware.dfu file with MicroPython
v1.12-464-gcae77daf0 compiled with the st7789 C driver and
the frozen python font files for the Pyboard v1.1.

Frozen python bitmap font files included:

- vga1_8x8
- vga2_8x8

- vga1_8x16
- vga2_8x16

- vga1_16x16
- vga2_16x16

- vga1_bold_16x16
- vga2_bold_16x16

- vga1_16x32
- vga2_16x32

- vga1_bold_16x32
- vga2_bold_16x32

When using this firmware you can use the VGA fonts directly from flash to
save RAM. For example, in the ttgo_hello.py program change the font import
line from:

`from fonts import vga2_bold_16x32 as font`

to:

`import vga2_bold_16x32 as font`
