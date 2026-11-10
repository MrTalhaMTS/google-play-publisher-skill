# Google Play Publisher, a skill for Claude

Publish an Android app to Google Play with Claude, from source code to "sent for review".

It covers what usually takes a day of clicking:

- **Build** a signed release bundle (.aab) for Expo/EAS, React Native, native Android or Flutter.
- **Check** the bundle's permissions so your Advertising ID and Data safety answers match it.
- **Write** the store listing (title, short and full description) in as many languages as you like, checked against Play's limits.
- **Make** phone and tablet screenshots from an emulator and turn them into captioned store images, plus a 1024×500 feature graphic.
- **Fill in Play Console** in your own Chrome with Claude in Chrome: create the app, store settings, listing and translations, asset uploads, countries, and the production release.

You stay in control of the parts that are legally yours: Claude prepares the declaration answers and asks before submitting them, you drag in the .aab (browser uploads are limited to 10 MB), and you press **Send for review**.

## Install

**Claude Code**
```
/plugin marketplace add MrTalhaMTS/google-play-publisher-skill
/plugin install google-play-publisher@google-play-publisher
```

**Claude apps (claude.ai / desktop)**: download `google-play-publisher.skill` from the [latest release](https://github.com/MrTalhaMTS/google-play-publisher-skill/releases) and upload it under Settings → Capabilities → Skills.

## Use

Ask Claude something like:
- "Publish my Expo app in this folder to Google Play."
- "Build the aab and make the Play Store listing in English, Arabic and Urdu."
- "Fill Play Console for my app, it's already built."

For the Play Console part, install the [Claude in Chrome](https://claude.ai/chrome) extension in the Chrome profile that is signed in to your developer account.

## Requirements

- A Google Play developer account (the $25 sign-up and identity verification are yours to do).
- For builds: the toolchain your app already uses (Node + EAS CLI, Gradle/JDK 17, or Flutter).
- For screenshots: Android SDK with an emulator image, Python 3 with Pillow (`pip install pillow`).

## Data and services

The skill runs entirely on your computer and in your own browser. It stores nothing and has no server of its own.

- **Google Play Console** (play.google.com/console): through Claude in Chrome it enters your app's listing text, images, screenshots, contact email, website and privacy policy URL, using your own signed-in account.
- **Expo EAS** (expo.dev), only if your app uses it: builds are run with your own Expo login.
- **Your Android SDK / Gradle / Flutter**: local builds and emulator screenshots, nothing sent anywhere.

It reads the developer contact details you provide (support email, website, privacy URL) only to fill those Play Console fields.

## What's inside

```
skills/google-play-publisher/
  SKILL.md                  workflow Claude follows
  references/build.md       build paths, keys, version codes
  references/store-assets.md  limits, emulator screenshot recipe
  references/play-console.md  URL map, uploads, browser troubleshooting
  references/declarations.md  App content forms, question by question
  scripts/check_aab.py      package, permissions, AD_ID check
  scripts/check_listing.py  listing length limits for every language
  scripts/compose_screenshots.py  captioned store screenshots
  scripts/feature_graphic.py      1024×500 feature graphic
```

## Privacy

See [PRIVACY.md](PRIVACY.md).

## License

MIT
