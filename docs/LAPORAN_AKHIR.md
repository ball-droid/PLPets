# Laporan Akhir

## 1. Hasil evaluasi

Keluaran `python evaluate.py` terhadap `data/ground_truth.csv` (27 triple):

```text
Dievaluasi: audit.sql, campuran_error.sql, laporan_penjualan.sql, pemeliharaan.sql (27 triple)

Metode   Precision  Recall     F1
parser        1.00    1.00   1.00
regex         0.65    0.81   0.72

[regex]
  salah ditemukan (FP): ('audit.sql', 16, 'sesi', 'R')
  salah ditemukan (FP): ('campuran_error.sql', 4, 'pesanan', 'R')
  salah ditemukan (FP): ('campuran_error.sql', 8, 'keranjang', 'R')
  salah ditemukan (FP): ('laporan_penjualan.sql', 2, 'pelanggan', 'D')
  salah ditemukan (FP): ('laporan_penjualan.sql', 2, 'pelanggan', 'R')
  salah ditemukan (FP): ('laporan_penjualan.sql', 2, 'pesanan', 'R')
  salah ditemukan (FP): ('laporan_penjualan.sql', 2, 'rahasia', 'R')
  salah ditemukan (FP): ('laporan_penjualan.sql', 15, 'pesanan', 'R')
  salah ditemukan (FP): ('pemeliharaan.sql', 2, 'crm.alamat', 'R')
  salah ditemukan (FP): ('pemeliharaan.sql', 2, 'crm.pelanggan', 'R')
  salah ditemukan (FP): ('pemeliharaan.sql', 2, 'pelanggan_lama', 'U')
  salah ditemukan (FP): ('pemeliharaan.sql', 15, 'crm.alamat', 'R')
  terlewat (FN):       ('audit.sql', 2, 'pesanan', 'R')
  terlewat (FN):       ('laporan_penjualan.sql', 3, 'pelanggan', 'R')
  terlewat (FN):       ('laporan_penjualan.sql', 3, 'pesanan', 'R')
  terlewat (FN):       ('pemeliharaan.sql', 3, 'crm.alamat', 'R')
  terlewat (FN):       ('pemeliharaan.sql', 3, 'crm.pelanggan', 'R')
```

Setelah Bug 7 diperbaiki (error recovery berhenti di `;` berikutnya), parser mencapai
precision, recall, dan F1 **1.00**: kedua statement sesudah statement rusak di
`campuran_error.sql` (`UPDATE produk`, `DELETE keranjang`) kini ikut diproses, sehingga
tidak ada lagi false negative pada parser.

## 2. Tiga kasus di mana regex salah

Untuk tiap kasus: SQL-nya, kesalahan regex, dan mengapa parser benar (kaitkan dengan konsep
lexing, parsing, atau resolusi).

1. **Daftar tabel dipisahkan koma — tabel kedua terlewat.**

   ```sql
   SELECT p.id FROM pelanggan p, pesanan o;
   ```

   Regex hanya mengambil nama yang langsung mengikuti `FROM`, sehingga menghasilkan
   `pelanggan: R` dan melewatkan `pesanan: R`. Parser membaca aturan
   `FROM table_ref { "," table_ref }`, sehingga kedua tabel masuk CRUD matrix. Ini
   membutuhkan parsing struktur daftar sumber, bukan pencarian pola teks tunggal.

2. **Kata `FROM` di dalam string dianggap sebagai tabel.**

   ```sql
   SELECT p.nama FROM pelanggan p WHERE p.catatan <> 'FROM rahasia';
   ```

   Regex menemukan `FROM rahasia` di dalam literal dan menambahkan false positive
   `rahasia: R`. Lexer mengenali seluruh `'FROM rahasia'` sebagai satu token `STRING`;
   karena itu parser tidak menganggap teks di dalamnya sebagai klausa SQL.

3. **Target `DELETE` ikut salah dihitung sebagai operasi baca.**

   ```sql
   DELETE FROM pesanan WHERE tanggal < :batas;
   ```

   Regex menghasilkan `pesanan: D` sekaligus `pesanan: R`, sebab pola generik `FROM` juga
   cocok pada target `DELETE`. Parser membedakan konteks statement: tabel target `DELETE`
   mendapat operasi `D`, sementara operasi `R` hanya diberikan pada tabel yang benar-benar
   dibaca, misalnya melalui subquery. Untuk query ini hasil yang benar hanya `pesanan: D`.

## 3. Batas pendekatan kami

Minimal tiga hal yang **tidak bisa** ditangani dengan benar oleh tool ini meskipun semua bug
sudah diperbaiki. Untuk tiap batas: contoh SQL atau situasinya, akibatnya pada CRUD matrix,
dan informasi apa yang dibutuhkan untuk mengatasinya.

1. **Tidak ada katalog skema atau metadata kolom.** Contoh: `SELECT id FROM pelanggan p
   JOIN pesanan o ON o.pelanggan_id = p.id;`. CRUD matrix tingkat tabel masih dapat
   menunjukkan `pelanggan: R` dan `pesanan: R`, tetapi kolom tanpa qualifier seperti `id`
   ambigu sehingga tidak bisa diatribusikan dengan benar dalam keluaran `--kolom`.
   Diperlukan metadata skema yang memetakan tabel ke kolomnya (atau qualifier eksplisit
   dalam query).

