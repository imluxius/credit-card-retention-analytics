# Analysis results — generated from SQL

Source: [Kaggle Credit Card Customers](https://www.kaggle.com/datasets/sakshigoyal7/credit-card-customers).

## Executive brief

The snapshot contains **10,127 customers**, including **1,627 labelled attrited (16.07%)** and 8,500 existing customers.

This is a cross-sectional association analysis. Observation dates and the timing of measurements versus attrition are unavailable; no causal or predictive claims are made.

## Findings and their practical meaning

1. Attrited customers average **44.9 transactions**, versus **68.7** for existing customers. Lower activity is associated with attrition, but may also be a consequence of leaving.
2. The <40-transaction segment contains **1,802 customers**, with **30.08%** labelled attrited. It accounts for **33.31%** of all attrited customers. Review both the rate and the population size when choosing a segment to investigate.
3. Mean recorded contacts are **2.97** for attrited versus **2.36** for existing customers. The data does not specify whether these are complaints, inbound calls, or outreach; more contacts do not prove poor service.
4. An illustrative cohort (<60 transactions and >=3 inactive months) contains **1,903 customers**, including **848 attrited** and **1,055 existing**. Its historical attrition proportion is **44.56%**. This is a retrospective exploration rule, not a validated score or deployment-ready contact list.

## Recommendation and validation plan

- Prioritize discovery into low activity: request dated transaction history, closure dates, reason codes, fees and service-contact outcomes. Check that all proposed inputs precede the outcome.
- Interview service/CRM stakeholders to understand why activity drops and what recorded contacts mean.
- If current, consented operational data confirms a useful segment, run a randomized retention pilot. Define eligibility before randomization; measure 90-day active retention on all assigned customers (intention to treat), with contact cost, opt-out and complaint guardrails.
- No intervention uplift, prevented churn, savings or ROI can be estimated as an achieved result from this dataset. Pricing and fee recommendations require data not present here.

## Segment evidence

| Dimension | Segment | Customers | Attrited | Attrition proportion | Share of attrited |
|---|---|---:|---:|---:|---:|
| card_category | Platinum | 20 | 5 | 25.00% | 0.31% |
| card_category | Gold | 116 | 21 | 18.10% | 1.29% |
| card_category | Blue | 9,436 | 1,519 | 16.10% | 93.36% |
| card_category | Silver | 555 | 82 | 14.77% | 5.04% |
| contact_band | 4+ | 1,622 | 428 | 26.39% | 26.31% |
| contact_band | 3 | 3,380 | 681 | 20.15% | 41.86% |
| contact_band | 2 | 3,227 | 403 | 12.49% | 24.77% |
| contact_band | 0-1 | 1,898 | 115 | 6.06% | 7.07% |
| inactivity_band | 4+ | 737 | 181 | 24.56% | 11.12% |
| inactivity_band | 3 | 3,846 | 826 | 21.48% | 50.77% |
| inactivity_band | 2 | 3,282 | 505 | 15.39% | 31.04% |
| inactivity_band | 0-1 | 2,262 | 115 | 5.08% | 7.07% |
| income_category | $120K + | 727 | 126 | 17.33% | 7.74% |
| income_category | Less than $40K | 3,561 | 612 | 17.19% | 37.62% |
| income_category | Unknown | 1,112 | 187 | 16.82% | 11.49% |
| income_category | $80K - $120K | 1,535 | 242 | 15.77% | 14.87% |
| income_category | $40K - $60K | 1,790 | 271 | 15.14% | 16.66% |
| income_category | $60K - $80K | 1,402 | 189 | 13.48% | 11.62% |
| transaction_band | 40-59 | 2,134 | 835 | 39.13% | 51.32% |
| transaction_band | <40 | 1,802 | 542 | 30.08% | 33.31% |
| transaction_band | 60-79 | 3,468 | 214 | 6.17% | 13.15% |
| transaction_band | 80+ | 2,723 | 36 | 1.32% | 2.21% |
| utilization_band | Zero | 2,470 | 893 | 36.15% | 54.89% |
| utilization_band | (0, 0.3) | 3,776 | 385 | 10.20% | 23.66% |
| utilization_band | [0.6, 1] | 1,815 | 182 | 10.03% | 11.19% |
| utilization_band | [0.3, 0.6) | 2,066 | 167 | 8.08% | 10.26% |

## Quality and limitations

- Source SHA-256: `c91b525a2a6755a1b0b80dad1d0d008ca97ec4df34552c8f47ffa12b6184b779`.
- 10,127 records; no duplicate IDs or blank cells; 'Unknown' categories retained as reported.
- Two supplied Naive Bayes output columns are excluded to avoid target leakage.
- Small groups (<100 records) are flagged, not treated as reliable ranked targets.
- No dates, individual transaction events, confirmed currency, fees, or reason for leaving.
- No named bank or verified real-world provenance. Do not generalize to Vietnamese banks.
- Associations were explored on the full snapshot; no out-of-time validation or causal design.
- Demographic groups may describe the sample; do not use them as eligibility rules.

Reproduce with `python pipeline.py`. Full query outputs are in `reports/*.csv`.
