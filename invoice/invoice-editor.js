/**
 * Editable invoice preview + load from sheet / URL / generate PDF via Apps Script.
 */
(function () {
  var $ = function (id) { return document.getElementById(id); };
  var statusEl = $('status');

  function setStatus(msg, isErr) {
    if (!statusEl) return;
    statusEl.textContent = msg || '';
    statusEl.className = 'status' + (isErr ? ' err' : '');
  }

  function fmtMoney(n) {
    var v = parseFloat(String(n).replace(/,/g, '')) || 0;
    return 'MYR' + v.toLocaleString('en-MY', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
  }

  function fmtNum(n) {
    return (parseFloat(String(n).replace(/,/g, '')) || 0).toLocaleString('en-MY', {
      minimumFractionDigits: 2,
      maximumFractionDigits: 2
    });
  }

  function todayMyr() {
    return new Date().toLocaleDateString('en-MY', { day: 'numeric', month: 'short', year: 'numeric' });
  }

  function contactLine() {
    var parts = [];
    if ($('fPhone').value) parts.push('Tel: ' + $('fPhone').value);
    if ($('fEmail').value) parts.push($('fEmail').value);
    if ($('fIc').value) parts.push('IC: ' + $('fIc').value);
    return parts.join(' · ');
  }

  function syncFormToPreview() {
    $('pName').textContent = $('fName').value;
    $('pContact').textContent = contactLine();
    $('pInvNum').textContent = $('fInvNum').value;
    $('pInvDate').textContent = $('fInvDate').value;
    $('pDueDate').textContent = $('fDueDate').value;
    $('pTerms').textContent = $('fTerms').value;
    $('pDesc').textContent = $('fDesc').value;
    $('pQty').textContent = $('fQty').value;
    $('pRate').textContent = $('fRate').value;
    $('pAmount').textContent = $('fAmount').value;
    recalcTotals();
  }

  function recalcTotals() {
    var amt = parseFloat(String($('fAmount').value).replace(/,/g, '')) || 0;
    var paid = parseFloat(String($('fPaid').value).replace(/,/g, '')) || 0;
    var bal = Math.max(0, amt - paid);
    $('pSub').textContent = fmtNum(amt);
    $('pTotal').textContent = fmtMoney(amt);
    $('pPaid').textContent = paid > 0 ? '(-) ' + fmtNum(paid) : '(-) 0.00';
    $('pBalance').textContent = fmtMoney(bal);
    $('pBal2').textContent = fmtMoney(bal);
  }

  function applyData(d) {
    if (!d) return;
    $('fInvNum').value = d.invoiceNumber || $('fInvNum').value;
    $('fInvDate').value = d.invoiceDate || todayMyr();
    $('fDueDate').value = d.dueDate || $('fInvDate').value;
    $('fTerms').value = d.terms || 'Due on Receipt';
    $('fName').value = d.billName || '';
    $('fPhone').value = d.billPhone || '';
    $('fEmail').value = d.billEmail || '';
    $('fIc').value = d.billIc || '';
    $('fDesc').value = d.lineDescription || '';
    $('fQty').value = d.lineQty || '1';
    $('fRate').value = d.lineRate || '';
    $('fAmount').value = d.lineAmount || '';
    var paidMatch = String(d.paymentMade || '').replace(/[^\d.]/g, '');
    $('fPaid').value = paidMatch || '';
    syncFormToPreview();
  }

  function loadFromRow(rowIndex) {
    if (!window.google || !google.script || !google.script.run) {
      setStatus('Set CALIXLAB_GAS_EXEC_URL in config.js to load clients.', true);
      return;
    }
    setStatus('Loading client row ' + rowIndex + '…');
    google.script.run
      .withSuccessHandler(function (res) {
        if (!res || !res.html) {
          setStatus('Could not build invoice for row ' + rowIndex, true);
          return;
        }
        openPreviewHtml(res.html);
        $('fInvNum').value = res.invoiceNumber || '';
        setStatus('Loaded invoice for row ' + rowIndex);
      })
      .withFailureHandler(function (e) {
        setStatus(e.message || 'Load failed', true);
      })
      .previewInvoiceHtml({ sheetRowIndex: parseInt(rowIndex, 10), type: 'onboarding' });
  }

  function openPreviewHtml(html) {
    var wrap = $('invoicePreview');
    if (!wrap) return;
    var doc = new DOMParser().parseFromString(html, 'text/html');
    var body = doc.body;
    if (body) wrap.innerHTML = body.innerHTML;
  }

  function generatePdf() {
    var row = parseInt($('loadRow').value, 10);
    var payload = {
      type: 'onboarding',
      saveToDrive: true
    };
    if (row >= 2) payload.sheetRowIndex = row;
    else {
      payload.clientData = {
        fullName: $('fName').value,
        phone: $('fPhone').value,
        email: $('fEmail').value,
        ic: $('fIc').value,
        trainerName: '',
        packageType: $('fDesc').value.split('·')[0].trim(),
        sessions: $('fQty').value,
        ratePerSession: $('fRate').value,
        totalPackageValue: $('fAmount').value,
        amountPaid: $('fPaid').value
      };
    }
    if ($('fInvNum').value) payload.invoiceNumber = $('fInvNum').value;

    if (!window.google || !google.script || !google.script.run) {
      setStatus('Backend not configured — use Print to save PDF locally.', true);
      window.print();
      return;
    }
    setStatus('Generating PDF…');
    google.script.run
      .withSuccessHandler(function (res) {
        if (res.pdfBase64) window.CalixlabInvoice.openPdfBase64(res.pdfBase64, res.invoiceNumber + '.pdf');
        if (res.driveUrl) setStatus('Saved: ' + res.invoiceNumber + ' → Drive');
        else setStatus('PDF ready: ' + (res.invoiceNumber || ''));
        if (res.invoiceNumber) $('fInvNum').value = res.invoiceNumber;
      })
      .withFailureHandler(function (e) {
        setStatus(e.message || 'PDF failed', true);
      })
      .generateInvoice(payload);
  }

  function initFromQuery() {
    var q = new URLSearchParams(window.location.search);
    var row = q.get('row');
    var type = q.get('type') || 'onboarding';
    if (row) {
      $('loadRow').value = row;
      loadFromRow(parseInt(row, 10));
      return;
    }
    $('fInvDate').value = todayMyr();
    $('fDueDate').value = todayMyr();
    syncFormToPreview();
  }

  ['fInvNum', 'fInvDate', 'fDueDate', 'fTerms', 'fName', 'fPhone', 'fEmail', 'fIc',
    'fDesc', 'fQty', 'fRate', 'fAmount', 'fPaid'].forEach(function (id) {
    var el = $(id);
    if (el) el.addEventListener('input', syncFormToPreview);
  });

  $('btnRecalc').addEventListener('click', recalcTotals);
  $('btnPrint').addEventListener('click', function () { window.print(); });
  $('btnPdf').addEventListener('click', generatePdf);
  $('btnLoadRow').addEventListener('click', function () {
    var row = parseInt($('loadRow').value, 10);
    if (row < 2) { setStatus('Enter a Client sheet row # (2+)', true); return; }
    loadFromRow(row);
  });
  $('btnHub').addEventListener('click', function () {
    window.location.href = '../index.html';
  });

  initFromQuery();
})();
