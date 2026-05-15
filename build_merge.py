#!/usr/bin/env python3
"""Merge Session Log + Onboarding HTML into one scoped webapp."""
import re
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


def extract_master_panel_css(ob_style: str) -> str:
    start = ob_style.index("/* ── CARD ──")
    end = ob_style.index("/* ── TRAINER ──")
    return ob_style[start:end].strip()


SHARED_HEADER_CSS = """
.header { text-align: center; margin-bottom: 24px; }
.logo {
  margin: 0 auto 12px;
  display: flex; align-items: center; justify-content: center;
}
.logo img.calix-logo-full {
  max-width: min(300px, 94vw); height: auto; display: block;
}
.header h1 { font-size: 22px; font-weight: 700; color: #0C447C; line-height: 1.2; }
.header p { font-size: 14px; color: #666; margin-top: 4px; }
.session-date-pill {
  display: inline-flex; align-items: center; gap: 7px;
  margin-top: 12px; padding: 8px 14px;
  background: #E6F1FB; border: 1px solid #B5D4F4; border-radius: 20px;
  font-size: 13px; color: #0C447C; font-weight: 500;
}
"""

SESSION_HEADER_HTML = """
<div class="header">
  <motion class="logo">
    <img class="calix-logo-full" src="assets/calixlab-logo-header.png" alt="Cali Lab" width="280" height="56"/>
  </div>
  <h1>Session Log</h1>
  <p>Submit immediately after every session.</p>
  <p class="session-date-pill" id="hDate">📅 —</p>
</motion>
""".replace("<motion ", "<div ").replace("</motion>", "</div>")

