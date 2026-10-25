"""Bilingual normalization, lexicon and contextual acronym handling.

This module is intentionally local and dependency-free. It is the shared
normalization layer for the legacy ranker and the modular recommender.
"""
from collections import Counter
import re
import unicodedata


STOP = set("""
a an and are as at be been being by can could did do does for from had has have he her here
his how if in into is it its may might more most must not of on or our out over should so some
such than that the their them then there these they this those through to under up use used
using was we were what when where which while who will with within without would you your
also however therefore thus among between during after before across around both each other
only same very just now
de da do das dos e em para por um uma os as que no na nos nas com como mais menos entre sobre
foi foram ser sao ser seu sua seus suas nosso nossa nossos nossas este esta estes estas esse
essa esses essas apos ate ja tambem pode podem ainda muito muita muitos muitas novo nova novos
novas artigo artigos article articles paper papers trabalho trabalhos estudo estudos study
studies sistema sistemas investiga investigam investigacao investigacoes indicador indicadores
indicadore pesquisa pesquisas research revista revistas journal journals
metodo metodos method methods resultado resultados result results conclusao conclusoes conclusion
conclusions discussao discussoes discussion introducao introduction objetivo objetivos objective
background dados data analise analises analysis using based
ao aos pelo pela pelos pelas num numa nuns numas se sem mas porem contudo entretanto assim apenas
durante antes depois atraves mediante segundo conforme deve devem sendo sido havia houve ha nao
sim tem ter estar estao quando onde qual quais
analisar analisado analisada analisados analisadas avaliar avaliado avaliada investigar investigado
investigada discutir discute discutem apresentar apresenta apresentam mostrar mostra mostram
indicar indica indicam observar observa observam verificar verifica verificam comparar compara
comparam identificar identifica identificam descrever descreve descrevem sugerir sugere sugerem
concluir conclui concluem recomendar recomenda recomendam realizar realiza realizam
analyze analyzed analyse analysed evaluate evaluated investigate investigated discuss discussed
present presented presenting show showed showing indicate indicated indicating observe observed observing
verify verified verifying compare compared comparing identify identified identifying describe described
describing suggest suggested suggesting conclude concluded concluding recommend recommended recommending
perform performed performing develop developed developing analyze analyzing evaluate evaluating
investigate investigating discuss discussing
analisando avaliando investigando discutindo apresentando mostrando indicando observando verificando
comparando identificando descrevendo sugerindo concluindo recomendando realizando desenvolvendo
""".split())


