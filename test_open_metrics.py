import unittest
import tempfile
import gzip
import base64
import json
from pathlib import Path
import pandas as pd
from open_metrics import (enrich_catalog, filter_catalog, chart_records, safe_url,
                          issn_key, read_snapshot, METRIC, H_INDEX, AREA)


class OpenMetricTests(unittest.TestCase):
    def setUp(self):
        self.catalog = {'Springer Nature': pd.DataFrame([
            {'Título da Revista': 'Journal A', 'ISSN': '1234-567X', 'Cobertura APC': '100%', 'Modelo': 'Hybrid'},
            {'Título da Revista': 'Journal B', 'ISSN': '2345-6789', 'Cobertura APC': 'Pendente', 'Modelo': 'Hybrid'},
            {'Título da Revista': 'Journal C', 'ISSN': '3456-7890', 'Cobertura APC': '100%', 'Modelo': 'Hybrid'},
        ]), 'Nature Portfolio': pd.DataFrame([
            {'Título da Revista': 'Nature Test', 'ISSN': '4567-8901', 'Cobertura APC': '100%', 'Modelo': 'Hybrid'},
        ])}
        self.snapshot = {'retrieved_at': '2026-10-23T20:00:00Z', 'records': [
            {'id': 'https://openalex.org/S1', 'issns': ['1234-567X'], 'stats': {'2yr_mean_citedness': 4.5, 'h_index': 40}, 'homepage': 'https://example.org/a', 'field': 'Medicine'},
            {'id': 'https://openalex.org/S2', 'issns': ['2345-6789'], 'stats': {'2yr_mean_citedness': 0, 'h_index': 0}, 'homepage': 'https://example.org/b'},
            {'id': 'https://openalex.org/S3', 'issns': ['4567-8901'], 'stats': {'2yr_mean_citedness': 6, 'h_index': 20}, 'homepage': 'https://example.org/nature'},
        ]}
        self.frame = enrich_catalog(self.catalog, self.snapshot)

    def test_join_by_exact_issn_and_preserve_unmatched(self):
        self.assertEqual(len(self.frame), 4)
        row = self.frame[self.frame['ISSN'] == '1234-567X'].iloc[0]
        self.assertEqual(row[METRIC], 4.5)
        self.assertEqual(row['Página da revista'], 'https://example.org/a')
        self.assertEqual(row[AREA], 'Medicina')
        self.assertTrue(pd.isna(self.frame.iloc[2][METRIC]))

    def test_zero_is_real_missing_is_not_zero(self):
        self.assertEqual(self.frame.iloc[1][METRIC], 0)
        self.assertTrue(pd.isna(self.frame.iloc[2][METRIC]))
        result = filter_catalog(self.frame, metric_only=True)
        self.assertEqual(len(result), 3)

    def test_ambiguous_issn_has_no_metric(self):
        self.snapshot['records'].append({'id': 'https://openalex.org/S99', 'issns': ['1234-567X'], 'stats': {'2yr_mean_citedness': 99}})
        frame = enrich_catalog(self.catalog, self.snapshot)
        self.assertTrue(pd.isna(frame.iloc[0][METRIC]))
        self.assertIn('ambíguo', frame.iloc[0]['Correspondência'])

    def test_invalid_negative_and_nonfinite_metrics_are_missing(self):
        self.snapshot['records'][0]['stats'] = {'2yr_mean_citedness': -1, 'h_index': float('inf')}
        frame = enrich_catalog(self.catalog, self.snapshot)
        self.assertTrue(pd.isna(frame.iloc[0][METRIC]))
        self.assertTrue(pd.isna(frame.iloc[0][H_INDEX]))

    def test_sort_keeps_missing_last(self):
        result = filter_catalog(self.frame, order='Citações em 2 anos')
        self.assertEqual(result['ISSN'].tolist(), ['4567-8901', '1234-567X', '2345-6789', '3456-7890'])

    def test_literal_search_and_issn_without_hyphen(self):
        self.assertEqual(len(filter_catalog(self.frame, query='1234567x')), 1)
        self.assertTrue(filter_catalog(self.frame, query='[.*').empty)

    def test_filters_compose_and_separate_institution_portfolios(self):
        institutions = pd.DataFrame([['UFU', 'Springer Nature']], columns=['Nome da Instituição', 'Editora'])
        result = filter_catalog(self.frame, institutions=institutions, institution='UFU', full_coverage=True, metric_only=True)
        self.assertEqual(result['ISSN'].tolist(), ['1234-567X'])
        self.assertTrue(filter_catalog(self.frame, institutions=institutions, institution='Unknown').empty)

    def test_chart_link_is_from_same_issn_as_point(self):
        records = chart_records(self.frame)
        self.assertEqual(len(records), 3)
        self.assertEqual(next(r for r in records if r['ISSN'] == '1234-567X')['Página'], 'https://example.org/a')

    def test_missing_snapshot_records_do_not_hide_journals(self):
        frame = enrich_catalog(self.catalog, {'records': []})
        self.assertEqual(len(frame), 4)
        self.assertTrue(frame[METRIC].isna().all())
        self.assertEqual(chart_records(frame), [])

    def test_url_validation(self):
        for url in ['javascript:alert(1)', 'file:///secret', 'https://user:pass@example.org']:
            self.assertEqual(safe_url(url), '')
        self.assertEqual(issn_key('1234567X'), '1234567X')

    def test_compressed_public_snapshot_roundtrip(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'snapshot.json.gz.b64'
            path.write_bytes(base64.b64encode(gzip.compress(json.dumps(self.snapshot).encode())))
            self.assertEqual(read_snapshot(path), self.snapshot)


if __name__ == '__main__':
    unittest.main()