SESSION_COMPONENT_CSS = """
/* Session-only UI (onboarding master theme) */
.lbl {
  display: block; font-size: 13px; font-weight: 600; color: #444;
  margin-bottom: 7px; line-height: 1.3;
}
.lbl .r { color: #E24B4A; }
.hint { font-size: 12px; color: #999; margin-top: 7px; line-height: 1.5; }
.ferr { font-size: 12px; color: #E24B4A; margin-top: 6px; font-weight: 500; display: none; }
.prog {
  width: 100%; max-width: 560px; box-sizing: border-box;
  background: white; border: 1px solid #e8e8e8; border-radius: 16px;
  padding: 14px 20px; margin: 0 auto 14px;
  box-shadow: 0 1px 4px rgba(0,0,0,0.06);
}
.prog-top { display: flex; justify-content: space-between; align-items: center; margin-bottom: 9px; }
.prog-step { font-size: 13px; font-weight: 600; color: #185FA5; }
.prog-frac { font-size: 13px; color: #999; }
.prog-bar { height: 4px; background: #e8e8e8; border-radius: 2px; overflow: hidden; }
.prog-fill { height: 100%; background: #185FA5; border-radius: 2px; transition: width .4s ease; }
.body {
  width: 100%; max-width: 560px; margin: 0 auto;
  padding: 0; display: flex; flex-direction: column; gap: 14px; align-items: stretch;
}
.session-stack {
  width: 100%; max-width: 560px; margin: 0 auto;
  display: flex; flex-direction: column; gap: 14px; align-items: stretch;
}
.card { width: 100%; box-sizing: border-box; margin-bottom: 0; }
.body > .card { margin-bottom: 0; }
.card.err-card { border-color: #E24B4A !important; }
.sw { position: relative; }
.sw::after {
  content: '▾'; position: absolute; right: 14px; top: 50%;
  transform: translateY(-50%); color: #888; pointer-events: none;
}
.aw { position: relative; }
.ai {
  width: 100%; padding: 13px 14px; border: 1.5px solid #ddd; border-radius: 10px;
  font-size: 16px; color: #1a1a1a; background: #fafafa; outline: none;
  font-family: inherit; transition: border-color .15s, background .15s; min-height: 48px;
}
.ai:focus { outline: none; border-color: #185FA5; background: white; box-shadow: 0 0 0 3px rgba(24,95,165,0.12); }
.ai.filled { border-color: #B5D4F4; background: #f0f7ff; color: #0C447C; font-weight: 600; }
.adrop {
  position: absolute; top: calc(100% + 5px); left: 0; right: 0;
  background: white; border: 1.5px solid #185FA5; border-radius: 11px;
  box-shadow: 0 4px 16px rgba(0,0,0,0.1); max-height: 250px; overflow-y: auto; z-index: 300; display: none;
}
.adrop.open { display: block; }
.aitem {
  padding: 12px 16px; font-size: 14px; cursor: pointer;
  border-bottom: 1px solid #e8e8e8; display: flex; justify-content: space-between; align-items: center; gap: 10px;
}
.aitem:last-child { border-bottom: none; }
.aitem:hover, .aitem.hi { background: #E6F1FB; }
.aitem mark { background: none; color: #185FA5; font-weight: 700; }
.abadge { font-size: 10px; font-weight: 600; padding: 3px 8px; border-radius: 10px; white-space: nowrap; }
.ab-ok { background: #EAF3DE; color: #27500A; }
.ab-warn { background: #FFF8EE; color: #854F0B; }
.ab-bad { background: #FCEBEB; color: #A32D2D; }
.alead-badge { font-size: 10px; padding: 3px 8px; border-radius: 10px; background: #E6F1FB; color: #185FA5; }
.aempty { padding: 13px 16px; font-size: 13px; color: #999; font-style: italic; }
.si {
  margin-top: 12px; background: #f0f7ff; border: 1.5px solid #B5D4F4;
  border-radius: 16px; padding: 16px; display: none;
}
.si.show { display: block; }
.si-ttl { font-size: 11px; font-weight: 700; text-transform: uppercase; letter-spacing: .1em; color: #185FA5; margin-bottom: 12px; }
.si-grid { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 8px; margin-bottom: 12px; }
.si-box { background: white; border: 1px solid #B5D4F4; border-radius: 10px; padding: 10px; text-align: center; }
.si-v { font-size: 22px; font-weight: 700; color: #0C447C; line-height: 1; }
.si-k { font-size: 10px; color: #666; text-transform: uppercase; margin-top: 4px; }
.si-box.ok .si-v { color: #3B6D11; }
.si-box.warn .si-v { color: #854F0B; }
.si-box.bad .si-v { color: #A32D2D; }
.si-next { background: white; border: 1px solid #B5D4F4; border-radius: 10px; padding: 12px 14px; display: flex; gap: 10px; align-items: flex-start; }
.si-nb strong { display: block; font-size: 14px; color: #0C447C; margin-bottom: 3px; }
.si-nb span { font-size: 12px; color: #666; line-height: 1.4; }
.si-foot { font-size: 11px; color: #999; margin-top: 10px; }
.lead-auto {
  padding: 14px 16px; border-radius: 10px; border: 1.5px solid #ddd;
  background: #fafafa; display: flex; align-items: center; justify-content: space-between; min-height: 54px;
}
.lead-auto.set-calix { background: #f0f7ff; border-color: #B5D4F4; }
.lead-auto.set-own { background: #EAF3DE; border-color: #639922; }
.lead-mult { font-size: 26px; font-weight: 700; line-height: 1; }
.set-calix .lead-mult, .set-calix .lead-name { color: #185FA5; }
.set-own .lead-mult, .set-own .lead-name { color: #3B6D11; }
.lead-name { font-size: 15px; font-weight: 600; }
.lead-right { font-size: 11px; font-weight: 600; padding: 4px 10px; border-radius: 20px; }
.set-calix .lead-right { background: #E6F1FB; color: #185FA5; }
.set-own .lead-right { background: #EAF3DE; color: #3B6D11; }
.lead-empty { font-size: 13px; color: #999; font-style: italic; }
.chips { display: flex; gap: 8px; flex-wrap: wrap; }
.chip {
  flex: 1; min-width: 80px; padding: 12px 8px; border: 1.5px solid #ddd; border-radius: 10px;
  background: white; font-size: 14px; font-weight: 500; color: #555; cursor: pointer; text-align: center;
  font-family: inherit; min-height: 44px; transition: all .15s;
}
.chip:hover { border-color: #185FA5; background: #E6F1FB; }
.chip.t-g { background: #EAF3DE; border-color: #639922; color: #27500A; font-weight: 700; }
.chip.t-s { background: #FFF8EE; border-color: #FAC775; color: #854F0B; font-weight: 700; }
.chip.t-p { background: #FCEBEB; border-color: #E24B4A; color: #A32D2D; font-weight: 700; }
.ctr { display: flex; align-items: center; border: 1.5px solid #ddd; border-radius: 10px; overflow: hidden; background: #fafafa; }
.ctr.on { border-color: #185FA5; background: #f0f7ff; }
.cb { width: 54px; height: 52px; border: none; background: transparent; font-size: 22px; color: #555; cursor: pointer; }
.cv { flex: 1; text-align: center; font-size: 26px; font-weight: 700; border: none; background: transparent; outline: none; color: #1a1a1a; }
.ctr.on .cv { color: #185FA5; }
.sign-card {
  width: 100%; max-width: 560px; box-sizing: border-box; margin-left: auto; margin-right: auto;
  background: #f0f7ff; border: 2px solid #B5D4F4; border-radius: 16px; padding: 18px;
}
.sign-ttl { font-size: 15px; font-weight: 700; color: #185FA5; margin-bottom: 3px; }
.sign-sub { font-size: 12px; color: #666; margin-bottom: 14px; line-height: 1.5; }
.pad-wrap { background: white; border: 1.5px solid #B5D4F4; border-radius: 10px; position: relative; overflow: hidden; margin-bottom: 10px; }
.pad-lbl { position: absolute; top: 50%; left: 50%; transform: translate(-50%,-50%); text-align: center; font-size: 13px; color: #ccc; pointer-events: none; line-height: 1.7; }
canvas { display: block; width: 100%; height: 130px; touch-action: none; cursor: crosshair; }
.btn-clr { width: 100%; padding: 10px; border: 1.5px solid #ddd; border-radius: 10px; background: white; font-size: 13px; font-weight: 600; color: #555; cursor: pointer; font-family: inherit; }
.cfm-row { display: flex; align-items: flex-start; gap: 12px; margin-top: 12px; padding: 13px; background: white; border-radius: 10px; border: 1.5px solid #ddd; cursor: pointer; }
.cfm-row.on { border-color: #185FA5; background: #f0f7ff; }
.cfm-row input[type=checkbox] { width: 22px; height: 22px; accent-color: #185FA5; margin-top: 1px; }
.cfm-txt { font-size: 14px; color: #444; line-height: 1.5; }
.cfm-txt strong { color: #185FA5; }
.preview {
  width: 100%; max-width: 560px; box-sizing: border-box; margin-left: auto; margin-right: auto;
  background: white; border: 1px solid #e8e8e8; border-radius: 16px; padding: 16px 18px;
  display: none; box-shadow: 0 1px 4px rgba(0,0,0,0.06);
}
.preview.on { display: block; }
.prev-ttl { font-size: 11px; font-weight: 700; text-transform: uppercase; letter-spacing: .1em; color: #185FA5; margin-bottom: 12px; }
.prev-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; }
.pi .pk { font-size: 11px; color: #999; text-transform: uppercase; margin-bottom: 2px; }
.pi .pv { font-size: 14px; color: #1a1a1a; font-weight: 600; }
.btn-sub {
  width: 100%; padding: 17px; background: #185FA5; border: none; border-radius: 16px;
  font-size: 16px; font-weight: 700; color: white; cursor: pointer; margin-top: 10px; font-family: inherit;
}
.btn-sub:active { transform: scale(.98); }
.sub-note { text-align: center; font-size: 12px; color: #999; margin-top: 10px; }
.success { display: none; padding: 20px 16px 60px; text-align: center; max-width: 560px; margin: 0 auto; }
.success.on { display: block; }
.s-ring { width: 88px; height: 88px; border-radius: 50%; background: transparent; border: 2px solid #B5D4F4; display: flex; align-items: center; justify-content: center; margin: 0 auto 16px; padding: 8px; }
.s-title { font-size: 22px; font-weight: 700; color: #0C447C; margin-bottom: 8px; }
.s-sub { font-size: 14px; color: #666; line-height: 1.6; margin-bottom: 20px; }
.s-summ { background: white; border: 1px solid #e8e8e8; border-radius: 16px; padding: 18px; text-align: left; margin-bottom: 16px; box-shadow: 0 1px 4px rgba(0,0,0,0.06); }
.s-row { display: flex; justify-content: space-between; padding: 8px 0; border-bottom: 1px solid #e8e8e8; font-size: 14px; }
.s-row:last-child { border-bottom: none; }
.s-row .sk { color: #999; } .s-row .sv { font-weight: 600; color: #1a1a1a; }
.copy-box { background: #f0f7ff; border: 1.5px solid #B5D4F4; border-radius: 16px; padding: 16px; text-align: left; margin-bottom: 16px; }
.copy-lbl { font-size: 11px; font-weight: 700; text-transform: uppercase; letter-spacing: .08em; color: #185FA5; margin-bottom: 9px; }
.copy-txt { font-size: 11px; color: #444; line-height: 1.9; word-break: break-all; font-family: ui-monospace, monospace; }
.btn-copy { margin-top: 10px; width: 100%; padding: 12px; background: white; border: 1.5px solid #ddd; border-radius: 10px; font-size: 13px; font-weight: 600; color: #555; cursor: pointer; font-family: inherit; }
.btn-new { width: 100%; padding: 15px; background: #185FA5; border: none; border-radius: 16px; font-size: 15px; font-weight: 600; color: white; cursor: pointer; font-family: inherit; }
.toast { position: fixed; bottom: 20px; left: 16px; right: 16px; background: #E24B4A; color: white; padding: 13px 16px; border-radius: 10px; font-size: 14px; font-weight: 500; transform: translateY(100px); opacity: 0; transition: all .3s ease; z-index: 999; max-width: 528px; margin: 0 auto; }
.toast.show { transform: translateY(0); opacity: 1; }
.card:focus-within { border-color: #185FA5; box-shadow: 0 4px 16px rgba(0,0,0,0.08); }
.card { animation: up .28s ease both; }
.card:nth-child(1){animation-delay:.03s}
.card:nth-child(2){animation-delay:.07s}
.card:nth-child(3){animation-delay:.11s}
.card:nth-child(4){animation-delay:.15s}
.card:nth-child(5){animation-delay:.19s}
.card:nth-child(6){animation-delay:.23s}
@keyframes up { from{opacity:0;transform:translateY(10px)} to{opacity:1;transform:none} }
@keyframes pop { from{transform:scale(0);opacity:0} to{transform:scale(1);opacity:1} }
.s-ring { animation: pop .4s cubic-bezier(.34,1.56,.64,1); }
"""

