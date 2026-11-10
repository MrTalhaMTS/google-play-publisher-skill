#!/usr/bin/env python3
"""
Turn raw app screenshots into Play Store images with a caption on a gradient.
  python compose_screenshots.py <raw_dir> <out_dir> --captions captions.json [--top 0E5A45 --bottom 041E16 --text FBF6E8 --accent E3C373]
captions.json: {"01-home": ["Your Friday companion", "Countdown, daily blessing"], ...}  (keys are file stems)
Output images keep the input's pixel size, so 1080x1920 stays 1080x1920 (valid for Play).
"""
import argparse, json, os
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter
from _fonts import font


def hexcolor(s):
    s = s.lstrip('#')
    return tuple(int(s[i:i + 2], 16) for i in (0, 2, 4))


def gradient(w, h, top, bottom):
    col = Image.new('RGB', (1, h))
    for y in range(h):
        t = y / max(h - 1, 1)
        col.putpixel((0, y), tuple(int(top[i] + (bottom[i] - top[i]) * t) for i in range(3)))
    return col.resize((w, h))


def wrap(draw, text, fnt, max_w):
    lines, cur = [], ''
    for word in text.split():
        trial = (cur + ' ' + word).strip()
        if draw.textlength(trial, font=fnt) <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    return lines + [cur]


def compose(src, dst, title, sub, top, bottom, text, accent):
    shot = Image.open(src).convert('RGB')
    W, H = shot.size
    canvas = gradient(W, H, top, bottom).convert('RGBA')
    d = ImageDraw.Draw(canvas)
    landscape = W > H
    cap_h = int(H * (0.19 if landscape else 0.145))
    size = int(W * (0.038 if landscape else 0.062))
    big, small = font('serif-bold', size), font('serif', int(size * 0.5))
    y = int(cap_h * 0.18)
    for line in wrap(d, title, big, W * 0.86):
        d.text(((W - d.textlength(line, font=big)) / 2, y), line, font=big, fill=text)
        y += int(size * 1.18)
    if sub:
        d.text(((W - d.textlength(sub, font=small)) / 2, y + int(size * 0.1)), sub, font=small, fill=accent)
    scale = min(0.9, (H - cap_h - int(H * 0.03)) / H)
    sw, sh = int(W * scale), int(H * scale)
    r = int(sw * 0.045)
    small_shot = shot.resize((sw, sh), Image.LANCZOS).convert('RGBA')
    mask = Image.new('L', (sw, sh), 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, sw - 1, sh - 1], r, fill=255)
    small_shot.putalpha(mask)
    x = (W - sw) // 2
    shadow = Image.new('RGBA', canvas.size, (0, 0, 0, 0))
    ImageDraw.Draw(shadow).rounded_rectangle([x, cap_h + 14, x + sw, cap_h + sh + 14], r, fill=(0, 0, 0, 120))
    canvas = Image.alpha_composite(canvas, shadow.filter(ImageFilter.GaussianBlur(18)))
    canvas.alpha_composite(small_shot, (x, cap_h))
    ImageDraw.Draw(canvas).rounded_rectangle([x, cap_h, x + sw, cap_h + sh], r, outline=accent + (140,), width=3)
    canvas.convert('RGB').save(dst, optimize=True)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('raw_dir'); ap.add_argument('out_dir')
    ap.add_argument('--captions', required=True)
    ap.add_argument('--top', default='0E5A45'); ap.add_argument('--bottom', default='041E16')
    ap.add_argument('--text', default='FBF6E8'); ap.add_argument('--accent', default='E3C373')
    a = ap.parse_args()
    caps = json.load(open(a.captions, encoding='utf-8'))
    os.makedirs(a.out_dir, exist_ok=True)
    for f in sorted(Path(a.raw_dir).glob('*.png')):
        title, sub = (caps.get(f.stem) or [f.stem.replace('-', ' ').title(), ''])[:2]
        compose(f, Path(a.out_dir) / f.name, title, sub, hexcolor(a.top), hexcolor(a.bottom), hexcolor(a.text), hexcolor(a.accent))
        print('wrote', Path(a.out_dir) / f.name)


if __name__ == '__main__':
    main()
