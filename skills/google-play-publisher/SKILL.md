---
name: google-play-publisher
description: Publish an Android app to Google Play end to end - build a signed .aab, prepare the store listing (title, descriptions, translations, icon, feature graphic, phone and tablet screenshots), then drive Google Play Console in the user's own Chrome (Claude in Chrome) to create the app, fill store settings, listing, countries and App content declarations, and get a production release ready for review. Use this whenever the user wants to publish, release, launch, submit, upload or "make live" an Android / Expo / React Native / Flutter / Kotlin app on Google Play or the Play Store, asks for Play Console listing data, screenshots, feature graphics or data safety answers, or says things like "put my app on the Play Store", "build the aab and publish it", or "fill Play Console for me", even if they do not name Play Console.
---

# Google Play publisher

Takes an Android app from source code to "sent for review" on Google Play. The work splits into what happens on this computer (build, assets, text) and what happens in Play Console in the user's own browser. Doing the local half first means the browser half is mostly pasting finished material, which is where most mistakes and lost time happen.

## Ground rules that keep the user safe

Play Console acts on a real developer account with the user's legal identity behind it, so a few things belong to the user, not to you:

- **Legal declarations and agreements** (Developer Program Policies, US export laws, content rating questionnaire, target audience, data safety, health, financial features, AI-asset labels) are statements made in the user's name. Prepare the answers, show them, and get an explicit "yes, submit these" before ticking or saving any of them. A vague "ok" or "done" is not that approval; ask again in one sentence. Many harnesses will block you anyway, so offer the user the option of clicking them themselves with your answers in hand.
- **The final "Send for review" / "Start rollout to production" button** is the user's to press unless they told you in plain words to press it.
- **Never type passwords, keystore passwords, card numbers or API secrets.** Signing in, paying the $25 registration fee and identity verification are the user's.
- **Uploads over 10 MB**: the Claude in Chrome file-upload tool caps a call at 10 MB, and an .aab is usually 30-150 MB. Reveal the file in Finder/Explorer (`open -R <path>` on macOS) and ask the user to drag it onto "Drop app bundles here to upload". Everything else (icon, graphics, screenshots) you can upload.

## Phase 0: Find out where things stand (ask once, in one message)

Read the project before asking anything. Then confirm only what you can't find:

1. **Developer account**: which Google account / Chrome profile owns the Play Console account. Accounts that were removed or suspended show "Account removed" on the Policy status page; stop and tell the user if so.
2. **Package name** (`applicationId`, Expo `android.package`). It is permanent once the first bundle is uploaded.
3. **Personal or organization account**, and whether it already has production apps. New personal accounts must run a closed test with 12+ testers for 14 days before production. If the account already has production apps, production is open.
4. **Support email, privacy policy URL, website.** Check the privacy URL loads (HTTP 200) before using it.
5. **Ads, analytics, logins, payments** now or planned. This drives the Ads, Advertising ID and Data safety answers, and whether the listing may say "no ads".

## Phase 1: Build a signed release bundle

Pick the path that matches the project. Details and pitfalls: `references/build.md`.

- **Expo / EAS**: `npx eas-cli@latest build --platform android --profile production`. If the cloud free-tier quota is used up, the same command with `--local` builds on this machine with the same remote keystore, so the upload key stays consistent. `eas init` links the project; make sure it does not leave stray `android.permissions` in `app.json` (check `git diff app.json`).
- **Bare React Native / Kotlin / Java**: `./gradlew bundleRelease` with a release `signingConfig`.
- **Flutter**: `flutter build appbundle --release`.

Then run `python scripts/check_aab.py <path.aab>`. It prints the package name, permissions, and warns about `AD_ID`, storage, location, SMS and other permissions that trigger extra Play Console forms. Keep the result: the Advertising ID and Data safety answers must match it.

