# Calixlab production checklist

## One-time setup

1. **Drive parent folder** — [folder `1GcB2_GwLoE9cosyJPyoIOL5WCjUBZBt5`](https://drive.google.com/drive/folders/1GcB2_GwLoE9cosyJPyoIOL5WCjUBZBt5): deploy account must have **Editor** access.
2. **`apps-script/Config.gs`** — `RECEIPTS_FOLDER_ID` set (already in repo).
3. **Apps Script** — paste or `clasp push` `Code.gs`, `Config.gs`, `appsscript.json`.
4. **Deploy** — Manage deployments → Edit → **New version** → Deploy; approve OAuth (Spreadsheets + Drive).
5. **`config.js`** — `/exec` URL matches the deployment.
6. **GitHub Pages** — push `index.html`, `config.js`, `gas-client.js`, `trainers.js`, `image-compress.js`.

## E2E (use a test client name you can delete later)

| Step | Expected |
|------|----------|
| Load site | Trainers in Session Log dropdown |
| Onboarding + receipt + signature | **Client** row; files in `onboarding-receipts` / `onboarding-signatures` |
| lookupClient | Match found; **Sessions Remaining** correct |
| Record payment + receipt | **Additional Payments** updated; file in `payment-receipts` |
| Session Log + sign + checkbox | **Session Log** row; signature in `session-signatures`; checkbox toggles when clicked |
| Second session same client | Remaining count −1 |
| Add/delete trainer | **Trainer** tab updates |

## API smoke (after redeploy)

```bash
EXEC='https://script.google.com/macros/s/YOUR_ID/exec'
curl -s "$EXEC?action=listTrainers"
curl -s "$EXEC?action=lookupClient&q=Test"
```

POST `recordSessionLog` must return `ok:true` (not `Unknown action`).
