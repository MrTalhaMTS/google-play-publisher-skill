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
