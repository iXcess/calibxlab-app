/**
 * Invoice download sheet — shown after onboarding or payment submit (mobile-friendly).
 */
(function (global) {
  var state = {
    pdfBase64: null,
    fileName: 'invoice.pdf',
    blobUrl: null
  };

  function $(id) { return document.getElementById(id); }

  function revokeBlob() {
    if (state.blobUrl) {
      try { URL.revokeObjectURL(state.blobUrl); } catch (e) { /* ignore */ }
      state.blobUrl = null;
    }
  }

  function downloadPdfToDevice(b64, fileName) {
    if (!b64) return false;
    var bin = atob(b64);
    var bytes = new Uint8Array(bin.length);
    for (var i = 0; i < bin.length; i++) bytes[i] = bin.charCodeAt(i);
    var blob = new Blob([bytes], { type: 'application/pdf' });
    revokeBlob();
    state.blobUrl = URL.createObjectURL(blob);
    state.fileName = fileName || 'invoice.pdf';

    var a = document.createElement('a');
    a.href = state.blobUrl;
    a.download = state.fileName;
    a.rel = 'noopener';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);

    var isIos = /iPad|iPhone|iPod/.test(navigator.userAgent) && !window.MSStream;
    if (isIos) {
      setTimeout(function () {
        window.open(state.blobUrl, '_blank');
      }, 400);
    }
    return true;
  }

  function setLoading(on, msg) {
    var load = $('invoiceModalLoading');
    var dl = $('invoiceModalDownload');
    if (load) {
      load.hidden = !on;
      load.textContent = msg || 'Preparing your invoice…';
    }
    if (dl) dl.disabled = !!on;
  }

  function setReady(invoiceNumber) {
    setLoading(false);
    var dl = $('invoiceModalDownload');
    var sub = $('invoiceModalSub');
    if (dl) dl.disabled = false;
    if (sub && invoiceNumber) {
      sub.textContent = invoiceNumber + ' is ready. Tap below to save it on your phone.';
    }
  }

  function setError(msg) {
    setLoading(false);
    var sub = $('invoiceModalSub');
    var dl = $('invoiceModalDownload');
    if (sub) sub.textContent = msg || 'Could not create invoice. Try again later.';
    if (dl) {
      dl.disabled = true;
      dl.textContent = 'Unavailable';
    }
  }

  function hideModal() {
    var modal = $('invoiceModal');
    if (modal) {
      modal.classList.remove('open');
      modal.setAttribute('aria-hidden', 'true');
    }
    document.body.style.overflow = '';
  }

  function showModal(title, subtitle) {
    var modal = $('invoiceModal');
    if (!modal) return;
    $('invoiceModalTitle').textContent = title || 'Invoice ready';
    $('invoiceModalSub').textContent = subtitle || 'We are preparing your PDF…';
    $('invoiceModalDownload').disabled = true;
    $('invoiceModalDownload').textContent = 'Download invoice PDF';
    modal.classList.add('open');
    modal.setAttribute('aria-hidden', 'false');
    document.body.style.overflow = 'hidden';
  }

  function generatePayload(opts) {
    var payload = {
      type: opts.type || 'onboarding',
      sheetRowIndex: opts.row,
      saveToDrive: true
    };
    if (opts.paymentAmount != null) payload.paymentAmount = opts.paymentAmount;
    return payload;
  }

  /**
   * Call right after successful onboarding or payment submit.
   */
  function showAfterSubmit(opts) {
    opts = opts || {};
    if (!opts.row || opts.row < 2) {
      return;
    }

    state.pdfBase64 = null;
    revokeBlob();

    var title = opts.type === 'payment' ? 'Payment receipt ready' : 'Invoice ready';
    var sub = opts.clientName
      ? 'Creating PDF for ' + opts.clientName + '…'
      : 'Creating your PDF…';
    showModal(title, sub);
    setLoading(true);

    if (!window.google || !google.script || !google.script.run) {
      setError('Backend not configured. Set CALIXLAB_GAS_EXEC_URL in config.js.');
      return;
    }

    google.script.run
      .withSuccessHandler(function (res) {
        if (!res || !res.pdfBase64) {
          setError('Invoice could not be generated. Redeploy Apps Script with Invoice.gs.');
          return;
        }
        state.pdfBase64 = res.pdfBase64;
        state.fileName = (res.invoiceNumber || 'invoice') + '.pdf';
        setReady(res.invoiceNumber);
      })
      .withFailureHandler(function (err) {
        setError((err && err.message) || 'Invoice failed. Check connection and try again.');
      })
      .generateInvoice(generatePayload(opts));
  }

  function bindUi() {
    var modal = $('invoiceModal');
    if (!modal || modal.dataset.bound) return;
    modal.dataset.bound = '1';

    $('invoiceModalBackdrop').addEventListener('click', hideModal);
    $('invoiceModalClose').addEventListener('click', hideModal);
    $('invoiceModalLater').addEventListener('click', hideModal);

    $('invoiceModalDownload').addEventListener('click', function () {
      if (!state.pdfBase64) return;
      var ok = downloadPdfToDevice(state.pdfBase64, state.fileName);
      if (ok) {
        $('invoiceModalSub').textContent = 'Download started. Check your Downloads or Files app.';
        $('invoiceModalDownload').textContent = 'Download again';
      }
    });
  }

  function init() {
    bindUi();
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }

  /**
   * Inline invoice download on a success card (e.g. Payment Recorded).
   */
  function showInlineDownload(elementId, opts) {
    var el = $(elementId);
    if (!el || !opts.row || opts.row < 2) return;

    state.pdfBase64 = null;
    revokeBlob();
    el.textContent = 'Preparing your invoice…';

    if (!window.google || !google.script || !google.script.run) {
      el.textContent = 'Invoice unavailable — backend not configured.';
      return;
    }

    google.script.run
      .withSuccessHandler(function (res) {
        if (!res || !res.pdfBase64) {
          el.textContent = 'Invoice could not be generated. Redeploy Apps Script with Invoice.gs.';
          return;
        }
        state.pdfBase64 = res.pdfBase64;
        state.fileName = (res.invoiceNumber || 'invoice') + '.pdf';
        var num = res.invoiceNumber || 'Invoice';
        el.innerHTML = '';
        var btn = document.createElement('button');
        btn.type = 'button';
        btn.className = 'success-invoice-download';
        btn.textContent = 'Download ' + num + ' (PDF)';
        btn.addEventListener('click', function () {
          downloadPdfToDevice(state.pdfBase64, state.fileName);
          btn.textContent = 'Download again';
        });
        el.appendChild(btn);
        var hint = document.createElement('span');
        hint.className = 'success-invoice-hint';
        hint.textContent = 'Tap to save the invoice on your phone.';
        el.appendChild(hint);
      })
      .withFailureHandler(function (err) {
        el.textContent = (err && err.message) || 'Invoice could not be generated.';
      })
      .generateInvoice(generatePayload(opts));
  }

  global.CalixlabInvoiceModal = {
    showAfterSubmit: showAfterSubmit,
    showInlineDownload: showInlineDownload,
    hide: hideModal,
    downloadPdfToDevice: downloadPdfToDevice
  };
})(typeof window !== 'undefined' ? window : this);
