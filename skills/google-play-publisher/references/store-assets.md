# Store assets

## Limits (Play Console, 2026)
| Item | Limit |
|---|---|
| App name | 30 chars |
| Short description | 80 chars |
| Full description | 4000 chars |
| Release notes | 500 chars per language |
| App icon | 512×512, PNG or JPEG, ≤ 1 MB |
| Feature graphic | 1024×500, PNG or JPEG, ≤ 15 MB |
| Phone screenshots | 2-8, PNG/JPEG ≤ 8 MB each, 16:9 or 9:16, each side 320-3840 px |
| 7-inch tablet | up to 8, each side 320-3840 px |
| 10-inch tablet | up to 8, each side 1080-7680 px |
| Aspect ratio | long side at most twice the short side, so 1080×2400 is rejected |

At least 4 phone screenshots of 1080 px or more make the app eligible for promotion.

## Writing the listing
- Lead with what someone gets in the first line; Play truncates the full description.
- Use only claims that are true for this build. "No ads" or "no tracking" must go if ads or analytics are planned soon, or the listing becomes misleading the day they ship.
- If content in a language is only partly translated (for example guides only in English), say so.
- Keep a `listings.json` with every locale so the text is versioned and easy to paste:
  ```json
  {"en-US": {"title": "...", "short": "...", "full": "..."}, "ar": {...}}
  ```
- Common Play locale codes: en-US, ar, ur, hi-IN, bn-BD, id, tr-TR, fr-FR, de-DE, es-ES, pt-BR, ru-RU, ms, fa.
- Run `scripts/check_listing.py listings.json`.

## Screenshots from an emulator
```bash
export ANDROID_HOME=$HOME/Library/Android/sdk   # macOS default
PATH=$ANDROID_HOME/emulator:$ANDROID_HOME/platform-tools:$ANDROID_HOME/cmdline-tools/latest/bin:$PATH
IMG="system-images;android-35;google_apis;arm64-v8a"   # use an installed image: ls $ANDROID_HOME/system-images
echo no | avdmanager create avd -n shot-phone -k "$IMG" -d pixel_8
emulator -avd shot-phone -no-audio -no-boot-anim -no-snapshot &
adb wait-for-device; until [ "$(adb shell getprop sys.boot_completed | tr -d '\r')" = 1 ]; do sleep 5; done
adb shell wm size 1080x1920 && adb shell wm density 420     # 9:16, accepted by Play
adb install app-release.apk
adb shell am start -n <package>/.MainActivity
adb exec-out screencap -p > 01-home.png
```
- Tablets: create an AVD from a tablet profile (`pixel_c`, or edit `hw.lcd.width/height/density` in `~/.android/avd/<name>.avd/config.ini`): 1200×1920 at 320 dpi for 7-inch, 1600×2560 at 320 dpi for 10-inch.
- With more than one emulator running, address one with `adb -s emulator-5554`. In zsh, `S="-s emulator-5554"; adb $S ...` does not split; use a function: `A() { adb -s emulator-5554 "$@"; }`.
- Use `input tap x y` / `input swipe x1 y1 x2 y2 900` to navigate. Swipes under about 500 ms may not scroll React Native lists.
- Heavy Gradle builds can kill emulators on 16 GB machines. Build first, then boot the emulator.
- Delete the AVDs you created when done (`avdmanager delete avd -n shot-phone`).

## Captions and graphics
- `scripts/compose_screenshots.py` puts the raw shot below a short caption on a gradient, same pixel size as the input. Captions: 2-5 words plus a short subline; benefits, not feature names.
- `scripts/feature_graphic.py` makes a 1024×500 banner from an icon and two lines of text. Keep text off the outer 10% edges, where Play crops in some layouts.
- If any asset was made with AI help, the user decides how to answer Play's AI-asset label question.
