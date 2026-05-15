/**
 * Calixlab Onboarding — server handlers.
 * - Hosted in Apps Script: doGet serves HTML (optional).
 * - GitHub Pages / static: POST JSON { action, payload } to /exec (see gas-client.js).
 */

function jsonResponse_(obj) {
  return ContentService.createTextOutput(JSON.stringify(obj))
    .setMimeType(ContentService.MimeType.JSON);
}

function runApiAction_(action, payload) {
  if (action === 'lookupClient') {
    return lookupClient(typeof payload === 'string' ? payload : (payload && payload.q) || '');
  }
  if (action === 'listTrainers') return listTrainers();
  if (action === 'addTrainer') return addTrainer(payload || {});
  if (action === 'deleteTrainer') return deleteTrainer(payload || {});
  if (action === 'onboardClient') return onboardClient(payload || {});
  if (action === 'recordPayment') return recordPayment(payload || {});
  if (action === 'recordSessionLog') return recordSessionLog(payload || {});
  if (action === 'generateInvoice') return generateInvoice(payload || {});
  if (action === 'previewInvoiceHtml') return previewInvoiceHtml(payload || {});
  throw new Error('Unknown action: ' + action);
}

function parseApiPayload_(action, p) {
  if (action === 'lookupClient') {
    return p.q != null ? p.q : (p.payload || '');
  }
  var raw = p.payload;
  if (raw == null || raw === '') return {};
  if (typeof raw === 'object') return raw;
  try {
    return JSON.parse(String(raw));
  } catch (err) {
    throw new Error('Invalid JSON payload');
  }
}

function doGet(e) {
  var p = (e && e.parameter) || {};
  if (p.action) {
    try {
      return jsonResponse_({
        ok: true,
        result: runApiAction_(p.action, parseApiPayload_(p.action, p))
      });
    } catch (err) {
      return jsonResponse_({ ok: false, error: String(err.message || err) });
    }
  }
  return HtmlService.createHtmlOutputFromFile('index')
    .setTitle('Calixlab Trainer Hub')
    .setXFrameOptionsMode(HtmlService.XFrameOptionsMode.ALLOWALL);
}

function doPost(e) {
  try {
    var body = JSON.parse(e.postData.contents);
    var result = runApiAction_(body.action, body.payload);
    return jsonResponse_({ ok: true, result: result });
  } catch (err) {
    return jsonResponse_({ ok: false, error: String(err.message || err) });
  }
}

function getActiveSpreadsheetId_() {
  if (ACTIVE_TARGET === 'production') return PRODUCTION_SPREADSHEET_ID;
  if (ACTIVE_TARGET === 'staging') return STAGING_SPREADSHEET_ID;
  throw new Error('ACTIVE_TARGET must be "production" or "staging" in Config.gs.');
}

function getActiveSheetName_() {
  if (ACTIVE_TARGET === 'production') return PRODUCTION_SHEET_NAME;
  if (ACTIVE_TARGET === 'staging') return STAGING_SHEET_NAME;
  throw new Error('ACTIVE_TARGET must be "production" or "staging" in Config.gs.');
}

/** Spreadsheet used for reads/writes (see Config.gs). */
function getSubmissionSpreadsheet_() {
  var id = getActiveSpreadsheetId_();
  if (!id || String(id).indexOf('PASTE_') === 0) {
    throw new Error('Set spreadsheet ID in Config.gs for ACTIVE_TARGET="' + ACTIVE_TARGET + '".');
  }
  return SpreadsheetApp.openById(id);
}

function getClientSheet_() {
  var ss = getSubmissionSpreadsheet_();
  var name = getActiveSheetName_();
  var sheet = ss.getSheetByName(name);
  if (!sheet && ACTIVE_TARGET === 'production') {
    sheet = ss.getSheetByName('Client') || ss.getSheets()[0];
  }
  if (!sheet) {
    throw new Error('Sheet not found: "' + name + '". Create this tab or fix PRODUCTION_SHEET_NAME / STAGING_SHEET_NAME in Config.gs.');
  }
  return sheet;
}

