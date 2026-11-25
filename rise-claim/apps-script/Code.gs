/**
 * RISE Coach Claim: web app, kebenaran dan tindakan.
 * Setiap fungsi api_* dipanggil dari Index.html melalui google.script.run.
 */

var SKEMA = {
  Tetapan: ['kunci', 'nilai', 'keterangan'],
  Coach: ['id', 'nama', 'harga_pakej', 'aktif', 'tidycal', 'kunci_link', 'link'],
  JenisSesi: ['coach_id', 'booking_type_id', 'tajuk', 'kategori'],
  Sesi: ['id', 'coach_id', 'bulan', 'tarikh', 'masa', 'student', 'emel', 'kategori', 'sumber', 'sebab', 'lokasi',
    'tc_ids', 'tc_status', 'status', 'tolak_pakej', 'remark', 'disemak', 'bayaran', 'dikemas_kini'],
  Kos: ['id', 'coach_id', 'bulan', 'tarikh', 'perkara', 'jumlah', 'resit_url', 'disemak', 'dikemas_kini'],
  Claim: ['id', 'coach_id', 'bulan', 'status', 'dihantar_pada', 'remark_coach', 'nota_admin', 'diluluskan_pada', 'dibayar_pada', 'jumlah'],
  Pakej: ['id', 'coach_id', 'student', 'emel', 'jumlah_sesi', 'mula', 'dah_guna_sebelum', 'sumber', 'nota']
};
var TETAPAN_ASAL = [
  ['bahagian_coach', '70', 'Peratus harga sesi yang coach dapat'],
  ['harga_group', '300', 'Harga satu group session (RM), junior atau adult'],
  ['sesi_setiap_pakej', '10', 'Bilangan sesi dalam satu pakej private'],
  ['bayar_tak_datang', '0', 'Peratus bahagian coach bila student tak datang'],
  ['bayar_batal_lewat', '0', 'Peratus bahagian coach bila student batal lewat'],
  ['zon_masa', 'Asia/Kuala_Lumpur', 'Zon masa academy'],
  ['url_web_app', '', 'Tampal URL web app (berakhir dengan /exec) selepas deploy']
];

function sekarang_() { return new Date(); }
function props_() { return PropertiesService.getScriptProperties(); }
function ss_() {
  var id = props_().getProperty('SHEET_ID');
  return id ? SpreadsheetApp.openById(id) : SpreadsheetApp.getActiveSpreadsheet();
}

/* ---------- Jadual ringkas atas Google Sheets ---------- */

function Jadual(nama) {
  this.nama = nama;
  this.sh = ss_().getSheetByName(nama);
  if (!this.sh) throw new Error('Tab "' + nama + '" tiada. Jalankan menu RISE Claim → Sediakan sistem.');
  this._baru = [];
}
Jadual.prototype.header = function () {
  if (!this._h) this._h = this.sh.getRange(1, 1, 1, this.sh.getLastColumn()).getValues()[0].map(String);
  return this._h;
};
Jadual.prototype.semua = function () {
  var h = this.header(), kunci = h[0];
  var last = this.sh.getLastRow();
  if (last < 2) return [];
  var v = this.sh.getRange(2, 1, last - 1, h.length).getValues();
  var out = [];
  v.forEach(function (r, i) {
    var o = { _row: i + 2 };
    h.forEach(function (k, j) {
      var v = r[j];
      o[k] = v === null || v === undefined ? '' : (v instanceof Date ? Utilities.formatDate(v, 'Asia/Kuala_Lumpur', 'yyyy-MM-dd') : String(v));
    });
    if (o[kunci] !== '') out.push(o);
  });
  return out;
};
Jadual.prototype._baris = function (o) {
  return this.header().map(function (k) {
    var v = o[k];
    if (v === undefined || v === null) return '';
    v = String(v);
    return /^[=+@]/.test(v) ? "'" + v : v;
  });
};
Jadual.prototype.tulis = function (o) {
  if (o._row) this.sh.getRange(o._row, 1, 1, this.header().length).setValues([this._baris(o)]);
  else this._baru.push(o);
  return o;
};
Jadual.prototype.simpan = function () {
  if (!this._baru.length) return;
  var rows = this._baru.map(this._baris, this);
  var mula = this.sh.getLastRow() + 1;
  this.sh.getRange(mula, 1, rows.length, rows[0].length).setValues(rows);
  this._baru.forEach(function (o, i) { o._row = mula + i; });
  this._baru = [];
};
Jadual.prototype.buang = function (o) { this.sh.deleteRow(o._row); };