2. **Sintaks di luar grammar subset tidak dianalisis.** Contoh: `WITH aktif AS (SELECT id
   FROM pelanggan) SELECT id FROM aktif UNION SELECT id FROM arsip;`. CTE dan `UNION` ada
   di luar lingkup spesifikasi; statement dapat gagal diparse dan operasi tabel yang
   terlibat tidak lengkap di CRUD matrix. Diperlukan perluasan grammar, node AST, analyzer,
   dan test untuk dialek SQL yang ingin didukung.

3. **Efek tidak langsung dari view, trigger, prosedur, dan SQL dinamis tidak diketahui.**
   Contoh: `SELECT * FROM ringkasan_penjualan;` hanya mengungkap pemakaian nama view, bukan
   tabel dasar yang dibaca definisi view. Pemanggilan prosedur atau trigger juga bisa
   menyentuh tabel lain yang tidak tertulis di statement pemanggil. Diperlukan definisi
   view/prosedur/trigger, dependensi database, serta nilai runtime untuk SQL dinamis agar
   dampak CRUD dasarnya bisa ditelusuri.

## 4. Pembagian kerja

Siapa mengerjakan apa, dan bagaimana kalian memastikan keduanya memahami seluruh kode.

### Anggota 1 — Muhammad Iqbal (251524057)

| Lingkup | AI (MiMoCode) | Muhammad Iqbal |
| --- | --- | --- |
| TODO(T1) `INSERT ... SELECT` | Mengimplementasikan perubahan di `crud/parser.py::Parser._insert()` (memakai ulang `_select()` dan mengisi `Insert.query`), menambahkan test regresi/kasus tepi di `tests/test_tambahan.py`, serta menjalankan `pytest`. | Menentukan target TODO(T1), meninjau diff dan kesesuaiannya dengan SPESIFIKASI.md bagian 3 dan 5, menjalankan test, dan memverifikasi CRUD matrix query contoh (`arsip_pesanan` = C, `pesanan` = R). |
| TODO(T3) dan Bug 1–3 | Membantu perubahan lexer untuk keyword case-insensitive, operator `<>`, komentar blok, serta analyzer agar subquery selalu `R`; menambahkan test regresi. | Menentukan target dan meninjau perubahan terhadap spesifikasi, lalu memverifikasi test serta CRUD matrix. |
| Bug 6 presedensi `OR`/`AND` | Memisahkan `_logical()` menjadi `_or()` → `_and()` → `_not()` di `crud/parser.py` sesuai grammar §3.1, menambahkan test regresi `test_regresi_presedensi_or_dan_and`, dan memperbarui `LAPORAN_BUG.md` bagian Bug 6. | Menentukan target perbaikan dari temuan audit §3.1, meninjau diff terhadap grammar `or_expr`/`and_expr`, memverifikasi struktur AST dengan `pretty()` sebelum/sesudah, dan menjalankan seluruh test. |
| Bug 7 error recovery | Mengubah `crud/parser.py::_synchronize()` agar berhenti setelah mengonsumsi `;` berikutnya, menambahkan test regresi `test_regresi_error_recovery_berhenti_di_semicolon`, dan memperbarui `LAPORAN_BUG.md` bagian Bug 7. | Meninjau aturan §6, mereproduksi `SELECT id FROM; SELECT a FROM t;` (1 error, 0 statement), memverifikasi sebelum/sesudah dengan `pytest` dan `evaluate.py` (parser F1 1.00). |

### Anggota 2 — Muhammad Fawwaz Muzakki (251524056)

| Lingkup | AI (ChatGPT ASTRA) | Muhammad Fawwaz Muzakki |
| --- | --- | --- |
| TODO(T2) dan Bug 4 | Membantu meninjau perilaku yang ditentukan spesifikasi dan menyusun dokumentasi; implementasi TODO(T2) dan penutupan scope `DELETE` dikerjakan Muhammad Fawwaz. | Mengerjakan resolver sesuai SPESIFIKASI.md bagian 4 dan memverifikasi resolusi kolom serta scope `DELETE` dengan test. |
| Bug 5 dan Bug 8 | Membantu memperbaiki pemindaian kutip berpasangan pada string dan menerima `LEFT OUTER JOIN`; menambahkan test regresi. | Memperbaiki kedua bug yang ditemukan Muhammad Iqbal dan memverifikasi kasus valid maupun sintaks `INNER OUTER JOIN` yang harus tetap ditolak. |
| Bug 9 | Membantu mereproduksi shadowing, memperbaiki pencarian alias dari scope terdalam ke luar, dan menambahkan test shadowing serta correlated subquery. | Menemukan bug, menentukan perilaku yang diharapkan dari §4.3, dan memverifikasi perbaikan. |

Pemahaman lintas kode diperiksa dengan menelusuri alur lexer → parser/AST → resolver →
analyzer pada contoh SQL, meninjau perubahan sesuai bagian spesifikasi, dan menjalankan
test regresi. Seluruh 46 test lulus dan setelah Bug 7 diperbaiki seluruh bug pada
laporan ini sudah tertangani; evaluasi parser mencapai F1 1.00 terhadap 27 triple.