function getTrainerSheet_() {
  var ss = getSubmissionSpreadsheet_();
  var sheet = ss.getSheetByName(TRAINER_SHEET_NAME);
  if (!sheet) {
    throw new Error('Sheet not found: "' + TRAINER_SHEET_NAME + '". Add a tab named Trainer with names in column A.');
  }
  return sheet;
}

function isTrainerHeader_(val) {
  var h = String(val || '').trim().toLowerCase();
  return h === 'trainer' || h === 'name' || h === 'trainer name';
}

function ensureTrainerSheet_() {
  var sheet = getTrainerSheet_();
  if (sheet.getLastRow() === 0) {
    sheet.getRange(1, 1).setValue('Trainer').setFontWeight('bold');
    sheet.setFrozenRows(1);
  }
  return sheet;
}

/** One-time seed when Trainer tab has no names (edit/remove in the sheet anytime). */
function seedDefaultTrainersIfEmpty_() {
  var sheet = ensureTrainerSheet_();
  if (sheet.getLastRow() > 1) return;
  var defaults = ['Alex', 'Sarah', 'Hafiz', 'Nurul', 'Kendy'];
  defaults.forEach(function (n) { sheet.appendRow([n]); });
}

function listTrainers() {
  seedDefaultTrainersIfEmpty_();
  var sheet = getTrainerSheet_();
  var data = sheet.getDataRange().getValues();
  var names = [];
  for (var r = 0; r < data.length; r++) {
    var name = String(data[r][0] || '').trim();
    if (!name) continue;
    if (r === 0 && isTrainerHeader_(name)) continue;
    if (names.indexOf(name) === -1) names.push(name);
  }
  names.sort(function (a, b) { return a.localeCompare(b, undefined, { sensitivity: 'base' }); });
  return names;
}

function trainerNameFromPayload_(payload) {
  if (typeof payload === 'string') return String(payload).trim();
  return String((payload && payload.name) || '').trim();
}

function addTrainer(payload) {
  var name = trainerNameFromPayload_(payload);
  if (!name) throw new Error('Trainer name required.');
  var sheet = ensureTrainerSheet_();
  var existing = listTrainers();
  if (existing.indexOf(name) >= 0) throw new Error('Trainer already exists: ' + name);
  sheet.appendRow([name]);
  return { ok: true, name: name };
}

function deleteTrainer(payload) {
  var name = trainerNameFromPayload_(payload);
  if (!name) throw new Error('Trainer name required.');
  var sheet = getTrainerSheet_();
  var data = sheet.getDataRange().getValues();
  for (var r = data.length - 1; r >= 0; r--) {
    var cell = String(data[r][0] || '').trim();
    if (r === 0 && isTrainerHeader_(cell)) continue;
    if (cell === name) {
      sheet.deleteRow(r + 1);
      return { ok: true, name: name };
    }
  }
  throw new Error('Trainer not found: ' + name);
}

// ── Session Log tab ─────────────────────────────────────────────────────────
var SESSION_LOG_HEADERS = [
  'Timestamp', 'Session Date', 'Trainer', 'Client', 'Session Type',
  'Lead Source', 'Lead Multiplier', 'Session Number', 'Client Confirmed',
  'Client Sheet Row', 'Package Info', 'Signature File'
];

function getSessionLogSheet_() {
  var ss = getSubmissionSpreadsheet_();
  var sheet = ss.getSheetByName(SESSION_LOG_SHEET_NAME);
  if (!sheet) {
    sheet = ss.insertSheet(SESSION_LOG_SHEET_NAME);
  }
  return sheet;
}

