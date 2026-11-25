# RISE Coach Claim

Sistem claim bulanan untuk coach RISE Golf Academy. Booking ditarik dari link TidyCal setiap coach. Coach tanda setiap sesi dari telefon, dan admin cross-check serta luluskan claim hujung bulan.

- **Data**: satu Google Sheet milik academy (tab Tetapan, Coach, JenisSesi, Sesi, Kos, Claim, Pakej).
- **Resit**: folder Google Drive "RISE Claim: Resit", milik akaun yang deploy.
- **Akses**: setiap coach dapat link peribadi. Admin dapat link admin. Tiada login. Sesiapa yang ada link boleh buka, jadi jangan kongsi link.
- **TidyCal**: setiap coach sambung personal token sendiri. Token disimpan dalam Script Properties, tak dalam Sheet.

## Setup (sekali sahaja, lebih kurang 20 minit)

Buat semua langkah ni dengan akaun Google academy yang akan jadi pemilik data.

1. **Buat Google Sheet baru**, contohnya "RISE Coach Claim".
2. Dalam Sheet tu, pergi ke **Extensions → Apps Script**.
3. Dalam editor Apps Script:
   - Padam isi `Code.gs`, kemudian tampal isi fail [`apps-script/Code.gs`](apps-script/Code.gs).
   - Tambah fail skrip baru (butang **+ → Script**) untuk `Logic`, `Sync` dan `Setup`, dan tampal isi fail `.gs` yang sama nama.
   - Tambah fail HTML baru (**+ → HTML**) bernama `Index`, dan tampal isi [`apps-script/Index.html`](apps-script/Index.html).
   - Pergi ke **Project Settings**, tandakan "Show appsscript.json", kemudian tampal isi [`apps-script/appsscript.json`](apps-script/appsscript.json).
   - Tekan **Save**.
4. Kembali ke Sheet dan muat semula halaman. Menu **RISE Claim** akan keluar.
5. Pilih **RISE Claim → 1. Sediakan sistem**. Google akan minta kebenaran. Benarkan dengan akaun academy. Kalau keluar "Google hasn't verified this app", tekan **Advanced → Go to (nama projek)**, sebab skrip ni milik academy sendiri.
6. Dalam tab **Coach**, isi `nama` dan `harga_pakej` setiap coach, contohnya 2800 untuk pakej RM2,800 / 10 sesi. Tukar `aktif` kepada `Tidak` untuk baris yang tak digunakan.
7. Semak tab **Tetapan**: `bahagian_coach` 70, `harga_group` 300, `sesi_setiap_pakej` 10, dan polisi tak datang atau batal lewat 0.
8. Dalam editor Apps Script, tekan **Deploy → New deployment**, pilih jenis **Web app**:
   - Execute as: **Me**
   - Who has access: **Anyone**
   - Tekan **Deploy**, kemudian salin **Web app URL** (berakhir dengan `/exec`).
9. Tampal URL tu dalam tab **Tetapan**, baris `url_web_app`.
10. Pilih **RISE Claim → 2. Jana link coach dan admin**. Simpan link admin untuk diri sendiri. Hantar link setiap coach kepada coach tu secara peribadi.
11. Pilih **RISE Claim → 3. Pasang segerak automatik**. Booking akan ditarik setiap pagi sekitar 6:00.

## Langkah setiap coach (sekali)

1. Buka link peribadi di telefon. Tambah ke skrin utama supaya senang dibuka.
2. Dalam TidyCal, pergi ke **Integrations → Advanced → Manage API keys → Personal tokens**, buat token baru, dan salin.
3. Tampal token dalam kotak "Sambung TidyCal" dan tekan **Sambung**. Booking bulan ni dan bulan lepas akan terus masuk.

## Lepas sambung: semak jenis sesi

Selepas segerak pertama, tab **JenisSesi** akan senaraikan semua jenis booking TidyCal setiap coach. Sistem teka kategori dari nama:

| kategori | Maksud | Bayaran coach |
| --- | --- | --- |
| `pvt` | Private, ikut pakej | harga_pakej coach ÷ 10 × 70% |
| `jgroup` | Junior group | harga_group × 70% untuk satu sesi, berapa ramai pun student |
| `agroup` | Adult group | sama macam junior group |
| `abaikan` | Tak dikira, contohnya trial percuma atau mesyuarat | tiada |

Betulkan kategori yang salah. Perubahan berkuat kuasa pada segerak seterusnya.

## Pakej student

Sistem perlu tahu pakej setiap student untuk semak baki:

- **Automatik**: booking private yang dibayar sekurang-kurangnya separuh harga pakej coach dalam TidyCal direkod sebagai pakej baru 10 sesi.
- **Manual**: untuk pakej yang dibeli sebelum sistem mula, atau dibayar di kaunter, tambah baris dalam tab **Pakej**: `coach_id`, `student`, `emel` (sama macam dalam TidyCal), `jumlah_sesi`, `mula` (yyyy-mm-dd), dan `dah_guna_sebelum` (sesi yang dah digunakan sebelum tarikh mula sistem).

Sesi private tanpa pakej akan ditanda "Tiada pakej direkod" dalam semakan admin.

## Aliran bulanan

1. Setiap pagi, booking baru dan booking yang dibatalkan ditarik dari TidyCal.
2. Lepas setiap sesi, coach tekan **Selesai**, **Tak datang** (pilih tolak pakej atau tidak) atau **Batal lewat**, dan tambah remark kalau perlu. Walk-in dan kos dimasukkan sendiri.
3. Selepas sesi terakhir bulan tu, coach tekan **Hantar claim**. Bayaran setiap sesi dibekukan pada masa tu, jadi perubahan kadar selepas itu tak menjejaskan claim tu.
4. Admin buka link admin, tekan **Semak** pada setiap coach, dan selesaikan isu yang dikesan:
   - booking belum ditanda
   - status berbeza dengan TidyCal (dibatalkan tapi coach tanda Selesai)
   - pakej student habis atau tiada pakej
   - walk-in (semak dengan rekod kaunter)
   - kos tanpa resit
5. Admin tekan **Luluskan**, atau **Pulangkan kepada coach** dengan nota. Bila dah bayar, tekan **Tandakan dah bayar**.

## Bila kod dikemas kini

Tampal fail yang berubah dalam editor Apps Script, kemudian **Deploy → Manage deployments → Edit (pensel) → Version: New version → Deploy**. URL kekal sama, jadi link coach tak berubah.

## Keselamatan

- Link sesiapa yang terbocor: kosongkan `kunci_link` coach tu dalam tab Coach, dan jana link semula. Link lama terus tak berfungsi.
- Link admin terbocor: dalam editor Apps Script, **Project Settings → Script Properties**, padam `ADMIN_KEY`, kemudian jana link semula.
- Coach berhenti: tukar `aktif` kepada `Tidak`. Minta coach padam token dalam TidyCal.

## Ujian

Kod diuji dengan simulasi Google Sheets, Drive dan API TidyCal, tanpa akaun Google:

```
node rise-claim/test/run.js          # 21 ujian aliran penuh
node rise-claim/test/ui.js <folder>  # buka skrin dalam Chromium (perlukan Playwright) dan ambil gambar skrin
```