function cfg_() {
  var o = {};
  new Jadual('Tetapan').semua().forEach(function (r) { o[r.kunci] = r.nilai; });
  TETAPAN_ASAL.forEach(function (t) { if (o[t[0]] === undefined || o[t[0]] === '') o[t[0]] = t[1]; });
  return o;
}
function tz_() { try { return cfg_().zon_masa || 'Asia/Kuala_Lumpur'; } catch (e) { return 'Asia/Kuala_Lumpur'; } }
function fmt_(d, f) { return Utilities.formatDate(d, tz_(), f); }
function hariIni_() { return fmt_(sekarang_(), 'yyyy-MM-dd'); }
function cop_() { return fmt_(sekarang_(), 'yyyy-MM-dd HH:mm'); }
function idBaru_(p) { return p + Utilities.getUuid().replace(/-/g, '').slice(0, 10); }
function coachAktif_() {
  return new Jadual('Coach').semua().filter(function (c) { return c.nama && !/^tidak$/i.test(String(c.aktif).trim()); });
}
function kunci_(fn) {
  var lock = LockService.getScriptLock();
  lock.waitLock(20000);
  try { return fn(); } finally { lock.releaseLock(); }
}

/* ---------- Web app ---------- */

function doGet(e) {
  var t = HtmlService.createTemplateFromFile('Index');
  var k = (e && e.parameter && e.parameter.k) || '';
  t.kunciJson = JSON.stringify(String(k)).replace(/</g, '\\u003c');
  return t.evaluate()
    .setTitle('RISE Coach Claim')
    .addMetaTag('viewport', 'width=device-width, initial-scale=1, viewport-fit=cover');
}

function sahkan_(key) {
  key = String(key || '').trim();
  if (!key) throw new Error('Link ni tak lengkap. Minta link peribadi daripada admin.');
  if (key === props_().getProperty('ADMIN_KEY')) return { role: 'admin' };
  var c = coachAktif_().filter(function (c) { return String(c.kunci_link) === key; })[0];
  if (!c) throw new Error('Link ni dah tak sah. Minta link baru daripada admin.');
  return { role: 'coach', coach: c };
}
function adminSahaja_(a) { if (a.role !== 'admin') throw new Error('Hanya admin boleh buat ni.'); }

function senaraiBulan_(hariIni) {
  var b = hariIni.slice(0, 7), out = [];
  for (var i = 0; i < 6; i++) { out.push(b); b = bulanSebelum_(b); }
  return out;
}
function paparan_(a, bulan) {
  var hariIni = hariIni_();
  if (!/^\d{4}-\d{2}$/.test(String(bulan || ''))) bulan = hariIni.slice(0, 7);
  var cfg = cfg_();
  var sesi = new Jadual('Sesi').semua(), kos = new Jadual('Kos').semua();
  var claim = new Jadual('Claim').semua(), pakej = new Jadual('Pakej').semua();
  var senarai = a.role === 'coach' ? [a.coach] : coachAktif_();
  var p = props_();
  var coaches = senarai.map(function (c) {
    var r = ringkasCoach_(c, bulan, hariIni, cfg, sesi, kos, claim, pakej);
    r.disambung = !!p.getProperty('TC_' + c.id);
    r.akaunTc = c.tidycal || '';
    r.segerak = p.getProperty('SYNC_' + c.id) || '';
    r.ralatSegerak = p.getProperty('SYNCERR_' + c.id) || '';
    return r;
  });
  return {
    role: a.role, bulan: bulan, hariIni: hariIni, bulanPilihan: senaraiBulan_(hariIni),
    cfg: { bahagian_coach: num_(cfg.bahagian_coach, 70), harga_group: num_(cfg.harga_group), sesi_setiap_pakej: num_(cfg.sesi_setiap_pakej, 10),
      bayar_tak_datang: num_(cfg.bayar_tak_datang), bayar_batal_lewat: num_(cfg.bayar_batal_lewat) },
    coaches: coaches,
    sheetUrl: a.role === 'admin' ? ss_().getUrl() : ''
  };
}

