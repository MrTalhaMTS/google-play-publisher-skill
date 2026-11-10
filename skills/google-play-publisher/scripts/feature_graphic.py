#!/usr/bin/env python3
"""
Make a 1024x500 Play Store feature graphic: title on the left, the app icon on the right.
  python feature_graphic.py --title "Jumma Mubarak" --tagline "Friday blessings, duas & cards" \
      --subline "In 7 languages · Works offline" --icon icon.png --out feature-graphic.png \
      [--top 0E5A45 --bottom 041E16 --text FBF6E8 --accent E3C373]
Use a transparent-background icon or emblem for the best result.
"""
import argparse
from PIL import Image, ImageDraw, ImageFilter
from _fonts import font
from compose_screenshots import gradient, hexcolor

W, H, S = 1024, 500, 2


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--title', required=True); ap.add_argument('--tagline', default='')
    ap.add_argument('--subline', default=''); ap.add_argument('--icon', required=True)
    ap.add_argument('--out', default='feature-graphic-1024x500.png')
    ap.add_argument('--top', default='0E5A45'); ap.add_argument('--bottom', default='041E16')
    ap.add_argument('--text', default='FBF6E8'); ap.add_argument('--accent', default='E3C373')
    a = ap.parse_args()
    top, bottom, text, accent = (hexcolor(c) for c in (a.top, a.bottom, a.text, a.accent))

    img = gradient(W * S, H * S, top, bottom).convert('RGBA')
    icon = Image.open(a.icon).convert('RGBA')
    size = 360 * S
    icon = icon.resize((size, int(size * icon.height / icon.width)), Image.LANCZOS)
    cx, cy = 790 * S, 250 * S
    layer = Image.new('RGBA', img.size, (0, 0, 0, 0))
    layer.alpha_composite(icon, (cx - icon.width // 2, cy - icon.height // 2))
    img = Image.alpha_composite(img, layer.filter(ImageFilter.GaussianBlur(18 * S)))
    img = Image.alpha_composite(img, layer)
    rings = Image.new('RGBA', img.size, (0, 0, 0, 0))
    rd = ImageDraw.Draw(rings)
    for r, op in ((250, 70), (310, 40), (370, 22)):
        rd.ellipse([cx - r * S, cy - r * S, cx + r * S, cy + r * S], outline=accent + (op,), width=2 * S)
    img = Image.alpha_composite(img, rings)

    d = ImageDraw.Draw(img)
    x, y = 70 * S, 110 * S
    words = a.title.split()
    lines = [' '.join(words[: (len(words) + 1) // 2]), ' '.join(words[(len(words) + 1) // 2:])] if len(words) > 1 else words
    big = font('serif-bold', 84 * S)
    while max(d.textlength(l, font=big) for l in lines) > 560 * S and big.size > 40 * S:
        big = font('serif-bold', big.size - 4 * S)
    for line in lines:
        d.text((x, y), line, font=big, fill=text)
        y += int(big.size * 1.0)
    y += 12 * S
    d.line([(x, y), (x + 120 * S, y)], fill=accent, width=3 * S)
    if a.tagline:
        d.text((x, y + 18 * S), a.tagline, font=font('serif-italic', 34 * S), fill=accent)
    if a.subline:
        d.text((x, y + 74 * S), a.subline, font=font('serif', 26 * S), fill=text)
    img.convert('RGB').resize((W, H), Image.LANCZOS).save(a.out, optimize=True)
    print('wrote', a.out)


if __name__ == '__main__':
    main()
