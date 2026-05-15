/**
 * GitHub Pages → Apps Script web app.
 * Reads: GET. Writes (onboard, payment, trainers): POST (large payloads fail as GET).
 */
(function () {
  function gasUrl() {
    var u = window.CALIXLAB_GAS_EXEC_URL || '';
    if (!u || /YOUR_DEPLOYMENT_ID|PASTE_|REPLACE_/i.test(u)) return '';
    return u.replace(/\/$/, '');
  }

  function parseResponse(res) {
    if (!res.ok) throw new Error('Server returned ' + res.status);
    return res.json().then(function (body) {
      if (!body || body.ok === false) {
        throw new Error((body && body.error) || 'Request failed');
      }
      return body.result;
    });
  }

  function callGasGet(url, query) {
    return fetch(url + '?' + query, { method: 'GET', mode: 'cors' }).then(parseResponse);
  }

  function callGasPost(url, action, payload) {
    var body = JSON.stringify({ action: action, payload: payload == null ? {} : payload });
    return fetch(url, {
      method: 'POST',
      mode: 'cors',
      redirect: 'follow',
      headers: { 'Content-Type': 'text/plain;charset=utf-8' },
      body: body
    }).then(parseResponse);
  }

  function callGas(action, payload) {
    var url = gasUrl();
    if (!url) {
      return Promise.reject(new Error(
        'Backend not configured. Set CALIXLAB_GAS_EXEC_URL in config.js.'
      ));
    }

    if (action === 'lookupClient') {
      var q = encodeURIComponent(String(payload == null ? '' : payload));
      return callGasGet(url, 'action=lookupClient&q=' + q);
    }

    if (action === 'listTrainers') {
      return callGasGet(url, 'action=listTrainers');
    }

    return callGasPost(url, action, payload);
  }

  function createRunner() {
    var state = { ok: null, bad: null };
    var runner = {
      withSuccessHandler: function (fn) {
        state.ok = fn;
        return runner;
      },
      withFailureHandler: function (fn) {
        state.bad = fn;
        return runner;
      }
    };

    ['lookupClient', 'listTrainers', 'addTrainer', 'deleteTrainer', 'onboardClient', 'recordPayment', 'recordSessionLog', 'generateInvoice', 'previewInvoiceHtml'].forEach(function (action) {
      runner[action] = function (arg) {
        callGas(action, arg)
          .then(function (result) {
            if (state.ok) state.ok(result);
          })
          .catch(function (err) {
            if (state.bad) state.bad(err);
            else console.error('[Calixlab]', action, err);
          });
        return runner;
      };
    });

    return runner;
  }

  if (!gasUrl()) return;

  window.google = window.google || {};
  window.google.script = window.google.script || {};
  Object.defineProperty(window.google.script, 'run', {
    get: function () {
      return createRunner();
    },
    configurable: true
  });
  console.info('[Calixlab] Apps Script backend:', gasUrl());
})();
