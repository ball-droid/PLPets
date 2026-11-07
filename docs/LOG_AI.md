# Log Penggunaan AI

Riwayat pemakaian AI/coding agent oleh kedua anggota untuk pekerjaan kelompok ini —
setiap baris memuat tugas, keputusan penerimaan, alasan, dan cara verifikasinya.

| No | Siapa | Prompt / tugas (ringkas) | Hasil: diterima, diubah, atau ditolak | Alasan | Cara verifikasi |
| --- | --- | --- | --- | --- | --- |
| 1 | Muhammad Iqbal (251524057) — anggota 1 | Minta bantuan AI (MiMoCode) mengerjakan TODO(T1): dukung `INSERT INTO ... SELECT ...` sesuai SPESIFIKASI.md bagian 3 dan 5 | Diterima | Perubahan kecil dan terarah: `_insert()` memakai ulang `_select()` yang sudah ada, lalu mengisi `ast.Insert.query`; `values` tetap kosong. API publik dan aturan arsitektur tidak berubah. | `pytest -q` → 28 passed (sebelumnya 25 passed, 5 failed); AST `INSERT ... SELECT` dicek dengan `ast_nodes.pretty()`; `analyze_source()` menghasilkan `{'arsip_pesanan': 'C', 'pesanan': 'R'}` |
| 2 | Muhammad Iqbal (251524057) — anggota 1 | Verifikasi status TODO(T1) bersama AI (MiMoCode): memastikan implementasi `INSERT ... SELECT` di `crud/parser.py` sudah selesai, menjalankan ulang test, memperbarui catatan log ini, lalu push ke branch `Muhammad-Iqbal` dan merge ke `main` | Diterima | Implementasi T1 sudah ada dan test khusus T1 lulus; sisa kegagalan test berasal dari bug lexer yang belum dikerjakan (T3), bukan dari T1. | `pytest -q` → 29 passed, 3 failed (semua gagal di lexer: `test_keyword_huruf_kecil`, `test_komentar_blok`, `test_matrix_laporan_penjualan`); `pytest tests/test_tambahan.py` → 2 passed |
| 3 | Muhammad Iqbal (251524057) — anggota 1 | Bersama AI (MiMoCode): menyelesaikan TODO(T3) sekaligus **memperbaiki 3 bug** — (1) keyword tidak peka huruf besar/kecil (SPESIFIKASI.md §2.2), (2) operator `<>` terpecah jadi dua token (§2.5), (3) tabel dalam subquery `UPDATE`/`DELETE` salah ditandai `U`, harusnya selalu `R` (§5); ditambah `/* ... */` komentar blok (§2.3) | Diterima | Keempat perbaikan persis mengikuti spesifikasi: keyword dinormalkan ke huruf besar lewat `text.upper()`, `<>` di-lex dengan maximal munch, subquery selalu dipanggil dengan op `R`, komentar blok dikonsumsi sampai `*/`. Lalu ditambahkan 3 test regresi untuk bug 1–3 di `tests/test_tambahan.py`. | `pytest -q` → **35 passed, 0 failed** (sebelumnya 29 passed, 3 failed; +3 test regresi baru: `test_regresi_keyword_huruf_kecil`, `test_regresi_operator_tidak_sama_dengan`, `test_regresi_subquery_update_tidak_ditandai_u`); matrix `laporan_penjualan.sql` kini `{'arsip_pesanan': 'C', 'pelanggan': 'RU', 'pesanan': 'RD'}` |
| 4 | Muhammad Fawwaz Muzakki (251524056) | Meminta AI memeriksa bug pada `crud/resolver.py` dan mencatat temuan resolver terkait pencarian qualifier di scope bertingkat | Diterima | Bug ditemukan oleh Muhammad Fawwaz Muzakki; AI membantu menelusuri `_lookup()` dan mendokumentasikan temuan tanpa mengubah kode resolver pada tahap ini atau menimpa catatan anggota lain. | Menjalankan query reproduksi shadowing: kolom `p` pada subquery salah ter-resolve ke `pelanggan`, seharusnya `pesanan`; `py -m pytest tests/test_resolver.py -q` → 4 passed. |
| 5 | Muhammad Fawwaz Muzakki (251524056) | Meminta ChatGPT ASTRA memperbaiki bug pencarian qualifier di scope bertingkat pada `crud/resolver.py` (Bug 9). | Diterima | `_lookup()` sekarang mencari dari scope aktif ke scope induk; alias dalam subquery menutupi alias luar, sementara correlated subquery tetap dapat menemukan alias induk. | `py -m pytest -q` → 37 passed; ditambahkan test shadowing dan test correlated subquery di `tests/test_resolver.py`. |
| 6 | Muhammad Iqbal (251524057) — penemu; Muhammad Fawwaz Muzakki (251524056) — perbaikan | Memperbaiki Bug 5 (string dengan kutip `''`) dan Bug 8 (`LEFT OUTER JOIN`) dengan bantuan ChatGPT ASTRA. | Diterima | Lexer kini mengubah kutip tunggal berpasangan di dalam string menjadi satu karakter kutip; parser menerima `OUTER` opsional setelah `LEFT` sesuai grammar. | `py -m pytest tests/test_tambahan.py tests/test_lexer.py tests/test_parser.py -q` → 28 passed; kedua SQL reproduksi berhasil diparse dan `INNER OUTER JOIN` tetap ditolak. |
| 7 | Muhammad Iqbal (251524057) — anggota 1 | Memperbaiki Bug 6 (presedensi `OR`/`AND` terbalik, SPESIFIKASI.md §3.1) bersama AI (MiMoCode): memisahkan `_logical()` yang berloop tunggal menjadi `_or()` → `_and()` → `_not()` sesuai urutan grammar | Diterima | Sebelumnya `OR` dan `AND` diparse pada tingkat presedensi sama sehingga `a = 1 OR b = 2 AND c = 3` menjadi `(a OR b) AND c`; dengan pemisahan per nonterminal, `AND` mengikat lebih kuat dan hasilnya `a = 1 OR (b = 2 AND c = 3)` sesuai contoh eksplisit §3.1. | `python -m pytest -q` → **40 passed, 0 failed** (sebelumnya 39 passed; +1 test regresi `test_regresi_presedensi_or_dan_and` yang terbukti gagal saat perbaikan di-stash); AST dicek ulang dengan `ast_nodes.pretty()` — kini berakar `OR` dengan anak kanan `AND` |
| 8 | Muhammad Iqbal (251524057) — anggota 1 | Memperbaiki Bug 7 (error recovery membuang seluruh sisa file, SPESIFIKASI.md §6) bersama AI (MiMoCode): `_synchronize()` kini berhenti setelah mengonsumsi `;` berikutnya | Diterima | Sebelumnya satu error menghabiskan semua token sampai EOF sehingga statement valid sesudahnya hilang; kini buang token hanya sampai dan termasuk `;`, sesuai aturan panic mode §6 — tiap statement rusak menghasilkan tepat satu error dan statement sesudahnya tetap diproses. | `python -m pytest -q` → **41 passed, 0 failed** (sebelumnya 40; +1 test regresi `test_regresi_error_recovery_berhenti_di_semicolon` yang terbukti gagal saat perbaikan di-stash); `python evaluate.py` → parser **P 1.00 / R 1.00 / F1 1.00** (sebelumnya R 0.93 dengan 2 FN di `campuran_error.sql`) |
| 9 | Muhammad Iqbal (251524057) — anggota 1 | Menindaklanjuti pengumuman dosen bersama AI (MiMoCode): audit daftar periksa (deliverable, ground truth, TODO, struktur) dan audit SPESIFIKASI.md baris demi baris; menambah test regresi Bug 4 serta 4 test kasus tepi baru (total 5) di `tests/test_tambahan.py`; menambah `.gitignore` | Diterima | Daftar periksa menuntut satu test regresi per bug dan lima kasus tepi — Bug 4 sebelumnya belum punya test regresi. Audit §2–§8 (probe lexer/parser/resolver/analyzer/CLI terhadap spesifikasi) tidak menemukan pelanggaran baru. | `python -m pytest -q` → **46 passed, 0 failed** (sebelumnya 41; +1 regresi Bug 4 yang terbukti gagal saat `_pop()` di `_delete()` dihapus sementara; +4 kasus tepi); `python evaluate.py` → parser F1 1.00; `git diff --name-only` bersih untuk test terlihat dan `baseline/regex_extractor.py` |
| 10 | Muhammad Iqbal (251524057) — anggota 1 | Tindaklanjuti catatan kedua dosen bersama AI (MiMoCode): menghapus sisa teks instruksi templat di `test_tambahan.py`, `KARTU_DESAIN.md`, `LAPORAN_AKHIR.md`, `LOG_AI.md`, dan `LAPORAN_BUG.md`; menambah test regresi Bug 9 di `tests/test_tambahan.py` | Diterima | Catatan dosen mensyaratkan teks instruksi templat dihapus dan minimal 9 test regresi (satu per bug) + 5 kasus tepi di test tambahan; test regresi Bug 9 sebelumnya hanya ada di `tests/test_resolver.py`. | `python -m pytest -q` → **47 passed, 0 failed** (sebelumnya 46; `test_regresi_bug9_alias_subquery_menutupi_alias_luar` terbukti gagal saat `_lookup()` dikembalikan ke versi `reversed`, lulus setelahnya); total test tambahan kini 15 (9 regresi bug + 5 kasus tepi + 1 TODO T1) |

