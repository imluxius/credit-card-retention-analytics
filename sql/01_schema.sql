PRAGMA foreign_keys = ON;
CREATE TABLE customer_snapshot (
    customer_id TEXT PRIMARY KEY,
    attrition_flag TEXT NOT NULL CHECK (attrition_flag IN ('Existing Customer', 'Attrited Customer')),
    customer_age INTEGER NOT NULL CHECK (customer_age > 0),
    gender TEXT NOT NULL,
    dependent_count INTEGER NOT NULL CHECK (dependent_count >= 0),
    education_level TEXT NOT NULL,
    marital_status TEXT NOT NULL,
    income_category TEXT NOT NULL,
    card_category TEXT NOT NULL,
    months_on_book INTEGER NOT NULL CHECK (months_on_book >= 0),
    total_relationship_count INTEGER NOT NULL CHECK (total_relationship_count >= 0),
    months_inactive_12_mon INTEGER NOT NULL CHECK (months_inactive_12_mon BETWEEN 0 AND 12),
    contacts_count_12_mon INTEGER NOT NULL CHECK (contacts_count_12_mon >= 0),
    credit_limit REAL NOT NULL CHECK (credit_limit > 0),
    total_revolving_bal REAL NOT NULL CHECK (total_revolving_bal >= 0),
    avg_open_to_buy REAL NOT NULL CHECK (avg_open_to_buy >= 0),
    total_amt_chng_q4_q1 REAL NOT NULL CHECK (total_amt_chng_q4_q1 >= 0),
    total_trans_amt REAL NOT NULL CHECK (total_trans_amt >= 0),
    total_trans_ct INTEGER NOT NULL CHECK (total_trans_ct >= 0),
    total_ct_chng_q4_q1 REAL NOT NULL CHECK (total_ct_chng_q4_q1 >= 0),
    avg_utilization_ratio REAL NOT NULL CHECK (avg_utilization_ratio BETWEEN 0 AND 1)
);

-- One row per customer in a single snapshot; no invented dates or event history.
CREATE VIEW customer_features AS
SELECT *,
    CASE WHEN attrition_flag = 'Attrited Customer' THEN 1 ELSE 0 END AS churned,
    CASE WHEN total_trans_ct < 40 THEN '<40'
         WHEN total_trans_ct < 60 THEN '40-59'
         WHEN total_trans_ct < 80 THEN '60-79' ELSE '80+' END AS transaction_band,
    CASE WHEN months_inactive_12_mon <= 1 THEN '0-1'
         WHEN months_inactive_12_mon = 2 THEN '2'
         WHEN months_inactive_12_mon = 3 THEN '3' ELSE '4+' END AS inactivity_band,
    CASE WHEN contacts_count_12_mon <= 1 THEN '0-1'
         WHEN contacts_count_12_mon = 2 THEN '2'
         WHEN contacts_count_12_mon = 3 THEN '3' ELSE '4+' END AS contact_band,
    CASE WHEN avg_utilization_ratio = 0 THEN 'Zero'
         WHEN avg_utilization_ratio < 0.3 THEN '(0, 0.3)'
         WHEN avg_utilization_ratio < 0.6 THEN '[0.3, 0.6)' ELSE '[0.6, 1]' END AS utilization_band
FROM customer_snapshot;
