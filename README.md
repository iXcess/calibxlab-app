# Calixlab Trainer Hub

Merged static webapp for **Calixlab · Vibefam**:

- **Session Log** — post-session attendance log with client lookup, package status, and client sign-in.
- **Onboarding** — new client registration, liability waiver, and instalment payment recording.

## Local preview

```bash
python3 -m http.server 8765 --bind 127.0.0.1
```

Open [http://127.0.0.1:8765/](http://127.0.0.1:8765/).

## Rebuild from source HTML exports

If you update the original `.txt` HTML files in `~/Downloads`:

```bash
python3 build_merge.py
```

## Deploy

### Static UI (GitHub Pages)

Site: [https://ixcess.github.io/calibxlab-app/](https://ixcess.github.io/calibxlab-app/)

Serve `index.html`, `config.js`, and `gas-client.js` from the repo root.

### Form submissions → Google Sheet

GitHub Pages cannot run `google.script.run`. After you deploy **`apps-script/`** as a Google Apps Script **web app**, paste the `/exec` URL into **`config.js`** (`CALIXLAB_GAS_EXEC_URL`) and push. See **`apps-script/DEPLOY.md`**.

| File | Role |
|------|------|
| `config.js` | Apps Script web app `/exec` URL (required for live onboarding) |
| `gas-client.js` | `fetch` bridge; keeps existing onboarding JS working |
| `apps-script/Config.gs` | Spreadsheet routing (`ACTIVE_TARGET`, production ID) |
| `apps-script/Code.gs` | `doPost` API + `onboardClient`, `lookupClient`, `recordPayment` |

**Session Log** works on Pages without Apps Script (clipboard). **Onboarding** / **Record payment** need `config.js` set.

Without a valid URL, the app runs in **local test mode** (localStorage + banner).
