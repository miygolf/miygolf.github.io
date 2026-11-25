/**
 * RISE Coach Claim: segerak booking dari TidyCal.
 * Setiap coach simpan personal token TidyCal sendiri (Script Properties: TC_<coach id>).
 * API: https://tidycal.com/developer/docs
 */

var TC_API = 'https://tidycal.com/api';

function qs_(params) {
  var p = Object.keys(params || {}).filter(function (k) { return params[k] !== undefined && params[k] !== ''; })
    .map(function (k) { return encodeURIComponent(k) + '=' + encodeURIComponent(params[k]); });
  return p.length ? '?' + p.join('&') : '';
}
function tcFetch_(token, url) {
  for (var cuba = 0; cuba < 4; cuba++) {
    var r = UrlFetchApp.fetch(url, { headers: { Authorization: 'Bearer ' + token, Accept: 'application/json' }, muteHttpExceptions: true });
    var code = r.getResponseCode();
    if (code === 429) {
      var h = r.getHeaders() || {};
      Utilities.sleep(Math.min(60, num_(h['Retry-After'] || h['retry-after'], 5)) * 1000);
      continue;
    }
    if (code === 401 || code === 403) throw new Error('Token TidyCal tak sah atau dah dibatalkan. Buat token baru dan sambung semula.');
    if (code >= 300) throw new Error('TidyCal balas ralat ' + code + '.');
    return JSON.parse(r.getContentText());
  }
  throw new Error('TidyCal terlalu sibuk. Cuba lagi sekejap lagi.');
}
function tcSenarai_(token, path, params) {
  var out = [], url = TC_API + path + qs_(params), had = 0;
  while (url && had++ < 50) {
    var j = tcFetch_(token, url);
    (j.data || []).forEach(function (x) { out.push(x); });
    url = j.next_page_url || (j.links && !Array.isArray(j.links) && j.links.next) || null;
  }
  return out;
}
function tcMe_(token) {
  var j = tcFetch_(token, TC_API + '/me');
  return j.data || j;
}
function isoTempatan_(tarikh) {
  // 'yyyy-MM-dd' tengah malam waktu academy, dalam bentuk ISO 8601 dengan offset
  var tz = tz_();
  var d = new Date(tarikh + 'T00:00:00Z');
  var offsetMin = Math.round((new Date(Utilities.formatDate(d, tz, "yyyy-MM-dd'T'HH:mm:ss") + 'Z') - d) / 60000);
  return new Date(d.getTime() - offsetMin * 60000).toISOString();
}

