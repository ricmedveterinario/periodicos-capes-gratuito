"""Streamlit manuscript matching, isolated from the existing title search."""
import streamlit as st
from urllib.parse import urlparse
from capes_catalog import acceptance_status
from journal_recommender import JournalRecommender, institution_publishers


@st.cache_resource(show_spinner=False, max_entries=2)
def build_recommender(catalog):
    return JournalRecommender(catalog)


def render_recommender(catalog, institutions):
    st.markdown('<div id="recomendar-revista"></div>', unsafe_allow_html=True)
    st.write('**Qual é o tema do seu manuscrito?**')
    with st.form('manuscript_recommender'):
        title = st.text_input('Título do manuscrito', max_chars=500)
        keywords = st.text_input('Palavras-chave', placeholder='Ex.: resistência antimicrobiana; microbiologia veterinária', max_chars=1000)
        with st.expander('Adicionar resumo (opcional)'):
            abstract = st.text_area('Resumo', max_chars=12000, height=150)
        names = sorted(institutions['Nome da Instituição'].dropna().unique())
        institution = st.selectbox('Instituição do autor correspondente', ['Sem filtro institucional'] + names)
        integral = st.checkbox('Somente cobertura integral indicada na base', value=True,
                               help='Exclui descontos e registros de cobertura pendente. A indicação da base exige confirmação no acordo.')
        with st.expander('Mais opções'):
            accepted = st.date_input('Data de aceite para conferir vigência (opcional)', value=None, key='recommender_acceptance')
            limit = st.select_slider('Quantidade de sugestões', options=[5, 10, 20], value=10)
        submitted = st.form_submit_button('Encontrar revistas', type='primary', use_container_width=True)
    st.caption('Seu texto é processado no servidor do Publica Aberto, sem envio a serviços externos e sem gravação pelo recomendador. Permanece na sessão enquanto ela estiver aberta.')
    with st.expander('Como interpretar as sugestões'):
        st.write('Comparamos palavras do título, resumo e palavras-chave com títulos e áreas disponíveis no catálogo. Um vocabulário português–inglês ajuda a reconhecer temas. Título e palavras-chave têm maior peso. A pontuação ordena a relação temática; não é porcentagem de compatibilidade ou chance de aceite.')
        st.write('Esta primeira versão não analisa artigos publicados nem o escopo completo de cada revista. Periódicos multidisciplinares podem não aparecer. Confira o escopo e as instruções aos autores antes de escolher.')
    if not submitted:
        return
    if not any(text.strip() for text in (title, abstract, keywords)):
        st.warning('Informe o título, o resumo ou palavras-chave do trabalho.')
        return
    allowed = None if institution == 'Sem filtro institucional' else institution_publishers(institutions, institution)
    engine = build_recommender(catalog)
    results = engine.recommend(title, abstract, keywords, publishers=allowed, integral_only=integral, limit=limit)
    if results.empty:
        st.info('Não encontramos correspondências com esses critérios. Tente palavras-chave mais específicas, também em inglês, ou revise os filtros. Isso não significa que não existam revistas adequadas.')
        return
    st.success(f'{len(results)} sugestões para conferir')
    st.caption('A presença da instituição no acordo é preliminar. A cobertura depende também do título, modelo, vigência e requisitos do autor; a aprovação do custeio é da CAPES.')
    display_columns = ['Título da Revista', 'Editora', 'Pontuação temática', 'Termos relacionados', 'ISSN', 'Modelo', 'Cobertura APC']
    display = results[[column for column in display_columns if column in results]].copy()
    display['Conferência da data'] = results['Editora'].map(lambda publisher: acceptance_status(publisher, accepted))
    st.dataframe(display, hide_index=True, use_container_width=True)
    for position, (_, row) in enumerate(results.iterrows(), 1):
        with st.expander(f"{position}. {row['Título da Revista']} — {row['Editora']}"):
            st.write('**Termos relacionados:** ' + row['Termos relacionados'])
            st.write('**Cobertura registrada:** ' + str(row.get('Cobertura APC', 'Conferir')))
            st.write('**Instituição:** ' + ('não informada; confira a lista do acordo' if allowed is None else 'consta na lista deste grupo; demais requisitos pendentes'))
            for column in ('Situação da lista', 'Observações', 'Observação'):
                if column in row and str(row[column]).strip():
                    st.write(str(row[column]))
            st.write(acceptance_status(row['Editora'], accepted))
            url = str(row.get('URL', ''))
            parsed = urlparse(url)
            if parsed.scheme == 'https' and parsed.netloc and not parsed.username:
                st.link_button('Abrir página de referência da revista', url)
            st.caption('Confira o escopo, os tipos de artigo aceitos e as condições oficiais de publicação. Fator de impacto, prazo editorial e probabilidade de aceite não são estimados por este motor.')