# Curated bilingual/domain vocabulary. The first word of each line is the canonical term.
GROUPS = [
    'veterinary veterinaria veterinario veterinarias veterinarios veterinária',
    'animal animals animais animal',
    'zootechnics zootecnia zootecnico zootecnica zootecnicos zootecnicas',
    'microbiology microbiological microbiologia microbiano microbiana microbiologic',
    'bacteria bacterial bacterium bacterias bacteria bacteriano bacteriana bacterianos bacterianas',
    'antimicrobial antimicrobiano antimicrobiana antimicrobianos antimicrobianas',
    'resistance resistant resistencia resistente resistentes resistencia',
    'infection infections infectious infeccao infeccoes infecciosa infeccioso',
    'disease diseases doenca doencas patologia patologias',
    'medicine medical medicina medico medica medicos medicas',
    'health saude saudavel saudaveis',
    'public publica publico publicos publicas',
    'environment environmental ambiente ambiental ambientais meio',
    'ecology ecological ecologia ecologico ecologica',
    'agriculture agricultural agricultura agricola agraria agrarias agrario agrarios',
    'agronomy agronomia agronomico agronomica agronomicos agronomicas',
    'food foods alimento alimentos alimentar alimentares',
    'nutrition nutritional nutricao nutricional nutricionais',
    'cancer oncology oncologia oncologico oncologica oncologicos oncologicas',
    'immunology immunological imunologia imunologico imunologica imunologicos imunologicas',
    'genetics genetic genetica genetico geneticos geneticas genomics genomica genomico',
    'biology biological biologia biologico biologica biologicos biologicas',
    'molecular moleculares molecular molecular',
    'chemistry chemical quimica quimico quimica quimicas quimicos',
    'physics physical fisica fisico fisicas fisicos',
    'engineering engenharia engenharias engenheiro engenheiros',
    'computer computing computacao computacional computation computational',
    'education educational educacao educacional educacionais',
    'psychology psychological psicologia psicologico psicologica psicologicos psicologicas',
    'social sociais social',
    'science ciencia ciencias sciences scientific cientifico cientifica cientificos cientificas',
    'economics economic economia economico economica economicos economicas',
    'surgery surgical cirurgia cirurgico cirurgica cirurgicos cirurgicas',
    'cardiology cardiovascular cardiologia cardiologico cardiologica',
    'neuroscience neurology neurologia neurociencia neurociencias neurologico neurologica',
    'epidemiology epidemiological epidemiologia epidemiologico epidemiologica',
    'parasitology parasitologia parasitologico parasitologica',
    'virology virologia virologico virologica',
    'reproduction reproductive reproducao reprodutivo reprodutiva reprodutivas',
    'aquaculture aquicultura aquicultor aquicultora',
    'poultry avicultura aves ave avicola avicolas',
    'dairy leite lacteo lacteos lactea lacteas',
    'water agua aguas hidrico hidrica',
    'soil soils solo solos edafico edafica',
    'plant plants planta plantas vegetal vegetais vegetal',
    'clinical clinico clinica clinicos clinicas',
    'human humano humana humanos humanas',
    'patient pacientes paciente',
    'diagnosis diagnostic diagnostics diagnostico diagnostica diagnosticos diagnosticas diagnosticar',
    'treatment tratamento tratamentos tratar',
    'therapy terapia terapeutico terapeutica terapeuticas',
    'prevention prevencao preventivo preventiva preventivas',
    'control controle controles controlar',
    'risk risco riscos',
    'vaccine vacina vacinas vacinal vacinais',
    'immunization imunizacao imunizacoes',
    'nursing enfermagem enfermeiro enfermeira enfermeiros enfermeiras',
    'dentistry odontologia odontologico odontologica dental dentaria dentarias',
    'pharmacy farmacia farmaceutico farmaceutica farmaceuticos farmaceuticas',
    'pharmacology pharmacology farmacologia farmacologico farmacologica',
    'toxicology toxicologia toxicologico toxicologica',
    'biochemistry biochemical bioquimica bioquimico bioquimica bioquimicas',
    'biotechnology biotecnologia biotecnologico biotecnologica biotecnologicas',
    'bioinformatics bioinformatica bioinformatico bioinformatica',
    'proteomics proteomica proteomico proteomica',
    'metabolomics metabolomica metabolomico metabolomica',
    'microbiome microbiota microbioma',
    'mycology micologia micologico fungos fungo fungi fungus fungal fungica fungicas',
    'entomology entomologia entomologico insetos inseto insect insects',
    'zoology zoologia zoologico zoologica',
    'botany botanica botanico botanica',
    'forestry silvicultura',
    'fisheries pesca pesqueiro pesqueira pesqueiros pesqueiras',
    'biodiversity biodiversidade biodiversidades',
    'conservation conservacao preservacao conservacionista',
    'climate clima climatico climatica climaticos climaticas',
    'pollution poluicao poluente poluentes contaminacao contaminacoes',
    'waste residuos residuo rejeitos rejeito',
    'sanitation saneamento sanitario sanitaria sanitarios sanitarias',
    'urban urbano urbana urbanismo urbanos urbanas',
    'architecture arquitetura arquitetonico arquitetonica',
    'transport transporte transportes transport transportes',
    'logistics logistica logistico logistica logisticos logisticas',
    'business negocios negocio empresarial empresariais',
    'management gestao gerencial',
    'marketing mercadologia',
    'finance financas financeiro financeira financial',
    'accounting contabilidade contabil',
    'tourism turismo turistico turistica',
    'law direito juridico juridica legal',
    'criminology criminologia criminologico criminologica',
    'relations relacoes relacao',
    'international internacional internacionais',
    'political politics politico politicos politicas',
    'policy politica politicas',
    'administration administracao',
    'sociology sociologia sociologico sociologica',
    'anthropology antropologia antropologico antropologica',
    'archaeology arqueologia arqueologico arqueologica',
    'history historia historico historica historicos historicas',
    'geography geografia geografico geografica',
    'geology geologia geologico geologica',
    'oceanography oceanografia oceanografico oceanografica',
    'meteorology meteorologia meteorologico meteorologica',
    'astronomy astronomia astronomico astronomica',
    'mathematics mathematics matematica matematico matematica matematicos',
    'statistics statistical estatistica estatistico estatistica estatisticas',
    'data dados',
    'intelligence inteligencia',
    'learning aprendizado aprendizagem',
    'machine maquina maquinas',
    'robotics robotica robotico robotica roboticos',
    'materials materials materiais material',
    'energy energia energetico energetica energeticas',
    'sustainability sustentabilidade sustentavel sustentaveis',
    'renewable renovavel renovaveis',
    'sports esporte esportes sport',
    'rehabilitation reabilitacao reabilitacoes',
    'occupational ocupacional ocupacionais',
    'speech fonoaudiologia fala',
    'psychiatry psiquiatria psiquiatrico psiquiatrica',
    'cognitive cognitivo cognitiva cognition',
    'linguistics linguistica linguistico linguistica',
    'language lingua linguagem languages',
    'literature literatura literario literaria letras',
    'philosophy filosofia filosofico filosofica',
    'ethics etica etico etica',
    'religion religiao religioso religiosa',
    'arts arte artes artistico artistica',
    'music musica musical musicologia',
    'communication comunicacao comunicacoes comunicacional',
    'journalism jornalismo jornalistico jornalistica',
    'media midia midias midiatico',
    'library biblioteca biblioteconomia biblioteconomico',
    'information informacao informacoes informacional',
    'museum museu museologia museologico',
    'heritage patrimonio patrimonial',
    'gender genero generos',
    'race raca racas racial',
    'indigenous indigena indigenas',
    'disability deficiencia deficiencias',
    'leisure lazer',
    'gastronomy gastronomia gastronomico',
    'design desenho',
    'fashion moda',
    'hospitality hotelaria',
    'mining mineracao minerario mineradora',
    'metallurgy metalurgia metalurgico',
    'petroleum petroleo petrolifero',
    'telecommunications telecomunicacoes telecomunicacao',
    'electrical eletrica eletrico eletricos eletricas',
    'mechanical mecanica mecanico mecanicos mecanicas',
    'civil civil civis',
    'forest floresta florestal florestas',
    'change mudanca mudancas',
    'welfare bem estar bem-estar',
    'safety seguranca',
    'security security',
    'cybersecurity cybersecurity ciberseguranca cibersegurança',
    'cyber cyber ciber',
    'network network networking rede redes',
    'intrusion intrusion intrusao intrusoes',
    'attack attack ataque ataques',
    'threat threat ameaca ameacas',
    'defense defense defesa defesas defence',
    'infrastructure infrastructure infraestrutura infraestruturas',
    'critical critical critico critica criticos criticas',
    'distributed distributed distribuido distribuida distribuidos distribuídas',
    'malware malware',
    'ransomware ransomware',
    'phishing phishing',
    'encryption encryption criptografia',
    'privacy privacy privacidade',
    'protocol protocol protocolo protocolos',
    'wireless wireless',
    'cloud cloud nuvem',
    'neural neural',
    'production producao produtivo produtiva produtivas',
    'breeding melhoramento melhoramentos',
    'primary primaria primario primarios primarias',
    'care cuidado cuidados',
    'attention atencao',
    'collective coletiva coletivo coletivas coletivos',
    'surveillance vigilancia vigilâncias',
    'zoonosis zoonose zoonoses zoonotico zoonotica',
    'pathology patologia patologico patologica',
    'cellular celular celulas celula cell cells',
    'tissue tecido tecidos',
    'blood sangue sanguineo sanguinea',
    'urine urina urinario urinaria',
    'milk leite lacteo lacteos',
    'meat carne carnes',
    'egg ovos ovo',
    'bird aves ave passaros passaro',
    'swine suinos suino suina suinas pigs pig porcine piglets piglet leitao leitoes',
    'probiotic probiotics probiotico probiotica probioticos probioticas',
    'cattle bovinos bovino bovina',
    'goat caprinos caprino caprina',
    'sheep ovinos ovino ovina',
    'horse horses equine equinos equino equina',
    'dog dogs caes cao canino canina caninos caninas canine',
    'cat gatos gato felino felina',
    'fish peixes peixe',
    'bee abelhas abelha apicultura',
    'trial ensaio ensaios',
    'cohort coorte coortes',
    'case casos',
    'cross cruzada cruzado',
    'sectional seccional transversal transversais',
    'qualitative qualitativo qualitativa qualitativos qualitativas',
    'quantitative quantitativo quantitativa quantitativos quantitativas',
    'survey inquerito questionario questionarios',
    'interview entrevista entrevistas',
    'experimental experimental experimentais',
    'randomized randomizado randomizada randomizados randomizadas',
    'systematic sistematica sistematico sistematicos sistematicas',
    'review revisao revisoes',
    'higher superior',
    'distance distancia',
    'teacher professor professores docente docentes',
    'student aluno alunos estudantes student students',
    'curriculum curriculo curriculos',
    'assessment avaliacao avaliacoes avalia avaliar',
    'innovation inovacao inovador inovadora',
    'entrepreneurship empreendedorismo',
    'leadership lideranca',
    'governance governanca',
    'government governo governamental',
    'supply suprimentos',
    'chain cadeia cadeias',
    'activity atividade atividades',
    'chronic cronico cronica cronicos cronicas',
    'worker trabalhador trabalhadores trabalhadora trabalhadoras',
    'physiotherapy fisioterapia fisioterapeutico',
    'virus viruses viral virais virose viroses',
    'parasite parasites parasita parasitas parasito parasitos parasitic parasitario parasitaria',
    'vaccination vacinacao vacinacoes',
    'epidemic epidemia epidemias',
    'pandemic pandemia pandemias pandemico pandemica',
    'outbreak surto surtos',
    'mortality mortalidade',
    'morbidity morbidade',
    'incidence incidencia incidencias',
    'prevalence prevalencia prevalencias',
    'livestock pecuaria pecuario pecuarias',
    'seed seeds semente sementes',
    'fertilization adubacao adubacoes fertilizante fertilizantes',
    'irrigation irrigacao irrigacoes',
    'pest praga pragas',
    'phytopathology fitopatologia fitopatologico fitopatologica',
    'fertility fertilidade',
    'pasture pastagem pastagens',
    'forage forragem forragens',
    'feed racao racoes',
    'host hospedeiro hospedeiros',
    'vector vetor vetores sandfly flebotomineo flebotomineos phlebotomine',
    # Targeted disease and production-animal vocabulary. These additions were
    # driven by reproducible failures (canine leishmaniasis and laying-hen
    # welfare), not by fixing individual journal titles.
    'leishmaniasis leishmaniose leishmanioses leishmania',
    'toxoplasmosis toxoplasmose toxoplasma',
    'brucellosis brucelose brucella',
    'tuberculosis tuberculose mycobacterium',
    'mastitis mastite',
    'salmonellosis salmonelose salmonella',
    'ehrlichiosis erliquiose ehrlichia',
    'babesiosis babesiose babesia',
    'anaplasmosis anaplasmose anaplasma',
    'parvovirus parvovirose',
    'distemper cinomose',
    'dengue',
    'malaria paludismo',
    'hepatitis hepatite',
    'influenza gripe',
    'zika',
    'chikungunya',
    'hypertension hipertensao hipertenso hipertensa',
    'obesity obesidade obeso obesa',
    'depression depressao depressivo depressiva',
    'anxiety ansiedade ansioso ansiosa',
    'alzheimer',
    'parkinson',
    'autism autismo autista',
    'schizophrenia esquizofrenia esquizofrenico',
    'asthma asma asmatico',
    'arthritis artrite',
    'osteoporosis osteoporose',
    'wound ferida ferimento ferimentos',
    'pain dor dores',
    'fever febre',
    'diarrhea diarreia',
    'pneumonia pneumonia',
    'sepsis sepse',
    'seizure convulsao convulsoes',
    'kidney renal rim rins',
    'liver hepatico figado figados',
    'lung pulmonar pulmao pulmoes',
    'brain cerebral cerebro',
    'bone osso ossea osseos',
    'skin pele cutaneo cutanea',
    'eye ocular olho olhos',
    'chicken galinha galinhas frango frangos hen hens',
    'laying poedeira poedeiras postura',
    'crop crops safra safras',
    'child children crianca criancas',
    'adolescent adolescents adolescente adolescentes',
    'elderly idoso idosos idosa idosas',
    'woman women mulher mulheres',
    'man men homem homens',
    'family families familia familias',
    'community communities comunidade comunidades',
    'school schools escola escolas',
    'university universities universidade universidades',
    'consumer consumers consumidor consumidores',
    'farmer farmers agricultor agricultores',
    'multidisciplinary multidisciplinar',
    'behavior behaviour comportamento comportamental comportamentais',
    'technique techniques tecnica tecnicas metodologia metodologias',
    'microscopy microscopia microscopico microscopica',
    'spectroscopy espectroscopia espectroscopico espectroscopica',
    'chromatography cromatografia cromatografico cromatografica',
    'sequencing sequenciamento sequenciamentos',
    'simulation simulations simulacao simulacoes',
    'optimization optimisation otimizacao otimizacoes',
    'sample samples amostra amostras',
    'participant participants participante participantes',
    'algorithm algorithms algoritmo algoritmos',
    'antibiotic antibiotics antibiotico antibioticos',
    'drug drugs farmaco farmacos medicamento medicamentos',
    'supplementation suplementacao suplementacoes suplemento suplementos',
    'exercise exercicio exercicios',
    'diet dieta dietas dietary',
    'intervention interventions intervencao intervencoes',
    'program programs programa programas',
    'training treinamento treinamentos',
    'performance desempenho',
    'quality qualidade qualidades',
    'satisfaction satisfacao',
    'yield produtividade rendimento rendimentos',
    'growth crescimento',
    'survival sobrevivencia sobrevida',
    'efficiency eficiencia eficiente',
    'effectiveness efetividade efetivo efetiva',
    'impact impacto impactos',
    'access acesso',
    'adherence adesao aderencia',
    'accuracy acuracia',
    'sensitivity sensibilidade',
    'specificity especificidade',
    'outcome outcomes desfecho desfechos',
]
ALIASES = {word: group.split()[0] for group in GROUPS for word in group.split()}

