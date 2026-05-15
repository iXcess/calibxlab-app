# Hub navigation constants and helpers (imported by build_merge.py)
import re

HUB_NAV_HTML = """
<nav class="hub-mode-switcher" role="navigation" aria-label="Main">
  <button type="button" class="mode-btn active" id="hubNavOnboarding" onclick="calixSwitchHubView('onboarding')">Onboarding</button>
  <button type="button" class="mode-btn" id="hubNavPayment" onclick="calixSwitchHubView('payment')" aria-label="Payment Record">Pay</button>
  <button type="button" class="mode-btn" id="hubNavSession" onclick="calixSwitchHubView('session')" aria-label="Session Log">Log</button>
  <button type="button" class="mode-btn" id="hubNavAdmin" onclick="calixSwitchHubView('admin')">Admin</button>
</nav>
<div id="hub-header" class="header">
  <div class="logo">
    <img class="calix-logo-full" src="assets/calixlab-logo-header.png" alt="Cali Lab" width="182" height="36"/>
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
  position: sticky; top: env(safe-area-inset-top, 0); z-index: 2000;
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
.admin-panel-wrap { max-width: 560px; margin: 0 auto; }
.admin-panel-wrap.hidden { display: none !important; }
.admin-signout {
  display: block; width: 100%; max-width: 560px; margin: 0 auto 14px;
  text-align: right; font-size: 13px; color: #185FA5; font-weight: 600;
  background: none; border: none; cursor: pointer; font-family: inherit;
}
.admin-msg {
  font-size: 13px; margin-top: 10px; padding: 10px 12px; border-radius: 10px; display: none;
}
.admin-msg.show { display: block; }
.admin-msg.ok { background: #EAF3DE; color: #27500A; border: 1px solid #C0DD97; }
.admin-msg.err { background: #FCEBEB; color: #A32D2D; border: 1px solid #F09595; }
.payroll-results { display: flex; flex-direction: column; gap: 14px; margin-top: 14px; }
.payroll-grand .rp-val { font-size: 22px; }
.payroll-trainer-card .section-title { margin-bottom: 12px; }
.onboard-inner-switcher {
  display: flex; max-width: 560px; width: calc(100% - 32px); margin: 0 auto 16px;
  background: white; border-radius: 12px; padding: 4px;
  border: 1px solid #e8e8e8; box-shadow: 0 1px 4px rgba(0,0,0,0.06);
}
.onboard-inner-switcher .mode-btn {
  flex: 1; min-width: 0; padding: 10px 6px; border: none; border-radius: 9px;
  font-size: 12px; font-weight: 600; cursor: pointer; font-family: inherit;
  background: transparent; color: #888; transition: all 0.2s;
}
@media (min-width: 420px) {
  .onboard-inner-switcher .mode-btn { font-size: 13px; padding: 10px 8px; }
}
.onboard-inner-switcher .mode-btn.active {
  background: #185FA5; color: white;
  box-shadow: 0 1px 4px rgba(0,0,0,0.08);
}
.onboard-inner-switcher .mode-btn:focus-visible { outline: 2px solid #185FA5; outline-offset: 2px; }
@media (max-width: 380px) {
  #onboardNavTrainer { font-size: 11px; }
}
"""

ONBOARD_INNER_SWITCHER_HTML = """
<div class="onboard-inner-switcher" role="tablist" aria-label="Onboarding mode">
  <button type="button" class="mode-btn active" id="onboardNavClient" onclick="calixSwitchOnboardMode('client')">New Client</button>
  <button type="button" class="mode-btn" id="onboardNavTrainer" onclick="calixSwitchOnboardMode('trainer')">Register Trainer</button>
</div>
"""

