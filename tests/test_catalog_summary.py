import unittest
import pandas as pd
from catalog_summary import catalog_counts
from metrics_guide import example_h_index

class SummaryTests(unittest.TestCase):
    def setUp(self):
        self.frame=pd.DataFrame([
            {'Título da Revista':'A','ISSN':'1111-1111','Editora':'Elsevier','Modelo':'Híbrido','Cobertura APC':'100%','Fonte OpenAlex':''},
            {'Título da Revista':'B','ISSN':'2222-2222','Editora':'Wiley Gold','Modelo':'OA','Cobertura APC':'55% (você paga 45%)','Fonte OpenAlex':'https://openalex.org/S1'},
            {'Título da Revista':'C','ISSN':'3333-3333','Editora':'Nature Portfolio','Modelo':'Híbrido','Cobertura APC':'APC sujeita à elegibilidade do autor e da instituição','Fonte OpenAlex':''}])
    def test_coverage_does_not_depend_on_openalex(self):
        a=catalog_counts(self.frame,lambda *args,**kwargs:None)
        self.frame['Fonte OpenAlex']='https://openalex.org/S1'
        b=catalog_counts(self.frame,lambda *args,**kwargs:None)
        self.assertEqual((a['full'],a['partial'],a['other']),(1,1,1))
        self.assertEqual(a['full'],b['full'])
        self.assertEqual((a['openalex'],b['openalex']),(1,3))
    def test_counts_partition_catalogue_without_treating_discount_as_free(self):
        c=catalog_counts(self.frame,lambda title,**kwargs:{} if title=='B' else None)
        self.assertEqual(c['full']+c['partial']+c['other'],c['total'])
        self.assertEqual(c['google'],1)
    def test_h_index_example_is_not_mean_or_maximum(self):
        self.assertEqual(example_h_index([8,5,3,2,1]),3)
        self.assertEqual(example_h_index([20,12,8,4,1]),4)
        self.assertEqual(example_h_index([2,1,0,0,0]),1)
        self.assertEqual(example_h_index([]),0)