IRREGULAR = {
    'analysis': 'analysis', 'analyses': 'analysis', 'analise': 'analysis', 'analises': 'analysis',
    'diagnosis': 'diagnosis', 'diagnoses': 'diagnosis',
    'hypothesis': 'hypothesis', 'hypotheses': 'hypothesis', 'hipotese': 'hypothesis', 'hipoteses': 'hypothesis',
    'thesis': 'thesis', 'theses': 'thesis', 'tese': 'thesis', 'teses': 'thesis',
    'synthesis': 'synthesis', 'syntheses': 'synthesis', 'sintese': 'synthesis', 'sinteses': 'synthesis',
    'crisis': 'crisis', 'crises': 'crisis', 'crise': 'crisis',
    'species': 'species', 'especie': 'species', 'especies': 'species',
    'series': 'series', 'serie': 'series',
    'stimulus': 'stimulus', 'stimuli': 'stimulus', 'estimulo': 'stimulus', 'estimulos': 'stimulus',
    'nucleus': 'nucleus', 'nuclei': 'nucleus', 'nucleo': 'nucleus', 'nucleos': 'nucleus',
    'focus': 'focus', 'foci': 'focus', 'foco': 'focus', 'focos': 'focus',
    'bacillus': 'bacillus', 'bacilli': 'bacillus', 'bacilo': 'bacillus', 'bacilos': 'bacillus',
    'rabies': 'rabies', 'raiva': 'rabies',
    'scabies': 'scabies', 'sarna': 'scabies',
    'diabetes': 'diabetes', 'herpes': 'herpes',
    'measles': 'measles', 'sarampo': 'measles',
    'mumps': 'mumps', 'caxumba': 'mumps',
}

