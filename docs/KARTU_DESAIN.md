# Kartu Desain

Tuliskan lima keputusan desain penting dalam pekerjaan kalian. Untuk tiap keputusan, sebutkan
alternatif yang ditolak dan alasannya. Contoh topik (boleh memilih yang lain):

- bagaimana parser membedakan `*` sebagai "semua kolom" dan sebagai perkalian;
- di mana dan bagaimana presedensi `AND`/`OR` dinyatakan;
- mengapa error recovery berhenti di `;`, bukan di keyword `SELECT` berikutnya;
- urutan pencarian scope dan akibatnya pada shadowing serta correlated subquery;
- mengapa kolom tanpa qualifier hanya dilihat di scope terdalam, dan apa kelemahannya;
- bagaimana implementasi `INSERT ... SELECT` atau komentar blok kalian.

| No | Keputusan | Alternatif yang ditolak | Alasan |
| --- | --- | --- | --- |
| 1 | Memisahkan pipeline menjadi lexer → parser/AST → resolver → analyzer. | Mencari pola CRUD langsung dengan regex atau mencampur resolusi nama ke parser. | Token dan AST mempertahankan struktur SQL sehingga komentar/string tidak dianggap sintaks dan setiap tahap bisa diuji terpisah. Resolver juga membutuhkan scope yang sudah dibangun dari keseluruhan SELECT. |
| 2 | Mewakili `*` SELECT sebagai node `ast.Star`, sedangkan `*` perkalian menjadi `ast.BinaryOp`. | Menganggap setiap `*` sebagai wildcard atau selalu sebagai operator perkalian. | Makna `*` bergantung pada konteks grammar: `SELECT * FROM t` memilih semua kolom, sedangkan `harga * jumlah` adalah ekspresi. Node berbeda membuat maknanya eksplisit untuk tahap berikutnya. |
| 3 | Menggunakan rantai scope dan mencari qualifier dari scope terdalam ke luar. | Satu peta alias global atau pencarian scope luar lebih dahulu. | Alias subquery harus menutupi alias bernama sama di luar (shadowing), tetapi pencarian berlanjut ke induk bila alias lokal tidak ditemukan sehingga correlated subquery tetap bisa mengakses alias luar. |
| 4 | Resolusi kolom tanpa qualifier hanya melihat scope terdalam; hasil ambigu atau tanpa tabel dilaporkan sebagai warning. | Menebak tabel dari scope induk atau memilih salah satu tabel pada scope yang memiliki banyak tabel. | Tanpa katalog skema tidak ada dasar untuk mengetahui kepemilikan kolom. Warning dan `resolved=None` menghindari atribusi kolom yang tampak pasti tetapi bisa salah. |
| 5 | Analyzer menelusuri AST dan menetapkan operasi target statement secara terpisah; tabel yang dibaca di subquery selalu `R`. | Memindai teks SQL mentah atau mewariskan operasi luar (`U`/`D`) ke semua tabel pada subquery. | AST membedakan target statement dan sumber baca. Aturan eksplisit ini mencegah komentar/string memunculkan tabel palsu dan mengikuti aturan CRUD proyek untuk subquery. |
