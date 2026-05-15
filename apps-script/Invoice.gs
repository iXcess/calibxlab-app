/**
 * Invoice generation from Client sheet / onboarding / payment payloads.
 * Template: InvoiceTemplate.html → PDF via HtmlService.
 */

function formatDecimal_(n) {
  var v = parseFloat(n) || 0;
  var parts = Math.abs(v).toFixed(2).split('.');
  parts[0] = parts[0].replace(/\B(?=(\d{3})+(?!\d))/g, ',');
  return (v < 0 ? '-' : '') + parts.join('.');
}

function formatMoneyMyr_(n) {
  return 'MYR' + formatDecimal_(n);
}

function formatMoneyNeg_(n) {
  var v = parseFloat(n) || 0;
  if (v <= 0) return '(-) 0.00';
  return '(-) ' + formatDecimal_(v);
}

function formatDateMyr_(d) {
  if (!d) return Utilities.formatDate(new Date(), Session.getScriptTimeZone(), 'dd MMM yyyy');
  if (d instanceof Date) {
    return Utilities.formatDate(d, Session.getScriptTimeZone(), 'dd MMM yyyy');
  }
  var parsed = new Date(d);
  if (!isNaN(parsed.getTime())) {
    return Utilities.formatDate(parsed, Session.getScriptTimeZone(), 'dd MMM yyyy');
  }
  return String(d);
}

function escapeHtml_(s) {
  return String(s || '')
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}

/** Public HTTPS logo — works in HtmlService PDF (data URIs are stripped). */
function getInvoiceLogoSrc_() {
  return 'https://ixcess.github.io/calibxlab-app/assets/calixlab-logo-header.png';
}

function getInvoiceSheet_() {
  var ss = getSubmissionSpreadsheet_();
  var sheet = ss.getSheetByName(INVOICE_SHEET_NAME);
  if (!sheet) {
    sheet = ss.insertSheet(INVOICE_SHEET_NAME);
    sheet.getRange(1, 1, 1, 6).setValues([[
      'Timestamp', 'Invoice Number', 'Client', 'Type', 'Total', 'Drive File'
    ]]);
    sheet.getRange(1, 1, 1, 6).setFontWeight('bold');
    sheet.setFrozenRows(1);
  }
  return sheet;
}

function getNextInvoiceNumber_() {
  var sheet = getInvoiceSheet_();
  var data = sheet.getDataRange().getValues();
  var maxNum = INVOICE_START_NUMBER - 1;
  var re = new RegExp('^' + INVOICE_PREFIX.replace('-', '\\-') + '(\\d+)$', 'i');
  for (var r = 1; r < data.length; r++) {
    var cell = String(data[r][1] || '');
    var m = cell.match(re);
    if (m) maxNum = Math.max(maxNum, parseInt(m[1], 10));
  }
  var next = maxNum + 1;
  return INVOICE_PREFIX + Utilities.formatString('%05d', next);
}

function parseAdditionalPayments_(row) {
  try {
    return JSON.parse(row[23] || '[]');
  } catch (e) {
    return [];
  }
}

function totalPaidFromRow_(row) {
  var amountPaid = parseFloat(row[22]) || 0;
  var additional = parseAdditionalPayments_(row);
  var extra = additional.reduce(function (s, p) {
    return s + (parseFloat(p.amount) || 0);
  }, 0);
  return amountPaid + extra;
}

function buildLineItemDescription_(row, trainerOverride) {
  var pkg = row[12] || 'Personal Training Package';
  var sessions = parseInt(row[13], 10) || 0;
  var trainer = trainerOverride || row[7] || '';
  var desc = pkg;
  if (sessions) desc += ' · ' + sessions + ' session(s)';
  if (trainer) desc += ' w/ ' + trainer;
  return desc;
}