SESSION_MOBILE_CSS = """
@media (max-width: 480px) {
  .si-grid { grid-template-columns: 1fr 1fr; }
  .prev-grid { grid-template-columns: 1fr; }
  .lead-auto { flex-direction: column; align-items: flex-start; gap: 8px; }
  .chip { flex: 1 1 calc(50% - 4px); min-width: calc(50% - 4px); }
}
@media (max-width: 360px) {
  .si-grid { grid-template-columns: 1fr; }
  .si-v { font-size: 20px; }
}
.adrop { -webkit-overflow-scrolling: touch; }
"""

SESSION_SCOPE_CSS = """
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
:scope {
  -webkit-text-size-adjust: 100%;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  background: #f0efe9;
  min-height: 100vh;
  padding: 20px 16px 60px;
  color: #1a1a1a;
  font-size: 16px;
  -webkit-tap-highlight-color: transparent;
}
"""


def prep_session_style(_raw: str, master: str) -> str:
    return f"{SESSION_SCOPE_CSS}\n\n{master}\n\n{SESSION_COMPONENT_CSS}\n\n{SESSION_MOBILE_CSS}"


def prep_session_body(body: str) -> str:
    body = re.sub(
        r'<div class="hdr">[\s\S]*?\n\n<div class="prog">',
        SESSION_HEADER_HTML.strip() + "\n\n<div class=\"prog\">",
        body,
        count=1,
    )
    return body.replace(
        '<div style="padding:0 16px;max-width:560px;margin:0 auto;">',
        '<div class="session-stack">',
        1,
    )


