/**
 * Map Calixlab onboarding / payment / sheet client → invoice field object.
 */
(function (global) {
  function fmtMoney(n) {
    var v = parseFloat(n) || 0;
    return 'MYR' + v.toLocaleString('en-MY', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
  }

  function fmtNum(n) {
    return (parseFloat(n) || 0).toLocaleString('en-MY', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
  }

  function todayMyr() {
    return new Date().toLocaleDateString('en-MY', { day: 'numeric', month: 'short', year: 'numeric' });
  }

  function fromOnboardForm(getVal, getPill) {
    var sessions = parseInt(getVal('sessions'), 10) || 1;
    var rate = parseFloat(getVal('ratePerSession')) || 0;
    var total = parseFloat(getVal('totalPackageValue')) || sessions * rate;
    var paid = parseFloat(getVal('amountPaidFull')) || parseFloat(getVal('firstPayment')) || 0;
    var trainer = getVal('trainerNameHidden') || '';
    var pkg = getPill('packageType') || 'Personal Training';
    return {
      invoiceNumber: '',
      invoiceDate: todayMyr(),
      dueDate: todayMyr(),
      terms: 'Due on Receipt',
      billName: getVal('fullName') || '',
      billPhone: getVal('phone') || '',
      billEmail: getVal('email') || '',
      billIc: getVal('ic') || '',
      lineDescription: pkg + ' · ' + sessions + ' session(s)' + (trainer ? ' w/ ' + trainer : ''),
      lineQty: String(sessions),
      lineRate: fmtNum(rate),
      lineAmount: fmtNum(total),
      subTotal: fmtNum(total),
      total: fmtMoney(total),
      paymentMade: paid > 0 ? '(-) ' + fmtNum(paid) : '(-) 0.00',
      balanceDue: fmtMoney(Math.max(0, total - paid)),
      paymentMode: getPill('paymentMode') || ''
    };
  }

  function fromSheetClient(r, opts) {
    opts = opts || {};
    var sessions = parseInt(r.sessionsTotal, 10) || 1;
    var total = parseFloat(r.totalValue) || 0;
    var paid = parseFloat(r.amountPaid) || 0;
    var rate = sessions ? total / sessions : total;
    if (opts.paymentAmount != null) {
      var p = parseFloat(opts.paymentAmount) || 0;
      return {
        invoiceNumber: '',
        invoiceDate: todayMyr(),
        dueDate: todayMyr(),
        terms: 'Due on Receipt',
        billName: r.fullName || '',
        billPhone: r.phone || '',
        billEmail: r.email || '',
        billIc: r.ic || '',
        lineDescription: 'Instalment / payment — ' + (r.fullName || 'Client'),
        lineQty: '1',
        lineRate: fmtNum(p),
        lineAmount: fmtNum(p),
        subTotal: fmtNum(p),
        total: fmtMoney(p),
        paymentMade: '(-) ' + fmtNum(p),
        balanceDue: fmtMoney(0),
        sheetRowIndex: r.rowIndex
      };
    }
    return {
      invoiceNumber: '',
      invoiceDate: todayMyr(),
      dueDate: todayMyr(),
      terms: 'Due on Receipt',
      billName: r.fullName || '',
      billPhone: r.phone || '',
      billEmail: r.email || '',
      billIc: r.ic || '',
      lineDescription: (r.packageType || 'Package') + ' · ' + sessions + ' session(s)' +
        (r.trainerName ? ' w/ ' + r.trainerName : ''),
      lineQty: String(sessions),
      lineRate: fmtNum(rate),
      lineAmount: fmtNum(total),
      subTotal: fmtNum(total),
      total: fmtMoney(total),
      paymentMade: '(-) ' + fmtNum(paid),
      balanceDue: fmtMoney(Math.max(0, total - paid)),
      sheetRowIndex: r.rowIndex
    };
  }

  function openPdfBase64(b64, fileName) {
    var bin = atob(b64);
    var len = bin.length;
    var bytes = new Uint8Array(len);
    for (var i = 0; i < len; i++) bytes[i] = bin.charCodeAt(i);
    var blob = new Blob([bytes], { type: 'application/pdf' });
    var url = URL.createObjectURL(blob);
    window.open(url, '_blank');
    setTimeout(function () { URL.revokeObjectURL(url); }, 60000);
  }

  global.CalixlabInvoice = {
    fromOnboardForm: fromOnboardForm,
    fromSheetClient: fromSheetClient,
    openPdfBase64: openPdfBase64,
    fmtMoney: fmtMoney
  };
})(typeof window !== 'undefined' ? window : this);
