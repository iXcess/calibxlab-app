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
  display: flex; width: 100%; max-width: 560px;
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
.calix-demonote {
  max-width: 560px; margin: 0 auto; padding: 8px 16px 0;
  font-size: 12px; color: #5a6b7a; text-align: center; line-height: 1.45;
}
"""

STUB_JS = """
<script>
/* Local preview: Apps Script bridge is absent — stub google.script.run */
(function () {
  if (window.google && window.google.script && window.google.script.run && window.google.script.run.withSuccessHandler) return;
  var run = {
    _ok: function () {},
    _bad: function () {},
    withSuccessHandler: function (fn) { this._ok = fn; return this; },
    withFailureHandler: function (fn) { this._bad = fn; return this; },
    lookupClient: function () {
      var self = this;
      setTimeout(function () { self._ok([]); }, 120);
    },
    onboardClient: function () {
      var self = this;
      setTimeout(function () { self._ok({ folderUrl: 'https://example.com' }); }, 350);
    },
    recordPayment: function () {
      var self = this;
      setTimeout(function () { self._ok({}); }, 350);
    }
  };
  window.google = { script: { run: run } };
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
  calixSwitchTab('session');
});
</script>
"""

out = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no"/>
<title>Calixlab — Trainer Hub</title>
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
    <button type="button" class="calix-tab active" id="tabSession" onclick="calixSwitchTab('session')">Session Log</button>
    <button type="button" class="calix-tab" id="tabOnboard" onclick="calixSwitchTab('onboard')">Onboarding</button>
  </div>
</header>
<p class="calix-demonote">Onboarding client search / save uses Google Apps Script when deployed. Locally, search returns “new client” and submit simulates success.</p>

<div id="session-panel" class="active">
{session_body}
</div>

<div id="onboard-panel">
{onboard_body}
</div>

{STUB_JS}
</body>
</html>
"""

OUT = Path("/home/ting/Downloads/calixlab-app/index.html")
OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(out, encoding="utf-8")
print("Wrote", OUT, "bytes", len(out.encode("utf-8")))