function buildInvoiceModelFromRow_(row, rowIndex, options) {
  options = options || {};
  var type = options.type || 'onboarding';
  var today = new Date();
  var sessions = parseInt(row[13], 10) || 1;
  var rate = parseFloat(row[14]) || 0;
  var total = parseFloat(row[15]) || (sessions * rate);
  var paid = totalPaidFromRow_(row);
  if (options.paymentAmount != null) {
    paid = parseFloat(options.paymentAmount) || paid;
  }
  var balance = Math.max(0, total - paid);
  var lineItems = [];

  if (type === 'payment' && options.paymentAmount != null) {
    var inst = parseAdditionalPayments_(row).length + 1;
    var totalInst = parseInt(row[19], 10) || 1;
    lineItems.push({
      index: 1,
      description: 'Instalment / payment — ' + (row[1] || 'Client') +
        (totalInst > 1 ? ' (' + inst + ' of ' + totalInst + ')' : ''),
      qty: '1',
      rate: formatMoneyMyr_(options.paymentAmount).replace('MYR', ''),
      amount: formatMoneyMyr_(options.paymentAmount).replace('MYR', '')
    });
    total = parseFloat(options.paymentAmount) || 0;
    paid = total;
    balance = 0;
  } else {
    lineItems.push({
      index: 1,
      description: buildLineItemDescription_(row, options.trainerName),
      qty: formatDecimal_(sessions),
      rate: formatDecimal_(rate),
      amount: formatDecimal_(total)
    });
  }

  var contactParts = [];
  if (row[2]) contactParts.push('Tel: ' + row[2]);
  if (row[3]) contactParts.push(row[3]);
  if (row[4]) contactParts.push('IC: ' + row[4]);

  return {
    invoiceNumber: options.invoiceNumber || getNextInvoiceNumber_(),
    invoiceDate: formatDateMyr_(options.invoiceDate || today),
    dueDate: formatDateMyr_(options.dueDate || today),
    terms: options.terms || 'Due on Receipt',
    billName: row[1] || '',
    billContact: contactParts.join(' · '),
    lineItems: lineItems,
    subTotal: formatDecimal_(total),
    taxNote: '(Tax Inclusive)',
    total: formatMoneyMyr_(total),
    paymentMade: formatMoneyNeg_(paid),
    balanceDue: formatMoneyMyr_(balance),
    notesHtml: escapeHtml_(
      'All payments shall be made to:<br><strong>' + COMPANY_LEGAL_NAME + '</strong><br>' +
      COMPANY_BANK_NAME + '<br>' + COMPANY_BANK_ACCOUNT
    ),
    termsList: [
      'Validity of Package: 6 months from first session',
      'Payment before any booking of classes'
    ],
    companyLegal: COMPANY_LEGAL_NAME,
    companyDisplay: COMPANY_DISPLAY_NAME,
    companyAddress: COMPANY_ADDRESS_LINES,
    logoSrc: getInvoiceLogoSrc_(),
    meta: { rowIndex: rowIndex, type: type, totalValue: total, paid: paid, balance: balance }
  };
}

function buildInvoiceModelFromOnboard_(data, options) {
  options = options || {};
  var row = [
    new Date(),
    data.fullName, data.phone, data.email, data.ic,
    data.emergencyContact, data.emergencyPhone,
    data.trainerName, data.startDate,
    '', '', '',
    data.packageType, data.sessions, data.ratePerSession, data.totalPackageValue,
    data.leadType, data.paymentMode,
    data.instalmentPlan, data.totalInstalments || '', data.instalmentAmount || '',
    data.firstPaymentDate || '', data.amountPaid, data.additionalPayments || '[]',
    data.discoverySource, data.notes || '', '', '', ''
  ];
  var paid = parseFloat(data.amountPaid) || 0;
  return buildInvoiceModelFromRow_(row, options.sheetRowIndex || 0, {
    type: 'onboarding',
    invoiceNumber: options.invoiceNumber,
    trainerName: data.trainerName,
    paymentAmount: options.paymentOnly ? paid : null
  });
}

function renderInvoiceHtml_(model) {
  var t = HtmlService.createTemplateFromFile('InvoiceTemplate');
  t.companyLegal = model.companyLegal;
  t.companyDisplay = model.companyDisplay;
  t.companyAddress = model.companyAddress;
  t.logoSrc = model.logoSrc;
  t.billName = escapeHtml_(model.billName);
  t.billContact = escapeHtml_(model.billContact);
  t.invoiceNumber = escapeHtml_(model.invoiceNumber);
  t.invoiceDate = escapeHtml_(model.invoiceDate);
  t.dueDate = escapeHtml_(model.dueDate);
  t.terms = escapeHtml_(model.terms);
  t.lineItems = model.lineItems;
  t.subTotal = model.subTotal;
  t.taxNote = model.taxNote;
  t.total = model.total;
  t.paymentMade = model.paymentMade;
  t.balanceDue = model.balanceDue;
  t.notesHtml = model.notesHtml;
  t.termsList = model.termsList;
  return t.evaluate().getContent();
}

