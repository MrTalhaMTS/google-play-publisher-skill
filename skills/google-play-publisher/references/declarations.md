# App content declarations

Draft the answers from the code and `check_aab.py` (in `references/scripts.md`), show them to the user in one message, and get explicit approval before saving. These are legal statements in the user's name.

## Privacy policy
Public HTTPS page that names the app or clearly covers it, reachable without login, not a PDF. Check it returns HTTP 200.

## Ads
"Yes" if the current build contains any ad SDK (AdMob, Meta Audience Network, AppLovin, Unity Ads, ...). Search the dependencies. Planned ads don't count yet, but tell the user to update this before the release that adds them.

## Sign in details (formerly App access)
"No restricted access" when every feature works without an account. Otherwise give reviewers working test credentials, which the user creates and enters.

## Advertising ID
Must match the manifest. `check_aab.py` reports `com.google.android.gms.permission.AD_ID`. Present means "Yes" plus purposes; absent means "No". Firebase Analytics and ad SDKs add it automatically.

## Government, financial, health
"No" / "My app doesn't provide any financial features" / no health features, unless the app really is one of these.

## Target audience and content
Pick the youngest age group the app is designed for. Choosing anything under 13 brings in the Families policy (stricter ads, data and content rules); only do it if true. If the app doesn't target children, choose 13+ (or 18+) and answer "No" to "unintentionally appeals to children" unless it obviously does.

## Content rating (IARC)
Pick the closest category (Reference/News/Educational, Games, Social, Entertainment, All other). Answer each question literally: violence, sexual content, profanity, drugs, gambling, user-to-user communication, sharing location, digital purchases. Religious or informational content is not "hate" or "discrimination".

## Data safety
Work from what the build does:
- No analytics, ads, crash reporting or accounts, and only fetching public content: "No data collected or shared". Requests that only expose an IP address to a content host for delivery are transient and not "collection".
- Firebase Analytics / Crashlytics: device or other IDs, app interactions, crash logs, diagnostics; collected; often shared with Google as a service provider. Check the SDK's own data safety guidance.
- AdMob: device or other IDs, approximate location, app interactions; collected and shared for advertising.
- Accounts / sign-in: email, name, user IDs, plus a deletion path (URL) for account data.
- Encrypted in transit: yes if every endpoint is HTTPS.
Re-check this form whenever SDKs change.
