-- Illustrative retrospective cohort, NOT a validated predictive rule.
-- Thresholds are hand-chosen for exploration, not tuned to maximize performance.
WITH tagged AS (
    SELECT *, CASE WHEN total_trans_ct < 60 AND months_inactive_12_mon >= 3
                   THEN 'Investigate: low activity + inactivity'
                   ELSE 'Other customers' END AS cohort
    FROM customer_features
), aggregated AS (
    SELECT cohort, COUNT(*) AS customers, SUM(churned) AS churned,
           SUM(1 - churned) AS existing_customers,
           1.0 * SUM(churned) / COUNT(*) AS churn_rate
    FROM tagged GROUP BY cohort
)
SELECT *,
       1.0 * churned / NULLIF(SUM(churned) OVER (), 0) AS share_of_churn,
       1.0 * customers / SUM(customers) OVER () AS share_of_customers
FROM aggregated ORDER BY cohort;
