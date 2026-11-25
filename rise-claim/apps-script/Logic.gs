/**
 * RISE Coach Claim: kiraan tulen.
 * Fail ni tak sentuh Google Sheets, Drive atau TidyCal, supaya semua kiraan boleh diuji.
 */

var KATEGORI = {
  pvt: 'Private (pakej)',
  jgroup: 'Junior group',
  agroup: 'Adult group'
};
var STATUS_LABEL = {
  pending: 'Perlu disahkan',
  done: 'Selesai',
  noshow: 'Tak datang',
  late: 'Batal lewat',
  batal: 'Dibatalkan dalam TidyCal'
};
var CLAIM_BOLEH_UBAH = ['', 'draft', 'returned'];

function num_(v, d) {
  if (v === '' || v === null || v === undefined) return d || 0;
  var n = Number(String(v).replace(/[^0-9.\-]/g, ''));
  return isFinite(n) ? n : (d || 0);
}
function ya_(v) {
  return v === true || /^(ya|true|yes|1)$/i.test(String(v || '').trim());
}
function byTime_(a, b) {
  return (String(a.tarikh) + String(a.masa)).localeCompare(String(b.tarikh) + String(b.masa));
}
function bulanSebelum_(bulan) {
  var y = Number(bulan.slice(0, 4)), m = Number(bulan.slice(5, 7)) - 1;
  if (m === 0) { y--; m = 12; }
  return y + '-' + String(m).padStart(2, '0');
}
function bulanSelepas_(bulan) {
  var y = Number(bulan.slice(0, 4)), m = Number(bulan.slice(5, 7)) + 1;
  if (m === 13) { y++; m = 1; }
  return y + '-' + String(m).padStart(2, '0');
}

/* ---------- Bayaran ---------- */

function hargaSesi_(s, coach, cfg) {
  if (s.kategori === 'pvt') return num_(coach.harga_pakej) / Math.max(1, num_(cfg.sesi_setiap_pakej, 10));
  return num_(cfg.harga_group);
}
function bahagianCoach_(s, coach, cfg) {
  return hargaSesi_(s, coach, cfg) * num_(cfg.bahagian_coach, 70) / 100;
}
/** Bayaran untuk satu sesi. Bila claim dihantar, nilai ni dibekukan dalam lajur `bayaran`. */
function kiraBayaran_(s, coach, cfg) {
  if (s.bayaran !== '' && s.bayaran !== null && s.bayaran !== undefined) return num_(s.bayaran);
  var cut = bahagianCoach_(s, coach, cfg);
  if (s.status === 'done') return cut;
  if (s.status === 'noshow') return cut * num_(cfg.bayar_tak_datang) / 100;
  if (s.status === 'late') return cut * num_(cfg.bayar_batal_lewat) / 100;
  return 0;
}
function bundar_(n) { return Math.round(n * 100) / 100; }

/* ---------- Pakej student ---------- */

function gunaPakej_(s) {
  return s.kategori === 'pvt' && s.sumber === 'tidycal' &&
    (s.status === 'done' || s.status === 'pending' || (s.status === 'noshow' && ya_(s.tolak_pakej)));
}
function kunciStudent_(o) {
  var e = String(o.emel || '').trim().toLowerCase();
  return e || ('nama:' + String(o.student || '').trim().toLowerCase());
}
/**
 * Agih setiap sesi private kepada pakej student, ikut urutan masa (pakej paling awal dulu).
 * Pulangkan peta idSesi -> {n, total, over, tiada} dan senarai pakej dengan baki.
 */
function agihPakej_(sesiCoach, pakejCoach) {
  var kumpulan = {};
  function g(k) { return kumpulan[k] || (kumpulan[k] = { p: [], s: [] }); }
  pakejCoach.forEach(function (p) { g(kunciStudent_(p)).p.push(p); });
  sesiCoach.filter(gunaPakej_).forEach(function (s) { g(kunciStudent_(s)).s.push(s); });
  var peta = {}, senarai = [];
  Object.keys(kumpulan).forEach(function (k) {
    var grp = kumpulan[k];
    var ps = grp.p.slice().sort(function (a, b) { return String(a.mula).localeCompare(String(b.mula)); })
      .map(function (p) { return { p: p, used: num_(p.dah_guna_sebelum), total: Math.max(1, num_(p.jumlah_sesi, 10)) }; });
    grp.s.sort(byTime_).forEach(function (s) {
      var sasaran = null, akhir = null;
      for (var i = 0; i < ps.length; i++) {
        if (String(ps[i].p.mula) > String(s.tarikh)) continue;
        akhir = ps[i];
        if (!sasaran && ps[i].used < ps[i].total) sasaran = ps[i];
      }
      if (sasaran) { sasaran.used++; peta[s.id] = { n: sasaran.used, total: sasaran.total, over: false }; }
      else if (akhir) { akhir.used++; peta[s.id] = { n: akhir.used, total: akhir.total, over: true }; }
      else peta[s.id] = { n: 0, total: 0, over: true, tiada: true };
    });
    ps.forEach(function (x) {
      senarai.push({ id: x.p.id, student: x.p.student || x.p.emel, emel: x.p.emel, mula: x.p.mula,
        total: x.total, sebelum: num_(x.p.dah_guna_sebelum), digunakan: x.used, baki: x.total - x.used, sumber: x.p.sumber });
    });
  });
  senarai.sort(function (a, b) { return a.baki - b.baki || String(a.student).localeCompare(String(b.student)); });
  return { peta: peta, pakej: senarai };
}

