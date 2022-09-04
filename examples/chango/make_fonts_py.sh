#!/bin/sh

../../utils/font2bitmap.py ../../fonts/truetype/Chango-Regular.ttf 16 -c 0x20-0x7f > chango_16.py
../../utils/font2bitmap.py ../../fonts/truetype/Chango-Regular.ttf 32 -c 0x20-0x7f > chango_32.py
../../utils/font2bitmap.py ../../fonts/truetype/Chango-Regular.ttf 64 -c 0x20-0x7f > chango_64.py

mpy-cross chango_16.py
mpy-cross chango_32.py
mpy-cross chango_64.py

