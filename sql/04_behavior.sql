SELECT attrition_flag, COUNT(*) AS customers,
       AVG(total_trans_ct) AS avg_transactions,
       AVG(total_trans_amt) AS avg_transaction_amount,
       AVG(months_inactive_12_mon) AS avg_inactive_months,
       AVG(contacts_count_12_mon) AS avg_contacts,
       AVG(avg_utilization_ratio) AS avg_utilization,
       AVG(total_relationship_count) AS avg_relationships
FROM customer_features GROUP BY attrition_flag;
