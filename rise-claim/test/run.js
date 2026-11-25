// Ujian hujung-ke-hujung: node rise-claim/test/run.js
'use strict';
const assert = require('assert');
const { createEnv, contohTidyCal } = require('./harness');

let lulus = 0;
function ujian(nama, fn) {
  try { fn(); lulus++; console.log('  ok  ' + nama); }
  catch (e) { console.log('  GAGAL  ' + nama + '\n        ' + (e && e.stack || e).split('\n').slice(0, 4).join('\n        ')); process.exitCode = 1; }
}
const eq = (a, b, m) => assert.deepStrictEqual(JSON.parse(JSON.stringify(a)), b, m);
const throws = (fn, re) => assert.throws(fn, e => re.test(e.message), 'sepatutnya ralat ' + re);

/* ---------- Kiraan tulen ---------- */
console.log('Logic');
{
  const { ctx } = createEnv(contohTidyCal());
  ujian('agihPakej_ guna pakej paling awal dulu, kemudian pakej kedua', () => {
    const s = (id, t, st) => ({ id, tarikh: t, masa: '10:00', kategori: 'pvt', sumber: 'tidycal', status: st || 'done', emel: 'a@x', student: 'A' });
    const sesi = [s('a', '2026-11-01'), s('b', '2026-11-02'), s('c', '2026-11-03'), s('d', '2026-11-04', 'noshow'), s('e', '2026-11-05')];
    const pakej = [{ id: 'p1', emel: 'a@x', jumlah_sesi: '10', mula: '2026-10-01', dah_guna_sebelum: '8' }, { id: 'p2', emel: 'a@x', jumlah_sesi: '10', mula: '2026-11-02', dah_guna_sebelum: '0' }];
    const r = ctx.agihPakej_(sesi, pakej);
    eq([r.peta.a.n, r.peta.b.n, r.peta.c.n, r.peta.e.n], [9, 10, 1, 2]);
    assert.strictEqual(r.peta.d, undefined, 'tak datang tanpa tolak pakej tak guna pakej');
    assert.strictEqual(r.pakej.find(p => p.id === 'p2').baki, 8);
  });
  ujian('agihPakej_ tanda lebih bila pakej habis, dan tiada bila tiada pakej', () => {
    const sesi = [1, 2, 3].map(i => ({ id: 's' + i, tarikh: '2026-11-0' + i, masa: '10:00', kategori: 'pvt', sumber: 'tidycal', status: 'done', emel: 'b@x' }));
    const r = ctx.agihPakej_(sesi, [{ id: 'p', emel: 'b@x', jumlah_sesi: '10', mula: '2026-01-01', dah_guna_sebelum: '9' }]);
    eq([r.peta.s1.over, r.peta.s2.over, r.peta.s2.n], [false, true, 11]);
    assert.ok(ctx.agihPakej_(sesi, []).peta.s1.tiada);
  });
  ujian('bookingKeSesi_ gabung group pada slot sama jadi satu sesi', () => {
    const fmt = iso => ({ tarikh: iso.slice(0, 10), masa: iso.slice(11, 16) });
    const out = ctx.bookingKeSesi_([
      { id: 1, booking_type_id: 9, starts_at: '2026-11-08T09:00:00Z', contact: { name: 'A' } },
      { id: 2, booking_type_id: 9, starts_at: '2026-11-08T09:00:00Z', contact: { name: 'B' }, cancelled_at: 'x' },
      { id: 3, booking_type_id: 9, starts_at: '2026-11-08T09:00:00Z', contact: { name: 'C' } }
    ], 'c1', () => 'agroup', fmt);
    assert.strictEqual(out.length, 1);
    assert.strictEqual(out[0].student, 'Adult group: A, C');
    assert.strictEqual(out[0].tc_ids, '1,2,3');
  });
  ujian('tekaKategori_', () => {
    assert.strictEqual(ctx.tekaKategori_('Junior Group Class'), 'jgroup');
    assert.strictEqual(ctx.tekaKategori_('Adult Group Sunday'), 'agroup');
    assert.strictEqual(ctx.tekaKategori_('Private Lesson 60 min'), 'pvt');
  });
}

/* ---------- Aliran penuh ---------- */
console.log('Aliran penuh');
const tc = contohTidyCal();
const env = createEnv(tc);
const { ctx, ss, props, clock } = env;
const tab = n => new ctx.Jadual(n);
let ADMIN, AMIR, SARAH;

