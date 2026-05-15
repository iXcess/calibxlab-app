# Calixlab Trainer Hub

Merged static webapp for **Calixlab · Vibefam**:

- **Session Log** — post-session log with client lookup, package status, client signature, and Google Sheet + Drive backend.
- **Onboarding** — new client registration, liability waiver, and instalment payment recording.

Live site: [https://ixcess.github.io/calibxlab-app/](https://ixcess.github.io/calibxlab-app/)

## Local preview

```bash
cd ~/Downloads/calixlab-app
python3 -m http.server 8765 --bind 127.0.0.1
```

Open [http://127.0.0.1:8765/](http://127.0.0.1:8765/).

## Rebuild from source HTML exports

After editing `~/Downloads/Calixliab Session Form HTML.txt` or `~/Downloads/Calixlab Onboarding HTML.txt`:

```bash
python3 build_merge.py
```

## Deploy

| Component | Doc |
|-----------|-----|
| Apps Script + Sheets + Drive | [`apps-script/DEPLOY.md`](apps-script/DEPLOY.md) |
| Production verification | [`PRODUCTION_CHECKLIST.md`](PRODUCTION_CHECKLIST.md) |

| File | Role |
|------|------|
| `config.js` | Apps Script web app `/exec` URL |
| `gas-client.js` | `fetch` bridge (GET reads, POST writes) |
| `image-compress.js` | Receipt/signature compression for POST limits |
| `trainers.js` | Trainer dropdown + add/delete UI |
| `apps-script/Config.gs` | Spreadsheet + Drive folder IDs |
| `apps-script/Code.gs` | API handlers |

Without a valid `CALIXLAB_GAS_EXEC_URL`, the app runs in **local test mode** (localStorage).

## Brand assets

Logo and favicons live in [`assets/`](assets/). Regenerate from `assets/calixlab-logo.png`:

```bash
python3 scripts/generate_brand_assets.py
```

Includes `favicon.ico`, PNG icons (16–512px), `calixlab-mark.png` (icon mark), and `calixlab-logo-header.png` (horizontal wordmark).

## Invoices

- After **Onboarding** or **Record payment** submit, a bottom sheet offers **Download invoice PDF** (save to phone).
- Optional editor: [invoice/index.html](invoice/index.html).
- Apps Script: `generateInvoice` in `apps-script/Invoice.gs` (redeploy required).