function ensureSessionLogHeaderRow_(sheet) {
  if (sheet.getLastRow() === 0) {
    sheet.getRange(1, 1, 1, SESSION_LOG_HEADERS.length).setValues([SESSION_LOG_HEADERS]);
    sheet.getRange(1, 1, 1, SESSION_LOG_HEADERS.length).setFontWeight('bold');
    sheet.setFrozenRows(1);
    return;
  }
  var lastCol = sheet.getLastColumn();
  if (lastCol < SESSION_LOG_HEADERS.length) {
    sheet.getRange(1, lastCol + 1, 1, SESSION_LOG_HEADERS.length).setValues([
      SESSION_LOG_HEADERS.slice(lastCol)
    ]);
    sheet.getRange(1, 1, 1, SESSION_LOG_HEADERS.length).setFontWeight('bold');
  }
}

function recordSessionLog(data) {
  var sheet = getSessionLogSheet_();
  ensureSessionLogHeaderRow_(sheet);
  var sigName = '';
  if (RECEIPTS_FOLDER_ID && data.signatureBase64) {
    sigName = saveBase64File_(data.signatureBase64, data.signatureMimeType || 'image/jpeg', {
      subfolder: FOLDER_SESSION_SIGNATURES,
      kind: 'session-signature',
      category: 'Session Log',
      clientName: data.client,
      originalFileName: data.signatureFileName,
      details: {
        Trainer: data.trainer,
        'Session date': data.sessionDate,
        'Session type': data.sessionType,
        'Session #': data.sessionNumber,
        'Lead source': data.leadSource
      }
    });
  }
  var row = [
    new Date(),
    data.sessionDate || '',
    data.trainer || '',
    data.client || '',
    data.sessionType || '',
    data.leadSource || '',
    data.leadMultiplier || '',
    parseInt(data.sessionNumber, 10) || data.sessionNumber || '',
    data.clientConfirmed ? 'Yes' : 'No',
    data.clientSheetRow || '',
    data.packageInfo || '',
    sigName
  ];
  sheet.appendRow(row);
  return { rowIndex: sheet.getLastRow(), signatureFile: sigName };
}

// ── Column headers (row 1) — must match your new sheet ─────────────────────
var HEADERS = [
  'Timestamp', 'Full Name', 'Phone', 'Email', 'IC', 'Emergency Contact', 'Emergency Phone',
  'Trainer', 'Start Date', 'Fitness Level', 'Fitness Goals', 'Medical Conditions',
  'Package Type', 'Sessions', 'Rate/Session', 'Total Package', 'Lead Type', 'Payment Mode',
  'Instalment Plan', 'Total Instalments', 'Instalment Amount', 'First Payment Date',
  'Amount Paid', 'Additional Payments', 'Discovery Source', 'Notes',
  'Receipt File', 'Waiver Date', 'Signature File'
];

function ensureHeaderRow_(sheet) {
  if (sheet.getLastRow() === 0) {
    sheet.getRange(1, 1, 1, HEADERS.length).setValues([HEADERS]);
    sheet.getRange(1, 1, 1, HEADERS.length).setFontWeight('bold');
    sheet.setFrozenRows(1);
  }
}

function rowToClient_(row, rowIndex) {
  var sessions = parseInt(row[13], 10) || 0;
  var totalValue = parseFloat(row[15]) || 0;
  var amountPaid = parseFloat(row[22]) || 0;
  var totalInstalments = parseInt(row[19], 10) || 1;
  var instalmentAmt = parseFloat(row[20]) || 0;
  var additional = [];
  try {
    additional = JSON.parse(row[23] || '[]');
  } catch (e) {
    additional = [];
  }
  var instalmentsPaid = 1 + additional.length;
  var outstanding = Math.max(0, totalValue - amountPaid - additional.reduce(function (s, p) {
    return s + (parseFloat(p.amount) || 0);
  }, 0));
  var sessionsUsed = countSessionsLogged_(row[1], rowIndex);
  var sessionsRemaining = Math.max(0, sessions - sessionsUsed);

  return {
    fullName: row[1] || '',
    phone: row[2] || '',
    email: row[3] || '',
    ic: row[4] || '',
    emergencyContact: row[5] || '',
    emergencyPhone: row[6] || '',
    trainerName: row[7] || '',
    packageType: row[12] || '',
    sessionsTotal: sessions,
    leadType: row[16] || '',
    discoverySource: row[24] || '',
    amountPaid: amountPaid,
    totalValue: totalValue,
    outstanding: outstanding,
    sessionsRemaining: sessionsRemaining,
    instalmentsPaid: instalmentsPaid,
    totalInstalments: totalInstalments,
    isInstalment: (row[18] || '') === 'Yes',
    instalmentAmt: instalmentAmt,
    nextPayDate: computeNextPayDate_(row, additional),
    schedule: buildSchedule_(row, additional),
    rowIndex: rowIndex
  };
}

