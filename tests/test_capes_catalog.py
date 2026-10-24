from datetime import date
from unittest.mock import patch
import unittest
import tempfile
from pathlib import Path

import pandas as pd
from capes_catalog import load_catalog, acceptance_status, normalize, prepare_search, search_catalog


class CatalogTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from capes_catalog import PUBLISHERS, JOURNALS_FILE, INSTITUTIONS_FILE
        cls.temp = tempfile.TemporaryDirectory(dir=Path(__file__).resolve().parent)
        root = Path(cls.temp.name)
        cls.legacy_count = 0
        with pd.ExcelWriter(root/JOURNALS_FILE,engine='openpyxl') as writer:
            for sheet,publisher in PUBLISHERS.items():
                rows=[{'Título da Revista':'Example journal','ISSN':'1234-567X','Modelo':'Híbrido','Cobertura APC':'100%'}]
                if publisher=='Springer Nature':
                    rows += [{'Título da Revista':f'Read-only example {i}','ISSN':f'R{i}','Modelo':'Subscription','Cobertura APC':'Sem publicação indicada na lista oficial'} for i in range(38)]
                    rows += [{'Título da Revista':f'Pending example {i}','ISSN':f'P{i}','Modelo':'Fully Open Access','Cobertura APC':'Pendente: confirmar cobertura do modelo não híbrido'} for i in range(13)]
                cls.legacy_count+=len(rows)
                pd.DataFrame(rows).to_excel(writer,sheet_name=sheet,index=False)
            pd.DataFrame(columns=['Ícone','Editora','Tipo','Cobertura','Registros','Vigência','Obs']).to_excel(writer,sheet_name='📊 ÍNDICE',index=False)
            for sheet in ['✅ REQUISITOS','⚠️ AVISOS']:
                pd.DataFrame({'Texto':['Example requirement']}).to_excel(writer,sheet_name=sheet,index=False)
        pd.DataFrame([
            ['Springer Nature','ANP','Academia Nacional De Polícia','academia nacional de policia'],
            ['Elsevier','UFU','Universidade Federal De Uberlândia','ufu universidade federal de uberlandia'],
            ['Wiley','UFU','Universidade Federal De Uberlândia','ufu universidade federal de uberlandia'],
        ],columns=['Editora','Sigla','Nome da Instituição','Busca (normalizado)']).to_excel(root/INSTITUTIONS_FILE,index=False)
        with patch('urllib.request.urlopen', side_effect=AssertionError('Network must not be used')):
            cls.catalog, cls.institutions = load_catalog(data_dir=root)

    @classmethod
    def tearDownClass(cls):
        cls.temp.cleanup()

    def test_all_legacy_records_and_auxiliary_tabs_are_preserved(self):
        from capes_catalog import PUBLISHERS
        self.assertEqual(sum(len(self.catalog[p]) for p in PUBLISHERS.values()), self.legacy_count)
        self.assertEqual(len(self.catalog['Nature Portfolio']), 41)
        for name in ['INDICE','REQUISITOS','AVISOS']:
            self.assertIsNotNone(self.catalog[name])

    def test_nature_is_not_all_nature_branded_titles(self):
        titles = set(self.catalog['Nature Portfolio']['Título da Revista'])
        self.assertIn('Nature', titles)
        self.assertIn('Nature Energy', titles)
        self.assertNotIn('Scientific Reports', titles)
        self.assertNotIn('Nature Communications', titles)

    def test_institution_scope_is_portfolio_specific(self):
        groups = self.institutions.groupby('Editora').size()
        self.assertEqual(groups['Springer Nature'], 435)
        self.assertEqual(groups['Nature Portfolio'], 299)
        matches = self.institutions[self.institutions['Nome da Instituição'].map(normalize) == normalize('Academia Nacional De Polícia')]
        self.assertIn('Springer Nature', set(matches['Editora']))
        self.assertNotIn('Nature Portfolio', set(matches['Editora']))
        ufu = self.institutions[self.institutions['Nome da Instituição'].map(normalize) == normalize('Universidade Federal De Uberlândia')]
        self.assertTrue({'Springer Nature','Nature Portfolio'}.issubset(set(ufu['Editora'])))

    def test_acceptance_boundaries(self):
        for publisher, start in [('Springer Nature',date(2026,1,1)),('Nature Portfolio',date(2026,9,1)),('Elsevier',date(2026,1,1))]:
            self.assertIn('Dentro', acceptance_status(publisher,start))
            self.assertIn('Dentro', acceptance_status(publisher,date(2028,12,31)))
            self.assertIn('Fora', acceptance_status(publisher,date(2029,1,1)))
            self.assertIn('Informe', acceptance_status(publisher,None))
        self.assertIn('Fora', acceptance_status('Nature Portfolio', date(2026,8,31)))

    def test_search_is_literal_accent_insensitive_and_matches_issn_without_dash(self):
        frame=prepare_search(pd.DataFrame({'Título da Revista':['Ciência [A]'], 'ISSN':['1234-567X']}))
        for term in ['ciencia','[','1234567X','1234-567X']:
            self.assertEqual(len(search_catalog(frame,term)),1)
        self.assertEqual(len(search_catalog(frame,'.*')),0)

    def test_springer_uncertain_coverage_is_never_labeled_100_percent(self):
        coverage=self.catalog['Springer Nature']['Cobertura APC'].astype(str)
        self.assertEqual(coverage.str.contains('Sem publicação',regex=False).sum(),38)
        self.assertEqual(coverage.str.contains('Pendente:',regex=False).sum(),13)


if __name__=='__main__':
    unittest.main()