## Rincian pengerjaan TODO(T1) — `INSERT ... SELECT`

| Pihak | Yang dikerjakan |
| --- | --- |
| AI (MiMoCode) | Membaca SPESIFIKASI.md bagian 3 dan 5, lalu mengubah `crud/parser.py::Parser._insert()` agar `SELECT` setelah nama tabel/daftar kolom di-parse sebagai query sumber dan disimpan di `Insert.query`. Menambahkan test regresi `test_insert_select_sebelumnya_gagal_di_parse` dan kasus tepi `test_insert_select_tanpa_daftar_kolom` di `tests/test_tambahan.py`, serta menjalankan seluruh test. |
| Muhammad Iqbal (251524057) — anggota 1 | Menentukan target TODO(T1), meninjau diff `crud/parser.py`, memeriksa kesesuaiannya dengan grammar `insert_stmt` dan tabel aturan CRUD, lalu memverifikasi hasil dengan menjalankan `pytest` dan mencoba query contoh `INSERT INTO arsip_pesanan (id, total) SELECT ...` sebelum menerima perubahan. |

**Refleksi (3-5 kalimat).** AI paling membantu pada perubahan yang sudah dipetakan jelas oleh
spesifikasi: karena `Select` dan `Insert.query` sudah ada, implementasi TODO(T1) cukup
mengganti satu `raise` dengan pemanggilan `self._select()`. AI juga berguna untuk membuat test
regresi dan memeriksa keluaran AST/CRUD matrix. Namun AI sempat membuat kesimpulan yang
menyesatkan: setelah TODO(T1) selesai, `test_matrix_laporan_penjualan` masih gagal, dan
penyebabnya bukan TODO(T1) melainkan bug lexer (`<>` dan keyword huruf kecil) yang belum
dikerjakan. Karena itu hasil AI tidak boleh langsung dipercaya; verifikasi dilakukan dengan
membaca spesifikasi dan menjalankan test, bukan hanya melihat kode terlihat benar.

