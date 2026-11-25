// Simulasi Google Apps Script (Sheets, Drive, Properties, UrlFetch) dan API TidyCal untuk menguji kod tanpa akaun Google.
'use strict';
const fs = require('fs');
const path = require('path');
const vm = require('vm');

const SRC = path.join(__dirname, '..', 'apps-script');

class Range {
  constructor(sh, r, c, nr, nc) { Object.assign(this, { sh, r, c, nr, nc }); }
  getValues() {
    const out = [];
    for (let i = 0; i < this.nr; i++) {
      const row = this.sh.rows[this.r - 1 + i] || [];
      const o = [];
      for (let j = 0; j < this.nc; j++) { const v = row[this.c - 1 + j]; o.push(v === undefined ? '' : v); }
      out.push(o);
    }
    return out;
  }
  setValues(v) {
    v.forEach((row, i) => {
      const t = this.sh.rows[this.r - 1 + i] || (this.sh.rows[this.r - 1 + i] = []);
      row.forEach((val, j) => { t[this.c - 1 + j] = typeof val === 'string' && val.startsWith("'") ? val.slice(1) : val; });
    });
    return this;
  }
  setNumberFormat() { return this; }
  setFontWeight() { return this; }
  setDataValidation() { return this; }
}
class Sheet {
  constructor(name) { this.name = name; this.rows = []; }
  getName() { return this.name; }
  getLastRow() { for (let i = this.rows.length - 1; i >= 0; i--) if ((this.rows[i] || []).some(v => v !== '' && v != null)) return i + 1; return 0; }
  getLastColumn() { let n = 0; this.rows.forEach(r => (r || []).forEach((v, j) => { if (v !== '' && v != null) n = Math.max(n, j + 1); })); return n; }
  getMaxRows() { return 1000; }
  getMaxColumns() { return 26; }
  getRange(a, b, c, d) { return typeof a === 'string' ? new Range(this, 1, 1, 1, 1) : new Range(this, a, b, c || 1, d || 1); }
  setFrozenRows() {}
  deleteRow(r) { this.rows.splice(r - 1, 1); }
}
class Spreadsheet {
  constructor() { this.sheets = [new Sheet('Sheet1')]; }
  getSheetByName(n) { return this.sheets.find(s => s.name === n) || null; }
  insertSheet(n) { const s = new Sheet(n); this.sheets.push(s); return s; }
  getSheets() { return this.sheets; }
  deleteSheet(s) { this.sheets = this.sheets.filter(x => x !== s); }
  getId() { return 'sheet-123'; }
  getUrl() { return 'https://docs.google.com/spreadsheets/d/sheet-123/edit'; }
}

function formatDate(d, tz, f) {
  if (tz !== 'Asia/Kuala_Lumpur') throw new Error('zon masa ujian hanya Asia/Kuala_Lumpur');
  const x = new Date(d.getTime() + 8 * 3600 * 1000);
  const p = n => String(n).padStart(2, '0');
  const map = { yyyy: x.getUTCFullYear(), MM: p(x.getUTCMonth() + 1), dd: p(x.getUTCDate()), HH: p(x.getUTCHours()), mm: p(x.getUTCMinutes()), ss: p(x.getUTCSeconds()) };
  return f.replace(/yyyy|MM|dd|HH|mm|ss|'[^']*'/g, t => (t[0] === "'" ? t.slice(1, -1) : map[t]));
}

/** Pelayan TidyCal palsu. bookings: {token: [booking]}, types: {token: [type]} */
function fakeTidyCal(db) {
  db.calls = [];
  return function fetch(url, opt) {
    db.calls.push(url);
    const auth = (opt.headers.Authorization || '').replace('Bearer ', '');
    const res = (code, body) => ({ getResponseCode: () => code, getContentText: () => JSON.stringify(body), getHeaders: () => ({}) });
    if (!db.bookings[auth]) return res(401, { message: 'Unauthenticated.' });
    const u = new URL(url);
    const q = u.searchParams;
    const page = Number(q.get('page') || 1);
    const pg = (list, per) => {
      const data = list.slice((page - 1) * per, page * per);
      const next = page * per < list.length ? (() => { const n = new URL(url); n.searchParams.set('page', page + 1); return n.toString(); })() : null;
      return res(200, { data, current_page: page, next_page_url: next });
    };
    if (u.pathname === '/api/me') return res(200, { name: db.names[auth], email: auth + '@contoh.my' });
    if (u.pathname === '/api/booking-types') return pg(db.types[auth], 30);
    if (u.pathname === '/api/bookings') {
      const s = q.get('starts_at'), e = q.get('ends_at');
      let list = db.bookings[auth].filter(b => (!s || new Date(b.starts_at) >= new Date(s)) && (!e || new Date(b.ends_at) <= new Date(e)));
      list = q.get('cancelled') === 'true' ? list.filter(b => b.cancelled_at) : list.filter(b => !b.cancelled_at);
      return pg(list, 3);
    }
    return res(404, { message: 'Not found' });
  };
}

