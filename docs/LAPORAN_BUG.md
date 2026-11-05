# Laporan Bug

Laporan ini memuat seluruh **9 bug** pada codebase. Bug 1–3 serta draf akar masalah bug 5–9
dikerjakan **Muhammad Iqbal (251524057)** bersama AI MiMoCode; **bug 4** dikerjakan
**Muhammad Fawwaz Muzakki**. Bug yang belum diperbaiki diberi keterangan
*"belum dikerjakan & belum di-fix"*. Bagian **Akar masalah** masih berupa draf AI; wajib
disunting dengan kata-kata sendiri sebelum demo (bagian ini diuji lisan).

---

## Bug 1: Keyword tidak peka huruf besar/kecil

**Ditemukan oleh:** Muhammad Iqbal (251524057) · **Diperbaiki oleh:** Muhammad Iqbal (251524057) · **Commit:** `7db3739`

**Gejala.** `tokenize("Select id FrOm t")` menghasilkan `Select` dan `FrOm` sebagai `IDENT`.
Menurut SPESIFIKASI.md bagian 2.2 keduanya harus `KEYWORD` dengan nilai huruf besar
(`SELECT`, `FROM`). Akibatnya statement `select id FROM t;` gagal parse.

**Reproduksi minimal.** SQL terpendek yang memicu bug:

```sql
select id FROM t;
```

**Akar masalah.** Di `_word()`, teks kata dibandingkan apa adanya terhadap `KEYWORDS` yang
semua isinya huruf besar. Padahal pengenalan token di *scanner* (Crafting Interpreters bab 4)
harus mengenali makna kata, bukan bentuk hurufnya — karena `KEYWORDS` tidak dinormalkan,
`select` jatuh ke kategori identifier biasa (sama seperti `selection`), dan parser tidak
menerimanya sebagai awal statement. Intinya tahap *scanning* menggabungkan tugas "apakah ini
kata" dengan "seperti apa penulisannya".

**Perbaikan.** `crud/lexer.py::_word()`: bandingkan `text.upper()` terhadap `KEYWORDS` dan
simpan nilai keyword selalu dalam huruf besar. Alternatif yang dipertimbangkan: menormalkan
isi `KEYWORDS` menjadi huruf kecil lalu membandingkan `text.lower()` — ditolak karena nilai
token keyword tetap wajib huruf besar (§2.2), jadi tetap butuh konversi kedua; satu konversi
di jalur pembanding lebih sederhana.

**Test regresi.** `tests/test_tambahan.py::test_regresi_keyword_huruf_kecil` — gagal sebelum
perbaikan, lulus sesudahnya (test tervisible `test_keyword_huruf_kecil` juga ikut lulus).

**Peran AI.** MiMoCode menunjuk `_word()` sebagai lokasi bug berdasarkan §2.2 dan menulis
perbaikannya. Verifikasi: menjalankan `pytest`, membandingkan hasil `tokenize()` sebelum/
sesudah, dan memastikan `selection` tetap `IDENT`.

---

## Bug 2: Operator `<>` terpecah jadi dua token

**Ditemukan oleh:** Muhammad Iqbal (251524057) · **Diperbaiki oleh:** Muhammad Iqbal (251524057) · **Commit:** `7db3739`

**Gejala.** `tokenize("a <> 1")` menghasilkan `OP '<'` lalu `OP '>'`. SPESIFIKASI.md bagian
2.5 mensyaratkan `<>` diambil sebagai **satu** token `OP` (maximal munch). Akibatnya
`WHERE status <> 'LUNAS'` gagal parse: `diharapkan ekspresi, ditemukan '>'`.

**Reproduksi minimal.**

```sql
SELECT id FROM t WHERE status <> 'LUNAS';
```

