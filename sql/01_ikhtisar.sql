-- ============================================================
-- 01. Ikhtisar dataset
-- Cakupan waktu, jumlah pesanan, dan sebaran status.
-- ============================================================

-- Rentang waktu dan volume
SELECT MIN(date(order_purchase_timestamp)) AS tanggal_awal,
       MAX(date(order_purchase_timestamp)) AS tanggal_akhir,
       COUNT(*)                            AS total_pesanan,
       COUNT(DISTINCT customer_id)         AS total_pelanggan
FROM orders;

-- Sebaran status pesanan
SELECT order_status,
       COUNT(*)                                  AS jumlah,
       ROUND(100.0 * COUNT(*) / (SELECT COUNT(*) FROM orders), 2) AS persen
FROM orders
GROUP BY order_status
ORDER BY jumlah DESC;
