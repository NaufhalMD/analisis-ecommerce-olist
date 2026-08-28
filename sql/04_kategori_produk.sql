-- ============================================================
-- 04. Pendapatan dan kepuasan per kategori produk
-- Nama kategori diterjemahkan ke bahasa Inggris melalui
-- tabel category_translation.
-- ============================================================
SELECT COALESCE(t.product_category_name_english,
                p.product_category_name,
                '(tidak diketahui)')          AS kategori,
       COUNT(*)                               AS jumlah_item,
       ROUND(SUM(oi.price), 2)                AS total_pendapatan,
       ROUND(AVG(oi.price), 2)                AS rata_harga,
       ROUND(AVG(oi.freight_value), 2)        AS rata_ongkir,
       ROUND(AVG(r.review_score), 2)          AS rata_skor
FROM order_items oi
JOIN products p ON p.product_id = oi.product_id
LEFT JOIN category_translation t
       ON t.product_category_name = p.product_category_name
JOIN order_reviews r ON r.order_id = oi.order_id
GROUP BY kategori
HAVING COUNT(*) >= 100
ORDER BY total_pendapatan DESC
LIMIT 20;
