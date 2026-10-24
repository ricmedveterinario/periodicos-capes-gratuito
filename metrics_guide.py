"""An internal, lightweight learning page for journal metrics."""

def example_h_index(citations):
    return max((i for i,c in enumerate(sorted(citations,reverse=True),1) if c>=i),default=0)

def render_metrics_guide():
    import streamlit as st
    st.header('Entenda os índices')
    st.write('Escolher onde publicar envolve três perguntas: a revista combina com seu trabalho, a publicação pode ser custeada e como seus artigos circulam na comunidade? Cada informação responde a uma parte dessa decisão.')
    st.info('CAPES informa condições de custeio. OpenAlex e Google Scholar ajudam a explorar a literatura e suas citações. Ter uma métrica não torna uma revista elegível ao acordo CAPES.')
    left,right=st.columns(2)
    with left:
        st.subheader('OpenAlex: um mapa da pesquisa')
        st.write('É um catálogo aberto que conecta trabalhos científicos, autores, instituições e revistas. Aqui, usamos o ISSN para associar uma revista ao seu registro e apresentar temas e indicadores de citação.')
        st.write('Ajuda a conhecer a área de uma revista, encontrar oportunidades e contextualizar a circulação de seus artigos. A associação é complementar: uma revista sem correspondência continua no nosso catálogo CAPES.')
        st.caption('Consulta: [Site oficial do OpenAlex](https://openalex.org/)')
    with right:
        st.subheader('Google Scholar: literatura e visibilidade')
        st.write('O Google Acadêmico permite buscar literatura científica. O Google Scholar Metrics é a parte que apresenta h5-index e h5-mediana de publicações, organizados por edição.')
        st.write('Ajuda a observar a presença recente de uma revista na literatura citada pelo Google. Nosso site mostra apenas valores coletados e identificados, com período e procedência no cartão.')
        st.caption('Consulta: [Guia oficial do Google Scholar Metrics](https://scholar.google.com/intl/en/scholar/metrics.html#overview)')
    st.subheader('O que significa cada número?')
    st.markdown('''
| Indicador | Como ler | Atenção |
|---|---|---|
| Índice h · OpenAlex | h = 20 significa pelo menos 20 trabalhos com pelo menos 20 citações cada, na base OpenAlex. | Não usa necessariamente a janela de cinco anos do Google. |
| Média de citações · 2 anos | Resume citações em uma janela recente segundo o cálculo do OpenAlex. | Não é o fator de impacto JCR da Clarivate. |
| h5-index · Google Scholar | h5 = 20 significa pelo menos 20 artigos da janela de cinco anos com pelo menos 20 citações cada. | Confira a edição e o período. Edição 2025: artigos de 2020–2024. |
| h5-mediana · Google Scholar | É o valor central das citações dos artigos que compõem o núcleo h5. | Não é a média de todos os artigos da revista. |
| Linha anual · OpenAlex | Mostra contagens anuais de citações informadas pelo OpenAlex. | Não é uma evolução anual do fator de impacto nem do h5. |
''')
    with st.container(border=True):
        st.subheader('Um exemplo em 30 segundos')
        choice=st.radio('Citações de cinco artigos de uma mesma janela', ['8, 5, 3, 2, 1','20, 12, 8, 4, 1','2, 1, 0, 0, 0'], horizontal=True)
        values=[int(v.strip()) for v in choice.split(',')]
        h=example_h_index(values)
        st.write(f'**O índice h desse conjunto é {h}.** Há {h} artigos com pelo menos {h} citações cada. Se os artigos forem da janela de cinco anos avaliada pelo Google, o exemplo ilustra a lógica do h5.')
        st.caption('Exemplo didático, sem relação com os valores de uma revista real.')
    st.subheader('Como usar na escolha da revista')
    st.markdown('''
1. **Comece pelo tema.** Compare o escopo, o público e artigos recentes com o seu manuscrito.
2. **Confira o custeio.** Verifique revista, instituição, autoria correspondente, tipo de artigo e vigência do acordo.
3. **Use as métricas como contexto.** Compare a mesma fonte, edição e área. Valores de campos diferentes não são diretamente equivalentes.
4. **Leia além dos números.** Avalie práticas editoriais, transparência, prazos publicados e orientações aos autores.
''')
    with st.expander('Para aprofundar: limites e cobertura'):
        st.write('OpenAlex e Google rastreiam conjuntos diferentes de documentos e citações. Por isso, seus índices não devem ser somados, convertidos ou tratados como uma escala única. Um número de revista não mede a qualidade de cada artigo nem a competência de quem o escreveu.')
        st.write('O Scholar Metrics tem critérios próprios de inclusão e não cobre todas as revistas. Na nossa coleta, ausência também pode significar consulta pendente ou bloqueada. Nunca significa automaticamente índice zero. O campo e os temas OpenAlex refletem publicações associadas, não uma confirmação do escopo editorial.')
        st.write('Um ano de consulta não altera a edição da métrica. A cobertura Google deste site é parcial e foi validada com os lotes fornecidos; nem todos os registros foram consultados novamente online. Confira a fonte individual.')
    st.subheader('Fontes para continuar aprendendo')
    st.markdown('[OpenAlex: documentação dos indicadores](https://help.openalex.org/data/common-attributes/) · [OpenAlex: registros de revistas](https://help.openalex.org/data/sources/attributes/) · [Google Scholar Metrics: definições e cobertura](https://scholar.google.com/intl/en/scholar/metrics.html) · [Google Acadêmico: ajuda de pesquisa](https://scholar.google.com/intl/pt-BR/scholar/help.html)')
