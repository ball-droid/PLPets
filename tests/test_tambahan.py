"""Test tambahan buatan kelompok.

Isi dengan:
1. Satu test regresi untuk setiap bug yang kalian perbaiki (gagal sebelum perbaikan,
   lulus sesudahnya). Beri nama yang menjelaskan bug-nya.
2. Lima test kasus tepi, masing-masing dengan komentar singkat mengapa kasus itu berisiko.
"""
import pytest  # noqa: F401  (dipakai saat test kasus tepi ditambahkan)

from crud import ast_nodes as ast
from crud.analyzer import analyze_statement
from crud.lexer import TokenType, tokenize
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


# ---- regresi bug 1: keyword tidak peka huruf besar/kecil (bagian 2.2) ----
def test_regresi_keyword_huruf_kecil():
    """Sebelum perbaikan, 'Select'/'FrOm' di-lex sebagai IDENT (harus KEYWORD)."""
    toks = tokenize("Select id FrOm t")
    assert toks[0].type == TokenType.KEYWORD and toks[0].value == "SELECT"
    assert toks[2].type == TokenType.KEYWORD and toks[2].value == "FROM"


# ---- regresi bug 2: operator <> (bagian 2.5) ------------------------------
def test_regresi_operator_tidak_sama_dengan():
    """Sebelum perbaikan, '<>' terpecah jadi '<' lalu '>' (bukan maximal munch)."""
    vals = [t.value for t in tokenize("a <> 1") if t.type != TokenType.EOF]
    assert vals == ["a", "<>", "1"]


# ---- regresi bug 3: subquery di UPDATE selalu R (bagian 5) ---------------
def test_regresi_subquery_update_tidak_ditandai_u():
    """Sebelum perbaikan, tabel subquery WHERE ikut tercatat U (matrix jadi RUD)."""
    stmt = _one("UPDATE produk SET stok = 1 WHERE id IN (SELECT id FROM pesanan)")
    assert analyze_statement(stmt) == {"produk": {"U"}, "pesanan": {"R"}}