**Akar masalah.** Cabang `<` di `_scan_token()` hanya mengecek kemungkinan `<=`, sisanya
langsung `<`. Prinsip *maximal munch* pada scanner (Crafting Interpreters bab 4) menyatakan
scanner harus mengambil rangkaian karakter **terpanjang** yang cocok dengan satu aturan;
karena `<>` (dua karakter) dan `<` (satu karakter) sama-sama sah, scanner wajib mencocokkan
yang dua karakter dulu. Urutan keputusan di kode membalikkan logika itu: `<` diambil sebelum
`<>` sempat diperiksa.

**Perbaikan.** `crud/lexer.py` cabang `<`: cek `>` dahulu (→ `<>`), baru `=` (→ `<=`), baru
`<` tunggal. Alternatif yang dipertimbangkan: memindahkan operator dua karakter ke tabel
pencocokan khusus — ditolak karena scanning dilakukan karakter per karakter dan menambah
tabel berarti mengubah struktur fungsi tanpa keuntungan.

**Test regresi.** `tests/test_tambahan.py::test_regresi_operator_tidak_sama_dengan` — gagal
sebelum perbaikan, lulus sesudahnya.

**Peran AI.** MiMoCode memeriksa aturan §2.5 terhadap cabang `<`/`>` dan menulis perbaikan
serta test regresinya. Verifikasi: `pytest` dan probe `tokenize("a <> 1")`.

---

## Bug 3: Tabel dalam subquery di `UPDATE` ikut ditandai `U`, bukan `R`

**Ditemukan oleh:** Muhammad Iqbal (251524057) · **Diperbaiki oleh:** Muhammad Iqbal (251524057) · **Commit:** `7db3739`

**Gejala.** Untuk `UPDATE produk SET stok = 1 WHERE id IN (SELECT id FROM pesanan)`,
`analyze_statement()` menghasilkan `pesanan: {'U', 'R'}` (tertulis `RUD` di matrix).
SPESIFIKASI.md bagian 5 tegas: membaca tabel lewat subquery **selalu R**, apa pun jenis
statement luarnya; hasil yang benar `pesanan: {'R'}`. Ini menyebabkan
`test_matrix_laporan_penjualan` gagal (`RUD` vs `RD`).

**Reproduksi minimal.**

```sql
UPDATE produk SET stok = 1 WHERE id IN (SELECT id FROM pesanan);
```

**Akar masalah.** Fungsi rekursif `_collect()` meneruskan parameter `op` milik statement luar
ke pemanggilan `_collect_select()` untuk subquery. Konsepnya seperti traversal pohon di
Crafting Interpreters bab 6: data yang diwariskan ke setiap simpul harus sesuai makna simpul
tujuan — di sini "operasi statement" (`U`/`D`) salah dibawa turun ke dalam subquery yang
sebenarnya hanya *membaca*. Konteks "mengapa statement dijalankan" tertukar dengan "apa yang
dilakukan ekspresi di dalamnya".

**Perbaikan.** `crud/analyzer.py::_collect()`: dua pemanggilan `_collect_select()`
(klausa `IN (SELECT ...)` dan node `EXISTS`/`Subquery`) selalu memakai `"R"`. Alternatif yang
dipertimbangkan: mengubah hanya pemanggilan di `analyze_statement()` — ditolak karena `op`
juga bocor dari rekursi ekspresi lain (misal subquery bersarang di dalam `SET`), jadi
perbaikannya harus di titik rekursi.

**Test regresi.** `tests/test_tambahan.py::test_regresi_subquery_update_tidak_ditandai_u` —
gagal sebelum perbaikan, lulus sesudahnya.

**Peran AI.** MiMoCode menemukan akar masalah saat audit setelah lexer diperbaiki (gejala
tersisa di test matrix bukan karena lexer). Verifikasi: `pytest` sampai hijau penuh dan
membandingkan keluaran `analyze_statement()` dengan tabel §5.

---

## Bug 4: Scope `DELETE` tidak ditutup — alias bocor ke statement berikutnya

**Ditemukan oleh:** Muhammad Fawwaz Muzakki · **Diperbaiki oleh:** Muhammad Fawwaz Muzakki · **Commit:** `c5514fc`

