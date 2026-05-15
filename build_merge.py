#!/usr/bin/env python3
"""Merge Session Log + Onboarding HTML into one scoped webapp."""
from pathlib import Path

SESSION = Path("/home/ting/Downloads/Calixliab Session Form HTML.txt").read_text(encoding="utf-8")
ONBOARD = Path("/home/ting/Downloads/Calixlab Onboarding HTML.txt").read_text(encoding="utf-8")


def extract_between(s: str, start: str, end: str) -> str:
    i = s.index(start) + len(start)
    j = s.index(end, i)
    return s[i:j].strip()


def extract_body_inner(html: str) -> str:
    i = html.lower().index("<body")
    i = html.index(">", i) + 1
    j = html.lower().rindex("</body>")
    return html[i:j].strip()


session_style = extract_between(SESSION, "<style>", "</style>")
# Session: move :root out; scope the rest
if ":root" in session_style:
    root_end = session_style.index("}") + 1
    # find end of :root block (may have nested - session :root is flat)
    depth = 0
    start = session_style.index(":root")
    for k in range(start, len(session_style)):
        if session_style[k] == "{":
            depth += 1
        elif session_style[k] == "}":
            depth -= 1
            if depth == 0:
                root_block = session_style[start : k + 1]
                rest_style = session_style[k + 1 :].lstrip()
                break
    else:
        root_block = ""
        rest_style = session_style
else:
    root_block = ""
    rest_style = session_style

rest_style = rest_style.replace("body {", ":scope {", 1)
session_scoped = f"{root_block}\n@scope (#session-panel) {{\n{rest_style}\n}}"

ob_style = extract_between(ONBOARD, "<style>", "</style>")
# Drop html rule; body -> :scope once
ob_style = ob_style.replace("html { -webkit-text-size-adjust: 100%; }", "")
ob_style = ob_style.replace(
    "body {\n  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;",
    ":scope {\n  -webkit-text-size-adjust: 100%;\n  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;",
    1,
)
ob_scoped = f"@scope (#onboard-panel) {{\n{ob_style}\n}}"

session_body = extract_body_inner(SESSION)
onboard_body = extract_body_inner(ONBOARD)

