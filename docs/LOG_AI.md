# Log Penggunaan AI

Catat setiap penggunaan AI atau coding agent yang memengaruhi kode atau laporan.

| No | Siapa | Prompt / tugas (ringkas) | Hasil: diterima, diubah, atau ditolak | Alasan | Cara verifikasi |
| --- | --- | --- | --- | --- | --- |
| 1 | Muhammad Iqbal (251524057) — anggota 1 | Minta bantuan AI (MiMoCode) mengerjakan TODO(T1): dukung `INSERT INTO ... SELECT ...` sesuai SPESIFIKASI.md bagian 3 dan 5 | Diterima | Perubahan kecil dan terarah: `_insert()` memakai ulang `_select()` yang sudah ada, lalu mengisi `ast.Insert.query`; `values` tetap kosong. API publik dan aturan arsitektur tidak berubah. | `pytest -q` → 28 passed (sebelumnya 25 passed, 5 failed); AST `INSERT ... SELECT` dicek dengan `ast_nodes.pretty()`; `analyze_source()` menghasilkan `{'arsip_pesanan': 'C', 'pesanan': 'R'}` |
| 2 | Muhammad Iqbal (251524057) — anggota 1 | Verifikasi status TODO(T1) bersama AI (MiMoCode): memastikan implementasi `INSERT ... SELECT` di `crud/parser.py` sudah selesai, menjalankan ulang test, memperbarui catatan log ini, lalu push ke branch `Muhammad-Iqbal` dan merge ke `main` | Diterima | Implementasi T1 sudah ada dan test khusus T1 lulus; sisa kegagalan test berasal dari bug lexer yang belum dikerjakan (T3), bukan dari T1. | `pytest -q` → 29 passed, 3 failed (semua gagal di lexer: `test_keyword_huruf_kecil`, `test_komentar_blok`, `test_matrix_laporan_penjualan`); `pytest tests/test_tambahan.py` → 2 passed |
| 3 | Muhammad Iqbal (251524057) — anggota 1 | Bersama AI (MiMoCode): menyelesaikan TODO(T3) sekaligus **memperbaiki 3 bug** — (1) keyword tidak peka huruf besar/kecil (SPESIFIKASI.md §2.2), (2) operator `<>` terpecah jadi dua token (§2.5), (3) tabel dalam subquery `UPDATE`/`DELETE` salah ditandai `U`, harusnya selalu `R` (§5); ditambah `/* ... */` komentar blok (§2.3) | Diterima | Keempat perbaikan persis mengikuti spesifikasi: keyword dinormalkan ke huruf besar lewat `text.upper()`, `<>` di-lex dengan maximal munch, subquery selalu dipanggil dengan op `R`, komentar blok dikonsumsi sampai `*/`. Lalu ditambahkan 3 test regresi untuk bug 1–3 di `tests/test_tambahan.py`. | `pytest -q` → **35 passed, 0 failed** (sebelumnya 29 passed, 3 failed; +3 test regresi baru: `test_regresi_keyword_huruf_kecil`, `test_regresi_operator_tidak_sama_dengan`, `test_regresi_subquery_update_tidak_ditandai_u`); matrix `laporan_penjualan.sql` kini `{'arsip_pesanan': 'C', 'pelanggan': 'RU', 'pesanan': 'RD'}` |

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
