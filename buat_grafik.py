"""
buat_grafik.py
Menghasilkan seluruh grafik analisis ke folder output/.
Jalankan setelah load_data.py.
"""

import sqlite3
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

DB = "olist.db"
OUT = "output"

BIRU, MERAH, ABU = "#2563eb", "#dc2626", "#94a3b8"
plt.rcParams.update({
    "figure.dpi": 130, "savefig.dpi": 130, "font.size": 10,
    "axes.spines.top": False, "axes.spines.right": False,
    "axes.grid": True, "grid.alpha": 0.25, "grid.linestyle": "--",
    "figure.autolayout": True,
})

KOMA = lambda x, n=2: f"{x:.{n}f}".replace(".", ",")

# Pemisah desimal mengikuti kaidah bahasa Indonesia (koma)
FORMAT_KOMA = matplotlib.ticker.FuncFormatter(lambda v, _: KOMA(v, 1))


def q(conn, sql):
    return pd.read_sql(sql, conn)


def grafik_skor_vs_telat(conn):
    df = q(conn, """
        SELECT CAST(julianday(o.order_delivered_customer_date)
                    - julianday(o.order_estimated_delivery_date) AS INT) AS telat,
               COUNT(*) n, AVG(r.review_score) skor
        FROM orders o JOIN order_reviews r ON r.order_id = o.order_id
        WHERE o.order_status='delivered' AND o.order_delivered_customer_date IS NOT NULL
          AND julianday(o.order_delivered_customer_date)
              - julianday(o.order_estimated_delivery_date) BETWEEN 0 AND 10
        GROUP BY telat ORDER BY telat""")

    fig, ax = plt.subplots(figsize=(8, 4.5))
    ax.plot(df.telat, df.skor, marker="o", color=MERAH, lw=2.2, ms=6)
    ax.axhline(3, color=ABU, lw=1.2, ls="--")
    ax.text(9.6, 3.06, "batas netral (3,0)", ha="right", color="#64748b", fontsize=8.5)

    lewat = int(df[df.skor < 3].telat.min())
    ax.axvline(lewat, color=ABU, lw=1, ls=":")
    ax.annotate("skor jatuh di bawah netral\npada hari ke-" + str(lewat),
                xy=(lewat, 3), xytext=(lewat + 1.2, 3.6), fontsize=9, color="#334155",
                arrowprops=dict(arrowstyle="->", color=ABU, lw=1.1))

    ax.set_xlabel("Hari keterlambatan dari tanggal estimasi")
    ax.set_ylabel("Rata-rata skor ulasan")
    ax.set_title("Setiap hari keterlambatan menurunkan skor ulasan",
                 fontweight="bold", pad=12)
    ax.set_xticks(range(0, int(df.telat.max()) + 1))
    ax.set_ylim(1.4, 4.3)
    ax.yaxis.set_major_formatter(FORMAT_KOMA)
    fig.savefig(OUT + "/01_skor_vs_keterlambatan.png")
    plt.close(fig)
    return df


def grafik_kategori_telat(conn):
    df = q(conn, """
        WITH d AS (
            SELECT julianday(o.order_delivered_customer_date)
                   - julianday(o.order_estimated_delivery_date) AS s,
                   r.review_score AS rs
            FROM orders o JOIN order_reviews r ON r.order_id = o.order_id
            WHERE o.order_status='delivered'
              AND o.order_delivered_customer_date IS NOT NULL)
        SELECT CASE WHEN s<=0 THEN 'Tepat waktu'
                    WHEN s<=3 THEN 'Telat 1-3 hari'
                    WHEN s<=7 THEN 'Telat 4-7 hari'
                    ELSE 'Telat >7 hari' END AS k,
               COUNT(*) n, AVG(rs) skor,
               100.0*SUM(CASE WHEN rs<=2 THEN 1 ELSE 0 END)/COUNT(*) rendah
        FROM d GROUP BY k""")
    urut = ["Tepat waktu", "Telat 1-3 hari", "Telat 4-7 hari", "Telat >7 hari"]
    df = df.set_index("k").loc[urut].reset_index()

    fig, (a1, a2) = plt.subplots(1, 2, figsize=(10.5, 4.2))
    warna = [BIRU, "#60a5fa", "#f59e0b", MERAH]

    a1.bar(df.k, df.skor, color=warna)
    a1.set_ylabel("Rata-rata skor ulasan")
    a1.set_ylim(0, 5)
    a1.yaxis.set_major_formatter(FORMAT_KOMA)
    a1.set_title("Skor ulasan", fontweight="bold")
    for i, v in enumerate(df.skor):
        a1.text(i, v + .12, KOMA(v), ha="center", fontsize=9)

    a2.bar(df.k, df.rendah, color=warna)
    a2.set_ylabel("Ulasan 1-2 bintang (%)")
    a2.set_ylim(0, 100)
    a2.set_title("Proporsi ulasan buruk", fontweight="bold")
    for i, v in enumerate(df.rendah):
        a2.text(i, v + 2.5, KOMA(v, 1) + "%", ha="center", fontsize=9)

    for a in (a1, a2):
        a.tick_params(axis="x", labelrotation=18, labelsize=9)
    fig.suptitle("Dampak keterlambatan terhadap kepuasan pelanggan",
                 fontweight="bold", fontsize=12.5, y=1.04)
    fig.savefig(OUT + "/02_kategori_keterlambatan.png", bbox_inches="tight")
    plt.close(fig)
    return df


