# Privacy policy: Google Play Publisher (Claude skill)

_Last updated: November 10, 2026_

The Google Play Publisher skill is a set of instructions and local scripts for Claude. It has no server, no analytics and no tracking, and the author receives no data from it.

## What it reads
- Your app's source code and build files on your computer, to build the release bundle and check its permissions.
- Developer contact details you provide (support email, website, privacy policy URL) and your app's listing text and images.

## Where data goes
- **Google Play Console**, through Claude in Chrome in your own signed-in browser: listing text, images, screenshots, contact details, countries and release notes for your app. Google's privacy policy applies there.
- **Expo EAS**, only if your project uses it: your project is built with your own Expo login. Expo's privacy policy applies there.
- Nothing is sent anywhere else. The bundled scripts run locally and make no network requests.

## Credentials
The skill never asks for, types or stores passwords, keystore passwords or API keys. Builds use the sign-ins you already have (Expo CLI, Gradle signing config). You sign in to Play Console yourself.

## Retention
The skill stores nothing. Files it creates (bundles, screenshots, listing text) stay in your project folder.

## Contact
Questions: open an issue at https://github.com/MrTalhaMTS/google-play-publisher-skill/issues