## Rincian pengerjaan TODO(T2) — resolver

| Pihak | Yang dikerjakan |
| --- | --- |
| Muhammad Fawwaz Muzakki (251524056)| Mengimplementasikan resolusi kolom tanpa qualifier di `crud/resolver.py::Resolver._column()` sesuai SPESIFIKASI.md bagian 4.3: bila scope terdalam berisi tepat satu tabel, `ColumnRef.resolved` diisi dengan tabel tersebut; bila berisi lebih dari satu tabel, resolver memberi warning bahwa kolom ambigu; bila tidak ada tabel, resolver memberi warning bahwa kolom tidak dapat di-resolve. Pada `_delete()`, menambahkan `_pop()` setelah kondisi `WHERE` di-resolve agar scope `DELETE` ditutup dan alias tidak bocor ke statement berikutnya sesuai bagian 4.5. |
| ChatGPT ASTRA | Membantu memeriksa bug pencarian qualifier bertingkat (Bug 9), mereproduksi kasus shadowing, lalu mengubah `crud/resolver.py::Resolver._lookup()` agar mencari mulai dari scope aktif ke `parent`. Menambahkan test shadowing dan correlated subquery di `tests/test_resolver.py`, serta memperbarui laporan bug. |

Verifikasi: implementasi TODO(T2) diperiksa dengan `tests/test_resolver.py::test_kolom_tanpa_qualifier_satu_tabel`; perbaikan scope `DELETE` tercatat pada commit `c5514fc`. Perbaikan Bug 9 diverifikasi dengan `py -m pytest -q` → **37 passed**; alias terdalam menang dan correlated subquery tetap dapat merujuk alias induk.

## Rincian pengerjaan TODO(T3) — komentar blok dan perbaikan lexer

| Pihak | Yang dikerjakan |
| --- | --- |
| AI (MiMoCode) | Membaca SPESIFIKASI.md bagian 2.2, 2.3, 2.5, dan 5. Mengubah `crud/lexer.py`: (1) `/* ... */` dikonsumsi sampai penutup, boleh lintas baris, tidak ditutup → `LexError`; (2) cabang `<` menghasilkan `<>`/`<=`/`<` (maximal munch); (3) `_word()` membandingkan `text.upper()` terhadap `KEYWORDS` dan menyimpan nilai keyword dalam huruf besar. Memperbaiki `crud/analyzer.py::_collect` agar tabel di dalam subquery (`IN (SELECT ...)`, `EXISTS`, `Subquery`) selalu ditandai R, lalu menjalankan seluruh test. |
| Muhammad Iqbal (251524057) — anggota 1 | Menentukan target TODO(T3) dan bug lexer yang tersisa, meninjau diff terhadap aturan spesifikasi (komentar blok, keyword case-insensitive, operator terpanjang, aturan CRUD subquery), lalu memverifikasi dengan menjalankan `pytest` sampai seluruh test lulus sebelum perubahan di-push ke `main`. |

