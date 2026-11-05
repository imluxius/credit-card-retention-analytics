"""Business-relevant checks: leakage, denominators, bad input, and SQL reconciliation."""
import csv
import json
from pathlib import Path
import sqlite3
import tempfile
import unittest

from src.pipeline import ROOT, SOURCE_COLUMNS, read_source, make_connection, query_outputs


class PipelineTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows, cls.quality = read_source(ROOT / 'data/raw/BankChurners.csv')
        cls.con = make_connection(cls.rows)
        cls.result = query_outputs(cls.con)

    @classmethod
    def tearDownClass(cls):
        cls.con.close()

    def test_reference_snapshot(self):
        self.assertTrue(self.quality['reference_sha256_matches'])
        self.assertEqual(self.result['overview']['customers'], 10127)
        self.assertEqual(self.result['overview']['churned'], 1627)
        self.assertEqual(self.result['overview']['retained'], 8500)

    def test_sql_matches_independent_source_calculation(self):
        n = len(self.rows)
        expected = sum(r['attrition_flag'] == 'Attrited Customer' for r in self.rows)
        self.assertAlmostEqual(self.result['overview']['churn_rate'], expected / n)
        self.assertAlmostEqual(self.result['overview']['avg_transactions'],
                               sum(r['total_trans_ct'] for r in self.rows) / n)
        for segment in self.result['segments']:
            self.assertAlmostEqual(segment['churn_rate'], segment['churned'] / segment['customers'])

    def test_segment_denominators_and_churn_shares(self):
        for dimension in {r['dimension'] for r in self.result['segments']}:
            groups = [r for r in self.result['segments'] if r['dimension'] == dimension]
            self.assertEqual(sum(r['customers'] for r in groups), len(self.rows))
            self.assertEqual(sum(r['churned'] for r in groups), 1627)
            self.assertAlmostEqual(sum(r['share_of_churn'] for r in groups), 1)

    def test_unknown_is_retained_not_imputed(self):
        self.assertEqual(self.quality['unknown_categories']['income_category'], 1112)
        group = next(r for r in self.result['segments']
                     if r['dimension'] == 'income_category' and r['segment'] == 'Unknown')
        self.assertEqual(group['customers'], 1112)

    def test_model_outputs_excluded(self):
        columns = [r[1] for r in self.con.execute('PRAGMA table_info(customer_snapshot)')]
        self.assertEqual(len(columns), 21)
        self.assertFalse(any('naive' in c.lower() for c in columns))

    def test_small_sample_flag(self):
        platinum = next(r for r in self.result['segments']
                        if r['dimension'] == 'card_category' and r['segment'] == 'Platinum')
        self.assertEqual(platinum['customers'], 20)
        self.assertEqual(platinum['sample_note'], 'Small sample (<100)')

    def test_retrospective_cohort_partition(self):
        groups = self.result['cohorts']
        self.assertEqual(sum(r['customers'] for r in groups), 10127)
        investigation = next(r for r in groups if r['cohort'].startswith('Investigate'))
        direct = [r for r in self.rows if r['total_trans_ct'] < 60 and r['months_inactive_12_mon'] >= 3]
        self.assertEqual(investigation['customers'], len(direct))
        self.assertEqual(investigation['churned'] + investigation['existing_customers'], len(direct))

    def source_file(self, rows):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        path = Path(temporary.name) / 'test.csv'
        with path.open('w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=list(rows[0]))
            writer.writeheader()
            writer.writerows(rows)
        return path

    def source_record(self):
        with (ROOT / 'data/raw/BankChurners.csv').open() as f:
            return next(csv.DictReader(f))

    def test_duplicate_customer_rejected(self):
        record = self.source_record()
        with self.assertRaisesRegex(ValueError, 'Duplicate customer'):
            read_source(self.source_file([record, record]))

    def test_blank_numeric_rejected(self):
        record = self.source_record()
        record['Total_Trans_Ct'] = ''
        with self.assertRaisesRegex(ValueError, 'Missing value'):
            read_source(self.source_file([record]))

    def test_nonfinite_numeric_rejected(self):
        record = self.source_record()
        record['Credit_Limit'] = 'nan'
        with self.assertRaisesRegex(ValueError, 'Invalid Credit_Limit'):
            read_source(self.source_file([record]))

    def test_unrecognized_schema_rejected(self):
        record = self.source_record()
        del record['Total_Trans_Ct']
        with self.assertRaisesRegex(ValueError, 'source columns'):
            read_source(self.source_file([record]))

    def test_invalid_label_rejected(self):
        row = dict(self.rows[0], attrition_flag='Maybe')
        with self.assertRaises(sqlite3.IntegrityError):
            make_connection([row])

    def test_credit_identity_checked(self):
        record = self.source_record()
        record['Avg_Open_To_Buy'] = '1'
        with self.assertRaisesRegex(ValueError, 'balance reconciliation'):
            read_source(self.source_file([record]))

    def test_band_boundaries(self):
        rows = []
        for i, count in enumerate([39, 40, 59, 60, 79, 80]):
            rows.append(dict(self.rows[0], customer_id=str(i), total_trans_ct=count))
        con = make_connection(rows)
        self.addCleanup(con.close)
        bands = [r[0] for r in con.execute('SELECT transaction_band FROM customer_features ORDER BY customer_id')]
        self.assertEqual(bands, ['<40', '40-59', '40-59', '60-79', '60-79', '80+'])

    def test_empty_query_has_no_division_by_zero(self):
        con = make_connection([])
        self.addCleanup(con.close)
        overview = query_outputs(con)['overview']
        self.assertEqual(overview['customers'], 0)
        self.assertIsNone(overview['churn_rate'])

    def test_generated_metrics_match_current_queries(self):
        saved = json.loads((ROOT / 'reports/metrics.json').read_text())
        self.assertEqual(saved, self.result)


if __name__ == '__main__':
    unittest.main()