APP_SHELL_CSS = """
/* —— App shell (outside scoped panels) —— */
html { -webkit-text-size-adjust: 100%; }
body.app-body {
  margin: 0;
  min-height: 100vh;
  font-family: 'DM Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  background: #e8ecf1;
  color: #0e1c2a;
}
#session-panel, #onboard-panel { display: none; }
#session-panel.active, #onboard-panel.active { display: block; }
.calix-appbar {
  position: sticky; top: 0; z-index: 2000;
  display: flex; gap: 8px; align-items: center; justify-content: center;
  padding: 10px 12px 12px;
  background: linear-gradient(180deg, #0e1c2a 0%, #1a3c5e 100%);
  box-shadow: 0 4px 16px rgba(14,28,42,.18);
}
.calix-appbar-inner {
  display: flex; width: 100%; max-width: 560px; margin: 0 auto;
  background: rgba(255,255,255,.1); border-radius: 12px; padding: 4px;
  border: 1px solid rgba(255,255,255,.12);
}
.calix-tab {
  flex: 1; border: none; border-radius: 9px; padding: 11px 8px;
  font-size: 14px; font-weight: 600; cursor: pointer; font-family: inherit;
  background: transparent; color: rgba(255,255,255,.55);
  transition: color .15s, background .15s;
}
.calix-tab.active {
  background: #fff; color: #1a3c5e;
  box-shadow: 0 1px 4px rgba(0,0,0,.12);
}
.calix-tab:focus-visible { outline: 2px solid #7ab8f5; outline-offset: 2px; }
/* Shared brand images (usable inside scoped panels) */
.calix-logo-full { max-width: min(280px, 92vw); height: auto; display: block; margin: 0 auto; }
.calix-logo-mark { width: 48px; height: 48px; object-fit: contain; display: block; }
.hdr-logo-wrap {
  display: inline-flex; align-items: center; justify-content: center;
  margin-bottom: 14px;
}
.hdr-logo-wrap .calix-logo-hdr {
  height: 40px; width: auto; display: block;
  filter: brightness(0) invert(1); opacity: .96;
}
.brand-success-logo {
  width: 72px; height: 72px; object-fit: contain; margin: 0 auto 16px; display: block;
}
.brand-success-wrap {
  width: 88px; height: 88px; border-radius: 50%;
  background: transparent; border: 2px solid #B5D4F4;
  display: flex; align-items: center; justify-content: center;
  margin: 0 auto 16px; padding: 8px;
}
/* Invoice download sheet (after onboarding / payment) */
.invoice-modal {
  position: fixed; inset: 0; z-index: 5000;
  display: flex; align-items: flex-end; justify-content: center;
  pointer-events: none; opacity: 0; visibility: hidden;
  transition: opacity .2s, visibility .2s;
}
.invoice-modal.open { pointer-events: auto; opacity: 1; visibility: visible; }
.invoice-modal-backdrop {
  position: absolute; inset: 0;
  background: rgba(14, 28, 42, 0.55);
  backdrop-filter: blur(4px);
}
.invoice-modal-sheet {
  position: relative; z-index: 1;
  width: 100%; max-width: 480px;
  background: #fff;
  border-radius: 20px 20px 0 0;
  padding: 20px 20px calc(20px + env(safe-area-inset-bottom, 0px));
  box-shadow: 0 -8px 40px rgba(14, 28, 42, 0.2);
  text-align: center;
  transform: translateY(100%);
  transition: transform .28s cubic-bezier(.32, .72, .24, 1);
}
.invoice-modal.open .invoice-modal-sheet { transform: translateY(0); }
.invoice-modal-logo {
  width: 56px; height: 56px; object-fit: contain;
  margin: 0 auto 12px; display: block;
}
.invoice-modal-sheet h2 {
  font-size: 20px; font-weight: 700; color: #1a3c5e; margin: 0 0 8px;
}
.invoice-modal-sheet p {
  font-size: 14px; line-height: 1.5; color: #3d5166; margin: 0 0 16px;
}
.invoice-modal-loading {
  font-size: 14px; color: #8098ae; margin-bottom: 14px;
  display: flex; align-items: center; justify-content: center; gap: 10px;
}
.invoice-modal-loading::before {
  content: ''; width: 22px; height: 22px;
  border: 3px solid #e8f0f8; border-top-color: #1a3c5e;
  border-radius: 50%; animation: invSpin .7s linear infinite;
}
@keyframes invSpin { to { transform: rotate(360deg); } }
.invoice-modal-download {
  display: block; width: 100%;
  padding: 16px 20px; margin-bottom: 10px;
  border: none; border-radius: 14px;
  font: 700 16px/1.2 'DM Sans', system-ui, sans-serif;
  background: linear-gradient(135deg, #0e6b44, #1a3c5e);
  color: #fff; cursor: pointer;
  touch-action: manipulation;
  box-shadow: 0 4px 14px rgba(14, 107, 68, 0.35);
}
.invoice-modal-download:disabled {
  background: #b0c4d8; box-shadow: none; cursor: not-allowed;
}
.invoice-modal-secondary {
  display: block; width: 100%; padding: 12px;
  border: none; background: transparent;
  font: 600 14px 'DM Sans', system-ui, sans-serif;
  color: #3d5166; cursor: pointer;
}
.invoice-modal-close {
  position: absolute; top: 12px; right: 14px;
  width: 36px; height: 36px; border: none; border-radius: 50%;
  background: #f0f4f8; color: #3d5166; font-size: 20px; cursor: pointer;
}
"""

INVOICE_MODAL_HTML = """
<div id="invoiceModal" class="invoice-modal" aria-hidden="true" role="dialog" aria-labelledby="invoiceModalTitle">
  <div class="invoice-modal-backdrop" id="invoiceModalBackdrop"></div>
  <div class="invoice-modal-sheet">
    <button type="button" class="invoice-modal-close" id="invoiceModalClose" aria-label="Close">×</button>
    <img class="invoice-modal-logo" src="assets/calixlab-mark.png" alt="" width="56" height="56"/>
    <h2 id="invoiceModalTitle">Invoice ready</h2>
    <p id="invoiceModalSub">Preparing your PDF…</p>
    <div class="invoice-modal-loading" id="invoiceModalLoading">Preparing your invoice…</div>
    <button type="button" class="invoice-modal-download" id="invoiceModalDownload" disabled>Download invoice PDF</button>
    <button type="button" class="invoice-modal-secondary" id="invoiceModalLater">Done for now</button>
  </div>
</div>
"""