QUERY_EXPANSIONS = {
    'ai': ('ai', 'artificial', 'intelligence'), 'ia': ('ia', 'artificial', 'intelligence'),
    'ml': ('ml', 'machine', 'learning'), 'nlp': ('nlp', 'natural', 'language', 'processing'),
    'llm': ('llm', 'large', 'language', 'model'), 'iot': ('iot', 'internet', 'things'),
    'pcr': ('pcr', 'polymerase', 'chain', 'reaction'), 'amr': ('amr', 'antimicrobial', 'resistance'),
    'hiv': ('hiv', 'human', 'immunodeficiency', 'virus'),
    'aids': ('aids', 'acquired', 'immunodeficiency', 'syndrome'),
    'covid': ('covid', 'sars', 'cov'), 'sars': ('sars', 'cov'),
    'gmo': ('gmo', 'genetically', 'modified', 'organism'),
    'sdg': ('sdg', 'sustainable', 'development', 'goals'),
    'esg': ('esg', 'environmental', 'social', 'governance'),
    'gis': ('gis', 'geographic', 'information', 'systems'),
    'mri': ('mri', 'magnetic', 'resonance', 'imaging'),
    'nmr': ('nmr', 'nuclear', 'magnetic', 'resonance'),
    'hplc': ('hplc', 'high', 'performance', 'liquid', 'chromatography'),
    'elisa': ('elisa', 'enzyme', 'linked', 'immunosorbent', 'assay'),
    'uv': ('uv', 'ultraviolet'),
    'no': ('no', 'nitric', 'oxide'), 'ros': ('ros', 'reactive', 'oxygen', 'species'),
    'rns': ('rns', 'reactive', 'nitrogen', 'species'), 'os': ('os', 'overall', 'survival'),
    'tem': ('tem', 'transmission', 'electron', 'microscopy'),
    'sem': ('sem', 'scanning', 'electron', 'microscopy'),
    'afm': ('afm', 'atomic', 'force', 'microscopy'),
    'ftir': ('ftir', 'fourier', 'transform', 'infrared'),
    'xrd': ('xrd', 'ray', 'diffraction'), 'ha': ('ha', 'hyaluronic', 'acid'),
    'sim': ('sim', 'scanning', 'ion', 'microscopy'),
    'dna': ('dna', 'deoxyribonucleic', 'acid'), 'rna': ('rna', 'ribonucleic', 'acid'),
    'bmi': ('bmi', 'body', 'mass', 'index'), 'ct': ('ct', 'computed', 'tomography'),
    'bird': ('bird', 'poultry'), 'poultry': ('poultry', 'bird'),
    'milk': ('milk', 'dairy'), 'dairy': ('dairy', 'milk'),
    'fish': ('fish', 'fisheries'), 'fisheries': ('fisheries', 'fish'),
    'plant': ('plant', 'botany'), 'botany': ('botany', 'plant'),
    'forest': ('forest', 'forestry'), 'forestry': ('forestry', 'forest'),
    'worker': ('worker', 'occupational'), 'occupational': ('occupational', 'worker'),
    'attention': ('attention', 'care'), 'care': ('care', 'attention'),
    'virus': ('virus', 'virology'), 'virology': ('virology', 'virus'),
    'parasite': ('parasite', 'parasitology'), 'parasitology': ('parasitology', 'parasite'),
    'vaccine': ('vaccine', 'vaccination'), 'vaccination': ('vaccination', 'vaccine'),
    'immunization': ('immunization', 'vaccine', 'vaccination'),
    'epidemiology': ('epidemiology', 'epidemic'), 'epidemic': ('epidemic', 'outbreak', 'epidemiology'),
    'pandemic': ('pandemic', 'epidemic', 'outbreak'), 'outbreak': ('outbreak', 'epidemic'),
    'disease': ('disease', 'pathology'), 'pathology': ('pathology', 'disease'),
    'livestock': ('livestock', 'animal'), 'animal': ('animal', 'livestock'),
    'phytopathology': ('phytopathology', 'plant', 'pathology'),
    'feed': ('feed', 'nutrition'), 'nutrition': ('nutrition', 'feed'),
    'chicken': ('chicken', 'poultry'), 'poultry': ('poultry', 'chicken'),
    'laying': ('laying', 'egg'), 'egg': ('egg', 'laying'),
    'leishmaniasis': ('leishmaniasis', 'parasite', 'parasitology'),
    'toxoplasmosis': ('toxoplasmosis', 'parasite', 'parasitology'),
}

