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

/** Tab listing trainers (column A: name; row 1 header optional). */
const TRAINER_SHEET_NAME = 'Trainer';

/** Tab for Session Log form submissions. */
const SESSION_LOG_SHEET_NAME = 'Session Log';

/** Optional Drive folder ID for receipts & signatures (empty = skip uploads). */
const RECEIPTS_FOLDER_ID = '';