function computeNextPayDate_(row, additional) {
  if ((row[18] || '') !== 'Yes') return '—';
  var totalInst = parseInt(row[19], 10) || 0;
  var paid = 1 + additional.length;
  if (paid >= totalInst) return 'Paid in full';
  var firstDate = row[21];
  if (!firstDate) return '—';
  var d = new Date(firstDate);
  d.setMonth(d.getMonth() + paid);
  var today = new Date();
  today.setHours(0, 0, 0, 0);
  if (d < today) return 'Overdue — ' + Utilities.formatDate(d, Session.getScriptTimeZone(), 'd MMM yyyy');
  return Utilities.formatDate(d, Session.getScriptTimeZone(), 'd MMM yyyy');
}

function buildSchedule_(row, additional) {
  if ((row[18] || '') !== 'Yes') return [];
  var totalInst = parseInt(row[19], 10) || 0;
  var per = parseFloat(row[20]) || 0;
  var firstDate = row[21] ? new Date(row[21]) : new Date();
  var schedule = [];
  var today = new Date();
  today.setHours(0, 0, 0, 0);
  for (var i = 0; i < totalInst; i++) {
    var due = new Date(firstDate);
    due.setMonth(due.getMonth() + i);
    var paid = i === 0 || additional.length >= i;
    var overdue = !paid && due < today;
    var tomorrow = new Date(today);
    tomorrow.setDate(tomorrow.getDate() + 1);
    schedule.push({
      instalment: i + 1,
      dueDate: Utilities.formatDate(due, Session.getScriptTimeZone(), 'd MMM yyyy'),
      amount: i === 0 ? parseFloat(row[22]) || per : per,
      paid: paid,
      overdue: overdue,
      dueTomorrow: !paid && due.getTime() === tomorrow.getTime()
    });
  }
  return schedule;
}

/** Count Session Log rows for this client (by sheet row index, else name). */
function countSessionsLogged_(clientName, clientSheetRow) {
  var sheet = getSessionLogSheet_();
  if (sheet.getLastRow() < 2) return 0;
  var data = sheet.getDataRange().getValues();
  var nameKey = String(clientName || '').trim().toLowerCase();
  var rowKey = parseInt(clientSheetRow, 10);
  var useRow = !isNaN(rowKey) && rowKey >= 2;
  var count = 0;
  for (var r = 1; r < data.length; r++) {
    if (useRow) {
      var loggedRow = parseInt(data[r][9], 10);
      if (loggedRow === rowKey) count++;
    } else if (nameKey) {
      var loggedName = String(data[r][3] || '').trim().toLowerCase();
      if (loggedName === nameKey) count++;
    }
  }
  return count;
}

function lookupClient(query) {
  var sheet = getClientSheet_();
  var data = sheet.getDataRange().getValues();
  if (data.length < 2) return [];
  var q = String(query || '').trim().toLowerCase();
  if (q.length < 2) return [];
  var results = [];
  for (var r = 1; r < data.length; r++) {
    var name = String(data[r][1] || '');
    if (name.toLowerCase().indexOf(q) !== -1) {
      results.push(rowToClient_(data[r], r + 1));
    }
  }
  return results.slice(0, 8);
}