FAVICON_HEAD = """
<link rel="icon" href="assets/favicon.ico" sizes="any"/>
<link rel="icon" type="image/png" sizes="32x32" href="assets/favicon-32.png"/>
<link rel="icon" type="image/png" sizes="16x16" href="assets/favicon-16.png"/>
<link rel="apple-touch-icon" sizes="180x180" href="assets/icon-180.png"/>
<link rel="manifest" href="site.webmanifest"/>
<meta name="theme-color" content="#1a3c5e"/>
"""

GAS_SCRIPTS = """
<script src="image-compress.js"></script>
<script src="config.js"></script>
<script src="gas-client.js"></script>
<script src="trainers.js"></script>
<script src="invoice-actions.js"></script>
"""

STUB_JS = """
<script>
/* Local preview when config.js has no Apps Script URL. Submissions → localStorage. */
(function () {
  var runDesc = window.google && window.google.script &&
    Object.getOwnPropertyDescriptor(window.google.script, 'run');
  if (runDesc && runDesc.get) return;
  if (window.google && window.google.script && window.google.script.run &&
      window.google.script.run.withSuccessHandler && !runDesc) return;
  var LS_KEY = 'calixlab_local_test_log';
  var TRAINER_KEY = 'calixlab_trainers';
  function loadTrainers() {
    try { return JSON.parse(localStorage.getItem(TRAINER_KEY) || '[]'); } catch (e) { return ['Alex', 'Sarah', 'Hafiz', 'Nurul']; }
  }
  function saveTrainersLocal(list) { localStorage.setItem(TRAINER_KEY, JSON.stringify(list)); }
  function loadLog() {
    try { return JSON.parse(localStorage.getItem(LS_KEY) || '[]'); } catch (e) { return []; }
  }
  function saveLog(entry) {
    var log = loadLog();
    log.unshift(entry);
    localStorage.setItem(LS_KEY, JSON.stringify(log.slice(0, 50)));
    console.log('[Calixlab local test]', entry.type, entry);
  }
  window.calixlabLocalLog = loadLog;
  window.calixlabClearLocalLog = function () { localStorage.removeItem(LS_KEY); };
  var run = {
    _ok: function () {},
    _bad: function () {},
    withSuccessHandler: function (fn) { this._ok = fn; return this; },
    withFailureHandler: function (fn) { this._bad = fn; return this; },
    lookupClient: function (q) {
      var self = this;
      setTimeout(function () {
        var log = loadLog();
        var matches = log.filter(function (e) {
          return e.type === 'onboard' && e.data && e.data.fullName &&
            e.data.fullName.toLowerCase().indexOf(String(q || '').toLowerCase()) >= 0;
        });
        if (!matches.length) { self._ok([]); return; }
        self._ok(matches.map(function (m, i) {
          var sessions = parseInt(m.data.sessions, 10) || 0;
          return {
            fullName: m.data.fullName, trainerName: m.data.trainerName || 'Alex',
            packageType: m.data.packageType || '1-1',
            sessionsTotal: sessions,
            sessionsRemaining: sessions,
            leadType: m.data.leadType || '',
            discoverySource: m.data.discoverySource || '',
            amountPaid: parseFloat(m.data.amountPaid) || 0,
            totalValue: parseFloat(m.data.totalPackageValue) || 0, outstanding: 0,
            instalmentsPaid: 1, totalInstalments: 1, isInstalment: false,
            rowIndex: i + 2
          };
        }));
      }, 120);
    },
    onboardClient: function (data) {
      var self = this;
      setTimeout(function () {
        saveLog({ type: 'onboard', at: new Date().toISOString(), data: data });
        self._ok({ folderUrl: '', rowIndex: 2, local: true });
      }, 350);
    },
    recordPayment: function (data) {
      var self = this;
      setTimeout(function () {
        saveLog({ type: 'payment', at: new Date().toISOString(), data: data });
        self._ok({ folderUrl: '', local: true });
      }, 350);
    },
    listTrainers: function () {
      var self = this;
      setTimeout(function () { self._ok(loadTrainers()); }, 80);
    },
    addTrainer: function (data) {
      var self = this;
      setTimeout(function () {
        var n = (data && data.name) ? String(data.name).trim() : '';
        var list = loadTrainers();
        if (n && list.indexOf(n) < 0) list.push(n);
        saveTrainersLocal(list);
        self._ok({ ok: true, name: n });
      }, 80);
    },
    deleteTrainer: function (data) {
      var self = this;
      setTimeout(function () {
        var n = (data && data.name) ? String(data.name).trim() : '';
        saveTrainersLocal(loadTrainers().filter(function (t) { return t !== n; }));
        self._ok({ ok: true, name: n });
      }, 80);
    },
    recordSessionLog: function (data) {
      var self = this;
      setTimeout(function () {
        saveLog({ type: 'session', at: new Date().toISOString(), data: data });
        self._ok({ rowIndex: 2, local: true });
      }, 200);
    },
    generateInvoice: function () {
      var self = this;
      setTimeout(function () {
        self._ok({ invoiceNumber: 'CL-INV-LOCAL', pdfBase64: '', local: true });
      }, 200);
    },
    previewInvoiceHtml: function () {
      var self = this;
      setTimeout(function () {
        self._ok({ invoiceNumber: 'CL-INV-LOCAL', html: '<p>Local preview — configure Apps Script for full invoice.</p>', local: true });
      }, 200);
    }
  };
  window.google = { script: { run: run } };
  console.info('[Calixlab] Local dev mode. View test log: calixlabLocalLog() — clear: calixlabClearLocalLog()');
})();
function calixSwitchTab(which) {
  var s = document.getElementById('session-panel');
  var o = document.getElementById('onboard-panel');
  var ts = document.getElementById('tabSession');
  var to = document.getElementById('tabOnboard');
  var on = which === 'onboard';
  s.classList.toggle('active', !on);
  o.classList.toggle('active', on);
  ts.classList.toggle('active', !on);
  to.classList.toggle('active', on);
  window.scrollTo({ top: 0, behavior: 'auto' });
  if (on && typeof resizeCanvas === 'function') {
    requestAnimationFrame(function () { resizeCanvas(); });
  }
}
document.addEventListener('DOMContentLoaded', function () {
  calixSwitchTab('onboard');
  var u = window.CALIXLAB_GAS_EXEC_URL || '';
  if (!u || /YOUR_DEPLOYMENT_ID|PASTE_|REPLACE_/i.test(u)) {
    var bar = document.createElement('div');
    bar.setAttribute('role', 'alert');
    bar.style.cssText = 'background:#3d2a00;color:#ffd48a;padding:10px 14px;font:500 13px/1.4 DM Sans,sans-serif;text-align:center;border-bottom:1px solid #5c4200';
    bar.textContent = 'Onboarding saves are in local test mode. Set CALIXLAB_GAS_EXEC_URL in config.js (Apps Script /exec URL) for Google Sheets.';
    var appbar = document.querySelector('.calix-appbar');
    if (appbar && appbar.parentNode) appbar.parentNode.insertBefore(bar, appbar);
  }
});
</script>
"""

out = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no"/>
<title>Cali Lab — Trainer Hub</title>
{FAVICON_HEAD}
<link href="https://fonts.googleapis.com/css2?family=DM+Sans:ital,opsz,wght@0,9..40,300;0,9..40,400;0,9..40,500;0,9..40,600;0,9..40,700;1,9..40,400&family=DM+Mono:wght@400;500&display=swap" rel="stylesheet"/>
<style>
{APP_SHELL_CSS}
</style>
<style>
{session_scoped}
</style>
<style>
{ob_scoped}
</style>
</head>
<body class="app-body">

<header class="calix-appbar" role="navigation" aria-label="Main">
  <div class="calix-appbar-inner">
    <button type="button" class="calix-tab active" id="tabOnboard" onclick="calixSwitchTab('onboard')">Onboarding</button>
    <button type="button" class="calix-tab" id="tabSession" onclick="calixSwitchTab('session')">Session Log</button>
  </div>
</header>

<div id="session-panel">
{session_body}
</div>

<div id="onboard-panel" class="active">
{onboard_body}
</div>

{GAS_SCRIPTS}
{STUB_JS}
</body>
</html>
"""

OUT = Path("/home/ting/Downloads/calixlab-app/index.html")
OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(out, encoding="utf-8")
print("Wrote", OUT, "bytes", len(out.encode("utf-8")))