/* ---------- Bacaan ---------- */

function api_load(key, bulan) { return paparan_(sahkan_(key), bulan); }

/* ---------- Tindakan coach ---------- */

function claimRow_(coachId, bulan) {
  var t = new Jadual('Claim');
  var r = t.semua().filter(function (c) { return c.coach_id === coachId && c.bulan === bulan; })[0];
  return { t: t, r: r };
}
function pastikanBolehUbah_(coachId, bulan) {
  var r = claimRow_(coachId, bulan).r;
  if (r && CLAIM_BOLEH_UBAH.indexOf(r.status) < 0) throw new Error('Claim bulan ni dah dihantar. Minta admin pulangkan dulu kalau nak ubah.');
}
function sesiCoach_(a, id) {
  if (a.role !== 'coach') throw new Error('Hanya coach boleh ubah sesi.');
  var t = new Jadual('Sesi');
  var s = t.semua().filter(function (x) { return x.id === id; })[0];
  if (!s || s.coach_id !== a.coach.id) throw new Error('Sesi tak dijumpai.');
  pastikanBolehUbah_(s.coach_id, s.bulan);
  return { t: t, s: s };
}
function teks_(v, max) { return String(v || '').replace(/\s+/g, ' ').trim().slice(0, max || 500); }

function api_mark(key, bulan, id, status, deduct, remark) {
  var a = sahkan_(key);
  return kunci_(function () {
    if (['pending', 'done', 'noshow', 'late'].indexOf(status) < 0) throw new Error('Status tak dikenali.');
    var x = sesiCoach_(a, id);
    if (status !== 'pending' && x.s.tarikh > hariIni_()) throw new Error('Sesi ni belum berlaku lagi.');
    if (x.s.status === 'batal' && status !== 'pending') {
      // Booking dibatalkan dalam TidyCal tapi student datang juga: dibenarkan, admin akan nampak dalam semakan.
    }
    x.s.status = status;
    x.s.tolak_pakej = status === 'noshow' && deduct ? 'Ya' : '';
    if (remark !== undefined && remark !== null && teks_(remark)) x.s.remark = teks_(remark);
    x.s.dikemas_kini = cop_();
    x.t.tulis(x.s);
    return paparan_(a, bulan);
  });
}
function api_remark(key, bulan, id, text) {
  var a = sahkan_(key);
  return kunci_(function () {
    var x = sesiCoach_(a, id);
    x.s.remark = teks_(text);
    x.s.dikemas_kini = cop_();
    x.t.tulis(x.s);
    return paparan_(a, bulan);
  });
}
function api_addWalkin(key, bulan, o) {
  var a = sahkan_(key);
  if (a.role !== 'coach') throw new Error('Hanya coach boleh tambah sesi.');
  return kunci_(function () {
    var tarikh = String(o.tarikh || '');
    if (!/^\d{4}-\d{2}-\d{2}$/.test(tarikh)) throw new Error('Tarikh tak sah.');
    if (tarikh > hariIni_()) throw new Error('Walk-in hanya untuk sesi yang dah berlaku.');
    if (!KATEGORI[o.kategori]) throw new Error('Jenis sesi tak sah.');
    if (!teks_(o.student)) throw new Error('Isi nama student.');
    pastikanBolehUbah_(a.coach.id, tarikh.slice(0, 7));
    var t = new Jadual('Sesi');
    t.tulis({ id: idBaru_('m'), coach_id: a.coach.id, bulan: tarikh.slice(0, 7), tarikh: tarikh, masa: teks_(o.masa, 5) || '00:00',
      student: teks_(o.student, 80), emel: '', kategori: o.kategori, sumber: 'manual', sebab: teks_(o.sebab, 30) || 'Walk-in',
      lokasi: teks_(o.lokasi, 40), tc_status: '', status: 'done', remark: teks_(o.remark), dikemas_kini: cop_() });
    t.simpan();
    return paparan_(a, bulan);
  });
}
function api_deleteSession(key, bulan, id) {
  var a = sahkan_(key);
  return kunci_(function () {
    var x = sesiCoach_(a, id);
    if (x.s.sumber !== 'manual') throw new Error('Hanya sesi walk-in boleh dibuang. Booking TidyCal perlu dibatalkan dalam TidyCal.');
    x.t.buang(x.s);
    return paparan_(a, bulan);
  });
}
function folderResit_() {
  var p = props_(), id = p.getProperty('RESIT_FOLDER');
  if (id) { try { return DriveApp.getFolderById(id); } catch (e) { /* folder dipadam: buat baru */ } }
  var f = DriveApp.createFolder('RISE Claim: Resit');
  p.setProperty('RESIT_FOLDER', f.getId());
  return f;
}
function api_addExpense(key, bulan, o) {
  var a = sahkan_(key);
  if (a.role !== 'coach') throw new Error('Hanya coach boleh tambah kos.');
  return kunci_(function () {
    var tarikh = String(o.tarikh || '');
    if (!/^\d{4}-\d{2}-\d{2}$/.test(tarikh)) throw new Error('Tarikh tak sah.');
    var jumlah = num_(o.jumlah);
    if (!(jumlah > 0)) throw new Error('Isi jumlah lebih daripada RM0.');
    if (!teks_(o.perkara)) throw new Error('Isi perkara.');
    pastikanBolehUbah_(a.coach.id, tarikh.slice(0, 7));
    var url = '';
    if (o.fail && o.fail.data) {
      if (o.fail.data.length > 7000000) throw new Error('Gambar resit terlalu besar. Had 5MB.');
      var blob = Utilities.newBlob(Utilities.base64Decode(o.fail.data), o.fail.mime || 'application/octet-stream',
        a.coach.nama + ' ' + tarikh + ' ' + teks_(o.fail.name, 60));
      url = folderResit_().createFile(blob).getUrl();
    }
    var t = new Jadual('Kos');
    t.tulis({ id: idBaru_('k'), coach_id: a.coach.id, bulan: tarikh.slice(0, 7), tarikh: tarikh, perkara: teks_(o.perkara, 120),
      jumlah: jumlah.toFixed(2), resit_url: url, dikemas_kini: cop_() });
    t.simpan();
    return paparan_(a, bulan);
  });
}
function api_deleteExpense(key, bulan, id) {
  var a = sahkan_(key);
  return kunci_(function () {
    var t = new Jadual('Kos');
    var k = t.semua().filter(function (x) { return x.id === id; })[0];
    if (!k || a.role !== 'coach' || k.coach_id !== a.coach.id) throw new Error('Kos tak dijumpai.');
    pastikanBolehUbah_(k.coach_id, k.bulan);
    t.buang(k);
    return paparan_(a, bulan);
  });
}
function api_submit(key, bulan, remark) {
  var a = sahkan_(key);
  if (a.role !== 'coach') throw new Error('Hanya coach boleh hantar claim.');
  return kunci_(function () {
    pastikanBolehUbah_(a.coach.id, bulan);
    var cfg = cfg_(), hariIni = hariIni_();
    var tS = new Jadual('Sesi'), semua = tS.semua();
    var r = ringkasCoach_(a.coach, bulan, hariIni, cfg, semua, new Jadual('Kos').semua(), new Jadual('Claim').semua(), new Jadual('Pakej').semua());
    if (r.totals.pending) throw new Error('Tanda ' + r.totals.pending + ' sesi lagi sebelum hantar claim.');
    if (r.totals.upcoming) throw new Error('Masih ada ' + r.totals.upcoming + ' sesi akan datang bulan ni. Hantar claim selepas sesi terakhir.');
    semua.filter(function (s) { return s.coach_id === a.coach.id && s.bulan === bulan; }).forEach(function (s) {
      s.bayaran = bundar_(kiraBayaran_(Object.assign({}, s, { bayaran: '' }), a.coach, cfg)).toFixed(2);
      tS.tulis(s);
    });
    var c = claimRow_(a.coach.id, bulan);
    var row = c.r || { id: idBaru_('cl'), coach_id: a.coach.id, bulan: bulan };
    row.status = 'submitted';
    row.dihantar_pada = cop_();
    row.remark_coach = teks_(remark);
    row.jumlah = r.totals.total.toFixed(2);
    c.t.tulis(row); c.t.simpan();
    return paparan_(a, bulan);
  });
}
function api_saveToken(key, bulan, token) {
  var a = sahkan_(key);
  if (a.role !== 'coach') throw new Error('Hanya coach boleh sambung TidyCal sendiri.');
  token = String(token || '').trim();
  if (token.length < 20) throw new Error('Token tu nampak tak lengkap. Salin semula dari TidyCal.');
  var me = tcMe_(token);
  props_().setProperty('TC_' + a.coach.id, token);
  kunci_(function () {
    var t = new Jadual('Coach');
    var c = t.semua().filter(function (x) { return x.id === a.coach.id; })[0];
    c.tidycal = 'Disambung: ' + (me.name || me.email || 'akaun TidyCal');
    t.tulis(c);
  });
  segerakCoach_(a.coach);
  return paparan_(sahkan_(key), bulan);
}
function api_sync(key, bulan) {
  var a = sahkan_(key);
  if (a.role === 'coach') segerakCoach_(a.coach);
  else syncSemua();
  return paparan_(a, bulan);
}