# Multiword concepts that need a correction after literal tokenization.
PHRASE_EXPANSIONS = {
    ('education', 'physics'): ('physical', 'education'),
    ('activity', 'physics'): ('physical', 'activity'),
    ('science', 'policy'): ('political', 'science'),
}

# Coarse semantic roles used by the manuscript analyzer and reranker. These are
# deliberately small, inspectable sets; they are not a claim of full ontology.
POPULATION_TERMS = {
    'animal', 'dog', 'cat', 'cattle', 'goat', 'sheep', 'horse', 'fish', 'bee',
    'bird', 'poultry', 'chicken', 'swine', 'livestock', 'human', 'patient',
    'plant', 'crop', 'worker', 'student', 'teacher', 'child', 'adolescent',
    'elderly', 'woman', 'man', 'family', 'community', 'consumer', 'farmer',
}

DISEASE_TERMS = {
    'disease', 'infection', 'cancer', 'leishmaniasis', 'toxoplasmosis',
    'brucellosis', 'tuberculosis', 'mastitis', 'salmonellosis', 'ehrlichiosis',
    'babesiosis', 'anaplasmosis', 'parvovirus', 'distemper', 'dengue', 'malaria',
    'hepatitis', 'influenza', 'zika', 'chikungunya', 'hypertension', 'obesity',
    'depression', 'anxiety', 'alzheimer', 'parkinson', 'autism', 'schizophrenia',
    'asthma', 'arthritis', 'osteoporosis', 'wound', 'pain', 'fever', 'diarrhea',
    'pneumonia', 'sepsis', 'seizure', 'zoonosis',
}