ADMIN_PANEL_HTML = """
<div id="adminLoginPanel" class="admin-panel-wrap">
  <div class="card">
    <div class="section-title">
      <svg class="section-icon" viewBox="0 0 24 24" fill="currentColor"><path d="M12 1L3 5v6c0 5.55 3.84 10.74 9 12 5.16-1.26 9-6.45 9-12V5l-9-4zm0 10.99h7c-.53 4.12-3.28 7.79-7 8.94V12H5V6.3l7-3.11v8.8z"/></svg>
      Admin sign in
    </div>
    <div class="field">
      <label>Username <span class="req">*</span></label>
      <input type="text" id="adminUser" autocomplete="username" placeholder="Username"/>
    </div>
    <div class="field">
      <label>Password <span class="req">*</span></label>
      <input type="password" id="adminPass" autocomplete="current-password" placeholder="Password"/>
    </div>
    <div class="ferr" id="adminLoginErr" style="display:none;margin-top:8px;"></div>
  </div>
  <div class="submit-wrap">
    <button type="button" class="submit-btn" id="adminLoginBtn" onclick="adminLogin()">Sign in</button>
  </div>
</div>

<div id="adminToolsPanel" class="admin-panel-wrap hidden">
  <button type="button" class="admin-signout" onclick="adminSignOut()">Sign out</button>

  <div class="card">
    <div class="section-title red">
      <svg class="section-icon" viewBox="0 0 24 24" fill="currentColor"><path d="M6 19c0 1.1.9 2 2 2h8c1.1 0 2-.9 2-2V7H6v12zM19 4h-3.5l-1-1h-5l-1 1H5v2h14V4z"/></svg>
      Remove trainer
    </div>
    <p class="hint" style="margin-bottom:12px;">Select a trainer from the Google Sheet list. Removal deletes that row permanently.</p>
    <div class="field">
      <label>Trainer <span class="req">*</span></label>
      <select id="adminTrainerSelect">
        <option value="">— Select trainer —</option>
      </select>
    </div>
    <div class="admin-msg" id="adminRemoveMsg"></div>
  </div>
  <div class="submit-wrap" style="margin-top:-4px;margin-bottom:14px;">
    <button type="button" class="submit-btn" id="adminRemoveBtn" onclick="adminRemoveTrainer()" style="background:#A32D2D;">Remove trainer</button>
  </div>

  <div class="card">
    <div class="section-title">
      <svg class="section-icon" viewBox="0 0 24 24" fill="currentColor"><path d="M11.8 10.9c-2.27-.59-3-1.2-3-2.15 0-1.09 1.01-1.85 2.7-1.85 1.78 0 2.44.85 2.5 2.1h2.21c-.07-1.72-1.12-3.3-3.21-3.81V3h-3v2.16C9.31 5.92 8 7.27 8 9.14c0 2.02 1.55 3.15 4.15 3.85 2.6.7 3.15 1.46 3.15 2.49 0 1.12-1.02 1.92-2.75 1.92-2.05 0-2.82-.92-2.95-2.1H5.1c.12 2.19 1.76 3.42 3.95 3.83V21h3v-2.15c2.39-.49 4-1.86 4-4.12 0-2.09-1.44-3.24-4.25-3.83z"/></svg>
      Payroll summary
    </div>
    <p class="hint" style="margin-bottom:12px;">Earnings = sessions logged × client rate/session × lead multiplier (Calixlab 0.60, Own 0.70).</p>
    <div class="row2">
      <div class="field">
        <label>From <span class="req">*</span></label>
        <input type="date" id="payrollFrom"/>
      </div>
      <div class="field">
        <label>To <span class="req">*</span></label>
        <input type="date" id="payrollTo"/>
      </div>
    </div>
    <div class="admin-msg" id="adminPayrollMsg"></div>
  </div>
  <div class="submit-wrap" style="margin-bottom:14px;">
    <button type="button" class="submit-btn" id="adminPayrollBtn" onclick="adminGeneratePayroll()">Generate summary</button>
  </div>
  <div id="payrollResults" class="payroll-results"></div>
</div>
"""


