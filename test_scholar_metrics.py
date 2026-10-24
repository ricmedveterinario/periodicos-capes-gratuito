import unittest
from scholar_metrics import lookup, scholar_panel, snapshot

class ScholarTests(unittest.TestCase):
    def test_exact_identity_and_no_estimation(self):
        self.assertEqual(lookup('IEEE Transactions on Software Engineering')['h5_index'],77)
        self.assertIsNone(lookup('Transactions on Software Engineering'))
        self.assertIsNone(lookup('Nature'))
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

if __name__=='__main__': unittest.main()
