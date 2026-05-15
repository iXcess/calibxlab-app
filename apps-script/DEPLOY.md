# Apps Script deploy (form → Google Sheet)

Submissions are routed in **`Config.gs`**. Production spreadsheet:

- **ID:** `1rRQp0WWIBpnZfZQhXZCHp7RnxF5J9tBsA59cXkr9nv8`
- **Tab:** `PRODUCTION_SHEET_NAME` (default `Sheet1`)

```javascript
const ACTIVE_TARGET = 'production';
```

## GitHub Pages (required for forms)

GitHub Pages is static only — **`google.script.run` does not work there**. This repo uses **`fetch`** to your deployed Apps Script `/exec` URL instead.

1. Complete steps 2–3 below (deploy the web app).
2. Copy the deployment URL ending in **`/exec`**.
3. Edit **`config.js`** in the repo root:

   ```javascript
   window.CALIXLAB_GAS_EXEC_URL = 'https://script.google.com/macros/s/…/exec';
   ```

4. Commit and push. Open `https://ixcess.github.io/calibxlab-app/` and test onboarding.

**Session Log** (clipboard row) works without Apps Script. **Onboarding** and **Record payment** need the URL above.

## 1. Sheet tab

Ensure the production spreadsheet has a tab matching `PRODUCTION_SHEET_NAME` in `Config.gs` (or the first sheet is used as fallback). Header row is created on first submit if empty.

## 2. Install in Apps Script

**Option A — bound project**

1. Open the spreadsheet → **Extensions** → **Apps Script**.
2. Add/replace `Config.gs` and `Code.gs` from this folder (`doPost` / `doGet` JSON API for GitHub Pages).
3. **Deploy** → **New deployment** → **Web app** → execute as **Me**, who has access: **Anyone** (or your org).
4. Copy the **Web app URL** (`…/exec`). You do **not** need to paste `index.html` into Apps Script for GitHub Pages hosting.

**Option B — clasp**

```bash
cd calixlab-app/apps-script
clasp push
clasp deploy
```

## 3. Verify

1. Set `config.js` with the `/exec` URL and reload the site.
2. **Onboarding** → register a test client → new row on the sheet.
3. **Record payment** → updates the `Additional Payments` column.

Optional: run `testOnboardRandom()` in the Apps Script editor to verify sheet writes without the UI.

## Local preview

Without a real URL in `config.js`, the app uses **local test mode** (localStorage, no Sheets). Session Log still works.
