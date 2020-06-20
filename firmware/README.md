MicroPython v1.12-464-gcae77daf0 compiled using ESP IDF v3
with the st7789 C driver and the frozen python font files:

- vga1_8x8.py
- vga2_8x8.py

- vga1_8x16.py
- vga2_8x16.py

- vga1_16x16.py
- vga2_16x16.py

- vga1_bold_16x16.py
- vga2_bold_16x16.py

- vga1_16x32.py
- vga2_16x32.py

- vga1_bold_16x32.py
- vga2_bold_16x32.py

When using this firmware you can use the VGA fonts directly from flash to
save RAM. For example, in the ttgo_hello.py program change the font import
line from:

`from fonts import vga2_bold_16x32 as font`

to:

`import vga2_bold_16x32 as font`