/* ---------- Tindakan admin ---------- */

function api_check(key, bulan, jenis, id) {
  var a = sahkan_(key); adminSahaja_(a);
  return kunci_(function () {
    var t = new Jadual(jenis === 'kos' ? 'Kos' : 'Sesi');
    var r = t.semua().filter(function (x) { return x.id === id; })[0];
    if (!r) throw new Error('Rekod tak dijumpai.');
    r.disemak = 'Ya';
    t.tulis(r);
    return paparan_(a, bulan);
  });
}
function ubahClaim_(a, bulan, coachId, dari, fn) {
  adminSahaja_(a);
  return kunci_(function () {
    var c = claimRow_(coachId, bulan);
    if (!c.r || dari.indexOf(c.r.status) < 0) throw new Error('Status claim dah berubah. Muat semula halaman.');
    fn(c.r);
    c.t.tulis(c.r);
    return paparan_(a, bulan);
  });
}
function api_approve(key, bulan, coachId) {
  return ubahClaim_(sahkan_(key), bulan, coachId, ['submitted'], function (r) { r.status = 'approved'; r.diluluskan_pada = cop_(); });
}
function api_return(key, bulan, coachId, note) {
  if (!teks_(note)) throw new Error('Tulis apa yang coach perlu betulkan.');
  return ubahClaim_(sahkan_(key), bulan, coachId, ['submitted', 'approved'], function (r) {
    r.status = 'returned'; r.nota_admin = teks_(note, 1500); r.diluluskan_pada = '';
    var t = new Jadual('Sesi');
    t.semua().filter(function (s) { return s.coach_id === coachId && s.bulan === bulan && s.bayaran !== ''; })
      .forEach(function (s) { s.bayaran = ''; t.tulis(s); });
  });
}
function api_paid(key, bulan, coachId) {
  return ubahClaim_(sahkan_(key), bulan, coachId, ['approved'], function (r) { r.status = 'paid'; r.dibayar_pada = cop_(); });
}
function api_saveSettings(key, bulan, o) {
  var a = sahkan_(key); adminSahaja_(a);
  return kunci_(function () {
    var had = { bahagian_coach: [0, 100], harga_group: [0, 100000], sesi_setiap_pakej: [1, 100], bayar_tak_datang: [0, 100], bayar_batal_lewat: [0, 100] };
    var t = new Jadual('Tetapan'), rows = t.semua();
    Object.keys(o.cfg || {}).forEach(function (k) {
      if (!had[k]) return;
      var v = num_(o.cfg[k], NaN);
      if (!isFinite(v) || v < had[k][0] || v > had[k][1]) throw new Error('Nilai untuk ' + k + ' tak sah.');
      var r = rows.filter(function (x) { return x.kunci === k; })[0];
      if (r) { r.nilai = String(v); t.tulis(r); } else t.tulis({ kunci: k, nilai: String(v) });
    });
    t.simpan();
    var tc = new Jadual('Coach');
    tc.semua().forEach(function (c) {
      if (!o.pakej || o.pakej[c.id] === undefined) return;
      var v = num_(o.pakej[c.id], NaN);
      if (!isFinite(v) || v < 0) throw new Error('Harga pakej ' + c.nama + ' tak sah.');
      c.harga_pakej = String(v); tc.tulis(c);
    });
    return paparan_(a, bulan);
  });
}
