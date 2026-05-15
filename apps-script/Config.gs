/**
 * Form submission target (Google Sheet tab).
 *
 * Production = live Calixlab client sheet (do not use for experiments).
 * Staging = separate spreadsheet for tests (optional).
 */

// ── PRODUCTION (live) ──────────────────────────────────────────────────────
// https://docs.google.com/spreadsheets/d/1rRQp0WWIBpnZfZQhXZCHp7RnxF5J9tBsA59cXkr9nv8/edit?gid=0
const PRODUCTION_SPREADSHEET_ID = '1rRQp0WWIBpnZfZQhXZCHp7RnxF5J9tBsA59cXkr9nv8';
/** First tab is gid=0 — change if your tab has another name (e.g. Clients). */
const PRODUCTION_SHEET_NAME = 'Client';

// ── STAGING (optional test spreadsheet) ────────────────────────────────────
const STAGING_SPREADSHEET_ID = 'PASTE_NEW_SPREADSHEET_ID_HERE';
const STAGING_SHEET_NAME = 'Clients';

/**
 * Where submissions go: 'production' | 'staging'
 * Use 'staging' while testing; switch to 'production' when ready for live data.
 */
const ACTIVE_TARGET = 'production';

/** Tab listing trainers (row 1 headers; name in Trainer column, Timestamp may be column A). */
const TRAINER_SHEET_NAME = 'Trainer';

/** Tab for Session Log form submissions. */
const SESSION_LOG_SHEET_NAME = 'Session Log';

/** Tab logging issued invoice numbers (optional; created on first issue). */
const INVOICE_SHEET_NAME = 'Invoices';

/**
 * Parent Drive folder for all uploads.
 * https://drive.google.com/drive/folders/1GcB2_GwLoE9cosyJPyoIOL5WCjUBZBt5
 */
const RECEIPTS_FOLDER_ID = '1GcB2_GwLoE9cosyJPyoIOL5WCjUBZBt5';

/** Auto-created subfolders under RECEIPTS_FOLDER_ID. */
const FOLDER_ONBOARDING_RECEIPTS = 'onboarding-receipts';
const FOLDER_ONBOARDING_SIGNATURES = 'onboarding-signatures';
const FOLDER_PAYMENT_RECEIPTS = 'payment-receipts';
const FOLDER_SESSION_SIGNATURES = 'session-signatures';
const FOLDER_INVOICES = 'invoices';

// ── Invoice / company (from CL-INV-00160.pdf) ───────────────────────────────
const COMPANY_LEGAL_NAME = 'CALIXLAB EMPIRE';
const COMPANY_DISPLAY_NAME = 'Cali Lab';
const COMPANY_ADDRESS_LINES = [
  'D-G-53A, 10 Boulevard, Jalan Cempaka',
  'Kg. Sg. Kayu Ara, PJU 6A, Petaling Jaya',
  '47400 Selangor, Malaysia'
];
const COMPANY_BANK_NAME = 'HONG LEONG BANK';
const COMPANY_BANK_ACCOUNT = '05100348131';
const INVOICE_PREFIX = 'CL-INV-';
const INVOICE_START_NUMBER = 161;
