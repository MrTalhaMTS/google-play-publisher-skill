# Helper scripts

The directory only accepts text files, so the helper scripts live here as code blocks. When you need one, write it to a scratch folder (for example `$TMPDIR/gpp/`) with the exact file name shown, then run it with `python3`. `compose_screenshots.py` and `feature_graphic.py` import `_fonts.py` (and `feature_graphic.py` imports `compose_screenshots.py`), so write those files into the same folder first. They need Python 3 and Pillow (`pip install pillow`). None of them make network requests.

Quick way to extract all of them at once: read this file and, for each `### <name>` heading, save the following ```python block as `<name>`.

### _fonts.py

Shared font finder, needed by the two image scripts.

```python
"""Finds a serif/sans font that exists on this machine (macOS, Linux, Windows)."""
import os
from PIL import ImageFont

CANDIDATES = {
    'serif-bold': [
        '/System/Library/Fonts/Supplemental/Georgia Bold.ttf',
        '/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf',
        'C:/Windows/Fonts/georgiab.ttf',
    ],
    'serif': [
        '/System/Library/Fonts/Supplemental/Georgia.ttf',
        '/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf',
        'C:/Windows/Fonts/georgia.ttf',
    ],
    'serif-italic': [
        '/System/Library/Fonts/Supplemental/Georgia Italic.ttf',
        '/usr/share/fonts/truetype/dejavu/DejaVuSerif-Italic.ttf',
        'C:/Windows/Fonts/georgiai.ttf',
    ],
}


def font(kind, size, override=None):
    for path in ([override] if override else []) + CANDIDATES.get(kind, []):
        if path and os.path.exists(path):
            return ImageFont.truetype(path, size)
    return ImageFont.load_default(size=size)
```

### check_aab.py

Inspect a bundle before upload.

```python
"""
Inspect an Android App Bundle (.aab) before uploading it to Google Play.
  python check_aab.py app-release.aab
Prints the package name, version code (if bundletool is installed) and permissions,
and flags permissions that bring extra Play Console forms or must match declarations.
"""
import re, shutil, subprocess, sys, zipfile

FLAGS = {
    'com.google.android.gms.permission.AD_ID': 'Advertising ID declaration must be "Yes" (and Data safety must cover device IDs).',
    'android.permission.ACCESS_FINE_LOCATION': 'Precise location: Data safety + possibly the location permissions declaration.',
    'android.permission.ACCESS_COARSE_LOCATION': 'Approximate location: declare in Data safety.',
    'android.permission.ACCESS_BACKGROUND_LOCATION': 'Background location needs its own declaration form and video.',
    'android.permission.READ_SMS': 'SMS permissions need the SMS/Call Log declaration (usually rejected).',
    'android.permission.SEND_SMS': 'SMS permissions need the SMS/Call Log declaration.',
    'android.permission.READ_CALL_LOG': 'Call log permissions need a declaration.',
    'android.permission.MANAGE_EXTERNAL_STORAGE': 'All-files access needs a declaration and is usually rejected.',
    'android.permission.READ_EXTERNAL_STORAGE': 'Broad storage read: consider removing (blockedPermissions) unless needed.',
    'android.permission.READ_MEDIA_IMAGES': 'Photo/video permissions need a declaration on Android 13+ unless core to the app.',
    'android.permission.READ_MEDIA_VIDEO': 'Photo/video permissions need a declaration on Android 13+ unless core to the app.',
    'android.permission.QUERY_ALL_PACKAGES': 'Package visibility declaration required.',
    'android.permission.REQUEST_INSTALL_PACKAGES': 'Install-packages declaration required.',
    'android.permission.SYSTEM_ALERT_WINDOW': 'Draw-over-apps: usually from debug tooling; remove from release if unused.',
    'android.permission.USE_FULL_SCREEN_INTENT': 'Full-screen intent declaration required on Android 14+.',
    'android.permission.FOREGROUND_SERVICE': 'Foreground service types must be declared in Play Console.',
    'android.permission.CAMERA': 'Camera: declare in Data safety if images are collected.',
    'android.permission.RECORD_AUDIO': 'Microphone: declare in Data safety if audio is collected.',
}