ujian('Sediakan sistem buat semua tab dan tetapan', () => {
  ctx.sediakanSistem();
  ['Tetapan', 'Coach', 'JenisSesi', 'Sesi', 'Kos', 'Claim', 'Pakej'].forEach(n => assert.ok(ss.getSheetByName(n), n));
  assert.ok(!ss.getSheetByName('Sheet1'));
  assert.strictEqual(ctx.cfg_().harga_group, '300');
  assert.strictEqual(tab('Coach').semua().length, 4);
});
ujian('Jana link perlukan URL web app, kemudian beri link peribadi', () => {
  ctx.janaLink();
  assert.match(env.ui.alerts.pop(), /Deploy web app dulu/);
  const tC = tab('Coach'); const cs = tC.semua();
  Object.assign(cs[0], { nama: 'Coach Amir', harga_pakej: '2800' }); tC.tulis(cs[0]);
  Object.assign(cs[1], { nama: 'Coach Sarah', harga_pakej: '4500' }); tC.tulis(cs[1]);
  Object.assign(cs[2], { aktif: 'Tidak' }); tC.tulis(cs[2]);
  Object.assign(cs[3], { aktif: 'Tidak' }); tC.tulis(cs[3]);
  const tT = tab('Tetapan'); const u = tT.semua().find(r => r.kunci === 'url_web_app');
  u.nilai = 'https://script.google.com/macros/s/ABC/exec'; tT.tulis(u);
  ctx.janaLink();
  const baru = tab('Coach').semua();
  AMIR = baru[0].kunci_link; SARAH = baru[1].kunci_link; ADMIN = props.ADMIN_KEY;
  assert.ok(AMIR && SARAH && ADMIN && AMIR !== SARAH);
  assert.strictEqual(baru[0].link, 'https://script.google.com/macros/s/ABC/exec?k=' + AMIR);
  assert.match(env.ui.dialogs.pop(), /Link admin/);
});
ujian('Link salah ditolak; link coach hanya nampak diri sendiri', () => {
  throws(() => ctx.api_load('salah', ''), /tak sah/);
  throws(() => ctx.api_load('', ''), /tak lengkap/);
  const v = ctx.api_load(AMIR, '');
  assert.strictEqual(v.role, 'coach');
  assert.strictEqual(v.coaches.length, 1);
  assert.strictEqual(v.coaches[0].nama, 'Coach Amir');
  assert.strictEqual(v.sheetUrl, '');
  assert.strictEqual(ctx.api_load(ADMIN, '').coaches.length, 2, 'coach tak aktif tak dipapar');
});

clock.now = new Date('2026-11-20T04:00:00Z'); // 20 Nov, 12 tengah hari
let v;
ujian('Token TidyCal salah ditolak', () => {
  throws(() => ctx.api_saveToken(AMIR, '2026-11', 'tok_salah_0123456789abcdefghij'), /Token TidyCal tak sah/);
  throws(() => ctx.api_saveToken(AMIR, '2026-11', 'pendek'), /tak lengkap/);
  assert.ok(!props.TC_c1);
});
ujian('Sambung TidyCal dan segerak: private, group digabung, batal, pakej dikesan', () => {
  v = ctx.api_saveToken(AMIR, '2026-11', tc.token);
  const c = v.coaches[0];
  assert.ok(c.disambung);
  assert.strictEqual(tab('Coach').semua()[0].tidycal, 'Disambung: Amir Golf');
  const ids = c.sessions.map(s => s.id);
  eq(ids.filter(i => i.startsWith('tc-')).sort(), ['tc-1001', 'tc-1002', 'tc-1003', 'tc-1004', 'tc-1008']);
  const grp = c.sessions.filter(s => s.kategori !== 'pvt');
  assert.strictEqual(grp.length, 2, 'satu junior group (2 student) + satu adult group dibatalkan');
  const jr = grp.find(s => s.kategori === 'jgroup');
  assert.strictEqual(jr.student, 'Junior group: Aina, Ben Tan');
  assert.strictEqual(jr.masa, '09:00');
  assert.strictEqual(grp.find(s => s.kategori === 'agroup').status, 'batal');
  assert.strictEqual(c.sessions.find(s => s.id === 'tc-1004').status, 'batal');
  assert.strictEqual(c.sessions.find(s => s.id === 'tc-1001').masa, '10:00', 'masa ikut waktu Malaysia');
  assert.ok(!ids.includes('tc-1100'), 'booking Disember di luar julat');
  const pk = tab('Pakej').semua();
  assert.strictEqual(pk.length, 1);
  eq([pk[0].id, pk[0].mula, pk[0].jumlah_sesi], ['tcp-1001', '2026-11-03', '10']);
  assert.ok(tc.calls.some(u => u.includes('page=2')), 'halaman kedua dibaca');
  assert.strictEqual(tab('JenisSesi').semua().length, 3);
  assert.strictEqual(c.totals.pending, 4);
  assert.strictEqual(c.totals.upcoming, 1);
});
ujian('Oktober juga disegerak (bulan lepas)', () => {
  const okt = ctx.api_load(AMIR, '2026-10').coaches[0];
  eq(okt.sessions.map(s => s.id), ['tc-990']);
});
ujian('Coach tak boleh tanda sesi akan datang atau sesi coach lain', () => {
  throws(() => ctx.api_mark(AMIR, '2026-11', 'tc-1008', 'done', false, null), /belum berlaku/);
  throws(() => ctx.api_mark(SARAH, '2026-11', 'tc-1001', 'done', false, null), /tak dijumpai/);
  throws(() => ctx.api_mark(ADMIN, '2026-11', 'tc-1001', 'done', false, null), /Hanya coach/);
  throws(() => ctx.api_mark(AMIR, '2026-11', 'tc-1001', 'hack', false, null), /tak dikenali/);
});
ujian('Tanda sesi, tapi hantar claim disekat selagi ada sesi akan datang', () => {
  ['tc-1001', 'tc-1002', 'tc-1003'].forEach(id => ctx.api_mark(AMIR, '2026-11', id, 'done', false, null));
  const g = ctx.api_load(AMIR, '2026-11').coaches[0].sessions.find(s => s.kategori === 'jgroup');
  v = ctx.api_mark(AMIR, '2026-11', g.id, 'done', false, null);
  assert.strictEqual(v.coaches[0].totals.pending, 0);
  throws(() => ctx.api_submit(AMIR, '2026-11', ''), /sesi akan datang/);
});

