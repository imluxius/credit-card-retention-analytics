-- Rates must be accompanied by denominators. Share of all attrited customers
-- distinguishes high-rate small segments from high-volume segments.
WITH segments AS (
    SELECT 'transaction_band' AS dimension, transaction_band AS segment, churned FROM customer_features
    UNION ALL SELECT 'inactivity_band', inactivity_band, churned FROM customer_features
    UNION ALL SELECT 'contact_band', contact_band, churned FROM customer_features
    UNION ALL SELECT 'utilization_band', utilization_band, churned FROM customer_features
    UNION ALL SELECT 'card_category', card_category, churned FROM customer_features
    UNION ALL SELECT 'income_category', income_category, churned FROM customer_features
), grouped AS (
    SELECT dimension, segment, COUNT(*) AS customers, SUM(churned) AS churned,
           1.0 * SUM(churned) / COUNT(*) AS churn_rate
    FROM segments GROUP BY dimension, segment
)
SELECT *,
       1.0 * churned / NULLIF(SUM(churned) OVER (PARTITION BY dimension), 0) AS share_of_churn,
       churn_rate - (SELECT AVG(churned) FROM customer_features) AS difference_from_overall,
       CASE WHEN customers < 100 THEN 'Small sample (<100)' ELSE 'Descriptive only' END AS sample_note
FROM grouped ORDER BY dimension, churn_rate DESC, segment;
