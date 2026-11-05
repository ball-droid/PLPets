"""Test tambahan buatan kelompok.

Isi dengan:
1. Satu test regresi untuk setiap bug yang kalian perbaiki (gagal sebelum perbaikan,
   lulus sesudahnya). Beri nama yang menjelaskan bug-nya.
2. Lima test kasus tepi, masing-masing dengan komentar singkat mengapa kasus itu berisiko.
"""
import pytest  # noqa: F401  (dipakai saat test kasus tepi ditambahkan)

from crud import ast_nodes as ast
from crud.analyzer import analyze_statement
from crud.parser import parse_sql


def _one(sql):
    script = parse_sql(sql)
    assert script.errors == [], script.errors
    assert len(script.statements) == 1
    return script.statements[0]


# ---- regresi TODO(T1): INSERT ... SELECT --------------------------------
def test_insert_select_sebelumnya_gagal_di_parse():
    """Sebelum TODO(T1) dikerjakan, statement ini menghasilkan ParseError."""
    stmt = _one("INSERT INTO arsip (id) SELECT id FROM pesanan WHERE total > 10")

    assert isinstance(stmt, ast.Insert)
    assert stmt.columns == ["id"]
    assert stmt.values == []
    assert isinstance(stmt.query, ast.Select)
    assert stmt.query.sources[0].name == "pesanan"
    # Target INSERT hanya C; tabel sumber SELECT tetap R (SPESIFIKASI.md bagian 5).
    assert analyze_statement(stmt) == {"arsip": {"C"}, "pesanan": {"R"}}


# ---- kasus tepi TODO(T1) ------------------------------------------------
def test_insert_select_tanpa_daftar_kolom():
    """Risiko: '(' setelah nama tabel bisa disalahartikan sebagai daftar kolom."""
    stmt = _one("INSERT INTO arsip SELECT * FROM pesanan")

    assert stmt.columns == []
    assert isinstance(stmt.query.columns[0], ast.Star)
    assert analyze_statement(stmt) == {"arsip": {"C"}, "pesanan": {"R"}}