clock.now = new Date('2026-11-30T12:00:00Z');
ujian('Segerak semula tak buat pendua dan tak padam tanda coach', () => {
  const sebelum = tab('Sesi').semua().length;
  ctx.syncSemua();
  assert.strictEqual(tab('Sesi').semua().length, sebelum);
  assert.strictEqual(tab('Pakej').semua().length, 1);
  assert.strictEqual(ctx.api_load(AMIR, '2026-11').coaches[0].sessions.find(s => s.id === 'tc-1002').status, 'done');
});
ujian('Booking dibatalkan dalam TidyCal selepas coach tanda Selesai: kekal Selesai, admin nampak isu', () => {
  tc.bookings[tc.token].find(b => b.id === 1002).cancelled_at = '2026-11-25T01:00:00Z';
  ctx.syncSemua();
  const s = tab('Sesi').semua().find(x => x.id === 'tc-1002');
  eq([s.status, s.tc_status], ['done', 'dibatalkan']);
  const amir = ctx.api_load(ADMIN, '2026-11').coaches.find(c => c.id === 'c1');
  assert.strictEqual(amir.audit.find(a => a.key === 'tc').items.length, 1);
});
ujian('Tak datang dengan pilihan tolak pakej, remark, walk-in dan kos dengan resit', () => {
  v = ctx.api_mark(AMIR, '2026-11', 'tc-1008', 'noshow', true, 'Student tak muncul, tak angkat telefon');
  let s = v.coaches[0].sessions.find(x => x.id === 'tc-1008');
  eq([s.status, s.deduct, s.amount], ['noshow', true, 0]);
  assert.match(s.sub, /tolak pakej/);
  ctx.api_mark(AMIR, '2026-11', 'tc-1008', 'done', false, null);
  ctx.api_remark(AMIR, '2026-11', 'tc-1002', 'Student batal dalam TidyCal tapi datang juga');
  throws(() => ctx.api_addWalkin(AMIR, '2026-11', { tarikh: '2026-12-01', kategori: 'pvt', student: 'X' }), /dah berlaku/);
  v = ctx.api_addWalkin(AMIR, '2026-11', { tarikh: '2026-11-21', masa: '10:00', student: '=Encik Rahman', kategori: 'pvt', sebab: 'Walk-in', lokasi: 'Bay 2', remark: 'Bayar tunai' });
  const w = v.coaches[0].sessions.find(x => x.sumber === 'manual');
  assert.strictEqual(w.student, '=Encik Rahman', 'formula tak dijalankan, teks kekal');
  v = ctx.api_addExpense(AMIR, '2026-11', { tarikh: '2026-11-14', jumlah: '35', perkara: 'Bola range', fail: { name: 'resit.jpg', mime: 'image/jpeg', data: Buffer.from('jpg').toString('base64') } });
  assert.strictEqual(env.drive.files.length, 1);
  assert.ok(v.coaches[0].expenses[0].resit);
  throws(() => ctx.api_deleteSession(AMIR, '2026-11', 'tc-1001'), /Hanya sesi walk-in/);
});
let jumlahHantar;
ujian('Hantar claim: jumlah betul dan bayaran dibekukan', () => {
  v = ctx.api_submit(AMIR, '2026-11', 'Ada 1 walk-in');
  const c = v.coaches[0];
  // 4 private selesai (1001,1002,1003,1008) x RM196 + junior group RM210 + walk-in private RM196 + kos RM35
  assert.strictEqual(c.totals.total, 4 * 196 + 210 + 196 + 35);
  jumlahHantar = c.totals.total;
  assert.strictEqual(c.claim.status, 'submitted');
  assert.ok(tab('Sesi').semua().filter(s => s.coach_id === 'c1' && s.bulan === '2026-11' && s.status === 'done').every(s => s.bayaran !== ''));
  throws(() => ctx.api_mark(AMIR, '2026-11', 'tc-1001', 'late', false, null), /dah dihantar/);
  throws(() => ctx.api_addExpense(AMIR, '2026-11', { tarikh: '2026-11-15', jumlah: '5', perkara: 'x' }), /dah dihantar/);
});
ujian('Admin nampak semakan: walk-in, pakej, TidyCal, remark, baki pakej', () => {
  const c = ctx.api_load(ADMIN, '2026-11').coaches.find(x => x.id === 'c1');
  const isu = k => c.audit.find(a => a.key === k).items;
  assert.strictEqual(isu('manual').length, 1);
  assert.strictEqual(isu('tc')[0].remark, 'Student batal dalam TidyCal tapi datang juga');
  assert.strictEqual(isu('pkg').length, 1, 'Mei Ling tiada pakej');
  assert.match(isu('pkg')[0].why, /Tiada pakej/);
  assert.strictEqual(isu('rcpt').length, 0);
  const hafiz = c.pakej.find(p => p.student === 'Hafiz');
  eq([hafiz.digunakan, hafiz.baki], [3, 7]);
  assert.strictEqual(c.claim.remark, 'Ada 1 walk-in');
});
ujian('Ubah kadar tak ubah claim yang dah dihantar', () => {
  v = ctx.api_saveSettings(ADMIN, '2026-11', { cfg: { harga_group: '400' }, pakej: {} });
  assert.strictEqual(v.coaches.find(x => x.id === 'c1').totals.total, jumlahHantar);
  throws(() => ctx.api_saveSettings(ADMIN, '2026-11', { cfg: { bahagian_coach: '150' } }), /tak sah/);
  throws(() => ctx.api_saveSettings(AMIR, '2026-11', { cfg: { harga_group: '1' } }), /Hanya admin/);
});
ujian('Admin tanda dah semak, pulangkan (bayaran dikira semula), coach hantar semula, lulus, bayar', () => {
  const c = ctx.api_load(ADMIN, '2026-11').coaches.find(x => x.id === 'c1');
  v = ctx.api_check(ADMIN, '2026-11', 'sesi', c.audit.find(a => a.key === 'manual').items[0].id);
  assert.strictEqual(v.coaches.find(x => x.id === 'c1').audit.find(a => a.key === 'manual').items.length, 0);
  throws(() => ctx.api_paid(ADMIN, '2026-11', 'c1'), /Status claim dah berubah/);
  v = ctx.api_return(ADMIN, '2026-11', 'c1', 'Sila tambah remark untuk Mei Ling');
  assert.strictEqual(v.coaches.find(x => x.id === 'c1').totals.total, jumlahHantar + 70, 'group kini RM400 x 70%');
  const cc = ctx.api_load(AMIR, '2026-11').coaches[0];
  eq([cc.claim.status, cc.claim.note, cc.editable], ['returned', 'Sila tambah remark untuk Mei Ling', true]);
  ctx.api_remark(AMIR, '2026-11', 'tc-1008', 'Pakej baru dah dibayar di kaunter');
  ctx.api_submit(AMIR, '2026-11', 'Dah tambah remark');
  ctx.api_approve(ADMIN, '2026-11', 'c1');
  v = ctx.api_paid(ADMIN, '2026-11', 'c1');
  assert.strictEqual(v.coaches.find(x => x.id === 'c1').claim.status, 'paid');
});
ujian('Segerak selepas claim dibayar tak ubah bulan tu', () => {
  tc.bookings[tc.token].find(b => b.id === 1003).cancelled_at = '2026-11-30T01:00:00Z';
  const r = ctx.syncSemua();
  assert.strictEqual(tab('Sesi').semua().find(s => s.id === 'tc-1003').tc_status, 'ditempah');
  assert.strictEqual(r.find(x => x.coach === 'Coach Sarah').langkau, 'Belum sambung TidyCal');
});
ujian('Token yang dah dibatalkan direkod sebagai ralat segerak', () => {
  props.TC_c1 = 'tok_dibatalkan_0123456789abcdef';
  const r = ctx.syncSemua();
  assert.match(r[0].ralat, /Token TidyCal tak sah/);
  assert.match(ctx.api_load(ADMIN, '2026-11').coaches[0].ralatSegerak, /Token TidyCal tak sah/);
  props.TC_c1 = tc.token;
});

console.log('\n' + lulus + ' ujian lulus' + (process.exitCode ? ', ADA YANG GAGAL' : ''));