/* ---------- TidyCal -> sesi ---------- */

function tekaKategori_(tajuk) {
  var t = String(tajuk || '').toLowerCase();
  var group = /group|kumpulan|class|kelas|clinic/.test(t);
  if (group && /junior|kids|kanak/.test(t)) return 'jgroup';
  if (group) return 'agroup';
  return 'pvt';
}
/**
 * Tukar booking TidyCal kepada baris sesi.
 * Private: satu booking = satu sesi. Group: semua booking pada slot yang sama = satu sesi
 * (coach dibayar ikut sesi group, bukan ikut bilangan student).
 * fmt(iso) -> {tarikh:'yyyy-MM-dd', masa:'HH:mm'} dalam zon masa academy.
 */
function bookingKeSesi_(bookings, coachId, kategoriOf, fmt) {
  var out = [], group = {};
  bookings.forEach(function (b) {
    var kat = kategoriOf(b.booking_type_id);
    if (!kat || kat === 'abaikan' || !KATEGORI[kat]) return;
    var w = fmt(b.starts_at);
    var nama = (b.contact && b.contact.name) || '';
    var emel = (b.contact && b.contact.email) || '';
    var batal = !!b.cancelled_at;
    if (kat === 'pvt') {
      out.push({ id: 'tc-' + b.id, coach_id: coachId, bulan: w.tarikh.slice(0, 7), tarikh: w.tarikh, masa: w.masa,
        student: nama || emel, emel: emel, kategori: kat, sumber: 'tidycal', tc_ids: String(b.id),
        tc_status: batal ? 'dibatalkan' : 'ditempah', bayaranTc: b.payment ? num_(b.payment.amount) : 0 });
    } else {
      var key = 'tcg-' + coachId + '-' + b.booking_type_id + '-' + w.tarikh + '-' + w.masa.replace(':', '');
      var grp = group[key] || (group[key] = { id: key, tarikh: w.tarikh, masa: w.masa, kategori: kat, ids: [], aktif: [], semua: [] });
      grp.ids.push(String(b.id));
      grp.semua.push(nama || emel);
      if (!batal) grp.aktif.push(nama || emel);
    }
  });
  Object.keys(group).forEach(function (k) {
    var grp = group[k];
    var nama = grp.aktif.length ? grp.aktif : grp.semua;
    out.push({ id: grp.id, coach_id: coachId, bulan: grp.tarikh.slice(0, 7), tarikh: grp.tarikh, masa: grp.masa,
      student: KATEGORI[grp.kategori] + ': ' + nama.join(', '), emel: '', kategori: grp.kategori, sumber: 'tidycal',
      tc_ids: grp.ids.join(','), tc_status: grp.aktif.length ? 'ditempah' : 'dibatalkan', bayaranTc: 0 });
  });
  return out;
}
/**
 * Gabung sesi dari TidyCal dengan baris sedia ada tanpa memadam apa yang coach dah tanda.
 * Pulangkan baris yang perlu ditulis (baru atau berubah).
 */
function gabungSesi_(sedia, masuk, bulanTetingkap, cop) {
  var ikutId = {};
  sedia.forEach(function (s) { ikutId[s.id] = s; });
  var dilihat = {}, ubah = [];
  var MEDAN = ['bulan', 'tarikh', 'masa', 'student', 'emel', 'kategori', 'tc_ids', 'tc_status'];
  masuk.forEach(function (m) {
    dilihat[m.id] = true;
    var s = ikutId[m.id];
    if (!s) {
      var baru = {};
      MEDAN.forEach(function (f) { baru[f] = m[f]; });
      baru.id = m.id; baru.coach_id = m.coach_id; baru.sumber = 'tidycal';
      baru.status = m.tc_status === 'dibatalkan' ? 'batal' : 'pending';
      baru.dikemas_kini = cop;
      ubah.push(baru);
      return;
    }
    var berubah = false;
    MEDAN.forEach(function (f) { if (String(s[f]) !== String(m[f])) { s[f] = m[f]; berubah = true; } });
    if (s.status === 'pending' && m.tc_status === 'dibatalkan') { s.status = 'batal'; berubah = true; }
    if (s.status === 'batal' && m.tc_status === 'ditempah') { s.status = 'pending'; berubah = true; }
    if (berubah) { s.dikemas_kini = cop; ubah.push(s); }
  });
  sedia.forEach(function (s) {
    if (s.sumber !== 'tidycal' || dilihat[s.id] || bulanTetingkap.indexOf(s.bulan) < 0) return;
    if (s.tc_status === 'dibatalkan' && s.status !== 'pending') return;
    s.tc_status = 'dibatalkan';
    if (s.status === 'pending') s.status = 'batal';
    s.dikemas_kini = cop;
    ubah.push(s);
  });
  return ubah;
}

