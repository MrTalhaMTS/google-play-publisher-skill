#!/usr/bin/env python3
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
