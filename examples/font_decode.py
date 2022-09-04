"""Example showing how to deocode glyph bitmaps from a font module"""

import proverbs_font as font

text = "师父领进门，修行在个人"

def get_bitmap_offset(index):
    """ Return the bitmap bit offset for the glpyh at `index`"""
    offset_first = index * font.OFFSET_WIDTH
    offset = 0
    for offset_byte in range(font.OFFSET_WIDTH):
        offset = (offset << 8) + font.OFFSETS[offset_first + offset_byte]
    return offset

def get_pixel_color(bit):
    """Return the color of the pixel starting at `bit` comprised of `font.BPP` bits"""
    pixel_color = 0
    for _ in range(font.BPP):
        pixel_color = (pixel_color << 1) | font.BITMAPS[bit // 8] & 1 << (7 - (bit % 8))
        bit += 1

    return pixel_color

# Draw the string `text` one glyph at a time
for glyph in text:
    print({glyph})
    glyph_index = font.MAP.index(glyph)
    glyph_width = font.WIDTHS[glyph_index]
    glyph_bitmap_data = get_bitmap_offset(glyph_index)
    for _ in range(font.HEIGHT):
        for _ in range(glyph_width):
            color = get_pixel_color(glyph_bitmap_data)
            print('#' if color else ' ', end='')
            glyph_bitmap_data += font.BPP
        print()
    print("\n")