**Gejala.** Pada kode awal, sesudah `DELETE FROM sesi WHERE dibuat = 1;` statement berikutnya
`SELECT id FROM t WHERE sesi.id = 2;` **tidak menghasilkan error** — alias `sesi` masih
terbaca. SPESIFIKASI.md bagian 4.5: setelah satu statement selesai di-resolve tidak boleh ada
scope tersisa; alias statement sebelumnya tidak boleh terlihat oleh statement berikutnya.
Seharusnya muncul `error: alias 'sesi' tidak terdefinisi`.

**Reproduksi minimal.**

```sql
DELETE FROM sesi WHERE dibuat = 1;
SELECT id FROM t WHERE sesi.id = 2;
```

**Akar masalah.** `_delete()` memanggil `self._push()` untuk membuat scope target `DELETE`,
tetapi tidak memanggil `self._pop()` setelah `where` di-resolve — pasangan buka/tutup scope
tidak seimbang. Dalam Crafting Interpreters bab 8 (Scoping), setiap `beginScope()` wajib
berpasangan dengan `endScope()`; bila blok lupa menutup scope-nya, nama di dalamnya tetap
terikat pada rantai scope aktif dan terbaca oleh blok berikutnya — persis gejala di atas,
sehingga kemandirian statement (§4.5) dilanggar.

**Perbaikan.** `crud/resolver.py::_delete()`: tambah `self._pop()` setelah
`self._expr(dele.where)`. Dikerjakan Muhammad Fawwaz Muzakki bersamaan dengan pengerjaan
TODO(T2) di commit `c5514fc`.

**Test regresi.** Dicatat oleh yang mengerjakan (belum ada di `tests/test_tambahan.py`).

**Peran AI.** Dicatat oleh yang mengerjakan (Muhammad Fawwaz Muzakki).

---

## Bug 5: String dengan kutip ganda `''` pecah jadi dua token

**Ditemukan oleh:** Muhammad Iqbal (251524057) (audit bersama MiMoCode) · **Diperbaiki oleh:** belum dikerjakan & belum di-fix (masih terbuka)

**Gejala.** `tokenize("'O''Brien'")` menghasilkan dua token `STRING 'O'` dan `STRING 'Brien'`.
SPESIFIKASI.md bagian 2.4: dua kutip berturut-turut di dalam string adalah **satu** karakter
kutip — harusnya satu token `STRING` bernilai `O'Brien`. Akibatnya `pemeliharaan.sql` (baris
6 dan 9 memakai `'O''Brien'`/`'O''Neil'`) gagal parse.

**Reproduksi minimal.**

```sql
INSERT INTO t (nama) VALUES ('O''Brien');
```

**Akar masalah.** `_string()` berhenti pada setiap kutip yang ditemui tanpa mengecek apakah
kutip berikutnya juga kutip. Pada scanner (Crafting Interpreters bab 4), string adalah
mesin status: "di dalam string" vs "selesai". Keadaan "selesai" diambil terlalu dini karena
pasangan `''` tidak dibedakan dari kutip penutup tunggal, sehingga separuh string kedua
dibaca sebagai token baru.

**Perbaikan.** Belum. Rencana: setelah menemukan kutip, jika karakter berikutnya juga kutip,
lanjutkan sebagai isi string (konsumsi keduanya); selain itu tutup string.

**Test regresi.** Belum — akan ditambahkan bersama perbaikan.

**Peran AI.** MiMoCode menemukan bug ini saat audit terhadap §2.4 dan membuktikannya dengan
probe `tokenize()`; perbaikan belum dikerjakan.

---

## Bug 6: Presedensi `OR`/`AND` terbalik

**Ditemukan oleh:** Muhammad Iqbal (251524057) (audit bersama MiMoCode) · **Diperbaiki oleh:** belum dikerjakan & belum di-fix (masih terbuka)

**Gejala.** Untuk `a = 1 OR b = 2 AND c = 3`, akar AST adalah `AND` dengan anak `OR`, artinya
di-parse sebagai `(a OR b) AND c`. SPESIFIKASI.md bagian 3.1 (dengan contoh eksplisit di
spesifikasi): harus `a = 1 OR (b = 2 AND c = 3)` — `AND` mengikat lebih kuat dari `OR`.

