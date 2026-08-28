-- ============================================================
-- 02. Analisis utama: pengaruh keterlambatan terhadap ulasan
-- Membandingkan selisih tanggal tiba aktual dengan estimasi,
-- lalu mengaitkannya dengan skor ulasan pelanggan.
-- ============================================================

-- 2a. Skor rata-rata per kategori keterlambatan
WITH pengiriman AS (
    SELECT o.order_id,
           julianday(o.order_delivered_customer_date)
             - julianday(o.order_estimated_delivery_date) AS selisih_hari,
           r.review_score
    FROM orders o
    JOIN order_reviews r ON r.order_id = o.order_id
    WHERE o.order_status = 'delivered'
      AND o.order_delivered_customer_date IS NOT NULL
)
SELECT CASE
           WHEN selisih_hari <= 0 THEN 'Tepat waktu / lebih cepat'
           WHEN selisih_hari <= 3 THEN 'Telat 1-3 hari'
           WHEN selisih_hari <= 7 THEN 'Telat 4-7 hari'
           ELSE                       'Telat lebih dari 7 hari'
       END                                                      AS kategori,
       COUNT(*)                                                 AS jumlah_pesanan,
       ROUND(AVG(review_score), 2)                              AS rata_skor,
       ROUND(100.0 * SUM(CASE WHEN review_score <= 2 THEN 1 ELSE 0 END)
             / COUNT(*), 1)                                     AS persen_skor_rendah
FROM pengiriman
GROUP BY kategori
ORDER BY rata_skor DESC;

-- 2b. Penurunan skor per hari keterlambatan (mencari titik kritis)
SELECT CAST(julianday(o.order_delivered_customer_date)
            - julianday(o.order_estimated_delivery_date) AS INT) AS telat_hari,
       COUNT(*)                    AS jumlah_pesanan,
       ROUND(AVG(r.review_score), 2) AS rata_skor
FROM orders o
JOIN order_reviews r ON r.order_id = o.order_id
WHERE o.order_status = 'delivered'
  AND o.order_delivered_customer_date IS NOT NULL
  AND julianday(o.order_delivered_customer_date)
      - julianday(o.order_estimated_delivery_date) BETWEEN 0 AND 10
GROUP BY telat_hari
ORDER BY telat_hari;