ADMIN_JS = """
<script>
function adminIsAuthed() {
  return sessionStorage.getItem('calixAdminAuthed') === '1';
}
function adminUpdateHubHeader() {
  if (calixHubView !== 'admin') return;
  var ht = document.getElementById('hubTitle');
  var hs = document.getElementById('hubSub');
  if (!ht || !hs) return;
  if (adminIsAuthed()) {
    ht.textContent = 'Admin';
    hs.textContent = 'Trainer management & payroll';
  } else {
    ht.textContent = 'Admin';
    hs.textContent = 'Sign in to continue';
  }
}
function adminRefreshPanels() {
  var login = document.getElementById('adminLoginPanel');
  var tools = document.getElementById('adminToolsPanel');
  if (!login || !tools) return;
  if (adminIsAuthed()) {
    login.classList.add('hidden');
    tools.classList.remove('hidden');
    adminLoadTrainerSelect();
    adminInitPayrollDates();
  } else {
    login.classList.remove('hidden');
    tools.classList.add('hidden');
  }
  adminUpdateHubHeader();
}
function adminLogin() {
  var err = document.getElementById('adminLoginErr');
  var user = (document.getElementById('adminUser').value || '').trim();
  var pass = document.getElementById('adminPass').value || '';
  if (user !== 'admin' || pass !== 'admin') {
    if (err) { err.textContent = 'Invalid username or password.'; err.style.display = 'block'; }
    return;
  }
  if (err) err.style.display = 'none';
  sessionStorage.setItem('calixAdminAuthed', '1');
  document.getElementById('adminPass').value = '';
  adminRefreshPanels();
}
function adminSignOut() {
  sessionStorage.removeItem('calixAdminAuthed');
  adminRefreshPanels();
}
function adminShowMsg(el, text, ok) {
  if (!el) return;
  el.textContent = text;
  el.className = 'admin-msg show ' + (ok ? 'ok' : 'err');
}
function adminLoadTrainerSelect() {
  var sel = document.getElementById('adminTrainerSelect');
  if (!sel) return;
  if (!window.google || !google.script || !google.script.run) {
    sel.innerHTML = '<option value="">— Backend not configured —</option>';
    return;
  }
  google.script.run
    .withSuccessHandler(function (names) {
      var cur = sel.value;
      sel.innerHTML = '<option value="">— Select trainer —</option>';
      (names || []).forEach(function (n) {
        var o = document.createElement('option');
        o.value = n;
        o.textContent = n;
        sel.appendChild(o);
      });
      if (cur && names && names.indexOf(cur) >= 0) sel.value = cur;
    })
    .withFailureHandler(function (e) {
      sel.innerHTML = '<option value="">— Could not load trainers —</option>';
      console.warn('[Admin]', e);
    })
    .listTrainers();
}
function adminRemoveTrainer() {
  var sel = document.getElementById('adminTrainerSelect');
  var msg = document.getElementById('adminRemoveMsg');
  var name = sel ? sel.value.trim() : '';
  if (!name) {
    adminShowMsg(msg, 'Please select a trainer from the list.', false);
    return;
  }
  if (!confirm('Remove "' + name + '" from the Trainer sheet? This cannot be undone.')) return;
  var btn = document.getElementById('adminRemoveBtn');
  if (btn) { btn.disabled = true; btn.textContent = 'Removing…'; }
  google.script.run
    .withSuccessHandler(function () {
      if (btn) { btn.disabled = false; btn.textContent = 'Remove trainer'; }
      adminShowMsg(msg, name + ' was removed from the Trainer sheet.', true);
      if (sel) sel.value = '';
      adminLoadTrainerSelect();
      if (typeof calixlabRefreshTrainerDropdowns === 'function') calixlabRefreshTrainerDropdowns();
    })
    .withFailureHandler(function (e) {
      if (btn) { btn.disabled = false; btn.textContent = 'Remove trainer'; }
      adminShowMsg(msg, e.message || 'Could not remove trainer.', false);
    })
    .deleteTrainer({ name: name });
}
function adminInitPayrollDates() {
  var from = document.getElementById('payrollFrom');
  var to = document.getElementById('payrollTo');
  if (!from || !to || from.value) return;
  var end = new Date();
  var start = new Date();
  start.setDate(start.getDate() - 30);
  to.value = end.toISOString().slice(0, 10);
  from.value = start.toISOString().slice(0, 10);
}
function adminFormatRm(n) {
  return 'RM ' + Number(n || 0).toLocaleString('en-MY', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
}
function adminRenderPayroll(data) {
  var box = document.getElementById('payrollResults');
  if (!box) return;
  box.innerHTML = '';
  if (!data || !data.trainers || !data.trainers.length) {
    box.innerHTML = '<div class="card"><p class="hint">No trainers found for this period.</p></div>';
    return;
  }
  var grand = document.createElement('div');
  grand.className = 'card payroll-grand';
  grand.innerHTML =
    '<div class="section-title">All trainers — ' + data.startDate + ' to ' + data.endDate + '</div>' +
    '<div class="rp-summary">' +
    '<div class="rp-stat"><div class="rp-val">' + (data.grandTotalSessions || 0) + '</div><div class="rp-lbl">Total sessions</div></div>' +
    '<div class="rp-stat"><div class="rp-val green">' + adminFormatRm(data.grandTotalEarnings) + '</div><div class="rp-lbl">Total earnings</div></div>' +
    '</div>';
  box.appendChild(grand);
  data.trainers.forEach(function (t) {
    var card = document.createElement('div');
    card.className = 'card payroll-trainer-card';
    card.innerHTML =
      '<div class="section-title">' + (t.name || '—') + '</div>' +
      '<div class="rp-summary">' +
      '<div class="rp-stat"><div class="rp-val">' + (t.sessionCount || 0) + '</div><div class="rp-lbl">Sessions</div></div>' +
      '<div class="rp-stat"><div class="rp-val green">' + adminFormatRm(t.totalEarnings) + '</div><div class="rp-lbl">Earnings</div></div>' +
      '</div>';
    box.appendChild(card);
  });
}
function adminGeneratePayroll() {
  var from = document.getElementById('payrollFrom');
  var to = document.getElementById('payrollTo');
  var msg = document.getElementById('adminPayrollMsg');
  var btn = document.getElementById('adminPayrollBtn');
  var startDate = from ? from.value : '';
  var endDate = to ? to.value : '';
  if (!startDate || !endDate) {
    adminShowMsg(msg, 'Please select both dates.', false);
    return;
  }
  if (startDate > endDate) {
    adminShowMsg(msg, 'From date must be on or before To date.', false);
    return;
  }
  if (msg) { msg.className = 'admin-msg'; msg.textContent = ''; }
  if (btn) { btn.disabled = true; btn.textContent = 'Generating…'; }
  google.script.run
    .withSuccessHandler(function (data) {
      if (btn) { btn.disabled = false; btn.textContent = 'Generate summary'; }
      adminRenderPayroll(data);
    })
    .withFailureHandler(function (e) {
      if (btn) { btn.disabled = false; btn.textContent = 'Generate summary'; }
      adminShowMsg(msg, e.message || 'Could not generate payroll.', false);
      document.getElementById('payrollResults').innerHTML = '';
    })
    .getPayrollSummary({ startDate: startDate, endDate: endDate });
}
var _calixSwitchHubViewOrig = calixSwitchHubView;
calixSwitchHubView = function (view) {
  _calixSwitchHubViewOrig(view);
  if (view === 'admin') adminRefreshPanels();
};
</script>
"""

