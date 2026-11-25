// Buka Index.html dalam Chromium, disambung kepada simulasi server: node rise-claim/test/ui.js <folder-output>
'use strict';
const fs = require('fs');
const path = require('path');
const { chromium } = require('playwright');
const { createEnv, contohTidyCal } = require('./harness');

(async () => {
  const out = process.argv[2] || '.';
  const tc = contohTidyCal();
  const env = createEnv(tc);
  const { ctx } = env;
  ctx.sediakanSistem();
  const tC = new ctx.Jadual('Coach'); const cs = tC.semua();
  Object.assign(cs[0], { nama: 'Coach Amir', harga_pakej: '2800' }); tC.tulis(cs[0]);
  Object.assign(cs[1], { nama: 'Coach Sarah', harga_pakej: '4500' }); tC.tulis(cs[1]);
  [2, 3].forEach(i => { cs[i].aktif = 'Tidak'; tC.tulis(cs[i]); });
  const tT = new ctx.Jadual('Tetapan'); const u = tT.semua().find(r => r.kunci === 'url_web_app');
  u.nilai = 'https://script.google.com/macros/s/ABC/exec'; tT.tulis(u);
  ctx.janaLink();
  const keys = new ctx.Jadual('Coach').semua();
  const AMIR = keys[0].kunci_link, ADMIN = env.props.ADMIN_KEY;
  ctx.api_saveToken(AMIR, '2026-11', tc.token);
  ctx.api_mark(AMIR, '2026-11', 'tc-1001', 'done', false, null);

  const html = fs.readFileSync(path.join(__dirname, '..', 'apps-script', 'Index.html'), 'utf8');
  const shim = `<script>
    function makeRun(){ let ok=()=>{}, fail=()=>{}; const p = new Proxy({}, {get(_, prop){
      if (prop==='withSuccessHandler') return f => { ok=f; return p; };
      if (prop==='withFailureHandler') return f => { fail=f; return p; };
      return (...args) => window.__api(prop, JSON.stringify(args)).then(r => { const o = JSON.parse(r); o.err ? fail(new Error(o.err)) : ok(o.val); });
    }}); return p; }
    window.google = { script: { get run(){ return makeRun(); } } };
  </script>`;
  const page = (k) => html.replace('<?!= kunciJson ?>', JSON.stringify(k)).replace('<head>', '<head>' + shim);

  const b = await chromium.launch();
  const errs = [];
  async function open(k, opts) {
    const p = await b.newPage(opts);
    p.on('pageerror', e => errs.push(e.message));
    p.on('console', m => { if (m.type() === 'error' && !/fonts|ERR_|net::/.test(m.text())) errs.push(m.text()); });
    await p.exposeFunction('__api', (fn, a) => {
      try { return JSON.stringify({ val: ctx[fn](...JSON.parse(a)) }); }
      catch (e) { return JSON.stringify({ err: e.message }); }
    });
    await p.route(/fonts\.(googleapis|gstatic)\.com/, r => r.abort());
    await p.setContent(page(k));
    await p.waitForSelector('.stats', { timeout: 5000 });
    return p;
  }
  // Coach: telefon
  const c = await open(AMIR, { viewport: { width: 400, height: 860 }, deviceScaleFactor: 2 });
  await c.screenshot({ path: path.join(out, 'coach.png') });
  await c.click('[data-action=mark][data-st=done] >> nth=0');
  await c.waitForFunction(() => !document.body.classList.contains('busy'));
  const pendingAfter = await c.$eval('.stat b', e => e.textContent);
  await c.click('[data-action=noshow] >> nth=0');
  await c.check('input[name=deduct][value=tidak]');
  await c.fill('#rm-text', 'Student maklum sakit');
  await c.click('.sheet .btn.primary');
  await c.waitForFunction(() => document.getElementById('modal').hidden);
  await c.click('[data-f=all]');
  const remarks = await c.$$eval('.remark', els => els.map(e => e.textContent));
  // Admin: desktop
  const a = await open(ADMIN, { viewport: { width: 1100, height: 900 } });
  await a.screenshot({ path: path.join(out, 'admin.png'), fullPage: true });
  const rows = await a.$$eval('tbody tr', r => r.length);
  const sw = await c.evaluate(() => document.documentElement.scrollWidth);
  console.log(JSON.stringify({ errs, pendingAfter, remarks, adminRows: rows, phoneScrollWidth: sw }));
  await b.close();
})();
