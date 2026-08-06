import st7789
import tft_config
import framebuf
import random
import vga1_16x16 as font

tft = tft_config.config(3)

scale = 5 # should be 3 or greater (5 recommended)
xdim = tft.width() // scale
ydim = (tft.height()-font.HEIGHT-2) // scale

# create two lookup entries
lookup = bytearray(scale * scale * 4)
dead = st7789.BLACK
live = st7789.WHITE
grid = st7789.BLUE
fb = framebuf.FrameBuffer(lookup, scale * 2, scale, framebuf.RGB565)
fb.fill(grid)
fb.fill_rect(0, 0, scale - 1, scale - 1, dead)
fb.fill_rect(scale, 0, scale - 1, scale - 1, live)
fb = None

gen = 0
count = 0
least = 0
most = 0
now = bytearray()

def main():

    tft.init()
    tft.fill(0)

    init()
    while True:
        draw()
        update()

def init():
    global now, count, least, most
    now = bytearray([random.randint(0, 25) < 3 for x in range(0, xdim*ydim)])
    count = sum(now)
    least = count
    most = count

def draw():
    tft.text(font, f'{gen} {most}>{count}>{least}  ', 0, 0)
    tft.blit_bitmap_mosaic(now, 8, 0, font.HEIGHT+2, xdim, ydim, lookup, scale, scale)

def update():
    global now, gen, count, least, most

    next = bytearray(xdim*ydim)

    count = 0
    index = 0
    for y in range(0, ydim):
        for x in range(0, xdim):
            alive = -now[index]
            for dy in range(-1, 2):
                # process each neighbor by row
                for dx in range(-1, 2):
                    # process each neighbor by column
                    x1 = (x + dx + xdim) % xdim # wrap in x direction
                    y1 = (y + dy + ydim) % ydim # wrap in y direction
                    alive += now[x1 + y1*xdim] # neighbor
            if alive == 3 or alive == 2 and now[index] == 1:
                next[index] = 1
                count += 1
            index += 1
    now = next
    if count < least:
        least = count
    if count > most:
        most = count
    gen += 1

main()