**Reproduksi minimal.**

```sql
SELECT id FROM t WHERE a = 1 OR b = 2 AND c = 3;
```

**Akar masalah.** `_logical()` memakai **satu** loop `while AND atau OR` untuk keduanya,
sehingga `OR` dan `AND` berada pada tingkat presedensi yang sama. Grammar §3 punya dua
nonterminal bertingkat (`or_expr` memanggil `and_expr`, bukan sebaliknya). Dalam Crafting
Interpreters bab 6, tiap tingkat presedensi membutuhkan level pemanggilan sendiri
(presence climbing/Pratt) — satu fungsi berloop tunggal hanya menghasilkan asosiativitas
datar tanpa pemisahan tingkat; itulah kenapa operand `AND` "terseret" masuk ke dalam `OR`
terlebih dulu.

**Perbaikan.** Belum. Rencana: pisah menjadi `_or()` → `_and()` → `_not()` sesuai urutan
grammar, masing-masing berloop asosiatif kiri.

**Test regresi.** Belum — akan ditambahkan bersama perbaikan.

**Peran AI.** MiMoCode menemukan bug ini saat audit §3.1 dan memverifikasi struktur AST
dengan `pretty()`; perbaikan belum dikerjakan.

---

## Bug 7: Error recovery membuang seluruh sisa file, bukan sampai `;`

**Ditemukan oleh:** Muhammad Iqbal (251524057) (audit bersama MiMoCode) · **Diperbaiki oleh:** belum dikerjakan & belum di-fix (masih terbuka)

**Gejala.** `parse_sql("SELECT id FROM; SELECT a FROM t;")` menghasilkan 1 error dan
**0 statement**. SPESIFIKASI.md bagian 6: setelah error, buang token sampai dan termasuk
`;` berikutnya, lalu statement valid sesudahnya tetap diproses (dan tiap statement rusak
menghasilkan tepat satu error). Dampak nyata: `campuran_error.sql` kehilangan statement
`UPDATE produk` (baris 6) dan `DELETE keranjang` (baris 8) yang justru ada di
`ground_truth.csv`; `evaluate.py` menunjukkan recall parser 0.80 karena keduanya FN.

**Reproduksi minimal.**

```sql
SELECT id FROM; SELECT a FROM t;
```

**Akar masalah.** `_synchronize()` mengulang `self._advance()` sampai EOF — "titik aman"
panic mode (Crafting Interpreters bab 6, fungsi `synchronize()` pada Lox) salah didefinisikan
sebagai akhir file, padahal aman yang benar adalah akhir statement (`;`). Konsekuensinya dua
lapis: satu error memakan semua statement sesudahnya, dan statement rusak kedua tidak pernah
diparse sehingga tidak menghasilkan error — melanggar aturan "tepat satu error per statement
rusak". Gejala berantai ini juga membuat bug 8 terlihat seperti "file kosong total".

**Perbaikan.** Belum. Rencana: loop `synchronize` berhenti setelah menemukan `SEMICOLON`
(lalu konsumsi token `;` itu), atau berhenti di EOF memang hanya jika memang akhir file.

**Test regresi.** Belum — akan ditambahkan bersama perbaikan.

**Peran AI.** MiMoCode menemukan bug ini dari dua arah: probe langsung dan jejak
`ground_truth.csv` (dua baris yang menuntut statement sesudah error); perbaikan belum
dikerjakan.

---

## Bug 8: `LEFT OUTER JOIN` ditolak parser

**Ditemukan oleh:** Muhammad Iqbal (251524057) (audit bersama MiMoCode) · **Diperbaiki oleh:** belum dikerjakan & belum di-fix (masih terbuka)

