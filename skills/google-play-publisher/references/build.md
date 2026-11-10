# Building a signed Android App Bundle

## Expo / EAS (managed or prebuild)
- Link the project once: `npx eas-cli@latest init`. It writes `owner` and `extra.eas.projectId` to `app.json`. Review `git diff app.json` afterwards: an earlier `expo prebuild` can leave `android.permissions` and `extra.router` entries behind. Remove anything that contradicts `android.blockedPermissions`.
- Production bundle: `npx eas-cli@latest build --platform android --profile production`.
  - With `"appVersionSource": "remote"` and `"autoIncrement": true`, EAS raises the version code on its server for every production build, including failed or local ones. Read the real code from the build log ("Incrementing versionCode from N to N+1").
  - Free plans have a monthly cloud quota. When it is used up the CLI says so. Add `--local` to build on this machine with the same remote keystore; it needs the Android SDK (`ANDROID_HOME`), JDK 17 and a few GB of disk.
- Test APK for emulators: `--profile preview` (with `"buildType": "apk"`). It is signed with the same remote key, so it cannot replace an install signed with the debug key; uninstall first (`adb uninstall <package>`).
- Run `npx tsc --noEmit` and `npx expo lint` before building; a failed build costs ten minutes.

## Bare React Native / native Android
- Release signing config in `android/app/build.gradle` reading the keystore path and passwords from `~/.gradle/gradle.properties` or environment variables. Never commit the keystore or passwords.
- `cd android && ./gradlew bundleRelease` → `app/build/outputs/bundle/release/app-release.aab`.
- Raise `versionCode` in `build.gradle` for every upload.

## Flutter
- `key.properties` + `signingConfigs.release` in `android/app/build.gradle`.
- `flutter build appbundle --release` → `build/app/outputs/bundle/release/app-release.aab`.
- Version comes from `pubspec.yaml` `version: 1.0.0+<code>`.

## Keys
- Choose Play App Signing when Play offers it. The key you sign with becomes the upload key; Google holds the app signing key. Losing the upload key is recoverable through Play support; losing a self-managed app signing key is not.
- If EAS manages the key, it stays on the user's Expo account. Remind the user not to delete that project.

## Before the store build
Install a release APK on an emulator or phone and check the main screens at 1080×1920 and on a tablet. Bugs that only show on device are common: grid tiles that wrap because of sub-pixel rounding, screens that don't scroll on 16:9, fonts missing on older Android versions.

Large outputs (.aab, .apk, zips) should be gitignored (`*.aab`, `*.apk`).
