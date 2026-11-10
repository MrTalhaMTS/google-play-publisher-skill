# Driving Play Console with Claude in Chrome

## Connecting to the right profile
- `list_connected_browsers` shows every Chrome profile with the extension. Pick the one signed in to the developer account with `select_browser`.
- Each Chrome profile has its own Google sign-ins. `/console/u/0/` is the first account in that profile. If the developer account belongs to another profile, `/u/0/` will show the wrong account.
- If tool calls start failing with "tab is not in Claude's tab group" or the wrong account appears, control has jumped to another profile. Reselect, and if it keeps happening ask the user to close the other profile's window or disable its extension.
- Re-run `tabs_context_mcp` after any such error; tab ids from an old group are invalid.

## URL map (replace DEV and APP)
Base: `https://play.google.com/console/u/0/developers/DEV`
| Page | Path |
|---|---|
| Home / app list | `/home`, `/app-list` |
| Create app | `/create-new-app` |
| Policy status | `/policy-center` |
| Dashboard | `/app/APP/app-dashboard` |
| App content overview | `/app/APP/app-content/overview` |
| Privacy policy | `/app/APP/app-content/privacy-policy` |
| Ads | `/app/APP/app-content/ads-declaration` |
| Sign in details | `/app/APP/app-content/testing-credentials` |
| Advertising ID | `/app/APP/app-content/ad-id-declaration` |
| Government apps | `/app/APP/app-content/government-apps` |
| Financial features | `/app/APP/app-content/finance` |
| Store settings | `/app/APP/store-settings` |
| Store listings | `/app/APP/store-listings`, edit `/app/APP/store-listings/default/edit` |
| Production track | `/app/APP/tracks/production` |
| Publishing overview | `/app/APP/publishing` |

Guessed paths that don't exist (for example `/main-store-listing`) redirect to Home without an error.

## Working patterns
- Pages take 5-8 s to render. Wait, then `find` or `read_page` with `filter: interactive`.
- Sidebar buttons are often off-screen and ignore clicks. Navigate by URL instead.
- After each Save, refs change. Call `find` again before the next click.
- Radio buttons and checkboxes: click the ref from `find`; coordinates drift when banners appear.
- Text: `form_input` on the textbox ref, then Save. Check the character counter under the field.
- Dialogs ("Store listing contact details", "App category") open over the page; act on refs inside them and then Save in the dialog.

## Uploading assets
1. Click the slot's "Add assets" (icon, feature graphic, phone, 7-inch, 10-inch). A library panel opens on the right.
2. `find` "file input element in the asset panel" and call `file_upload` with that ref. Files land in the slot that was clicked. Several screenshots can go in one call if they total under 10 MB.
3. Upload order is not preserved. Reorder by dragging the thumbnails (`left_click_drag`), or leave it if the first image is a good one.
4. Close the panel with its X, then Save as draft.
5. App bundles (.aab) are too large for the tool. Reveal the file and let the user drag it in.

## Store listing translations
- Language dropdown → Manage languages → tick each language. The list shifts as you tick, so verify the right-hand "selected" column before Apply.
- Use "Next language" to step through each locale; `find` the three textboxes, `form_input`, Save as draft.

## AI asset declaration
On Next/Review, Play asks whether assets were AI-generated. If the user wants them labelled, choose that option. The dialog's thumbnails are `button.asset-card[role=checkbox]`; clicking one toggles `aria-checked`. The "Select all" text is only a tooltip label. Selecting all can be done with:
```js
[...document.querySelectorAll('button.asset-card[role=checkbox]')].filter(b=>b.getAttribute('aria-checked')!=='true').forEach(b=>b.click())
```
Then "Label assets and submit", and confirm the review page shows the label option still selected.

## Production release
- Countries / regions → Add → "Select all rows" → Save. Expect about 178 countries.
- Create new release → the user drops the .aab → release name defaults to the version → release notes → Next → read every warning → the user presses Send for review.
- Publishing overview then shows "Changes in review".