function createEnv(tc) {
  const ss = new Spreadsheet();
  const props = {};
  const drive = { files: [] };
  const ui = { alerts: [], dialogs: [] };
  const clock = { now: new Date('2026-11-30T12:00:00Z') };
  let uuid = 0;
  const ctx = {
    console: { log() {}, error() {} },
    SpreadsheetApp: {
      getActiveSpreadsheet: () => ss, openById: () => ss,
      getUi: () => ({ alert: m => ui.alerts.push(m), showModalDialog: (h, t) => ui.dialogs.push(h.html), createMenu: () => ({ addItem() { return this; }, addSeparator() { return this; }, addToUi() {} }) }),
      newDataValidation: () => ({ requireValueInList() { return this; }, build() { return {}; } })
    },
    PropertiesService: { getScriptProperties: () => ({ getProperty: k => (k in props ? props[k] : null), setProperty: (k, v) => { props[k] = String(v); }, deleteProperty: k => { delete props[k]; } }) },
    LockService: { getScriptLock: () => ({ waitLock() {}, releaseLock() {} }) },
    Utilities: {
      formatDate, getUuid: () => '00000000-0000-4000-8000-' + String(++uuid).padStart(12, '0'),
      base64Decode: s => Buffer.from(s, 'base64'), newBlob: (bytes, mime, name) => ({ bytes, mime, name }), sleep() {}
    },
    DriveApp: {
      createFolder: () => ({ getId: () => 'folder-1', createFile: b => { drive.files.push(b); return { getUrl: () => 'https://drive.google.com/file/d/f' + drive.files.length }; } }),
      getFolderById: () => ctx.DriveApp.createFolder()
    },
    UrlFetchApp: { fetch: fakeTidyCal(tc) },
    HtmlService: { createHtmlOutput: html => ({ html, setWidth() { return this; }, setHeight() { return this; } }) },
    ScriptApp: { getService: () => ({ getUrl: () => '' }), getProjectTriggers: () => [], newTrigger: () => ({ timeBased() { return this; }, everyDays() { return this; }, atHour() { return this; }, inTimezone() { return this; }, create() {} }) }
  };
  vm.createContext(ctx);
  const code = ['Logic.gs', 'Code.gs', 'Sync.gs', 'Setup.gs'].map(f => fs.readFileSync(path.join(SRC, f), 'utf8')).join('\n;\n');
  vm.runInContext(code + '\n;sekarang_ = function(){ return __clock.now; };', Object.assign(ctx, { __clock: clock }));
  return { ctx, ss, props, drive, ui, clock, tc };
}

/** Data contoh TidyCal: Coach Amir (disambung) dan Coach Sarah (belum). */
function contohTidyCal() {
  const T = 'tok_amir_0123456789abcdefghij';
  const b = (id, type, startUtc, name, extra) => Object.assign({
    id, booking_type_id: type, starts_at: startUtc, ends_at: new Date(new Date(startUtc).getTime() + 3600e3).toISOString().replace('.000', ''),
    cancelled_at: null, contact: { name, email: name.toLowerCase().replace(/\s+/g, '.') + '@mail.my' }, payment: null
  }, extra || {});
  return {
    token: T,
    names: { [T]: 'Amir Golf' },
    types: { [T]: [{ id: 101, title: 'Private Lesson 60 min (Pakej 10 sesi)' }, { id: 102, title: 'Junior Group Class' }, { id: 103, title: 'Adult Group Sunday' }] },
    bookings: { [T]: [
      b(990, 101, '2026-10-28T02:00:00Z', 'Hafiz'),
      b(1001, 101, '2026-11-03T02:00:00Z', 'Hafiz', { payment: { amount: '2800.00', currency: 'MYR' } }),
      b(1002, 101, '2026-11-10T02:00:00Z', 'Hafiz'),
      b(1003, 101, '2026-11-17T02:00:00Z', 'Hafiz'),
      b(1004, 101, '2026-11-24T02:00:00Z', 'Hafiz', { cancelled_at: '2026-11-20T01:00:00Z' }),
      b(1005, 102, '2026-11-08T01:00:00Z', 'Aina'),
      b(1006, 102, '2026-11-08T01:00:00Z', 'Ben Tan'),
      b(1007, 103, '2026-11-15T01:00:00Z', 'Chong', { cancelled_at: '2026-11-14T01:00:00Z' }),
      b(1008, 101, '2026-11-29T08:00:00Z', 'Mei Ling'),
      b(1100, 101, '2026-12-03T02:00:00Z', 'Hafiz')
    ] }
  };
}

module.exports = { createEnv, contohTidyCal };
