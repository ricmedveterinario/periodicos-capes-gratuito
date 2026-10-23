import unittest
import pandas as pd
from journal_recommender import JournalRecommender, institution_publishers
from journal_recommender import integral_candidate


class RecommenderTests(unittest.TestCase):
    def setUp(self):
        self.catalog = {
            'Springer Nature': pd.DataFrame([
                {'Título da Revista': 'Veterinary Microbiology', 'ISSN': '1', 'Cobertura APC': '100%', 'Modelo': 'Hybrid'},
                {'Título da Revista': 'Veterinary Research', 'ISSN': '2', 'Cobertura APC': 'Sem publicação indicada na lista oficial', 'Modelo': 'Subscription'},
                {'Título da Revista': 'Veterinary Biology', 'ISSN': '3', 'Cobertura APC': 'Pendente: confirmar cobertura', 'Modelo': 'Fully Open Access'},
            ]),
            'Nature Portfolio': pd.DataFrame([{'Título da Revista': 'Nature Microbiology', 'ISSN': '4', 'Cobertura APC': '100%', 'Modelo': 'Hybrid'}]),
            'Wiley Gold': pd.DataFrame([{'Título da Revista': 'Veterinary Science', 'ISSN': '5', 'Cobertura APC': '100%', 'Modelo': 'Gold'}]),
        }
        self.engine = JournalRecommender(self.catalog)

    def test_portuguese_query_matches_english_and_is_explained(self):
        results = self.engine.recommend(title='Microbiologia veterinária')
        self.assertEqual(results.iloc[0]['ISSN'], '1')
        self.assertIn('microbiology', results.iloc[0]['Termos relacionados'])

    def test_institution_filter_separates_springer_and_nature(self):
        results = self.engine.recommend(keywords='microbiology', publishers={'Springer Nature'})
        self.assertEqual(set(results['ISSN']), {'1'})
        self.assertTrue(self.engine.recommend(keywords='microbiology', publishers=set()).empty)

    def test_uncertain_and_discount_coverage_excluded_by_default(self):
        results = self.engine.recommend(keywords='veterinary')
        self.assertEqual(set(results['ISSN']), {'1'})
        self.assertEqual(len(self.engine.recommend(keywords='veterinary', integral_only=False)), 4)

    def test_empty_stopwords_and_unmatched_queries_return_no_random_results(self):
        for query in ['', 'the and estudo resultados', '[.*', 'zzzzzzzz']:
            self.assertTrue(self.engine.recommend(title=query).empty)

    def test_legacy_full_coverage_labels_are_recognized(self):
        for coverage in ['Sim', '0% (Gratuito)', '100%']:
            self.assertTrue(integral_candidate({'Cobertura APC': coverage, 'Editora': 'ACS'}))

    def test_exact_institution_selection_and_wiley_alias(self):
        frame = pd.DataFrame([['Universidade A', 'Springer Nature'], ['Universidade AB', 'Nature Portfolio'], ['Universidade A', 'Wiley']], columns=['Nome da Instituição', 'Editora'])
        publishers = institution_publishers(frame, 'Universidade A')
        self.assertNotIn('Nature Portfolio', publishers)
        self.assertIn('Wiley OnlineOpen', publishers)

    def test_deterministic_ranking_and_no_catalog_mutation(self):
        before = self.catalog['Springer Nature'].copy(deep=True)
        first = self.engine.recommend(title='microbiology')
        second = self.engine.recommend(title='microbiology')
        pd.testing.assert_frame_equal(first, second)
        pd.testing.assert_frame_equal(before, self.catalog['Springer Nature'])


if __name__ == '__main__':
    unittest.main()