/** Segerak bulan lepas dan bulan ni untuk seorang coach. */
function segerakCoach_(coach) {
  var p = props_();
  var token = p.getProperty('TC_' + coach.id);
  if (!token) return { coach: coach.nama, langkau: 'Belum sambung TidyCal' };
  try {
    var hasil = kunci_(function () { return segerakCoachDalam_(coach, token); });
    p.setProperty('SYNC_' + coach.id, cop_());
    p.deleteProperty('SYNCERR_' + coach.id);
    return hasil;
  } catch (e) {
    p.setProperty('SYNCERR_' + coach.id, cop_() + ': ' + e.message);
    throw e;
  }
}
function segerakCoachDalam_(coach, token) {
  var tz = tz_(), cfg = cfg_();
  var bulanIni = hariIni_().slice(0, 7), bulanLepas = bulanSebelum_(bulanIni);
  var julat = { starts_at: isoTempatan_(bulanLepas + '-01'), ends_at: isoTempatan_(bulanSelepas_(bulanIni) + '-01') };

  var ikutId = {};
  tcSenarai_(token, '/bookings', julat).forEach(function (b) { ikutId[b.id] = b; });
  tcSenarai_(token, '/bookings', Object.assign({ cancelled: 'true' }, julat)).forEach(function (b) { ikutId[b.id] = b; });
  var bookings = Object.keys(ikutId).map(function (k) { return ikutId[k]; });

  // Jenis sesi: booking type baru masuk ke tab JenisSesi dengan kategori tekaan, admin boleh ubah.
  var tJ = new Jadual('JenisSesi'), jenis = tJ.semua().filter(function (j) { return j.coach_id === coach.id; });
  var adaJenis = {};
  jenis.forEach(function (j) { adaJenis[String(j.booking_type_id)] = j; });
  tcSenarai_(token, '/booking-types', {}).forEach(function (bt) {
    var j = adaJenis[String(bt.id)];
    if (!j) { j = { coach_id: coach.id, booking_type_id: String(bt.id), tajuk: bt.title, kategori: tekaKategori_(bt.title) }; tJ.tulis(j); adaJenis[String(bt.id)] = j; }
    else if (j.tajuk !== bt.title) { j.tajuk = bt.title; tJ.tulis(j); }
  });
  tJ.simpan();
  bookings.forEach(function (b) {
    if (!adaJenis[String(b.booking_type_id)]) {
      var j = { coach_id: coach.id, booking_type_id: String(b.booking_type_id), tajuk: '(jenis sesi ' + b.booking_type_id + ')', kategori: 'pvt' };
      tJ.tulis(j); adaJenis[String(b.booking_type_id)] = j;
    }
  });
  tJ.simpan();

  var fmt = function (iso) {
    var d = new Date(iso);
    return { tarikh: Utilities.formatDate(d, tz, 'yyyy-MM-dd'), masa: Utilities.formatDate(d, tz, 'HH:mm') };
  };
  var masuk = bookingKeSesi_(bookings, coach.id, function (id) { var j = adaJenis[String(id)]; return j && j.kategori; }, fmt);

  var tS = new Jadual('Sesi');
  var sedia = tS.semua().filter(function (s) { return s.coach_id === coach.id; });
  var kunciBeku = {};
  new Jadual('Claim').semua().forEach(function (c) {
    if (c.coach_id === coach.id && CLAIM_BOLEH_UBAH.indexOf(c.status) < 0) kunciBeku[c.bulan] = true;
  });
  var tetingkap = [bulanLepas, bulanIni].filter(function (b) { return !kunciBeku[b]; });
  var ubah = gabungSesi_(sedia, masuk.filter(function (m) { return !kunciBeku[m.bulan]; }), tetingkap, cop_());
  ubah.forEach(function (s) { tS.tulis(s); });
  tS.simpan();

  // Pakej: booking private yang dibayar sekurang-kurangnya separuh harga pakej dikira sebagai pembelian pakej.
  var tP = new Jadual('Pakej'), adaPakej = {};
  tP.semua().forEach(function (x) { adaPakej[x.id] = true; });
  var harga = num_(coach.harga_pakej), pakejBaru = 0;
  masuk.forEach(function (m) {
    if (m.kategori !== 'pvt' || m.tc_status !== 'ditempah' || !harga || m.bayaranTc < harga * 0.5) return;
    var id = 'tcp-' + m.tc_ids;
    if (adaPakej[id]) return;
    tP.tulis({ id: id, coach_id: coach.id, student: m.student, emel: m.emel, jumlah_sesi: String(num_(cfg.sesi_setiap_pakej, 10)),
      mula: m.tarikh, dah_guna_sebelum: '0', sumber: 'TidyCal (bayaran RM' + m.bayaranTc.toFixed(2) + ')', nota: '' });
    adaPakej[id] = true; pakejBaru++;
  });
  tP.simpan();
  return { coach: coach.nama, booking: bookings.length, berubah: ubah.length, pakejBaru: pakejBaru };
}

/** Dipanggil oleh trigger harian dan butang "Segerak semua". */
function syncSemua() {
  var hasil = [];
  coachAktif_().forEach(function (c) {
    try { hasil.push(segerakCoach_(c)); }
    catch (e) { hasil.push({ coach: c.nama, ralat: e.message }); console.error('Segerak ' + c.nama + ': ' + e.message); }
  });
  console.log(JSON.stringify(hasil));
  return hasil;
}