METHOD_TERMS = {
    'diagnosis', 'molecular', 'pcr', 'elisa', 'technique', 'microscopy', 'spectroscopy',
    'chromatography', 'sequencing', 'nmr', 'mri', 'xrd', 'ftir', 'hplc', 'assay',
    'test', 'screening', 'survey', 'interview', 'questionnaire', 'statistics',
    'statistical', 'regression', 'model', 'machine', 'learning', 'bioinformatics',
    'proteomics', 'metabolomics', 'genomics', 'transcriptomics', 'culture',
    'isolation', 'characterization', 'evaluation', 'assessment', 'monitoring',
    'measurement', 'detection', 'quantification', 'simulation', 'optimization',
    'experimental', 'randomized', 'trial', 'cohort', 'case', 'control', 'cross',
    'sectional', 'qualitative', 'quantitative', 'sample', 'participant',
    'algorithm', 'computational',
}

INTERVENTION_TERMS = {
    'vaccine', 'vaccination', 'immunization', 'treatment', 'therapy', 'control',
    'prevention', 'nutrition', 'feed', 'fertilization', 'irrigation', 'management',
    'policy', 'education', 'training', 'rehabilitation', 'surgery', 'drug',
    'antibiotic', 'antimicrobial', 'supplementation', 'exercise', 'diet',
    'intervention', 'program',
}

OUTCOME_TERMS = {
    'welfare', 'mortality', 'morbidity', 'incidence', 'prevalence', 'production',
    'performance', 'quality', 'satisfaction', 'yield', 'growth', 'survival',
    'resistance', 'risk', 'efficiency', 'effectiveness', 'impact', 'access',
    'adherence', 'accuracy', 'sensitivity', 'specificity', 'outcome',
}

