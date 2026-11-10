#!/usr/bin/env python3
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
