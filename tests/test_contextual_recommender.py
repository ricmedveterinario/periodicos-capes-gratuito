import unittest
import pandas as pd
from journal_recommender import JournalRecommender, integral_candidate

class ContextTests(unittest.TestCase):
    def test_partial_subject_matches_fill_requested_page(self):
        engine=self.engine([{'Título da Revista':f'Animal Nutrition {i}', 'Temas OpenAlex':'Animal nutrition; probiotics; veterinary medicine'} for i in range(12)])
        result=engine.recommend(title='Probióticos em leitões', keywords='probiotics; swine', limit=10)
        self.assertEqual(len(result),10)
        self.assertIn('Outras revistas para explorar',result['Grupo de sugestões'].tolist())

    def engine(self, rows):
        return JournalRecommender(pd.DataFrame([dict({'Editora':'Example','ISSN':str(i),'Modelo':'Hybrid','Cobertura APC':'100%'},**row) for i,row in enumerate(rows)]))

    def test_both_metadata_sources_are_indexed(self):
        engine=self.engine([{'Título da Revista':'Example','Área':'Microbiology','Área (OpenAlex)':'Veterinary','Temas OpenAlex':'Bacterial infections'}])
        self.assertIn('microbiology',engine.index.field_terms['area'][0])
        self.assertIn('veterinary',engine.index.field_terms['area'][0])

    def test_poultry_does_not_recommend_explicit_laboratory_specialism(self):
        engine=self.engine([
            {'Título da Revista':'Lab Animal','Temas OpenAlex':'Animal welfare; animal behavior'},
            {'Título da Revista':'Applied Animal Behaviour Science','Temas OpenAlex':'Animal welfare; poultry production; animal behavior'},
        ])
        result=engine.recommend(title='Bem-estar de galinhas poedeiras',keywords='poultry; animal welfare')
        self.assertNotIn('Lab Animal',result['Título da Revista'].tolist())
        self.assertTrue(all(integral_candidate(r) for _,r in result.iterrows()))

    def test_actual_laboratory_study_keeps_laboratory_journal(self):
        engine=self.engine([{'Título da Revista':'Lab Animal','Temas OpenAlex':'Laboratory animal welfare; animal behavior'}])
        result=engine.recommend(title='Laboratory animal welfare',integral_only=True)
        self.assertFalse(result.empty)

    def test_network_context_does_not_match_deep_ocean(self):
        engine=self.engine([
            {'Título da Revista':'Deep Sea Research','Temas OpenAlex':'Oceanography; marine science'},
            {'Título da Revista':'Computers and Security','Temas OpenAlex':'Network security; intrusion detection; deep learning'},
        ])
        result=engine.recommend(title='Aprendizagem profunda para detecção de intrusão em redes',keywords='deep learning; cybersecurity')
        self.assertEqual(result.iloc[0]['Título da Revista'],'Computers and Security')
        self.assertNotIn('Deep Sea Research',result['Título da Revista'].tolist())

    def test_empty_and_publisher_filter(self):
        engine=self.engine([{'Título da Revista':'Veterinary Microbiology'}])
        self.assertTrue(engine.recommend().empty)
        self.assertTrue(engine.recommend(title='veterinary',publishers=set()).empty)

if __name__=='__main__':unittest.main()