AREA_TERMS = {
    'veterinary', 'medicine', 'health', 'nursing', 'dentistry', 'pharmacy',
    'psychology', 'neuroscience', 'immunology', 'microbiology', 'biology',
    'biochemistry', 'genetics', 'agriculture', 'agronomy', 'food', 'nutrition',
    'environment', 'ecology', 'chemistry', 'physics', 'engineering', 'computer',
    'mathematics', 'statistics', 'economics', 'business', 'management', 'finance',
    'law', 'education', 'sociology', 'anthropology', 'history', 'geography',
    'geology', 'oceanography', 'meteorology', 'astronomy', 'materials', 'energy',
    'sustainability', 'communication', 'linguistics', 'philosophy', 'arts',
    'music', 'literature', 'politics', 'policy', 'international', 'urban', 'rural',
    'forest', 'fisheries', 'biodiversity', 'conservation', 'climate', 'pollution',
    'waste', 'sanitation', 'transport', 'logistics', 'tourism', 'sports',
    'rehabilitation', 'occupational', 'speech', 'psychiatry', 'cognitive',
    'information', 'library', 'museum', 'heritage', 'gender', 'race',
    'indigenous', 'disability', 'leisure', 'gastronomy', 'design', 'fashion',
    'hospitality', 'mining', 'metallurgy', 'petroleum', 'telecommunications',
    'electrical', 'mechanical', 'civil', 'architecture', 'social', 'humanities',
    'multidisciplinary',
}

# Ambiguous acronyms need evidence from the surrounding text. The legacy
# engine keeps its old broad expansion table; the modular engine uses this
# contextual table instead.
CONTEXTUAL_ACRONYMS = {
    'no': (({'nitric', 'oxide', 'vascular', 'cell', 'biology', 'signaling', 'signal'}, ('nitric', 'oxide')),),
    'os': (
        ({'cancer', 'oncology', 'tumor', 'survival', 'patient'}, ('overall', 'survival')),
        ({'computer', 'software', 'system', 'network', 'operating'}, ('operating', 'system')),
    ),
    'tem': (({'microscopy', 'electron', 'material', 'cell'}, ('transmission', 'electron', 'microscopy')),),
    'sem': (({'microscopy', 'electron', 'material', 'cell'}, ('scanning', 'electron', 'microscopy')),),
    'ha': (({'acid', 'hyaluronic', 'joint', 'skin', 'dermal'}, ('hyaluronic', 'acid')),),
    'sim': (({'microscopy', 'ion', 'electron', 'material'}, ('scanning', 'ion', 'microscopy')),),
    'ct': (({'tomography', 'imaging', 'patient', 'medical'}, ('computed', 'tomography')),),
}

# Ambiguous ordinary words, not only acronyms. Portuguese "segurança" is
# normally safety; in a network/computer context it means security. The term
# itself stays searchable, and the contextual alternative is a bounded vote.
CONTEXTUAL_TERMS = {
    'safety': (
        ({'network', 'computer', 'cyber', 'cybersecurity', 'software', 'system',
          'intrusion', 'attack', 'threat', 'data', 'information', 'internet',
          'digital', 'online', 'cloud', 'malware', 'protocol'},
         ('security',)),
    ),
}

# Multiword concepts. Their constituent generic word must not behave as an
# independent topic. For example, "learning" in "deep learning" is not the
# education topic "learning"; the phrase remains the primary evidence.
PHRASE_CONCEPTS = {
    ('deep', 'learning'): {
        # Both words are generic on their own ("deep underground", "learning
        # styles"); the phrase and its bounded related terms carry the concept.
        'suppress': ('deep', 'learning'),
        'related': (('neural', 'network'), ('machine', 'learning')),
        'context': {
            'network', 'security', 'intrusion', 'detection', 'image', 'imaging',
            'vision', 'medical', 'data', 'computer', 'artificial', 'intelligence',
            'neural', 'classification', 'model', 'signal', 'speech', 'language',
        },
    },
    ('machine', 'learning'): {
        'suppress': ('machine', 'learning'),
        'related': (('deep', 'learning'), ('neural', 'network')),
        'context': {
            'network', 'security', 'intrusion', 'detection', 'image', 'imaging',
            'vision', 'medical', 'data', 'computer', 'artificial', 'intelligence',
            'neural', 'classification', 'model', 'signal', 'speech', 'language',
        },
    },
    ('federated', 'learning'): {
        'suppress': ('learning',),
        'related': (('machine', 'learning'), ('neural', 'network')),
        'context': {
            'privacy', 'health', 'medical', 'data', 'computer', 'network',
            'security', 'model', 'classification', 'detection',
        },
    },
}


