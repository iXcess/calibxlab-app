# Hub navigation constants and helpers (imported by build_merge.py)
import re

HUB_NAV_HTML = """
<nav class="hub-mode-switcher" role="navigation" aria-label="Main">
  <button type="button" class="mode-btn active" id="hubNavOnboarding" onclick="calixSwitchHubView('onboarding')">Onboarding</button>
  <button type="button" class="mode-btn" id="hubNavPayment" onclick="calixSwitchHubView('payment')">Payment Record</button>
  <button type="button" class="mode-btn" id="hubNavSession" onclick="calixSwitchHubView('session')">Session Log</button>
  <button type="button" class="mode-btn" id="hubNavTrainer" onclick="calixSwitchHubView('trainer')">Trainer</button>
  <button type="button" class="mode-btn" id="hubNavAdmin" onclick="calixSwitchHubView('admin')">Admin</button>
</nav>
<div id="hub-header" class="header">
  <div class="logo">
    <img class="calix-logo-full" src="assets/calixlab-logo-header.png" alt="Cali Lab" width="280" height="56"/>
  </div>
  <h1 id="hubTitle">Client Onboarding</h1>
  <p id="hubSub">New client registration</p>
</div>
"""

TRAINER_PANEL_HTML = """
<div class="card">
  <div class="section-title">
    <svg class="section-icon" viewBox="0 0 24 24" fill="currentColor"><path d="M12 12c2.7 0 4.8-2.1 4.8-4.8S14.7 2.4 12 2.4 7.2 4.5 7.2 7.2 9.3 12 12 12zm0 2.4c-3.2 0-9.6 1.6-9.6 4.8v2.4h19.2v-2.4c0-3.2-6.4-4.8-9.6-4.8z"/></svg>
    Personal Information
  </div>
  <div class="field">
    <label>Full Name <span class="req">*</span></label>
    <input type="text" id="toFullName" placeholder="As per IC / Passport" autocomplete="name"/>
  </div>
  <div class="row2">
    <div class="field">
      <label>Phone Number <span class="req">*</span></label>
      <input type="tel" id="toPhone" placeholder="01X-XXXXXXX"/>
    </div>
    <div class="field">
      <label>Email <span class="req">*</span></label>
      <input type="email" id="toEmail" placeholder="email@example.com"/>
    </div>
  </div>
  <div class="field">
    <label>IC / Passport Number <span class="req">*</span></label>
    <input type="text" id="toIc" placeholder="XXXXXX-XX-XXXX" inputmode="numeric"/>
  </div>
  <div class="row2">
    <div class="field">
      <label>Emergency Contact Name <span class="req">*</span></label>
      <input type="text" id="toEmergencyContact" placeholder="Full name"/>
    </div>
    <div class="field">
      <label>Emergency Contact Phone <span class="req">*</span></label>
      <input type="tel" id="toEmergencyPhone" placeholder="01X-XXXXXXX"/>
    </div>
  </div>
  <div class="ferr" id="toFormErr" style="display:none;margin-top:8px;"></div>
</div>
<div class="submit-wrap">
  <button type="button" class="submit-btn" id="toSubmitBtn" onclick="submitTrainerOnboarding()">Register Trainer</button>
</div>
<div class="success-card" id="toSuccessCard">
  <div class="brand-success-wrap"><img src="assets/calixlab-mark.png" alt="Cali Lab"/></div>
  <h2>Trainer Registered!</h2>
  <p id="toSuccessMsg">Trainer has been added to the sheet.</p>
  <button type="button" class="reset-btn" onclick="resetTrainerOnboarding()">Register Another Trainer</button>
</div>
"""

