# Laporan Akhir

## 1. Hasil evaluasi

Tempel keluaran `python evaluate.py` setelah `data/ground_truth.csv` dilengkapi.

```text

```

## 2. Tiga kasus di mana regex salah

Untuk tiap kasus: SQL-nya, kesalahan regex, dan mengapa parser benar (kaitkan dengan konsep
lexing, parsing, atau resolusi).

1.
2.
3.

## 3. Batas pendekatan kami

Minimal tiga hal yang **tidak bisa** ditangani dengan benar oleh tool ini meskipun semua bug
sudah diperbaiki. Untuk tiap batas: contoh SQL atau situasinya, akibatnya pada CRUD matrix,
dan informasi apa yang dibutuhkan untuk mengatasinya.

1.
2.
3.

## 4. Pembagian kerja

Siapa mengerjakan apa, dan bagaimana kalian memastikan keduanya memahami seluruh kode.

### Anggota 1 — Muhammad Iqbal (251524057)

| Lingkup | AI (OpenCode) | Muhammad Iqbal |
| --- | --- | --- |
| TODO(T1) `INSERT ... SELECT` | Mengimplementasikan perubahan di `crud/parser.py::Parser._insert()` (memakai ulang `_select()` dan mengisi `Insert.query`), menambahkan test regresi/kasus tepi di `tests/test_tambahan.py`, serta menjalankan `pytest`. | Menentukan target TODO(T1), meninjau diff dan kesesuaiannya dengan SPESIFIKASI.md bagian 3 dan 5, menjalankan test, dan memverifikasi CRUD matrix query contoh (`arsip_pesanan` = C, `pesanan` = R). |

Pemahaman kode dipastikan dengan saling menjelaskan alur `parser._insert()` → `Insert.query`
→ `analyzer`/`resolver`, lalu mengecek ulang lewat AST (`ast_nodes.pretty`) dan test yang
gagal sebelum perbaikan.