/* ---------- Ringkasan untuk paparan ---------- */

function barisSesi_(s) {
  var d = String(s.tarikh).slice(8, 10).replace(/^0/, '');
  return d + ' ' + namaBulanPendek_(String(s.tarikh).slice(5, 7)) + ', ' + s.masa + ' · ' + s.student + ' · ' + (KATEGORI[s.kategori] || s.kategori);
}
function namaBulanPendek_(mm) {
  return ['Jan', 'Feb', 'Mac', 'Apr', 'Mei', 'Jun', 'Jul', 'Ogo', 'Sep', 'Okt', 'Nov', 'Dis'][Number(mm) - 1] || mm;
}
function auditCoach_(sesiBulan, kosBulan, peta, hariIni) {
  var checks = [
    { key: 'pending', label: 'Semua booking TidyCal dah disahkan coach', kind: 'warn', fixable: false,
      items: sesiBulan.filter(function (s) { return s.status === 'pending' && s.tarikh <= hariIni; }),
      why: function () { return 'Coach belum tanda'; } },
    { key: 'tc', label: 'Status sama dengan TidyCal', kind: 'bad', fixable: true,
      items: sesiBulan.filter(function (s) { return s.tc_status === 'dibatalkan' && s.status === 'done' && !ya_(s.disemak); }),
      why: function () { return 'Batal dalam TidyCal, tapi coach tanda Selesai'; } },
    { key: 'pkg', label: 'Pakej student masih ada baki', kind: 'bad', fixable: true,
      items: sesiBulan.filter(function (s) { var p = peta[s.id]; return s.status === 'done' && p && p.over && !ya_(s.disemak); }),
      why: function (s) {
        var p = peta[s.id];
        return p.tiada ? 'Tiada pakej direkod untuk student ni' :
          'Sesi ke-' + p.n + ' daripada pakej ' + p.total + ' sesi. Semak pakej baru dah dibayar';
      } },
    { key: 'manual', label: 'Walk-in disemak dengan rekod kaunter', kind: 'warn', fixable: true,
      items: sesiBulan.filter(function (s) { return s.sumber === 'manual' && s.status !== 'batal' && !ya_(s.disemak); }),
      why: function (s) { return (s.sebab || 'Manual') + ', tiada dalam TidyCal'; } },
    { key: 'rcpt', label: 'Semua kos tambahan ada resit', kind: 'warn', fixable: true, kos: true,
      items: kosBulan.filter(function (k) { return !k.resit_url && !ya_(k.disemak); }),
      why: function () { return 'Tiada resit'; } }
  ];
  return checks.map(function (c) {
    return { key: c.key, label: c.label, kind: c.kind, fixable: c.fixable,
      items: c.items.map(function (it) {
        return c.kos
          ? { id: it.id, jenis: 'kos', line: it.tarikh + ' · ' + it.perkara + ' · RM' + num_(it.jumlah).toFixed(2), why: c.why(it), remark: '' }
          : { id: it.id, jenis: 'sesi', line: barisSesi_(it), why: c.why(it), remark: it.remark || '' };
      }) };
  });
}

/**
 * Semua yang paparan perlukan untuk seorang coach dalam satu bulan.
 */