**Refleksi (3-5 kalimat).** Setelah TODO(T3) dan dua bug lexer dikerjakan, `pytest` masih
menunjukkan satu kegagalan: matrix `laporan_penjualan` menghasilkan `pesanan = 'RUD'`.
Ternyata penyebabnya bukan lexer melainkan `crud/analyzer.py` yang mewariskan op `U` dari
`UPDATE` ke tabel di dalam subquery WHERE, padahal spesifikasi bagian 5 tegas bahwa membaca
tabel lewat subquery selalu R. Pelajarannya: kegagalan test tidak selalu ada di tempat yang
terlihat pertama kali — telusuri sampai aturan spesifikasi yang dilanggar, jangan berhenti di
perbaikan pertama yang membuat sebagian test hijau.

## Rincian perbaikan Bug 5 dan Bug 8

| Pihak | Yang dikerjakan |
| --- | --- |
| Muhammad Iqbal (251524057) | Menemukan Bug 5 pada pemindaian string dengan kutip tunggal berpasangan dan Bug 8 pada parsing `LEFT OUTER JOIN`. |
| Muhammad Fawwaz Muzakki (251524056) | Memperbaiki kedua bug dan menambahkan test regresi. |
| ChatGPT ASTRA | Membantu mengubah `crud/lexer.py::Lexer._string()` agar `''` di dalam string menjadi satu kutip literal, serta `crud/parser.py::Parser._join()` agar `OUTER` opsional diterima setelah `LEFT`. Menambahkan test di `tests/test_tambahan.py`. |

Verifikasi: `py -m pytest tests/test_tambahan.py tests/test_lexer.py tests/test_parser.py -q` → **28 passed**. SQL `INSERT INTO t (nama) VALUES ('O''Brien')` menghasilkan satu nilai string `O'Brien`; `LEFT OUTER JOIN` berhasil diparse, sedangkan `INNER OUTER JOIN` tetap menghasilkan error.

## Rincian perbaikan Bug 6

| Pihak | Yang dikerjakan |
| --- | --- |
| Muhammad Iqbal (251524057) | Menemukan Bug 6 saat audit §3.1, memastikan gejala dengan `pretty()` (`a = 1 OR b = 2 AND c = 3` berakar `AND`), meninjau perubahan parser terhadap grammar `or_expr`/`and_expr`, lalu menjalankan seluruh test sebelum dikerjakan. |
| AI (MiMoCode) | Menunjuk `crud/parser.py::_logical()` sebagai akar masalah (satu loop untuk `AND` dan `OR`), mengubahnya menjadi `_or()` → `_and()` → `_not()` sesuai urutan grammar §3.1, menambahkan test regresi `test_regresi_presedensi_or_dan_and` di `tests/test_tambahan.py`, dan memperbarui `docs/LAPORAN_BUG.md` bagian Bug 6. |

Verifikasi: `python -m pytest -q` → **40 passed, 0 failed**. Test regresi terbukti gagal saat perbaikan parser di-stash (akar `AND`) dan lulus setelah perbaikan (akar `OR`, anak kanan `AND`). Perbaikan Bug 6 di-commit sebagai `4f7ae06` dan sudah di-push ke `main`.

## Rincian perbaikan Bug 7

| Pihak | Yang dikerjakan |
| --- | --- |
| Muhammad Iqbal (251524057) | Menemukan Bug 7 saat audit §6 dan jejak `ground_truth.csv`, memastikan gejala (`SELECT id FROM; SELECT a FROM t;` → 1 error, 0 statement), meninjau perbaikan terhadap aturan "buang token sampai dan termasuk `;`", dan memverifikasi dengan `evaluate.py`. |
| AI (MiMoCode) | Menunjuk `crud/parser.py::_synchronize()` sebagai akar masalah (loop berhenti di EOF, bukan di `;`), mengubahnya agar berhenti setelah mengonsumsi token `SEMICOLON`, menambahkan test regresi `test_regresi_error_recovery_berhenti_di_semicolon` di `tests/test_tambahan.py`, dan memperbarui `LAPORAN_BUG.md` bagian Bug 7 serta `LAPORAN_AKHIR.md`. |

Verifikasi: `python -m pytest -q` → **41 passed, 0 failed**; test regresi terbukti gagal saat perbaikan di-stash (0 statement) dan lulus sesudahnya (1 error, statement sesudah `;` lolos); `python evaluate.py` → parser **P 1.00 / R 1.00 / F1 1.00** (2 FN `campuran_error.sql` hilang).
