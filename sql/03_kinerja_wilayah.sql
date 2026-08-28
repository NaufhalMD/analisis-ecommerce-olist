-- ============================================================
-- 03. Kinerja pengiriman per negara bagian
-- Mengukur durasi kirim, tingkat keterlambatan, dan kepuasan
-- untuk wilayah dengan minimal 500 pesanan.
-- ============================================================
SELECT cu.customer_state                                              AS negara_bagian,
       COUNT(*)                                                       AS pesanan,
       ROUND(AVG(julianday(o.order_delivered_customer_date)
                 - julianday(o.order_purchase_timestamp)), 1)         AS rata_hari_kirim,
       ROUND(100.0 * SUM(CASE
                WHEN julianday(o.order_delivered_customer_date)
                     > julianday(o.order_estimated_delivery_date)
                THEN 1 ELSE 0 END) / COUNT(*), 1)                     AS persen_telat,
       ROUND(AVG(r.review_score), 2)                                  AS rata_skor
FROM orders o
JOIN customers      cu ON cu.customer_id = o.customer_id
JOIN order_reviews  r  ON r.order_id     = o.order_id
WHERE o.order_status = 'delivered'
  AND o.order_delivered_customer_date IS NOT NULL
GROUP BY cu.customer_state
HAVING COUNT(*) >= 500
ORDER BY persen_telat DESC;
