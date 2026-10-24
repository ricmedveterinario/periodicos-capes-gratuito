import unittest
from unittest.mock import patch
from scholar_metrics import lookup, scholar_panel, snapshot

class ScholarTests(unittest.TestCase):
    def test_direct_google_value_has_own_provenance(self):
        self.assertEqual(lookup('3 Biotech')['h5_index'],53)
        self.assertEqual(lookup('3 Biotech')['h5_median'],92)
        html=scholar_panel('3 Biotech')
        self.assertIn('2026-10-24',html)
        self.assertNotIn('ASSERT-KTH',html)
    def test_exact_identity_and_no_estimation(self):
        self.assertEqual(lookup('Journal of Systems and Software')['h5_index'],72)
        self.assertIsNone(lookup('Transactions on Software Engineering'))
        self.assertIsNone(lookup('Unknown journal'))
        missing=scholar_panel('missing')
        self.assertIn('Não disponível na nossa amostra',missing)
        self.assertNotIn('font-size:1.875rem',missing)
    def test_duplicate_identity_is_rejected(self):
        record=snapshot()['records'][0]
        self.assertIsNone(lookup(record['title'],{'records':[record,record]}))
    def test_edition_and_provenance_always_visible(self):
        html=scholar_panel('Journal of Systems and Software')
        for value in ('72','112','2025','2020','2024','captura','Não é consulta ao vivo','target="_blank"'):
            self.assertIn(value,html)
        self.assertNotIn('JIF',html)
    def test_issn_mismatch_cannot_receive_a_title_match(self):
        data={'records':[{'title':'Test journal','issn':'1234-567X','h5_index':12}]}
        self.assertIsNone(lookup('Test journal',data,issn='0000-0000'))
        self.assertEqual(lookup('Test journal',data,issn='1234-567X')['h5_index'],12)
    def test_provided_collection_is_not_called_independent_live_check(self):
        data={'edition':2025,'period':'2020–2024','records':[{'title':'Test journal','h5_index':12,'h5_median':20,'verification':'provided_collection','checked_at':'2026-10-24','source_url':'https://scholar.google.com/citations?view_op=list_hcore&venue=test.2025'}]}
        with patch('scholar_metrics.snapshot',return_value=data):
            html=scholar_panel('Test journal')
        self.assertIn('12',html)
        self.assertIn('20',html)
        self.assertIn('lotes fornecidos',html)
        self.assertNotIn('conferido diretamente',html)

if __name__=='__main__': unittest.main()
