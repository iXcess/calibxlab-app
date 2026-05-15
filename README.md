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

This repo is a static site (`index.html`). Enable **GitHub Pages** (branch `main`, folder `/ (root)`) for a public URL.

Onboarding **client lookup / save** expects [Google Apps Script](https://developers.google.com/apps-script) (`google.script.run`) when deployed inside that environment. Local preview includes a stub so the UI can be exercised without Sheets/Drive.