def find_phrase_concepts(sequences):
    """Return known multiword concepts present in ordered token sequences."""
    found = []
    for sequence in sequences:
        sequence = tuple(sequence)
        for concept in PHRASE_CONCEPTS:
            size = len(concept)
            if any(sequence[position:position + size] == concept
                   for position in range(max(0, len(sequence) - size + 1))):
                found.append(concept)
    return tuple(dict.fromkeys(found))


def contextual_expansions(term, context_terms):
    """Return safe expansions for a canonical term.

    Ambiguous acronyms and words only expand when the query contains supporting
    context; otherwise the original term remains searchable. Non-ambiguous terms
    keep the curated expansion table.
    """
    if term in CONTEXTUAL_ACRONYMS:
        context = set(context_terms)
        for cues, alternatives in CONTEXTUAL_ACRONYMS[term]:
            if context & cues:
                return (term,) + alternatives
        return (term,)
    if term in CONTEXTUAL_TERMS:
        context = set(context_terms)
        for cues, alternatives in CONTEXTUAL_TERMS[term]:
            if context & cues:
                return (term,) + alternatives
        return (term,)
    return QUERY_EXPANSIONS.get(term, (term,))


STEM_EXCEPTIONS = {
    'analysis', 'basis', 'crisis', 'diagnosis', 'emphasis', 'hypothesis', 'synthesis', 'thesis',
    'species', 'series', 'rabies', 'scabies', 'diabetes', 'herpes', 'measles', 'mumps',
    'physics', 'mathematics', 'statistics', 'economics', 'genetics', 'ethics', 'politics',
    'business', 'class', 'glass', 'process', 'access', 'success', 'stress', 'progress',
    'congress', 'news', 'virus', 'status', 'campus', 'corpus', 'census', 'consensus',
}

def clean(text):
    text = unicodedata.normalize('NFKD', str(text)).encode('ascii', 'ignore').decode().lower()
    return text


# Normalize curated keys once so accented variants also match cleaned tokens.
ALIASES = {clean(word): canonical for word, canonical in ALIASES.items()}
IRREGULAR = {clean(word): canonical for word, canonical in IRREGULAR.items()}


def label_key(text):
    """Stable, accent-insensitive key for column names."""
    return re.sub(r'[^a-z0-9]+', ' ', clean(text)).strip()


def raw_tokens(text):
    """Words as typed (case and accents kept so uppercase acronyms survive)."""
    return re.findall(r'[^\W_]+', str(text), flags=re.UNICODE)


def singularize(word):
    """Conservative plural folding for words not covered by the curated lexicon."""
    if len(word) <= 3 or word in STEM_EXCEPTIONS:
        return word
    if word.endswith('ies') and len(word) > 4:
        return word[:-3] + 'y'
    if word.endswith('oes') and len(word) > 4:
        return word[:-3] + 'ao'
    if word.endswith('ais') and len(word) > 4:
        return word[:-2] + 'l'
    if word.endswith('eis') and len(word) > 4:
        return word[:-2] + 'l'
    if word.endswith('s') and not word.endswith(('ss', 'us', 'is')) and len(word) > 4:
        return word[:-1]
    return word


def canonical_token(raw, allow_acronym=True):
    word = clean(raw)
    acronym = (allow_acronym and len(raw) <= 5 and raw.isupper()
               and any(character.isalpha() for character in raw))
    if word.isdigit() or len(word) < 2 or (word in STOP and not acronym):
        return None
    if word in ALIASES:
        return ALIASES[word]
    if word in IRREGULAR:
        return IRREGULAR[word]
    singular = singularize(word)
    if singular in STOP and not acronym:
        return None
    if singular in ALIASES:
        return ALIASES[singular]
    if singular in IRREGULAR:
        return IRREGULAR[singular]
    return singular


def token_pairs(text):
    """Return (canonical term, display word) pairs, preserving the user's wording."""
    raws = raw_tokens(text)
    # In an all-caps title every short word looks like an acronym; only trust
    # uppercase short words when the surrounding text has normal casing.
    allow_acronym = not (len(raws) > 1 and str(text).isupper())
    pairs = []
    for raw in raws:
        term = canonical_token(raw, allow_acronym=allow_acronym)
        if term:
            display_word = (raw if raw.isupper() and len(raw) <= 5
                            and any(character.isalpha() for character in raw) else raw.lower())
            pairs.append((term, display_word))
    return pairs


def tokens(text):
    return [term for term, _ in token_pairs(text)]


def phrase_terms(terms):
    """Bigrams and trigrams from an ordered token list."""
    phrases = set()
    for size in (2, 3):
        for position in range(max(0, len(terms) - size + 1)):
            phrases.add(' '.join(terms[position:position + size]))
    return phrases