function ringkasCoach_(coach, bulan, hariIni, cfg, semuaSesi, semuaKos, semuaClaim, semuaPakej) {
  var sesiCoach = semuaSesi.filter(function (s) { return s.coach_id === coach.id; });
  var pakejCoach = semuaPakej.filter(function (p) { return p.coach_id === coach.id; });
  var agih = agihPakej_(sesiCoach, pakejCoach);
  var sesiBulan = sesiCoach.filter(function (s) { return s.bulan === bulan; }).sort(byTime_);
  var kosBulan = semuaKos.filter(function (k) { return k.coach_id === coach.id && k.bulan === bulan; });
  var claimRow = semuaClaim.filter(function (c) { return c.coach_id === coach.id && c.bulan === bulan; })[0] || {};
  var status = claimRow.status || 'draft';
  var share = num_(cfg.bahagian_coach, 70);

  var t = { pending: 0, upcoming: 0, done: 0, missed: 0, sesi: 0, kos: 0, issues: 0 };
  var sessions = sesiBulan.map(function (s) {
    var upcoming = s.tarikh > hariIni;
    var amount = kiraBayaran_(s, coach, cfg);
    var harga = hargaSesi_(s, coach, cfg);
    if (s.status === 'pending') { if (upcoming) t.upcoming++; else t.pending++; }
    else if (s.status === 'done') t.done++;
    else if (s.status !== 'batal') t.missed++;
    t.sesi += amount;
    var pct = s.status === 'noshow' ? num_(cfg.bayar_tak_datang) : s.status === 'late' ? num_(cfg.bayar_batal_lewat) : null;
    var sub = s.status === 'done' ? share + '% × RM' + harga.toFixed(2)
      : pct === null ? '' : (pct ? pct + '% bahagian coach' : 'Tak dibayar');
    if (s.status === 'noshow' && s.kategori === 'pvt') sub += ya_(s.tolak_pakej) ? ' · tolak pakej' : ' · tak tolak pakej';
    return { id: s.id, tarikh: s.tarikh, masa: s.masa, student: s.student, kategori: s.kategori,
      label: KATEGORI[s.kategori] || s.kategori, lokasi: s.lokasi || '', sumber: s.sumber, sebab: s.sebab || '',
      tc: s.tc_status || '', status: s.status, deduct: ya_(s.tolak_pakej), remark: s.remark || '',
      amount: bundar_(amount), sub: sub, pkg: agih.peta[s.id] || null, upcoming: upcoming };
  });
  var expenses = kosBulan.map(function (k) {
    t.kos += num_(k.jumlah);
    return { id: k.id, tarikh: k.tarikh, perkara: k.perkara, jumlah: num_(k.jumlah), resit: !!k.resit_url, resit_url: k.resit_url || '' };
  });
  var audit = auditCoach_(sesiBulan, kosBulan, agih.peta, hariIni);
  t.issues = audit.reduce(function (a, c) { return a + c.items.length; }, 0);
  t.total = bundar_(t.sesi + t.kos);
  t.sesi = bundar_(t.sesi);

  var pecahan = Object.keys(KATEGORI).map(function (k) {
    var ss = sesiBulan.filter(function (s) { return s.kategori === k && s.status === 'done'; });
    var unit = k === 'pvt' ? num_(coach.harga_pakej) / Math.max(1, num_(cfg.sesi_setiap_pakej, 10)) : num_(cfg.harga_group);
    return { kategori: k, label: KATEGORI[k], bil: ss.length, harga: bundar_(unit),
      jumlah: bundar_(ss.reduce(function (a, s) { return a + kiraBayaran_(s, coach, cfg); }, 0)) };
  }).filter(function (r) { return r.bil; });
  ['noshow', 'late'].forEach(function (st) {
    var ss = sesiBulan.filter(function (s) { return s.status === st; });
    if (ss.length) pecahan.push({ kategori: st, label: STATUS_LABEL[st], bil: ss.length, harga: null,
      jumlah: bundar_(ss.reduce(function (a, s) { return a + kiraBayaran_(s, coach, cfg); }, 0)) });
  });

  var pakejDipapar = agih.pakej.filter(function (p) {
    return p.baki > 0 || sesiBulan.some(function (s) { return kunciStudent_(s) === kunciStudent_(p); });
  });

  return {
    id: coach.id, nama: coach.nama, hargaPakej: num_(coach.harga_pakej),
    sesiSatu: bundar_(num_(coach.harga_pakej) / Math.max(1, num_(cfg.sesi_setiap_pakej, 10))),
    bahagianPvt: bundar_(num_(coach.harga_pakej) / Math.max(1, num_(cfg.sesi_setiap_pakej, 10)) * share / 100),
    bahagianGroup: bundar_(num_(cfg.harga_group) * share / 100),
    claim: { status: status, at: claimRow.dihantar_pada || '', remark: claimRow.remark_coach || '', note: claimRow.nota_admin || '',
      approvedAt: claimRow.diluluskan_pada || '', paidAt: claimRow.dibayar_pada || '' },
    editable: CLAIM_BOLEH_UBAH.indexOf(status) >= 0,
    sessions: sessions, expenses: expenses, totals: t, audit: audit, pecahan: pecahan, pakej: pakejDipapar,
    akhirSesi: sesiBulan.length ? sesiBulan[sesiBulan.length - 1].tarikh : ''
  };
}
