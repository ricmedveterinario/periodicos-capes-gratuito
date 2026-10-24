import unittest
from import_scholar_collection import same_title, official_key

class ImportTests(unittest.TestCase):
    def test_only_explicit_aliases_are_accepted(self):
        self.assertTrue(same_title('4OR','4OR-A Quarterly Journal of Operations Research'))
        self.assertTrue(same_title('ACM Transactions on Graphics','ACM Transactions on Graphics (TOG)'))
        self.assertFalse(same_title('Nature','Nature Communications'))
        self.assertFalse(same_title('Journal','Journal: unrelated edition'))
    def test_non_google_urls_and_unconfirmed_editions_are_rejected(self):
        for url in ['https://evil.test/citations?view_op=list_hcore&venue=A.2025',
                    'https://scholar.google.com/citations?view_op=list_hcore&venue=A.2020',
                    'https://scholar.google.com/citations?user=A']:
            with self.assertRaises(ValueError): official_key(url)
    def test_venue_identifier_ignores_language_parameters(self):
        a='https://scholar.google.com/citations?hl=en&view_op=list_hcore&venue=A.2025'
        self.assertEqual(official_key(a),official_key(a.replace('hl=en','hl=pt-BR')))