**Gejala.** `SELECT a.id FROM a LEFT OUTER JOIN b ON b.a_id = a.id;` menghasilkan
`ParseError: Baris 1, kolom 25: diharapkan JOIN, ditemukan 'OUTER'`. Grammar §3:
`join = [ "INNER" | "LEFT" [ "OUTER" ] ] "JOIN" ...` — `OUTER` opsional setelah `LEFT`
sehingga konstruk ini **sah**. Dampak berantai: statement pertama `pemeliharaan.sql` gagal,
lalu digabung dengan bug 7 sehingga seluruh file tidak menghasilkan matrix sama sekali.

**Reproduksi minimal.**

```sql
SELECT a.id FROM a LEFT OUTER JOIN b ON b.a_id = a.id;
```

**Akar masalah.** `_join()` mem-parse sampai `LEFT` lalu langsung `_expect_kw("JOIN")` —
bagian opsional `[ "OUTER" ]` pada produksi grammar tidak direpresentasikan sama sekali.
Dalam Crafting Interpreters bab 5, tiap bagian produksi grammar (termasuk yang di dalam
tanda `[]`) berpadanan dengan keputusan di fungsi parser; satu bagian yang terlewat membuat
fungsi parser **menolak bahasa yang diterima grammar** — ujiannya persis: "apakah fungsi ini
menerima semua yang diterima grammar, dan hanya itu?"

**Perbaikan.** Belum. Rencana: setelah mencocokkan `LEFT`, coba `_match_kw("OUTER")` yang
opsional sebelum `JOIN` (dan tetap menolak `OUTER` tanpa `LEFT`, serta `INNER OUTER`).

**Test regresi.** Belum — akan ditambahkan bersama perbaikan.

**Peran AI.** MiMoCode menemukan bug ini saat audit produksi `join` terhadap grammar §3 dan
membuktikannya dengan probe; perbaikan belum dikerjakan.

---

## Bug 9: Pencarian qualifier resolver terbalik — shadowing alias mati

**Ditemukan oleh:** Muhammad Iqbal (251524057) (audit bersama MiMoCode) · **Diperbaiki oleh:** belum dikerjakan & belum di-fix (masih terbuka)

**Gejala.** Untuk `SELECT p.id FROM pelanggan p WHERE p.id IN (SELECT p.pelanggan_id FROM
pesanan p)`, kolom `p.pelanggan_id` di dalam subquery di-resolve ke `pelanggan` (scope luar).
SPESIFIKASI.md bagian 4.3: pencarian qualifier mulai dari scope **terdalam ke luar**, yang
pertama ditemukan dipakai — alias subquery `p` harus **menutupi** (shadowing) alias luar, jadi
harusnya `pesanan`. Berdampak ke `--kolom` `audit.sql` baris 12 yang salah mencantumkan
`pelanggan` untuk kolom milik `pesanan`.

**Reproduksi minimal.**

```sql
SELECT p.id FROM pelanggan p WHERE p.id IN (SELECT p.pelanggan_id FROM pesanan p);
```

**Akar masalah.** `_lookup()` membangun `chain` dari scope paling dalam ke luar, tetapi
iterasinya memakai `reversed(chain)` — pencarian jadi luar ke dalam, kebalikan dari aturan
spek. Konsep resolusi nama pada Crafting Interpreters bab 8 (Scoping): pengikatan nama
menyusuri rantai scope dari lingkup **paling dalam** ke luar sehingga nama inner meng-shadow
nama outer; begitu urutan traversal dibalik, nama terluar selalu menang dan shadowing tidak
pernah terjadi (correlated subquery masih tampak benar kebetulan karena namanya tidak
bermasalah di situ).

**Perbaikan.** Belum. Rencana: iterasi `chain` tanpa `reversed` (atau bangun chain dari
luar ke dalam lalu iterasi biasa) sehingga yang diperiksa pertama adalah scope terdalam.

**Test regresi.** Belum — akan ditambahkan bersama perbaikan.

**Peran AI.** MiMoCode menemukan bug ini saat audit §4.3 dan memverifikasinya langsung
dengan menjalankan resolver pada SQL shadowing; perbaikan belum dikerjakan.
