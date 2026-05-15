/**
 * GitHub Pages: call Apps Script web app via GET (POST redirects drop the body).
 */
(function () {
  /** Entire JSON body in URL; images should be pre-compressed via image-compress.js */
  var MAX_GET_PAYLOAD = 200000;

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

  function callGas(action, payload) {
    var url = gasUrl();
    if (!url) {
      return Promise.reject(new Error(
        'Backend not configured. Set CALIXLAB_GAS_EXEC_URL in config.js.'
      ));
    }

    if (action === 'lookupClient') {
      var q = encodeURIComponent(String(payload == null ? '' : payload));
      return fetch(url + '?action=lookupClient&q=' + q, { method: 'GET', mode: 'cors' })
        .then(parseResponse);
    }

    var json = JSON.stringify(payload == null ? {} : payload);
    if (json.length > MAX_GET_PAYLOAD) {
      return Promise.reject(new Error(
        'Form data is too large for this connection (receipt/signature). Try smaller images or contact support.'
      ));
    }
    var u = url + '?action=' + encodeURIComponent(action) +
      '&payload=' + encodeURIComponent(json);
    return fetch(u, { method: 'GET', mode: 'cors' }).then(parseResponse);
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

    ['lookupClient', 'onboardClient', 'recordPayment'].forEach(function (action) {
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
  console.info('[Calixlab] Apps Script backend (GET):', gasUrl());
})();
