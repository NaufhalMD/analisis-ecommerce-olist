-- ============================================================
-- 06. Tren bulanan pesanan dan pendapatan
-- Pertumbuhan bulan-ke-bulan dihitung memakai LAG().
-- ============================================================
WITH bulanan AS (
    SELECT strftime('%Y-%m', o.order_purchase_timestamp) AS bulan,
           COUNT(DISTINCT o.order_id)                    AS pesanan,
           SUM(oi.price)                                 AS pendapatan
    FROM orders o
    JOIN order_items oi ON oi.order_id = o.order_id
    WHERE o.order_status = 'delivered'
    GROUP BY bulan
)
SELECT bulan,
       pesanan,
       ROUND(pendapatan, 2)                                            AS pendapatan,
       ROUND(100.0 * (pendapatan - LAG(pendapatan) OVER (ORDER BY bulan))
             / LAG(pendapatan) OVER (ORDER BY bulan), 1)               AS pertumbuhan_persen
FROM bulanan
ORDER BY bulan;