ob_style = extract_between(ONBOARD, "<style>", "</style>")
MASTER_PANEL_CSS = extract_master_panel_css(ob_style)
session_style_raw = extract_between(SESSION, "<style>", "</style>")
session_scoped = (
    "@scope (#session-panel) {\n"
    + prep_session_style(session_style_raw, MASTER_PANEL_CSS)
    + "\n}"
)
# Drop html rule; body -> :scope once
ob_style = ob_style.replace("html { -webkit-text-size-adjust: 100%; }", "")
ob_style = ob_style.replace(
    "body {\n  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;",
    ":scope {\n  -webkit-text-size-adjust: 100%;\n  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;",
    1,
)
from hub_merge import (
    ADMIN_JS,
    ADMIN_PANEL_HTML,
    HUB_APP_SHELL_CSS,
    HUB_JS,
    HUB_NAV_HTML,
    ONBOARD_INNER_SWITCHER_HTML,
    TRAINER_PANEL_HTML,
    prep_onboard_body,
)

ob_scoped = (
    "@scope (#view-onboarding, #view-payment, #view-admin) {\n"
    + ob_style
    + "\n}"
)

session_body = prep_session_body(extract_body_inner(SESSION))
_onboard_raw = extract_body_inner(ONBOARD)
onboard_shared, onboard_client, onboard_payment, onboard_scripts = prep_onboard_body(_onboard_raw)

