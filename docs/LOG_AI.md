# Log Penggunaan AI

Catat setiap penggunaan AI atau coding agent yang memengaruhi kode atau laporan.

| No | Siapa | Prompt / tugas (ringkas) | Hasil: diterima, diubah, atau ditolak | Alasan | Cara verifikasi |
| --- | --- | --- | --- | --- | --- |
| 1 | Muhammad Iqbal (251524057) — anggota 1 | Minta bantuan AI (MiMoCode) mengerjakan TODO(T1): dukung `INSERT INTO ... SELECT ...` sesuai SPESIFIKASI.md bagian 3 dan 5 | Diterima | Perubahan kecil dan terarah: `_insert()` memakai ulang `_select()` yang sudah ada, lalu mengisi `ast.Insert.query`; `values` tetap kosong. API publik dan aturan arsitektur tidak berubah. | `pytest -q` → 28 passed (sebelumnya 25 passed, 5 failed); AST `INSERT ... SELECT` dicek dengan `ast_nodes.pretty()`; `analyze_source()` menghasilkan `{'arsip_pesanan': 'C', 'pesanan': 'R'}` |
| 2 | Muhammad Iqbal (251524057) — anggota 1 | Verifikasi status TODO(T1) bersama AI (MiMoCode): memastikan implementasi `INSERT ... SELECT` di `crud/parser.py` sudah selesai, menjalankan ulang test, memperbarui catatan log ini, lalu push ke branch `Muhammad-Iqbal` dan merge ke `main` | Diterima | Implementasi T1 sudah ada dan test khusus T1 lulus; sisa kegagalan test berasal dari bug lexer yang belum dikerjakan (T3), bukan dari T1. | `pytest -q` → 29 passed, 3 failed (semua gagal di lexer: `test_keyword_huruf_kecil`, `test_komentar_blok`, `test_matrix_laporan_penjualan`); `pytest tests/test_tambahan.py` → 2 passed |

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