function htmlToPdfBlob_(html, fileName) {
  var blob = HtmlService.createHtmlOutput(html)
    .setWidth(794)
    .setHeight(1123)
    .getAs('application/pdf');
  blob.setName(fileName || 'invoice.pdf');
  return blob;
}

function saveInvoicePdfToDrive_(blob, invoiceNumber, clientName, invoiceMeta) {
  if (!RECEIPTS_FOLDER_ID) return { fileName: blob.getName(), url: '', fileId: '' };
  invoiceMeta = invoiceMeta || {};
  var details = {
    'Invoice number': invoiceNumber,
    'Invoice type': invoiceMeta.type || 'onboarding'
  };
  if (invoiceMeta.paymentAmount != null) {
    details['Payment amount'] = invoiceMeta.paymentAmount;
  }
  return saveDriveBlob_(blob, {
    subfolder: FOLDER_INVOICES,
    kind: 'invoice',
    category: 'Invoice',
    clientName: clientName,
    originalFileName: invoiceNumber + '.pdf',
    details: details
  });
}

function logInvoice_(model, driveInfo) {
  var sheet = getInvoiceSheet_();
  sheet.appendRow([
    new Date(),
    model.invoiceNumber,
    model.billName,
    model.meta.type,
    model.meta.totalValue,
    driveInfo.fileName || ''
  ]);
}

/**
 * API: build invoice HTML/PDF from sheet row or inline onboarding/payment data.
 * payload: { type, sheetRowIndex, clientData, paymentAmount, invoiceNumber, saveToDrive, pdfOnly }
 */
function generateInvoice(payload) {
  payload = payload || {};
  var model;
  var type = payload.type || 'onboarding';

  if (payload.sheetRowIndex && payload.sheetRowIndex >= 2) {
    var sheet = getClientSheet_();
    var row = sheet.getRange(payload.sheetRowIndex, 1, payload.sheetRowIndex, HEADERS.length).getValues()[0];
    var payAmt = payload.paymentAmount != null ? payload.paymentAmount : null;
    if (type === 'payment' && payAmt == null) {
      payAmt = totalPaidFromRow_(row);
    }
    model = buildInvoiceModelFromRow_(row, payload.sheetRowIndex, {
      type: type,
      invoiceNumber: payload.invoiceNumber,
      paymentAmount: type === 'payment' ? payAmt : null
    });
  } else if (payload.clientData) {
    model = buildInvoiceModelFromOnboard_(payload.clientData, {
      invoiceNumber: payload.invoiceNumber,
      sheetRowIndex: payload.sheetRowIndex
    });
  } else {
    throw new Error('Provide sheetRowIndex or clientData for generateInvoice.');
  }

  if (payload.invoiceNumber) {
    model.invoiceNumber = payload.invoiceNumber;
  }

  var html = renderInvoiceHtml_(model);
  var result = {
    invoiceNumber: model.invoiceNumber,
    html: html,
    balanceDue: model.meta.balance,
    total: model.meta.totalValue
  };

  if (payload.htmlOnly) {
    return result;
  }

  var pdfBlob = htmlToPdfBlob_(html, model.invoiceNumber + '.pdf');
  result.pdfBase64 = Utilities.base64Encode(pdfBlob.getBytes());

  if (payload.saveToDrive !== false && RECEIPTS_FOLDER_ID) {
    var driveInfo = saveInvoicePdfToDrive_(pdfBlob, model.invoiceNumber, model.billName, {
      type: model.meta.type,
      paymentAmount: model.meta.type === 'payment' ? model.meta.paid : null
    });
    result.driveUrl = driveInfo.url;
    result.driveFileName = driveInfo.fileName;
    logInvoice_(model, driveInfo);
  }

  return result;
}

function previewInvoiceHtml(payload) {
  payload = payload || {};
  payload.htmlOnly = true;
  return generateInvoice(payload);
}