PERM_RE = re.compile(rb'(?:android|com|me|org|net|io|co|de)(?:\.[A-Za-z0-9_]+)*\.permission\.[A-Z0-9_]+')
CLASS_RE = re.compile(rb'(?:com|org|net|io|me|co|de|app|dev)(?:\.[A-Za-z0-9_]+)+\.Main(?:Activity|Application)')


def strings(data):
    # The manifest is protobuf; each string is preceded by length bytes that can look like
    # letters, so match from known prefixes instead of taking whole runs of characters.
    return {m.group().decode() for m in PERM_RE.finditer(data)} | {m.group().decode() for m in CLASS_RE.finditer(data)}


def main(path):
    with zipfile.ZipFile(path) as z:
        manifest = z.read('base/manifest/AndroidManifest.xml')
    found = strings(manifest)
    perms = sorted(s for s in found if '.permission.' in s and not s.endswith('_PERMISSION'))
    classes = [s for s in found if s.endswith(('.MainActivity', '.MainApplication'))]
    package = classes[0].rsplit('.', 1)[0] if classes else '(unknown)'

    print(f'Package (best guess): {package}')
    if shutil.which('bundletool'):
        out = subprocess.run(['bundletool', 'dump', 'manifest', '--bundle', path, '--xpath', '/manifest/@android:versionCode'],
                             capture_output=True, text=True)
        print(f'Version code: {out.stdout.strip() or out.stderr.strip()}')
    else:
        print('Version code: install bundletool to read it, or check the build log')
    print(f'\nPermissions ({len(perms)}):')
    for p in perms:
        print(f'  {p}')
    flagged = [p for p in perms if p in FLAGS]
    print('\nNeeds attention:' if flagged else '\nNo permissions that need extra Play Console forms.')
    for p in flagged:
        print(f'  - {p}: {FLAGS[p]}')
    print(f"\nAdvertising ID declaration should be: {'Yes' if 'com.google.android.gms.permission.AD_ID' in perms else 'No'}")


if __name__ == '__main__':
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    main(sys.argv[1])
```

### check_listing.py

Check listing text limits.

```python
"""
Check Play Store listing text against Play Console limits.
  python check_listing.py listings.json
listings.json: {"en-US": {"title": "...", "short": "...", "full": "..."}, "ar": {...}, ...}
Optional key per locale: "release_notes" (500 max).
"""
import json, re, sys

LIMITS = {'title': 30, 'short': 80, 'full': 4000, 'release_notes': 500}
RISKY = [r'\bno ads\b', r'\bad[- ]free\b', r'\bno tracking\b', r'\b#1\b', r'\bbest app\b', r'\bfree forever\b']


def main(path):
    data = json.load(open(path, encoding='utf-8'))
    bad = 0
    for locale, fields in data.items():
        parts = []
        for key, limit in LIMITS.items():
            if key not in fields:
                if key != 'release_notes':
                    parts.append(f'{key}: MISSING')
                    bad += 1
                continue
            n = len(fields[key])
            ok = 0 < n <= limit
            bad += not ok
            parts.append(f"{key} {n}/{limit}{'' if ok else ' TOO LONG' if n else ' EMPTY'}")
        print(f'{locale:8} ' + ', '.join(parts))
        text = ' '.join(str(v) for v in fields.values()).lower()
        for pattern in RISKY:
            if re.search(pattern, text):
                print(f'         note: contains "{pattern.strip(chr(92) + "b")}". Is it true for this build and the next ones?')
    print('\nAll within limits.' if not bad else f'\n{bad} problem(s).')
    sys.exit(1 if bad else 0)


if __name__ == '__main__':
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    main(sys.argv[1])
```

### compose_screenshots.py

Captioned store screenshots.

```python
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
```

### feature_graphic.py

1024×500 feature graphic.

```python
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
```