Before building for real, install a release APK on an emulator or phone and look at the main screens. In practice this is where layout bugs show up that look fine in the browser (rounding that wraps grid tiles, content that doesn't scroll on 16:9 screens). Fix them before the store screenshots, because screenshots of a bug are worse than no screenshots.

## Phase 2: Store assets

Read `references/store-assets.md` for the exact limits. Short version:

| Asset | Requirement |
|---|---|
| App name | ≤ 30 chars |
| Short description | ≤ 80 chars |
| Full description | ≤ 4000 chars |
| Icon | 512×512 PNG, ≤ 1 MB |
| Feature graphic | 1024×500 PNG/JPG |
| Phone screenshots | 2-8, each side 320-3840 px, long side ≤ 2× short side (so 1080×2400 is rejected; use 1080×1920) |
| 7-inch / 10-inch tablet | up to 8 each; e.g. 1200×1920 and 1600×2560 |

1. **Listing text**: write `listings.json` keyed by Play locale (`en-US`, `ar`, `hi-IN`, `bn-BD`, `id`, `tr-TR`, `ur`, ...), each with `title`, `short`, `full`. Run `python scripts/check_listing.py listings.json` to verify limits. Describe only what the app does today. Avoid "no ads" if ads are planned, and say when parts of the app are English-only.
2. **Screenshots**: capture real screens from an emulator running the release build (`references/store-assets.md` has the adb recipe: set `wm size 1080x1920`, install, tap through, `screencap`). Then `python scripts/compose_screenshots.py <dir>` adds a caption band on a gradient. Keep the raw set too.
3. **Feature graphic**: `python scripts/feature_graphic.py --title ... --tagline ... --icon icon.png --out feature.png`. Look at the result before uploading.

## Phase 3: Play Console in the user's Chrome

Load the Claude in Chrome tools, then follow `references/play-console.md`. It holds the URL map, the asset-upload flow, and fixes for the problems that cost the most time:

- **Several Chrome profiles connected**: `list_connected_browsers`, then `select_browser` the profile signed in to the right Google account. If control keeps jumping back to the other profile, ask the user to close that profile's window or switch its extension off.
- **Direct URLs** are faster than the sidebar, which often ignores clicks: `.../app/<appId>/app-content/overview`, `/store-settings`, `/store-listings/default/edit`, `/tracks/production`, `/publishing`.
- **Asset slots**: click the slot's "Add assets", then upload to the file input inside the library panel that opens. The upload lands in that slot.
- **Text fields**: `form_input` on the textbox refs works for long multilingual text, including newlines and RTL scripts.
- **Re-find refs after every save**: Play Console re-renders and old refs go stale.

Order of work:
1. **Create app** (name, default language, App, Free). The user ticks the two declarations.
2. **App content**: privacy policy, ads, sign-in details (app access), advertising ID, government, financial, health, target audience, content rating, data safety. Prepare answers from `references/declarations.md` and get consent as described above.
3. **Store settings**: category, contact email, website.
4. **Default store listing**: text, then icon, feature graphic, phone and tablet screenshots. Save as draft often. Then "Manage languages" for each translation, and "Next language" through each locale, pasting from `listings.json`. Answer the AI-asset question the way the user chooses.
5. **Countries**: production track → Countries / regions → select all → Save.
6. **Production release**: Create new release, the user drags in the .aab, add release notes (≤ 500 chars per language), Next, review warnings, then the user presses Send for review.

## Phase 4: Report

Tell the user, in plain words: what is now in review, which countries, what Play said in its warnings, what is still theirs to do, and how long review usually takes (a few days for a new app). If they plan ads or tracking later, remind them to update Ads, Advertising ID and Data safety **before** that release, or it can be rejected.

## Files in this skill

- `references/build.md`: Expo/EAS, Gradle, Flutter build paths, keystore and version-code notes.
- `references/store-assets.md`: limits, emulator screenshot recipe, caption and graphic tips.
- `references/play-console.md`: URL map, upload flow, browser troubleshooting.
- `references/declarations.md`: question-by-question guide for App content forms.
- `scripts/check_aab.py`: inspect a bundle's package and permissions.
- `scripts/check_listing.py`: verify listing text limits for every locale.
- `scripts/compose_screenshots.py`: captioned store screenshots from raw captures.
- `scripts/feature_graphic.py`: 1024×500 feature graphic from an icon and two lines of text.