MOBILE_RESPONSIVE_CSS = """
/* Mobile polish — test widths: 320 / 375 / 390 / 414 */
#hub-header { margin-bottom: 20px; }
@media (max-width: 480px) {
  .row2 { grid-template-columns: 1fr; }
  .rp-summary { grid-template-columns: 1fr 1fr; }
  .prev-grid { grid-template-columns: 1fr; }
  .trainer-select-row { flex-wrap: wrap; }
  .trainer-select-row select { flex: 1 1 100%; min-width: 0; }
  .trainer-select-row .icon-btn { min-width: 48px; min-height: 48px; }
  .preset-row .preset-btn { flex: 1 1 calc(50% - 4px); min-width: calc(50% - 4px); }
  #grp-leadType.toggle-group { width: 100%; }
  #grp-leadType .toggle-btn { width: 100%; text-align: left; }
  .waiver-scroll { height: min(260px, 40vh); -webkit-overflow-scrolling: touch; }
  .hub-view.active .card,
  .admin-panel-wrap .card,
  .payroll-results .card { margin-left: auto; margin-right: auto; width: calc(100% - 24px); max-width: 560px; }
  #hub-header { margin-bottom: 16px; }
}
@media (max-width: 360px) {
  .rp-summary { grid-template-columns: 1fr; }
  .rp-val { font-size: 15px; word-break: break-word; }
}
.rp-val, .admin-msg, #rpSelectedName, .payroll-trainer-card .section-title {
  word-break: break-word;
}
.lookup-card, #lookupResults, #rpLookupResults { -webkit-overflow-scrolling: touch; }
.icon-btn, .chip-btn, .toggle-btn, .preset-btn, .mode-btn { min-height: 44px; }
"""

