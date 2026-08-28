"""
load_data.py
Memuat 9 berkas CSV Olist ke dalam basis data SQLite (olist.db)
agar relasi antar tabel dapat dikueri menggunakan SQL.

Jalankan sekali sebelum membuka notebook:
    python load_data.py
"""

import os
import sqlite3
import pandas as pd

DATA_DIR = "data"
DB_PATH = "olist.db"

# Nama berkas -> nama tabel
TABLES = {
    "olist_customers_dataset.csv": "customers",
    "olist_orders_dataset.csv": "orders",
    "olist_order_items_dataset.csv": "order_items",
    "olist_order_payments_dataset.csv": "order_payments",
    "olist_order_reviews_dataset.csv": "order_reviews",
    "olist_products_dataset.csv": "products",
    "olist_sellers_dataset.csv": "sellers",
    "olist_geolocation_dataset.csv": "geolocation",
    "product_category_name_translation.csv": "category_translation",
}

# Kolom bertipe tanggal per tabel
DATE_COLS = {
    "orders": [
        "order_purchase_timestamp",
        "order_approved_at",
        "order_delivered_carrier_date",
        "order_delivered_customer_date",
        "order_estimated_delivery_date",
    ],
    "order_items": ["shipping_limit_date"],
    "order_reviews": ["review_creation_date", "review_answer_timestamp"],
}

# Indeks untuk mempercepat JOIN
INDEXES = [
    "CREATE INDEX IF NOT EXISTS idx_orders_customer ON orders(customer_id)",
    "CREATE INDEX IF NOT EXISTS idx_items_order     ON order_items(order_id)",
    "CREATE INDEX IF NOT EXISTS idx_items_product   ON order_items(product_id)",
    "CREATE INDEX IF NOT EXISTS idx_items_seller    ON order_items(seller_id)",
    "CREATE INDEX IF NOT EXISTS idx_reviews_order   ON order_reviews(order_id)",
    "CREATE INDEX IF NOT EXISTS idx_payments_order  ON order_payments(order_id)",
]


def main():
    if not os.path.isdir(DATA_DIR):
        raise SystemExit(
            f"Folder '{DATA_DIR}' tidak ditemukan.\n"
            "Unduh dataset dari Kaggle terlebih dahulu (lihat README)."
        )

    missing = [f for f in TABLES if not os.path.exists(os.path.join(DATA_DIR, f))]
    if missing:
        raise SystemExit("Berkas CSV berikut belum ada:\n  " + "\n  ".join(missing))

    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)

    conn = sqlite3.connect(DB_PATH)
    print(f"Membuat {DB_PATH}\n")

    for filename, table in TABLES.items():
        df = pd.read_csv(os.path.join(DATA_DIR, filename))

        # Simpan tanggal dalam format ISO agar bisa diolah SQL maupun pandas
        for col in DATE_COLS.get(table, []):
            df[col] = pd.to_datetime(df[col], errors="coerce")

        df.to_sql(table, conn, if_exists="replace", index=False)
        print(f"  {table:22} {len(df):>8,} baris  x {len(df.columns)} kolom")

    for stmt in INDEXES:
        conn.execute(stmt)
    conn.commit()

    size_mb = os.path.getsize(DB_PATH) / 1048576
    print(f"\nSelesai. {DB_PATH} ({size_mb:.1f} MB), {len(TABLES)} tabel, "
          f"{len(INDEXES)} indeks.")
    conn.close()


if __name__ == "__main__":
    main()
