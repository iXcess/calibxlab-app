/**
 * Load trainer names from Google Sheet tab "Trainer" (via Apps Script listTrainers).
 */
(function (global) {
  var cache = null;

  function fillSelect(sel, names, placeholder) {
    if (!sel) return;
    var cur = sel.value;
    sel.innerHTML = '';
    var o0 = document.createElement('option');
    o0.value = '';
    o0.textContent = placeholder;
    sel.appendChild(o0);
    names.forEach(function (n) {
      var o = document.createElement('option');
      o.value = n;
      o.textContent = n;
      if (n === cur) o.selected = true;
      sel.appendChild(o);
    });
  }

  global.calixlabGetTrainers = function (refresh) {
    if (cache && !refresh) return Promise.resolve(cache.slice());
    if (!global.google || !global.google.script || !global.google.script.run) {
      return Promise.reject(new Error('Trainer list unavailable — check config.js'));
    }
    return new Promise(function (resolve, reject) {
      global.google.script.run
        .withSuccessHandler(function (list) {
          cache = list || [];
          resolve(cache.slice());
        })
        .withFailureHandler(reject)
        .listTrainers();
    });
  };

  global.calixlabRefreshTrainerDropdowns = function () {
    return global.calixlabGetTrainers(true).then(function (names) {
      fillSelect(document.getElementById('trainerSelect'), names, '— Select Trainer —');
      fillSelect(document.getElementById('trainerSel'), names, '— Select your name —');
      if (typeof global.calixlabOnTrainersLoaded === 'function') {
        global.calixlabOnTrainersLoaded(names);
      }
      return names;
    });
  };

  document.addEventListener('DOMContentLoaded', function () {
    global.calixlabRefreshTrainerDropdowns().catch(function (err) {
      console.warn('[Calixlab] Could not load trainers:', err.message || err);
    });
  });
})(typeof window !== 'undefined' ? window : this);