function onboardClient(data) {
  var sheet = getClientSheet_();
  ensureHeaderRow_(sheet);
  var folderUrl = '';
  var receiptName = '';
  var sigName = '';
  if (RECEIPTS_FOLDER_ID && data.receiptBase64) {
    receiptName = saveBase64File_(data.receiptBase64, data.receiptMimeType, {
      subfolder: FOLDER_ONBOARDING_RECEIPTS,
      kind: 'onboarding-receipt',
      category: 'Onboarding',
      clientName: data.fullName,
      originalFileName: data.receiptFileName,
      details: {
        Trainer: data.trainerName,
        'Package': data.packageType,
        'Sessions': data.sessions,
        'Amount paid': data.amountPaid,
        'Payment mode': data.paymentMode
      }
    });
    folderUrl = 'https://drive.google.com/drive/folders/' + RECEIPTS_FOLDER_ID;
  }
  if (RECEIPTS_FOLDER_ID && data.signatureBase64) {
    sigName = saveBase64File_(data.signatureBase64, data.signatureMimeType || 'image/jpeg', {
      subfolder: FOLDER_ONBOARDING_SIGNATURES,
      kind: 'waiver-signature',
      category: 'Onboarding',
      clientName: data.fullName,
      originalFileName: data.fullName + '-signature.jpg',
      details: {
        Trainer: data.trainerName,
        'Waiver date': data.waiverDate
      }
    });
  }
  var row = [
    new Date(),
    data.fullName, data.phone, data.email, data.ic,
    data.emergencyContact, data.emergencyPhone,
    data.trainerName, data.startDate,
    data.fitnessLevel, data.fitnessGoals, data.medicalConditions,
    data.packageType, data.sessions, data.ratePerSession, data.totalPackageValue,
    data.leadType, data.paymentMode,
    data.instalmentPlan, data.totalInstalments || '', data.instalmentAmount || '',
    data.firstPaymentDate || '', data.amountPaid, data.additionalPayments || '[]',
    data.discoverySource, data.notes || '',
    receiptName, data.waiverDate || '', sigName
  ];
  sheet.appendRow(row);
  return { folderUrl: folderUrl, rowIndex: sheet.getLastRow() };
}

function recordPayment(data) {
  var sheet = getClientSheet_();
  var rowIndex = data.sheetRowIndex;
  if (!rowIndex || rowIndex < 2) throw new Error('Invalid client row.');
  var row = sheet.getRange(rowIndex, 1, rowIndex, HEADERS.length).getValues()[0];
  var additional = [];
  try {
    additional = JSON.parse(row[23] || '[]');
  } catch (e) {
    additional = [];
  }
  var entry = {
    amount: data.paymentAmount,
    date: data.paymentDate,
    method: data.paymentMethod,
    notes: data.notes || '',
    recordedAt: new Date().toISOString()
  };
  if (data.receiptBase64 && RECEIPTS_FOLDER_ID) {
    entry.receiptFile = saveBase64File_(data.receiptBase64, data.receiptMimeType, {
      subfolder: FOLDER_PAYMENT_RECEIPTS,
      kind: 'payment-receipt',
      category: 'Record payment',
      clientName: data.clientName,
      originalFileName: data.receiptFileName,
      details: {
        'Payment amount': data.paymentAmount,
        'Payment date': data.paymentDate,
        'Payment method': data.paymentMethod,
        Notes: data.notes || ''
      }
    });
  }
  additional.push(entry);
  sheet.getRange(rowIndex, 24).setValue(JSON.stringify(additional));
  var folderUrl = RECEIPTS_FOLDER_ID
    ? 'https://drive.google.com/drive/folders/' + RECEIPTS_FOLDER_ID
    : '';
  return { folderUrl: folderUrl };
}

function sanitizeFileStem_(name) {
  return String(name || 'client').replace(/[^\w\s-]/g, '').replace(/\s+/g, '-').slice(0, 60) || 'client';
}

