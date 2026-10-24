import unittest
from urllib.parse import urlparse, parse_qs
from discovery_links import scholar_journal_url, scholar_topic_url, summary_cards


class DiscoveryLinkTests(unittest.TestCase):
    def test_journal_uses_publication_filter_not_impact_metric(self):
        url = scholar_journal_url('Ciência & Saúde "A"')
        self.assertEqual(urlparse(url).netloc, 'scholar.google.com')
        self.assertEqual(parse_qs(urlparse(url).query)['as_publication'], ['Ciência & Saúde "A"'])

    def test_topic_is_encoded_and_has_no_abstract_parameter(self):
        query = parse_qs(urlparse(scholar_topic_url('bacteria & resistance')).query)
        self.assertEqual(query['q'], ['bacteria & resistance'])
        self.assertEqual(set(query), {'q', 'hl'})

    def test_summary_has_distinct_responsive_tiles(self):
        html = summary_cards({'total':5936,'full':5277,'openalex':5918,'google':226})
        self.assertEqual(html.count('class="pa-summary-item"'), 4)
        self.assertIn('5.936', html)


if __name__ == '__main__':
    unittest.main()
