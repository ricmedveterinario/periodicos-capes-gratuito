import unittest
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
        self.assertEqual(lookup('Nature')['h5_index'],490)
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
        self.assertIsNone(lookup('3 Biotech',issn='0000-0000'))
        self.assertEqual(lookup('3 Biotech',issn='2190-5738')['h5_index'],53)
    def test_provided_collection_is_not_called_independent_live_check(self):
        html=scholar_panel('ACM Computing Surveys')
        self.assertIn('184',html)
        self.assertIn('313',html)
        self.assertIn('lotes fornecidos',html)
        self.assertNotIn('conferido diretamente',html)

if __name__=='__main__': unittest.main()