HUB_JS = """
<script>
var calixHubView = 'onboarding';
var calixOnboardMode = 'client';
var HUB_HEADERS = {
  onboarding: ['Client Onboarding', 'New client registration'],
  payment: ['Payment Record', 'Record instalment payment'],
  session: ['Session Log', 'Submit immediately after every session.'],
  admin: ['Admin', '']
};
function calixSwitchOnboardMode(mode) {
  calixOnboardMode = mode;
  var clientSec = document.getElementById('onboardClientSection');
  var trainerSec = document.getElementById('onboardTrainerSection');
  var innerNav = document.querySelector('.onboard-inner-switcher');
  if (clientSec) clientSec.classList.toggle('hidden', mode !== 'client');
  if (trainerSec) trainerSec.classList.toggle('hidden', mode !== 'trainer');
  if (innerNav) innerNav.classList.toggle('hidden', calixHubView !== 'onboarding');
  var nc = document.getElementById('onboardNavClient');
  var nt = document.getElementById('onboardNavTrainer');
  if (nc) nc.classList.toggle('active', mode === 'client');
  if (nt) nt.classList.toggle('active', mode === 'trainer');
  if (calixHubView === 'onboarding') {
    var ht = document.getElementById('hubTitle');
    var hs = document.getElementById('hubSub');
    if (mode === 'trainer') {
      if (ht) ht.textContent = 'Trainer Onboarding';
      if (hs) hs.textContent = 'Register a new trainer';
    } else {
      if (ht) ht.textContent = HUB_HEADERS.onboarding[0];
      if (hs) hs.textContent = HUB_HEADERS.onboarding[1];
    }
  }
  window.scrollTo({ top: 0, behavior: 'auto' });
}
function calixSwitchHubView(view) {
  calixHubView = view;
  ['onboarding','payment','session','admin'].forEach(function (v) {
    var el = document.getElementById(v === 'session' ? 'session-panel' : 'view-' + v);
    if (el) el.classList.toggle('active', v === view);
  });
  var navMap = { onboarding: 'hubNavOnboarding', payment: 'hubNavPayment', session: 'hubNavSession', admin: 'hubNavAdmin' };
  Object.keys(navMap).forEach(function (k) {
    var btn = document.getElementById(navMap[k]);
    if (btn) btn.classList.toggle('active', k === view);
  });
  var payForm = document.getElementById('recordPayForm');
  if (payForm) payForm.classList.toggle('hidden', view !== 'payment');
  if (typeof hideProgress === 'function') hideProgress();
  var hubHdr = document.getElementById('hub-header');
  if (hubHdr) {
    hubHdr.classList.remove('hidden');
    if (view === 'onboarding') {
      calixSwitchOnboardMode(calixOnboardMode);
    } else {
      var t = HUB_HEADERS[view] || ['Cali Lab', ''];
      var ht = document.getElementById('hubTitle');
      var hs = document.getElementById('hubSub');
      if (ht) ht.textContent = t[0];
      if (hs) hs.textContent = t[1];
      var innerNav = document.querySelector('.onboard-inner-switcher');
      if (innerNav) innerNav.classList.toggle('hidden', view !== 'onboarding');
    }
  }
  if (typeof currentMode !== 'undefined') currentMode = view === 'payment' ? 'record' : 'new';
  var eb = document.getElementById('error-banner');
  if (eb) eb.classList.remove('show');
  if (view === 'payment') {
    var sc = document.getElementById('successCard');
    var rpc = document.getElementById('rpSuccessCard');
    if (sc) sc.classList.remove('show');
    if (rpc) rpc.classList.remove('show');
  }
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
      document.querySelectorAll('#onboardTrainerSection .card, #onboardTrainerSection .submit-wrap').forEach(function (el) { el.classList.add('hidden'); });
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
  document.querySelectorAll('#onboardTrainerSection .card, #onboardTrainerSection .submit-wrap').forEach(function (el) { el.classList.remove('hidden'); });
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
    def find_div_end(src: str, start: int) -> int:
        i = start
        depth = 0
        while i < len(src):
            next_open = src.find("<div", i)
            next_close = src.find("</div>", i)
            if next_close < 0:
                break
            if next_open != -1 and next_open < next_close:
                depth += 1
                gt = src.find(">", next_open)
                if gt < 0:
                    break
                i = gt + 1
                continue
            depth -= 1
            i = next_close + len("</div>")
            if depth == 0:
                return i
        raise ValueError("Could not find matching </div> while preparing onboarding body.")

    header_i = body.find('<div class="header">')
    if header_i >= 0:
        header_end = find_div_end(body, header_i)
        body = body[:header_i] + body[header_end:]

    mode_i = body.find('<div class="mode-switcher">')
    if mode_i >= 0:
        mode_end = find_div_end(body, mode_i)
        body = body[:mode_i] + body[mode_end:]

    script_i = body.rfind("<script>")
    scripts = body[script_i:] if script_i >= 0 else ""
    main = body[:script_i] if script_i >= 0 else body
    new_i = main.find('<div id="newClientForm"')
    pay_i = main.find('<div id="recordPayForm"')
    succ_i = main.find("<!-- SUCCESS SCREENS -->")
    if new_i < 0 or pay_i < 0:
        raise ValueError("Onboarding HTML missing newClientForm or recordPayForm")

    new_end = find_div_end(main, new_i)
    pay_end = find_div_end(main, pay_i)
    shared = main[:new_i].strip()
    client_block = main[new_i:new_end].strip()
    pay_block = main[pay_i:pay_end].strip()
    succ_block = main[succ_i:].strip() if succ_i >= 0 else ""

    def extract_success_block(src: str, marker: str) -> str:
        start = src.find(marker)
        if start < 0:
            return ""
        end = find_div_end(src, start)
        return src[start:end].strip()

    success_client = extract_success_block(succ_block, '<div class="success-card" id="successCard">')
    success_payment = extract_success_block(succ_block, '<div class="success-card" id="rpSuccessCard">')
    pay_block = re.sub(
        r'<div id="recordPayForm"\s+class="hidden"',
        '<div id="recordPayForm"',
        pay_block,
        count=1,
    )
    client_html = client_block + ("\n" + success_client if success_client else "")
    payment_html = pay_block + ("\n" + success_payment if success_payment else "")
    scripts = re.sub(
        r"function switchMode\(mode\) \{[\s\S]*?window\.scrollTo\(\{top: 0, behavior: 'smooth'\}\);\n\}",
        "",
        scripts,
        count=1,
    )
    return shared, client_html, payment_html, scripts
