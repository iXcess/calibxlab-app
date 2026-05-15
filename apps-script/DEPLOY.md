# Apps Script deploy (Calixlab Trainer Hub)

Submissions are routed in **`Config.gs`**.

| Target | Spreadsheet | Tabs |
|--------|-------------|------|
| Production | `1rRQp0WWIBpnZfZQhXZCHp7RnxF5J9tBsA59cXkr9nv8` | **Client**, **Trainer**, **Session Log** |

```javascript
const ACTIVE_TARGET = 'production';
const RECEIPTS_FOLDER_ID = '1GcB2_GwLoE9cosyJPyoIOL5WCjUBZBt5';
```

Drive uploads use subfolders under that parent (created on first upload):

- `onboarding-receipts`
- `onboarding-signatures`
- `payment-receipts`
- `session-signatures`

## GitHub Pages (required for forms)

GitHub Pages is static only — **`google.script.run` does not work there**. This repo uses **`fetch`** to your deployed Apps Script `/exec` URL.

1. Deploy the web app (steps below).
2. Copy the deployment URL ending in **`/exec`**.
3. Set **`config.js`** in the repo root:

   ```javascript
   window.CALIXLAB_GAS_EXEC_URL = 'https://script.google.com/macros/s/…/exec';
   ```

4. Commit and push. Hard-refresh [https://ixcess.github.io/calibxlab-app/](https://ixcess.github.io/calibxlab-app/).

**Session Log**, **Onboarding**, **Record payment**, and **Trainer** CRUD all need the URL above.

## Install / update Apps Script

**Option A — bound project**

1. Open the spreadsheet → **Extensions** → **Apps Script**.
2. Replace **`Config.gs`**, **`Code.gs`**, **`Invoice.gs`**, **`InvoiceTemplate.html`**, and **`appsscript.json`** from this folder.
3. **Deploy** → **Manage deployments** → **Edit** (pencil) → **New version** → **Deploy**.
4. Re-authorize when prompted (Spreadsheets + Drive scopes).

**Option B — clasp**

```bash
cd calixlab-app/apps-script
clasp push
clasp deploy
```

> Old deployment URLs keep old code until you create a **new version** on the existing deployment.

## API actions (GitHub Pages `gas-client.js`)

| Action | Method | Notes |
|--------|--------|--------|
| `lookupClient` | GET | Query `q` |
| `listTrainers` | GET | |
| `onboardClient` | POST | Receipt + waiver signature → Drive |
| `recordPayment` | POST | Receipt → Drive |
| `recordSessionLog` | POST | Session signature → Drive |
| `generateInvoice` | POST | PDF invoice → Drive `invoices/` subfolder |
| `previewInvoiceHtml` | POST | HTML preview only |
| `addTrainer` / `deleteTrainer` | POST | |

## Invoices

- Editable UI: `invoice/index.html` on GitHub Pages.
- Reference PDF: `apps-script/CL-INV-00160.pdf`.
- After onboarding/payment success, use **Download invoice PDF** on the hub.

## Verify

1. `listTrainers` — trainer dropdown populates on the site.
2. **Onboarding** — row on **Client**; files in Drive subfolders.
3. **Session Log** — row on **Session Log**; signature in `session-signatures`.
4. **lookupClient** — sessions remaining = package sessions − Session Log count.

See **`PRODUCTION_CHECKLIST.md`** in the repo root.

## Local preview

Without a valid URL in `config.js`, the app uses **local test mode** (localStorage). Session Log still validates UI but does not hit Sheets/Drive.