HUB_APP_SHELL_CSS = """
.hub-view { display: none; }
.hub-view.active { display: block; }
.hub-mode-switcher {
  position: sticky; top: 0; z-index: 2000;
  display: flex; max-width: 560px; width: calc(100% - 32px); margin: 12px auto;
  background: white; border-radius: 12px; padding: 4px;
  border: 1px solid #e8e8e8; box-shadow: 0 1px 4px rgba(0,0,0,0.06);
}
.hub-mode-switcher .mode-btn {
  flex: 1; min-width: 0; padding: 10px 4px; border: none; border-radius: 9px;
  font-size: 11px; font-weight: 600; cursor: pointer; font-family: inherit;
  background: transparent; color: #888; transition: all 0.2s;
}
@media (min-width: 420px) {
  .hub-mode-switcher .mode-btn { font-size: 13px; padding: 10px 6px; }
}
.hub-mode-switcher .mode-btn.active {
  background: #185FA5; color: white;
  box-shadow: 0 1px 4px rgba(0,0,0,0.08);
}
.hub-mode-switcher .mode-btn:focus-visible { outline: 2px solid #185FA5; outline-offset: 2px; }
#hub-header.hidden { display: none; }
.hub-admin-placeholder {
  max-width: 560px; margin: 40px auto; padding: 48px 24px; text-align: center;
  background: white; border-radius: 16px; border: 1px dashed #ddd; color: #999;
  font-size: 15px;
}
"""

HUB_JS = """
<script>
var calixHubView = 'onboarding';
var HUB_HEADERS = {
  onboarding: ['Client Onboarding', 'New client registration'],
  payment: ['Payment Record', 'Record instalment payment'],
  trainer: ['Trainer Onboarding', 'Register a new trainer'],
  admin: ['Admin', '']
};
function calixSwitchHubView(view) {
  calixHubView = view;
  ['onboarding','payment','session','trainer','admin'].forEach(function (v) {
    var el = document.getElementById(v === 'session' ? 'session-panel' : 'view-' + v);
    if (el) el.classList.toggle('active', v === view);
  });
  var navMap = { onboarding: 'hubNavOnboarding', payment: 'hubNavPayment', session: 'hubNavSession', trainer: 'hubNavTrainer', admin: 'hubNavAdmin' };
  Object.keys(navMap).forEach(function (k) {
    var btn = document.getElementById(navMap[k]);
    if (btn) btn.classList.toggle('active', k === view);
  });
  var hubHdr = document.getElementById('hub-header');
  if (hubHdr) {
    if (view === 'session') hubHdr.classList.add('hidden');
    else {
      hubHdr.classList.remove('hidden');
      var t = HUB_HEADERS[view] || ['Cali Lab', ''];
      var ht = document.getElementById('hubTitle');
      var hs = document.getElementById('hubSub');
      if (ht) ht.textContent = t[0];
      if (hs) hs.textContent = t[1];
    }
  }
  if (typeof currentMode !== 'undefined') currentMode = view === 'payment' ? 'record' : 'new';
  var eb = document.getElementById('error-banner');
  if (eb) eb.classList.remove('show');
  window.scrollTo({ top: 0, behavior: 'auto' });
  if (view === 'session' && typeof resizeCanvas === 'function') {
    requestAnimationFrame(function () { resizeCanvas(); });
  }
}
function switchMode(mode) {
  calixSwitchHubView(mode === 'record' ? 'payment' : 'onboarding');
}
function submitTrainerOnboarding() {
  var errEl = document.getElementById('toFormErr');
  var fields = [
    ['toFullName', 'Full name'], ['toPhone', 'Phone number'], ['toEmail', 'Email'],
    ['toIc', 'IC / Passport'], ['toEmergencyContact', 'Emergency contact name'],
    ['toEmergencyPhone', 'Emergency contact phone']
  ];
  for (var i = 0; i < fields.length; i++) {
    var el = document.getElementById(fields[i][0]);
    if (!el || !el.value.trim()) {
      if (errEl) { errEl.textContent = 'Please enter ' + fields[i][1] + '.'; errEl.style.display = 'block'; }
      if (el) el.focus();
      return;
    }
  }
  if (errEl) errEl.style.display = 'none';
  var data = {
    name: document.getElementById('toFullName').value.trim(),
    phone: document.getElementById('toPhone').value.trim(),
    email: document.getElementById('toEmail').value.trim(),
    ic: document.getElementById('toIc').value.trim(),
    emergencyContact: document.getElementById('toEmergencyContact').value.trim(),
    emergencyPhone: document.getElementById('toEmergencyPhone').value.trim()
  };
  var btn = document.getElementById('toSubmitBtn');
  if (btn) { btn.disabled = true; btn.textContent = 'Saving…'; }
  if (!window.google || !google.script || !google.script.run) {
    alert('Backend not configured.');
    if (btn) { btn.disabled = false; btn.textContent = 'Register Trainer'; }
    return;
  }
  google.script.run
    .withSuccessHandler(function () {
      if (btn) { btn.disabled = false; btn.textContent = 'Register Trainer'; }
      document.getElementById('toSuccessMsg').textContent = data.name + ' has been added to the Trainer sheet.';
      document.querySelectorAll('#view-trainer .card, #view-trainer .submit-wrap').forEach(function (el) { el.classList.add('hidden'); });
      document.getElementById('toSuccessCard').classList.add('show');
      if (typeof calixlabRefreshTrainerDropdowns === 'function') calixlabRefreshTrainerDropdowns();
    })
    .withFailureHandler(function (e) {
      if (btn) { btn.disabled = false; btn.textContent = 'Register Trainer'; }
      if (errEl) { errEl.textContent = e.message || 'Could not register trainer.'; errEl.style.display = 'block'; }
    })
    .addTrainer(data);
}
function resetTrainerOnboarding() {
  ['toFullName','toPhone','toEmail','toIc','toEmergencyContact','toEmergencyPhone'].forEach(function (id) {
    var el = document.getElementById(id);
    if (el) el.value = '';
  });
  var errEl = document.getElementById('toFormErr');
  if (errEl) errEl.style.display = 'none';
  document.getElementById('toSuccessCard').classList.remove('show');
  document.querySelectorAll('#view-trainer .card, #view-trainer .submit-wrap').forEach(function (el) { el.classList.remove('hidden'); });
}
document.addEventListener('DOMContentLoaded', function () {
  calixSwitchHubView('onboarding');
  var u = window.CALIXLAB_GAS_EXEC_URL || '';
  if (!u || /YOUR_DEPLOYMENT_ID|PASTE_|REPLACE_/i.test(u)) {
    var bar = document.createElement('div');
    bar.setAttribute('role', 'alert');
    bar.style.cssText = 'background:#3d2a00;color:#ffd48a;padding:10px 14px;font:500 13px/1.4 inherit;text-align:center;border-bottom:1px solid #5c4200';
    bar.textContent = 'Onboarding saves are in local test mode. Set CALIXLAB_GAS_EXEC_URL in config.js (Apps Script /exec URL) for Google Sheets.';
    var nav = document.querySelector('.hub-mode-switcher');
    if (nav && nav.parentNode) nav.parentNode.insertBefore(bar, nav);
  }
});
</script>
"""


