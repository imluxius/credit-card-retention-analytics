# Data dictionary and metric definitions

Grain: **one customer per snapshot**. There is no observation date, event history, cancellation date, fee, intervention outcome, or verified currency. Meanings below follow the source column labels; ambiguous business definitions require clarification before operational use.

| Source → SQLite | Type | Interpretation / handling |
|---|---|---|
| CLIENTNUM → customer_id | text | Source identifier; unique key, never an analytical feature |
| Attrition_Flag → attrition_flag | text | `Existing Customer` or `Attrited Customer`; observed label |
| Customer_Age → customer_age | integer | Customer age; descriptive only |
| Gender → gender | text | Source gender label; not used for retention eligibility |
| Dependent_count → dependent_count | integer | Reported dependent count |
| Education_Level → education_level | text | Source education category; retain Unknown |
| Marital_Status → marital_status | text | Source marital-status category; retain Unknown |
| Income_Category → income_category | text | Source income bands; preserve labels including `$`; do not assert a verified currency |
| Card_Category → card_category | text | Blue, Silver, Gold, Platinum |
| Months_on_book → months_on_book | integer | Recorded relationship duration in months |
| Total_Relationship_Count → total_relationship_count | integer | Number of products/relationships recorded by source |
| Months_Inactive_12_mon → months_inactive_12_mon | integer | Recorded inactive-month count in 12 months; not necessarily consecutive |
| Contacts_Count_12_mon → contacts_count_12_mon | integer | Recorded contact count in 12 months; direction, reason and outcome unknown |
| Credit_Limit → credit_limit | real | Recorded credit limit; currency not verified |
| Total_Revolving_Bal → total_revolving_bal | real | Recorded revolving balance |
| Avg_Open_To_Buy → avg_open_to_buy | real | Available credit; reconciled to limit minus revolving balance within 0.02 source units |
| Total_Amt_Chng_Q4_Q1 → total_amt_chng_q4_q1 | real | Source-labelled Q4/Q1 transaction-amount change ratio; exact dates unavailable |
| Total_Trans_Amt → total_trans_amt | real | Recorded total transaction amount over the source's 12-month window |
| Total_Trans_Ct → total_trans_ct | integer | Recorded total transaction count over the source's 12-month window |
| Total_Ct_Chng_Q4_Q1 → total_ct_chng_q4_q1 | real | Source-labelled Q4/Q1 transaction-count change ratio |
| Avg_Utilization_Ratio → avg_utilization_ratio | real | Recorded utilization; check against revolving balance / credit limit within 0.0011 |
| Naive_Bayes_Classifier_* (2 columns) | excluded | Model outputs closely tied to the outcome; excluded to prevent leakage |

## KPIs

| Metric | Definition | Interpretation |
|---|---|---|
| Customers | Count of rows after filters | Distinct IDs validated before loading |
| Attrited customers | Count where Attrition_Flag = Attrited Customer | Observed source label |
| Attrition proportion | Attrited / all selected customers | Snapshot proportion; **not monthly churn rate** |
| Segment attrition proportion | Attrited in segment / customers in segment | Compare with denominator and sample size |
| Share of attrited | Attrited in segment / all attrited in selected population | Not the segment attrition proportion |
| Average transactions | Sum Total_Trans_Ct / selected customer count | Includes existing and attrited unless stated otherwise |
| Difference from overall | Segment proportion minus full-population proportion | Express as percentage points, not percent change |
| Average utilization | Arithmetic mean of per-customer ratios | Not sum of balances / sum of limits |

Zero denominators return NULL (`—` in the dashboard). Source money amounts are not used to claim revenue, profit, or financial loss.

## Segments

- Transaction count: `<40`, `40–59`, `60–79`, `80+` (inclusive lower boundaries).
- Inactive months and recorded contacts: `0–1`, `2`, `3`, `4+`.
- Utilization: exactly zero, `(0, 0.3)`, `[0.3, 0.6)`, `[0.6, 1]`.
- Groups below 100 customers carry a small-sample flag. The threshold is a presentation heuristic, not a statistical significance test.
- Illustrative investigation cohort: `<60 transactions AND >=3 inactive months`. Thresholds are exploratory, not learned or validated for future outcomes.

All measures might overlap or follow the attrition event. No feature is considered temporally safe for prediction without dated operational data.
