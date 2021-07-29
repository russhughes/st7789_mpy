import math
from PIL import Image, ImageDraw, ImageFont

# create an image
out = Image.new("RGB", (240, 240), (255, 255, 255))

# get a font
fnt = ImageFont.truetype("./LibreBaskerville-Regular.ttf", 24)
# get a drawing context
d = ImageDraw.Draw(out)
radius = int(120 * 0.8)
cx = int(120)
# cx = 120

for minute in range(1, 60):
    second = 0
    angle = ((minute*math.pi/30)+(second*math.pi/1800))

    y1 = -cx * math.cos(angle) * 0.76
    x1 = cx * math.sin(angle) * 0.76

    y2 = -cx * math.cos(angle) * 0.7
    x2 = cx * math.sin(angle) * 0.7

    d.line([x1+cx, y1+cx, x2+cx, y2+cx], width=1, fill="#000000")

for hour in range(1, 13):
    angle = (hour*math.pi/6)

    y = -cx * math.cos(angle) * 0.9
    x = cx * math.sin(angle) * 0.9

    size = d.textbbox((0, 0), str(hour), font=fnt)
    d.text(
        (x+cx-((size[2]+size[0] >> 1)), y+cx-((size[3]+size[1]) >> 1)),
        str(hour),
        font=fnt,
        fill=(0, 0, 0),
        align="center")

    y1 = -cx * math.cos(angle) * 0.76
    x1 = cx * math.sin(angle) * 0.76

    y2 = -cx * math.cos(angle) * 0.7
    x2 = cx * math.sin(angle) * 0.7

    d.line([x1+cx, y1+cx, x2+cx, y2+cx], width=5, fill="#ff0000")

out.show()