function formatDriveTimestamp_(d) {
  var when = d instanceof Date ? d : new Date();
  return Utilities.formatDate(when, Session.getScriptTimeZone(), 'yyyyMMdd-HHmmss');
}

function formatDriveTimestampHuman_(d) {
  var when = d instanceof Date ? d : new Date();
  return Utilities.formatDate(when, Session.getScriptTimeZone(), 'dd MMM yyyy, HH:mm:ss');
}

function extensionFromMimeOrName_(mimeType, originalFileName) {
  var name = String(originalFileName || '');
  var dot = name.lastIndexOf('.');
  if (dot > 0 && dot < name.length - 1) {
    return name.slice(dot).toLowerCase();
  }
  var mime = String(mimeType || '').toLowerCase();
  if (mime.indexOf('jpeg') >= 0 || mime.indexOf('jpg') >= 0) return '.jpg';
  if (mime.indexOf('png') >= 0) return '.png';
  if (mime.indexOf('pdf') >= 0) return '.pdf';
  if (mime.indexOf('webp') >= 0) return '.webp';
  return '.bin';
}

/**
 * meta: { kind, clientName, category, subfolder, originalFileName, details: {key: value} }
 */
function buildDriveFileName_(meta, mimeType, uploadedAt) {
  var ts = formatDriveTimestamp_(uploadedAt);
  var kind = sanitizeFileStem_(meta.kind || 'upload');
  var client = sanitizeFileStem_(meta.clientName || 'client');
  var ext = extensionFromMimeOrName_(mimeType, meta.originalFileName);
  return ts + '_' + kind + '_' + client + ext;
}

function buildDriveDescription_(meta, uploadedAt) {
  var lines = [
    'Calixlab Trainer Hub upload',
    'Uploaded: ' + formatDriveTimestampHuman_(uploadedAt) + ' (' + Session.getScriptTimeZone() + ')'
  ];
  if (meta.category) lines.push('Category: ' + meta.category);
  if (meta.kind) lines.push('File type: ' + meta.kind);
  if (meta.clientName) lines.push('Client: ' + meta.clientName);
  if (meta.originalFileName) lines.push('Original filename: ' + meta.originalFileName);
  var details = meta.details || {};
  Object.keys(details).forEach(function (key) {
    var val = details[key];
    if (val !== '' && val != null) lines.push(key + ': ' + val);
  });
  return lines.join('\n');
}

function getUploadSubfolder_(subfolderName) {
  var parent = DriveApp.getFolderById(RECEIPTS_FOLDER_ID);
  var it = parent.getFoldersByName(subfolderName);
  if (it.hasNext()) return it.next();
  return parent.createFolder(subfolderName);
}

function saveDriveBlob_(blob, meta) {
  if (!RECEIPTS_FOLDER_ID) return { fileName: blob.getName(), url: '', fileId: '' };
  var uploadedAt = meta.uploadedAt || new Date();
  var driveName = buildDriveFileName_(meta, blob.getContentType(), uploadedAt);
  blob.setName(driveName);
  var folder = meta.subfolder ? getUploadSubfolder_(meta.subfolder) : DriveApp.getFolderById(RECEIPTS_FOLDER_ID);
  var file = folder.createFile(blob);
  file.setDescription(buildDriveDescription_(meta, uploadedAt));
  return { fileName: file.getName(), url: file.getUrl(), fileId: file.getId() };
}

function saveBase64File_(base64, mimeType, meta) {
  if (!RECEIPTS_FOLDER_ID) return '';
  var raw = String(base64 || '');
  var comma = raw.indexOf(',');
  if (comma >= 0) raw = raw.slice(comma + 1);
  var blob = Utilities.newBlob(
    Utilities.base64Decode(raw),
    mimeType || 'application/octet-stream',
    meta.originalFileName || 'upload'
  );
  return saveDriveBlob_(blob, meta).fileName;
}
