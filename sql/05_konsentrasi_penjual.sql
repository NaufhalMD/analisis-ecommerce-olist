-- ============================================================
-- 05. Konsentrasi pendapatan penjual (analisis Pareto)
-- Menggunakan window function untuk menghitung kontribusi
-- kumulatif tiap penjual terhadap total pendapatan.
-- ============================================================
WITH pendapatan_penjual AS (
    SELECT seller_id, SUM(price) AS pendapatan
    FROM order_items
    GROUP BY seller_id
),
peringkat AS (
    SELECT seller_id,
           pendapatan,
           ROW_NUMBER() OVER (ORDER BY pendapatan DESC)                       AS peringkat,
           SUM(pendapatan) OVER (ORDER BY pendapatan DESC
                                 ROWS UNBOUNDED PRECEDING)                    AS pendapatan_kumulatif,
           SUM(pendapatan) OVER ()                                            AS pendapatan_total,
           COUNT(*)        OVER ()                                            AS jumlah_penjual
    FROM pendapatan_penjual
)
SELECT peringkat,
       seller_id,
       ROUND(pendapatan, 2)                                           AS pendapatan,
       ROUND(100.0 * peringkat / jumlah_penjual, 1)                    AS persen_penjual,
       ROUND(100.0 * pendapatan_kumulatif / pendapatan_total, 1)       AS persen_pendapatan_kumulatif
FROM peringkat
WHERE peringkat <= 20;
