/**
 * RISE Coach Claim: menu dalam Google Sheet dan langkah setup.
 */

function onOpen() {
  SpreadsheetApp.getUi().createMenu('RISE Claim')
    .addItem('1. Sediakan sistem', 'sediakanSistem')
    .addItem('2. Jana link coach dan admin', 'janaLink')
    .addItem('3. Pasang segerak automatik (setiap pagi)', 'pasangTrigger')
    .addSeparator()
    .addItem('Segerak TidyCal sekarang', 'segerakDariMenu')
    .addToUi();
}

function sediakanSistem() {
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  props_().setProperty('SHEET_ID', ss.getId());
  Object.keys(SKEMA).forEach(function (nama) {
    var sh = ss.getSheetByName(nama) || ss.insertSheet(nama);
    if (sh.getLastRow() === 0) {
      sh.getRange(1, 1, 1, SKEMA[nama].length).setValues([SKEMA[nama]]).setFontWeight('bold');
      sh.setFrozenRows(1);
    }
    sh.getRange(1, 1, sh.getMaxRows(), sh.getMaxColumns()).setNumberFormat('@');
  });
  var tT = new Jadual('Tetapan'), ada = {};
  tT.semua().forEach(function (r) { ada[r.kunci] = true; });
  TETAPAN_ASAL.forEach(function (t) { if (!ada[t[0]]) tT.tulis({ kunci: t[0], nilai: t[1], keterangan: t[2] }); });
  tT.simpan();
  var tC = new Jadual('Coach');
  if (!tC.semua().length) {
    for (var i = 1; i <= 4; i++) tC.tulis({ id: 'c' + i, nama: 'Coach ' + i, harga_pakej: '', aktif: 'Ya' });
    tC.simpan();
  }
  var kat = SpreadsheetApp.newDataValidation().requireValueInList(['pvt', 'jgroup', 'agroup', 'abaikan'], true).build();
  ss.getSheetByName('JenisSesi').getRange('D2:D').setDataValidation(kat);
  var lalai = ss.getSheetByName('Sheet1') || ss.getSheetByName('Helaian1');
  if (lalai && lalai.getLastRow() === 0 && ss.getSheets().length > 1) ss.deleteSheet(lalai);
  folderResit_();
  SpreadsheetApp.getUi().alert('Sistem dah disediakan.\n\n' +
    'Seterusnya:\n1. Dalam tab Coach, isi nama dan harga pakej (RM untuk ' + cfg_().sesi_setiap_pakej + ' sesi) setiap coach.\n' +
    '2. Deploy web app (Deploy → New deployment → Web app).\n' +
    '3. Tampal URL web app dalam tab Tetapan (url_web_app).\n' +
    '4. Pilih menu RISE Claim → 2. Jana link coach dan admin.');
}

function urlWebApp_() {
  var u = String(cfg_().url_web_app || '').trim();
  if (/\/exec$/.test(u)) return u;
  var s = ScriptApp.getService().getUrl() || '';
  return /\/exec$/.test(s) ? s : '';
}

function janaLink() {
  var ui = SpreadsheetApp.getUi();
  var url = urlWebApp_();
  if (!url) { ui.alert('Deploy web app dulu, kemudian tampal URL yang berakhir dengan /exec dalam tab Tetapan (url_web_app).'); return; }
  var p = props_();
  if (!p.getProperty('ADMIN_KEY')) p.setProperty('ADMIN_KEY', Utilities.getUuid().replace(/-/g, ''));
  var t = new Jadual('Coach'), baris = [];
  t.semua().forEach(function (c) {
    if (!c.nama) return;
    if (!c.id) c.id = idBaru_('c');
    if (!c.kunci_link) c.kunci_link = Utilities.getUuid().replace(/-/g, '');
    c.link = url + '?k=' + c.kunci_link;
    t.tulis(c);
    baris.push('<tr><td>' + esc_(c.nama) + '</td><td><input readonly value="' + esc_(c.link) + '" onclick="this.select()"></td></tr>');
  });
  var adminLink = url + '?k=' + p.getProperty('ADMIN_KEY');
  var html = '<style>body{font:14px system-ui;margin:0}td{padding:4px 6px}input{width:100%;font:12px monospace;padding:4px}h3{margin:8px 0}</style>' +
    '<h3>Link admin (jangan kongsi)</h3><input readonly value="' + esc_(adminLink) + '" onclick="this.select()">' +
    '<h3>Link peribadi setiap coach</h3><p>Hantar link ni kepada coach masing-masing secara peribadi. Link coach juga disimpan dalam tab Coach.</p>' +
    '<table style="width:100%">' + baris.join('') + '</table>' +
    '<p>Kalau link terbocor, kosongkan lajur kunci_link coach tu dan jana semula.</p>';
  ui.showModalDialog(HtmlService.createHtmlOutput(html).setWidth(640).setHeight(420), 'Link RISE Coach Claim');
}
function esc_(s) { return String(s).replace(/[&<>"]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]; }); }

function pasangTrigger() {
  ScriptApp.getProjectTriggers().forEach(function (t) { if (t.getHandlerFunction() === 'syncSemua') ScriptApp.deleteTrigger(t); });
  ScriptApp.newTrigger('syncSemua').timeBased().everyDays(1).atHour(6).inTimezone(tz_()).create();
  SpreadsheetApp.getUi().alert('Segerak automatik dipasang. Booking TidyCal akan ditarik setiap pagi sekitar 6:00.');
}

function segerakDariMenu() {
  var h = syncSemua();
  SpreadsheetApp.getUi().alert(h.map(function (x) {
    return x.coach + ': ' + (x.ralat ? 'RALAT, ' + x.ralat : x.langkau ? x.langkau : x.booking + ' booking, ' + x.berubah + ' sesi dikemas kini');
  }).join('\n'));
}