def grafik_tren(conn):
    df = q(conn, """
        SELECT strftime('%Y-%m', o.order_purchase_timestamp) bulan,
               COUNT(DISTINCT o.order_id) pesanan, SUM(oi.price) pendapatan
        FROM orders o JOIN order_items oi ON oi.order_id = o.order_id
        WHERE o.order_status='delivered'
          AND o.order_purchase_timestamp >= '2017-01-01'
          AND o.order_purchase_timestamp <  '2018-09-01'
        GROUP BY bulan ORDER BY bulan""")

    fig, ax = plt.subplots(figsize=(9.5, 4.3))
    ax.bar(df.bulan, df.pendapatan / 1000, color=BIRU, alpha=.85)
    ax.set_ylabel("Pendapatan (ribu R$)")
    ax.set_title("Pendapatan bulanan — puncak pada November 2017 (Black Friday)",
                 fontweight="bold", pad=12)
    ax.tick_params(axis="x", labelrotation=60, labelsize=8)

    puncak = int(df.pendapatan.idxmax())
    ax.annotate("Black Friday",
                xy=(puncak, df.pendapatan[puncak] / 1000),
                xytext=(puncak - 3.4, df.pendapatan[puncak] / 1000 + 130),
                fontsize=9, color="#334155",
                arrowprops=dict(arrowstyle="->", color=ABU, lw=1.1))
    fig.savefig(OUT + "/03_tren_bulanan.png")
    plt.close(fig)
    return df


def grafik_kategori(conn):
    df = q(conn, """
        SELECT COALESCE(t.product_category_name_english,
                        p.product_category_name) kategori,
               SUM(oi.price) pendapatan, AVG(r.review_score) skor
        FROM order_items oi
        JOIN products p ON p.product_id = oi.product_id
        LEFT JOIN category_translation t
               ON t.product_category_name = p.product_category_name
        JOIN order_reviews r ON r.order_id = oi.order_id
        GROUP BY kategori ORDER BY pendapatan DESC LIMIT 10""")
    df = df.iloc[::-1]

    fig, ax = plt.subplots(figsize=(8.5, 4.6))
    ax.barh(df.kategori.str.replace("_", " "), df.pendapatan / 1000, color=BIRU)
    ax.set_xlabel("Pendapatan (ribu R$)")
    ax.set_title("10 kategori produk dengan pendapatan tertinggi",
                 fontweight="bold", pad=12)
    for i, (v, s) in enumerate(zip(df.pendapatan / 1000, df.skor)):
        ax.text(v + 14, i, "skor " + KOMA(s), va="center",
                fontsize=8.5, color="#64748b")
    ax.set_xlim(0, df.pendapatan.max() / 1000 * 1.18)
    fig.savefig(OUT + "/04_kategori_produk.png")
    plt.close(fig)
    return df


def grafik_wilayah(conn):
    df = q(conn, """
        SELECT cu.customer_state wilayah, COUNT(*) n,
               100.0*SUM(CASE WHEN julianday(o.order_delivered_customer_date)
                    > julianday(o.order_estimated_delivery_date)
                    THEN 1 ELSE 0 END)/COUNT(*) telat,
               AVG(julianday(o.order_delivered_customer_date)
                   - julianday(o.order_purchase_timestamp)) hari
        FROM orders o JOIN customers cu ON cu.customer_id = o.customer_id
        WHERE o.order_status='delivered'
          AND o.order_delivered_customer_date IS NOT NULL
        GROUP BY wilayah HAVING COUNT(*)>=500
        ORDER BY telat DESC LIMIT 12""")
    df = df.iloc[::-1]

    fig, ax = plt.subplots(figsize=(8.5, 4.8))
    warna = [MERAH if t >= 12 else "#f59e0b" if t >= 9 else BIRU for t in df.telat]
    ax.barh(df.wilayah, df.telat, color=warna)
    ax.set_xlabel("Pesanan terlambat (%)")
    ax.set_title("Keterlambatan tertinggi di wilayah utara dan timur laut",
                 fontweight="bold", pad=12)
    for i, (t, h) in enumerate(zip(df.telat, df.hari)):
        ax.text(t + .3, i, KOMA(h, 0) + " hari", va="center",
                fontsize=8.5, color="#64748b")
    ax.set_xlim(0, df.telat.max() * 1.22)
    fig.savefig(OUT + "/05_wilayah.png")
    plt.close(fig)
    return df


def main():
    conn = sqlite3.connect(DB)
    langkah = [
        ("skor vs keterlambatan", grafik_skor_vs_telat),
        ("kategori keterlambatan", grafik_kategori_telat),
        ("tren bulanan", grafik_tren),
        ("kategori produk", grafik_kategori),
        ("kinerja wilayah", grafik_wilayah),
    ]
    for nama, fn in langkah:
        fn(conn)
        print("  OK  " + nama)
    conn.close()
    print("\nSeluruh grafik tersimpan di " + OUT + "/")


if __name__ == "__main__":
    main()
