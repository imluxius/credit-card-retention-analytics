"""Validate a Kaggle snapshot, load SQLite, run SQL, and export evidence.

Run from any directory: python -m src.pipeline (from the repository root).
All metrics are calculated from source rows; no hand-entered headline results.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE_URL = 'https://www.kaggle.com/datasets/sakshigoyal7/credit-card-customers'
SOURCE_SHA256 = 'c91b525a2a6755a1b0b80dad1d0d008ca97ec4df34552c8f47ffa12b6184b779'
SOURCE_COLUMNS = [
    'CLIENTNUM', 'Attrition_Flag', 'Customer_Age', 'Gender', 'Dependent_count',
    'Education_Level', 'Marital_Status', 'Income_Category', 'Card_Category',
    'Months_on_book', 'Total_Relationship_Count', 'Months_Inactive_12_mon',
    'Contacts_Count_12_mon', 'Credit_Limit', 'Total_Revolving_Bal', 'Avg_Open_To_Buy',
    'Total_Amt_Chng_Q4_Q1', 'Total_Trans_Amt', 'Total_Trans_Ct',
    'Total_Ct_Chng_Q4_Q1', 'Avg_Utilization_Ratio',
]
COLUMNS = ['customer_id'] + [x.lower() for x in SOURCE_COLUMNS[1:]]
TEXT_COLUMNS = set(SOURCE_COLUMNS[:2] + ['Gender', 'Education_Level', 'Marital_Status',
                                      'Income_Category', 'Card_Category'])
INTEGER_COLUMNS = {'Customer_Age', 'Dependent_count', 'Months_on_book',
                   'Total_Relationship_Count', 'Months_Inactive_12_mon',
                   'Contacts_Count_12_mon', 'Total_Trans_Ct'}
QUERIES = {
    'overview': '02_overview.sql', 'segments': '03_segments.sql',
    'behavior': '04_behavior.sql', 'cohorts': '05_investigation_cohort.sql',
}


def read_source(path: Path) -> tuple[list[dict], dict]:
    """Fail on schema drift and invalid records; retain explicit Unknown categories."""
    rows, identifiers = [], set()
    with path.open(encoding='utf-8-sig', newline='') as handle:
        reader = csv.DictReader(handle)
        headers = reader.fieldnames or []
        excluded = [c for c in headers if c.startswith('Naive_Bayes_Classifier_')]
        if len(headers) != len(set(headers)):
            raise ValueError('Duplicate column names')
        if set(headers) != set(SOURCE_COLUMNS + excluded):
            raise ValueError('Unexpected or missing source columns')
        for line, row in enumerate(reader, 2):
            if None in row or any(v is None or v.strip() == '' for v in row.values()):
                raise ValueError(f'Missing value or malformed CSV at line {line}')
            clean = {}
            for src, dest in zip(SOURCE_COLUMNS, COLUMNS):
                value = row[src].strip()
                try:
                    if src in TEXT_COLUMNS:
                        clean[dest] = value
                    elif src in INTEGER_COLUMNS:
                        clean[dest] = int(value)
                    else:
                        clean[dest] = float(value)
                        if not math.isfinite(clean[dest]):
                            raise ValueError('Non-finite number')
                except ValueError as exc:
                    raise ValueError(f'Invalid {src} at line {line}') from exc
            if clean['customer_id'] in identifiers:
                raise ValueError(f'Duplicate customer identifier at line {line}')
            identifiers.add(clean['customer_id'])
            # These identities should hold within source rounding precision.
            if clean['credit_limit'] <= 0:
                raise ValueError(f'Credit limit must be positive at line {line}')
            if abs(clean['credit_limit'] - clean['total_revolving_bal'] - clean['avg_open_to_buy']) > 0.02:
                raise ValueError(f'Credit balance reconciliation failed at line {line}')
            if abs(clean['avg_utilization_ratio'] - clean['total_revolving_bal'] / clean['credit_limit']) > 0.0011:
                raise ValueError(f'Utilization reconciliation failed at line {line}')
            rows.append(clean)
    if not rows:
        raise ValueError('Empty dataset')
    quality = {
        'rows': len(rows), 'source_columns': len(headers), 'retained_columns': len(COLUMNS),
        'excluded_model_columns': excluded, 'duplicate_customer_ids': 0,
        'missing_cells': 0,
        'unknown_categories': {c: sum(r[c] == 'Unknown' for r in rows)
                               for c in ['education_level', 'marital_status', 'income_category']},
        'source_sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
        'reference_sha256_matches': hashlib.sha256(path.read_bytes()).hexdigest() == SOURCE_SHA256,
        'checks': ['schema', 'required values', 'unique customer IDs', 'finite numeric values',
                   'SQLite domain constraints', 'credit balance identity', 'utilization identity'],
    }
    return rows, quality


def make_connection(rows: list[dict], database: str | Path = ':memory:') -> sqlite3.Connection:
    con = sqlite3.connect(str(database))
    con.row_factory = sqlite3.Row
    try:
        con.executescript((ROOT / 'sql/01_schema.sql').read_text())
        names = ','.join(COLUMNS)
        placeholders = ','.join('?' for _ in COLUMNS)
        with con:
            con.executemany(f'INSERT INTO customer_snapshot ({names}) VALUES ({placeholders})',
                            [tuple(row[c] for c in COLUMNS) for row in rows])
    except Exception:
        con.close()
        raise
    return con


def query_outputs(con: sqlite3.Connection) -> dict:
    result = {key: [dict(r) for r in con.execute((ROOT / 'sql' / name).read_text())]
              for key, name in QUERIES.items()}
    result['overview'] = result['overview'][0]
    # Export only aggregate charts + anonymous behavior/filter attributes.
    result['dashboard_rows'] = [dict(r) for r in con.execute('''
        SELECT churned, card_category, income_category, total_trans_ct,
               total_trans_amt, months_inactive_12_mon, contacts_count_12_mon,
               avg_utilization_ratio, total_relationship_count
        FROM customer_features ORDER BY customer_id
    ''')]
    return result


def write_csv(path: Path, rows: list[dict]) -> None:
    with path.open('w', encoding='utf-8', newline='') as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator='\n')
        writer.writeheader()
        writer.writerows(rows)


def render_report(result: dict, quality: dict) -> str:
    o = result['overview']
    behavior = {r['attrition_flag']: r for r in result['behavior']}
    lost, kept = behavior['Attrited Customer'], behavior['Existing Customer']
    segment = next(r for r in result['segments']
                   if r['dimension'] == 'transaction_band' and r['segment'] == '<40')
    cohort = next(r for r in result['cohorts'] if r['cohort'].startswith('Investigate'))
    lines = [
        '# Analysis results — generated from SQL', '',
        f'Source: [Kaggle Credit Card Customers]({SOURCE_URL}).', '',
        '## Executive brief', '',
        f"The snapshot contains **{o['customers']:,} customers**, including **{o['churned']:,} "
        f"labelled attrited ({o['churn_rate']:.2%})** and {o['retained']:,} existing customers.", '',
        'This is a cross-sectional association analysis. Observation dates and the timing of '
        'measurements versus attrition are unavailable; no causal or predictive claims are made.', '',
        '## Findings and their practical meaning', '',
        f"1. Attrited customers average **{lost['avg_transactions']:.1f} transactions**, versus "
        f"**{kept['avg_transactions']:.1f}** for existing customers. Lower activity is associated "
        'with attrition, but may also be a consequence of leaving.',
        f"2. The <40-transaction segment contains **{segment['customers']:,} customers**, "
        f"with **{segment['churn_rate']:.2%}** labelled attrited. It accounts for "
        f"**{segment['share_of_churn']:.2%}** of all attrited customers. Review both the rate "
        'and the population size when choosing a segment to investigate.',
        f"3. Mean recorded contacts are **{lost['avg_contacts']:.2f}** for attrited versus "
        f"**{kept['avg_contacts']:.2f}** for existing customers. The data does not specify "
        'whether these are complaints, inbound calls, or outreach; more contacts do not prove poor service.',
        f"4. An illustrative cohort (<60 transactions and >=3 inactive months) contains "
        f"**{cohort['customers']:,} customers**, including **{cohort['churned']:,} attrited** "
        f"and **{cohort['existing_customers']:,} existing**. Its historical attrition proportion "
        f"is **{cohort['churn_rate']:.2%}**. This is a retrospective exploration rule, not "
        'a validated score or deployment-ready contact list.', '',
        '## Recommendation and validation plan', '',
        '- Prioritize discovery into low activity: request dated transaction history, closure dates, '
        'reason codes, fees and service-contact outcomes. Check that all proposed inputs precede the outcome.',
        '- Interview service/CRM stakeholders to understand why activity drops and what recorded contacts mean.',
        '- If current, consented operational data confirms a useful segment, run a randomized retention pilot. '
        'Define eligibility before randomization; measure 90-day active retention on all assigned customers '
        '(intention to treat), with contact cost, opt-out and complaint guardrails.',
        '- No intervention uplift, prevented churn, savings or ROI can be estimated as an achieved result '
        'from this dataset. Pricing and fee recommendations require data not present here.', '',
        '## Segment evidence', '',
        '| Dimension | Segment | Customers | Attrited | Attrition proportion | Share of attrited |',
        '|---|---|---:|---:|---:|---:|',
    ]
    for r in result['segments']:
        lines.append(f"| {r['dimension']} | {r['segment']} | {r['customers']:,} | {r['churned']:,} | "
                     f"{r['churn_rate']:.2%} | {r['share_of_churn']:.2%} |")
    lines.extend(['', '## Quality and limitations', '',
                  f"- Source SHA-256: `{quality['source_sha256']}`.",
                  f"- {quality['rows']:,} records; no duplicate IDs or blank cells; "
                  "'Unknown' categories retained as reported.",
                  '- Two supplied Naive Bayes output columns are excluded to avoid target leakage.',
                  '- Small groups (<100 records) are flagged, not treated as reliable ranked targets.',
                  '- No dates, individual transaction events, confirmed currency, fees, or reason for leaving.',
                  '- No named bank or verified real-world provenance. Do not generalize to Vietnamese banks.',
                  '- Associations were explored on the full snapshot; no out-of-time validation or causal design.',
                  '- Demographic groups may describe the sample; do not use them as eligibility rules.', '',
                  'Reproduce with `python -m src.pipeline`. Full query outputs are in `reports/*.csv`.'])
    return '\n'.join(lines) + '\n'


def run(source: Path, output: Path) -> dict:
    rows, quality = read_source(source)
    output.mkdir(parents=True, exist_ok=True)
    processed = ROOT / 'data/processed'
    processed.mkdir(parents=True, exist_ok=True)
    # Rebuild into a temporary file; preserve a successful prior build on validation failure.
    temporary = processed / 'retention.build.sqlite'
    temporary.unlink(missing_ok=True)
    con = make_connection(rows, temporary)
    try:
        result = query_outputs(con)
        total = result['overview']['customers']
        for dimension in {r['dimension'] for r in result['segments']}:
            group = [r for r in result['segments'] if r['dimension'] == dimension]
            if sum(r['customers'] for r in group) != total:
                raise ValueError('Segment denominator reconciliation failed')
            if sum(r['churned'] for r in group) != result['overview']['churned']:
                raise ValueError('Segment attrition reconciliation failed')
    finally:
        con.close()
    temporary.replace(processed / 'retention.sqlite')
    for key in ['segments', 'behavior', 'cohorts']:
        write_csv(output / f'{key}.csv', result[key])
    (output / 'quality.json').write_text(json.dumps(quality, indent=2) + '\n')
    public = {k: v for k, v in result.items() if k != 'dashboard_rows'}
    (output / 'metrics.json').write_text(json.dumps(public, indent=2) + '\n')
    (output / 'analysis.md').write_text(render_report(result, quality), encoding='utf-8')
    from src.dashboard import build_dashboard
    build_dashboard(result, ROOT / 'dashboard/index.html')
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, default=ROOT / 'data/raw/BankChurners.csv')
    parser.add_argument('--output', type=Path, default=ROOT / 'reports')
    args = parser.parse_args()
    result = run(args.source, args.output)
    print(json.dumps(result['overview'], indent=2))
    print('Built reports/, data/processed/retention.sqlite and dashboard/index.html')


if __name__ == '__main__':
    main()
