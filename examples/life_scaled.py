import st7789
import tft_config
import random
import vga1_16x16 as font

tft = tft_config.config(0)

scale = 5 # should be 3 or greater (5 recommended)
xdim = tft.width() // scale
ydim = (tft.height()-font.HEIGHT-2) // scale

if scale == 1:
    pattern = [0xff]
elif scale <= 8:
    pattern = bytes([0x00] + [0x7f]*7)
elif scale <= 16:
    pattern = bytes([0x00]*2 + [0x7f, 0xff, 0xff, 0xff]*14)
else:
    pattern = bytes([0xff]*(scale*(scale+7)//8))

gen = 0
count = 0
least = 0
most = 0
now = None
now_blit = bytearray(xdim*ydim*2)

def main():

    tft.init()
    tft.fill(0)

    init()
    while True:
        draw()
        update()

def init():
    global now, count, least, most
    now = [random.randint(0, 25) < 3 for x in range(0, xdim*ydim)]
    count = sum(now)
    least = count
    most = count

def draw():
    index2 = 0
    for index in range(0, xdim*ydim):
        b = (now[index] == 1) * 0xff
        now_blit[index2] = b
        now_blit[index2+1] = b
        index2 += 2
    tft.text(font, f'{gen} {most}>{count}>{least}  ', 0, 0)
    tft.blit_buffer_scaled(now_blit, 0, font.HEIGHT+2, xdim, ydim, pattern, scale, scale, st7789.BLUE)

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