def prep_onboard_body(body: str) -> tuple[str, str, str, str]:
    body = re.sub(r'<div class="header">[\s\S]*?</div>\s*', '', body, count=1)
    body = re.sub(r'<!-- MODE SWITCHER -->[\s\S]*?</div>\s*', '', body, count=1)
    script_i = body.rfind("<script>")
    scripts = body[script_i:] if script_i >= 0 else ""
    main = body[:script_i] if script_i >= 0 else body
    new_i = main.find('<div id="newClientForm"')
    pay_i = main.find('<div id="recordPayForm"')
    succ_i = main.find("<!-- SUCCESS SCREENS -->")
    if new_i < 0 or pay_i < 0:
        raise ValueError("Onboarding HTML missing newClientForm or recordPayForm")
    shared = main[:new_i].strip()
    client_block = main[new_i:pay_i].strip()
    pay_block = main[pay_i:succ_i].strip() if succ_i >= 0 else main[pay_i:].strip()
    succ_block = main[succ_i:].strip() if succ_i >= 0 else ""
    m_ok = re.search(r'<div class="success-card" id="successCard">[\s\S]*?</div>\s*', succ_block)
    m_rp = re.search(r'<div class="success-card" id="rpSuccessCard">[\s\S]*?</div>\s*', succ_block)
    client_html = client_block + ("\n" + m_ok.group(0).strip() if m_ok else "")
    payment_html = pay_block + ("\n" + m_rp.group(0).strip() if m_rp else "")
    scripts = re.sub(
        r"function switchMode\(mode\) \{[\s\S]*?window\.scrollTo\(\{top: 0, behavior: 'smooth'\}\);\n\}",
        "",
        scripts,
        count=1,
    )
    return shared, client_html, payment_html, scripts