APP_SHELL_CSS = """
/* —— App shell (onboarding master theme) —— */
html { -webkit-text-size-adjust: 100%; }
body.app-body {
  margin: 0;
  min-height: 100vh;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  background: #f0efe9;
  color: #1a1a1a;
  font-size: 16px;
  overflow-x: clip;
  padding-bottom: calc(60px + env(safe-area-inset-bottom, 0px));
}
""" + HUB_APP_SHELL_CSS + SHARED_HEADER_CSS + MOBILE_RESPONSIVE_CSS + """
/* Shared brand images */
.calix-logo-full { max-width: min(300px, 94vw); height: auto; display: block; margin: 0 auto; }
.calix-logo-mark { width: 48px; height: 48px; object-fit: contain; display: block; }
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
  font-size: 20px; font-weight: 700; color: #0C447C; margin: 0 0 8px;
}
.invoice-modal-sheet p {
  font-size: 14px; line-height: 1.5; color: #666; margin: 0 0 16px;
}
.invoice-modal-loading {
  font-size: 14px; color: #8098ae; margin-bottom: 14px;
  display: flex; align-items: center; justify-content: center; gap: 10px;
}
.invoice-modal-loading::before {
  content: ''; width: 22px; height: 22px;
  border: 3px solid #e8f0f8; border-top-color: #185FA5;
  border-radius: 50%; animation: invSpin .7s linear infinite;
}
@keyframes invSpin { to { transform: rotate(360deg); } }
.invoice-modal-download {
  display: block; width: 100%;
  padding: 16px 20px; margin-bottom: 10px;
  border: none; border-radius: 14px;
  font: 700 16px/1.2 inherit;
  background: #185FA5;
  color: #fff; cursor: pointer;
  touch-action: manipulation;
  box-shadow: 0 4px 14px rgba(24, 95, 165, 0.35);
}
.invoice-modal-download:disabled {
  background: #b0c4d8; box-shadow: none; cursor: not-allowed;
}
.invoice-modal-secondary {
  display: block; width: 100%; padding: 12px;
  border: none; background: transparent;
  font: 600 14px inherit;
  color: #666; cursor: pointer;
}
.invoice-modal-close {
  position: absolute; top: 12px; right: 14px;
  width: 36px; height: 36px; border: none; border-radius: 50%;
  background: #f0efe9; color: #666; font-size: 20px; cursor: pointer;
}
/* Shared overlays (outside @scope — must be global) */
.error-banner {
  display: none; background: #FCEBEB; border: 1.5px solid #E24B4A; color: #791F1F;
  padding: 12px 16px; border-radius: 10px; font-size: 14px; font-weight: 500;
  max-width: 560px; margin: 0 auto 14px; text-align: center;
}
.error-banner.show { display: block; }
.progress-overlay {
  display: none; position: fixed; inset: 0; background: rgba(0,0,0,0.5);
  z-index: 9999; align-items: center; justify-content: center;
}
.progress-overlay.show { display: flex; }
.progress-box {
  background: white; border-radius: 16px; padding: 28px 32px; text-align: center; max-width: 300px; width: 90%;
}
.progress-box p { font-size: 15px; font-weight: 600; color: #0C447C; margin-bottom: 6px; }
.progress-box small { font-size: 12px; color: #888; }
.hidden { display: none !important; }
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
<meta name="theme-color" content="#185FA5"/>
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
    getPayrollSummary: function (data) {
      var self = this;
      setTimeout(function () {
        self._ok({
          startDate: (data && data.startDate) || '',
          endDate: (data && data.endDate) || '',
          grandTotalSessions: 4,
          grandTotalEarnings: 720,
          trainers: [
            { name: 'Alex', sessionCount: 3, totalEarnings: 540, sessions: [] },
            { name: 'Sarah', sessionCount: 1, totalEarnings: 180, sessions: [] }
          ],
          local: true
        });
      }, 120);
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
</script>
"""

out = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no"/>
<title>Cali Lab — Trainer Hub</title>
{FAVICON_HEAD}
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

{HUB_NAV_HTML}

{onboard_shared}

<div id="view-onboarding" class="hub-view active">
{ONBOARD_INNER_SWITCHER_HTML}
<div id="onboardClientSection">
{onboard_client}
</div>
<div id="onboardTrainerSection" class="hidden">
{TRAINER_PANEL_HTML}
</div>
</div>

<div id="view-payment" class="hub-view">
{onboard_payment}
</div>

<div id="session-panel" class="hub-view">
{session_body}
</div>

<div id="view-admin" class="hub-view">
{ADMIN_PANEL_HTML}
</div>

{onboard_scripts}
{HUB_JS}
{ADMIN_JS}
{GAS_SCRIPTS}
{STUB_JS}
</body>
</html>
"""

OUT = Path("/home/ting/Downloads/calixlab-app/index.html")
OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(out, encoding="utf-8")
print("Wrote", OUT, "bytes", len(out.encode("utf-8")))
