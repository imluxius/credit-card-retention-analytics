-- Attrition is an observed snapshot label, not a monthly churn event rate.
SELECT COUNT(*) AS customers,
       SUM(churned) AS churned,
       COUNT(*) - SUM(churned) AS retained,
       1.0 * SUM(churned) / NULLIF(COUNT(*), 0) AS churn_rate,
       AVG(total_trans_ct) AS avg_transactions,
       AVG(total_trans_amt) AS avg_transaction_amount,
       AVG(avg_utilization_ratio) AS avg_utilization
FROM customer_features;
