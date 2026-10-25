"""Streamlit manuscript matching, isolated from the existing title search."""
import streamlit as st
from urllib.parse import urlparse
from capes_catalog import acceptance_status
from journal_recommender import JournalRecommender, institution_publishers
from open_metrics import enrich_catalog, read_snapshot, SNAPSHOT_PATH, AREA, safe_url
from metric_visuals import metric_panel, journal_chips
from discovery_links import scholar_journal_url


@st.cache_resource(show_spinner=False, max_entries=2)
def build_recommender(catalog, snapshot_version=0):
    # Resolve the release explicitly and invalidate the old cached engine.
    from modular_recommender import ModularJournalRecommender
    frame = enrich_catalog(catalog, read_snapshot())
    enriched = {name: group.copy() for name, group in frame.groupby('Editora', sort=False)}
    return ModularJournalRecommender(enriched)


def render_recommender(catalog, institutions):
    st.markdown('<div id="recomendar-revista"></div>', unsafe_allow_html=True)
    st.write('**Cole o título ou o resumo e encontre oportunidades de publicação.**')
    st.caption('Preencha pelo menos um dos dois. Palavras-chave ajudam a destacar o foco do trabalho.')
    with st.form('manuscript_recommender'):
        title = st.text_input('Título do manuscrito', max_chars=500)
        keywords = st.text_input('Palavras-chave', placeholder='Ex.: resistência antimicrobiana; microbiologia veterinária', max_chars=1000)
        with st.expander('Colar resumo (opcional)', expanded=True):
            abstract = st.text_area('Resumo', max_chars=12000, height=150)
        names = sorted(institutions['Nome da Instituição'].dropna().unique())
        institution = st.selectbox('Instituição do autor correspondente', ['Sem filtro institucional'] + names)
        integral = st.checkbox('Somente cobertura integral indicada na base', value=True,
                               help='Exclui descontos e registros de cobertura pendente. A indicação da base exige confirmação no acordo.')
        with st.expander('Mais opções'):
            accepted = st.date_input('Data de aceite para conferir vigência (opcional)', value=None, key='recommender_acceptance')
            limit = st.select_slider('Quantidade de sugestões', options=[5, 10, 20], value=10)
        submitted = st.form_submit_button('Encontrar revistas', type='primary', width="stretch")
    st.caption('Seu texto é processado no servidor do Publica Aberto, sem envio a serviços externos e sem gravação pelo recomendador. Permanece na sessão enquanto ela estiver aberta.')
    with st.expander('Como interpretar as sugestões'):
        st.write('O motor local identifica assunto, população e métodos do manuscrito, compara nomes de revistas, áreas e temas e reordena os candidatos pelo contexto. Um vocabulário português–inglês reconhece termos e expressões. Aderência e evidência são sinais heurísticos, não validação editorial nem chance de aceite.')
        st.write('Esta primeira versão não analisa artigos publicados nem o escopo completo de cada revista. Periódicos multidisciplinares podem não aparecer. Confira o escopo e as instruções aos autores antes de escolher.')
    if not submitted:
        return
    if not any(text.strip() for text in (title, abstract, keywords)):
        st.warning('Informe o título, o resumo ou palavras-chave do trabalho.')
        return
    allowed = None if institution == 'Sem filtro institucional' else institution_publishers(institutions, institution)
    version = SNAPSHOT_PATH.stat().st_mtime_ns if SNAPSHOT_PATH.exists() else 0
    engine = build_recommender(catalog, version)
    results = engine.recommend(title, abstract, keywords, publishers=allowed, integral_only=integral, limit=limit)
    if results.empty:
        st.info('Não encontramos correspondências com esses critérios. Tente palavras-chave mais específicas, também em inglês, ou revise os filtros. Isso não significa que não existam revistas adequadas.')
        return
    st.success(f'{len(results)} sugestões para conferir')
    if not results['Aderência'].isin(['Forte', 'Boa']).any():
        st.info('As correspondências encontradas são exploratórias ou fracas. Confira o escopo e experimente termos mais específicos; esta lista não confirma adequação editorial.')
    st.caption('A presença da instituição no acordo é preliminar. A cobertura depende também do título, modelo, vigência e requisitos do autor; a aprovação do custeio é da CAPES.')
    display_columns = ['Título da Revista', 'Editora', 'Aderência', 'Cobertura temática', 'Evidência', 'Termos do seu texto', 'ISSN', 'Modelo', 'Cobertura APC']
    display = results[[column for column in display_columns if column in results]].copy()
    if accepted is not None:
        display['Conferência da data'] = results['Editora'].map(lambda publisher: acceptance_status(publisher, accepted))
    with st.expander('Comparar sugestões em tabela'):
        st.dataframe(display, hide_index=True, width="stretch")
    current_group = None
    for position, (_, row) in enumerate(results.iterrows(), 1):
        group = row.get('Grupo de sugestões', 'Mais relacionadas')
        if group != current_group:
            st.subheader(group)
            if group == 'Outras revistas para explorar':
                st.caption('Correspondências parciais: podem compartilhar o problema ou a área sem cobrir todo o manuscrito. Confira o escopo antes de escolher.')
            current_group = group
        with st.container(border=True):
            st.markdown(f"**{position}. {row['Título da Revista']}**")
            st.markdown(journal_chips(row.get(AREA, ''), row['Editora'], row.get('_full_coverage', False)), unsafe_allow_html=True)
            st.caption('Aderência temática: ' + str(row['Aderência']))
            if str(row.get('Origem da sugestão', '')).startswith('Busca ampliada'):
                st.caption(row['Origem da sugestão'])
            st.write('**Por que apareceu:** ' + (row['Termos do seu texto'] or row['Termos relacionados'] or 'associação exploratória com o tema informado'))
            topics = str(row.get('Temas OpenAlex', '')).strip()
            if topics:
                st.caption('Temas da revista no OpenAlex: ' + topics)
            st.markdown(metric_panel(row), unsafe_allow_html=True)
            url = safe_url(row.get('Página da revista', ''))
            if url:
                st.link_button('Abrir revista e conferir escopo ↗', url, width='stretch')
            st.link_button('Pesquisar artigos no Google Acadêmico ↗', scholar_journal_url(row['Título da Revista']), width='stretch')
        with st.expander('Ver condições: ' + str(row['Título da Revista'])):
            st.write('**Perfil identificado:** ' + str(row.get('Perfil detectado', '')))
            if str(row.get('Origem da sugestão', '')).startswith('Busca ampliada'):
                st.caption('Resultado exploratório de uma busca ampliada. Não atribuímos percentual de correspondência ao manuscrito original.')
            else:
                st.caption(f"Cobertura textual ponderada: {row['Cobertura temática']:.0f}%. Evidência heurística: {row['Evidência']:.0f}/100. Não são probabilidades e não devem ser comparadas entre manuscritos como uma escala validada.")
            st.write('**Termos relacionados:** ' + row['Termos relacionados'])
            st.write('**Cobertura registrada:** ' + str(row.get('Cobertura APC', 'Conferir')))
            st.write('**Instituição:** ' + ('não informada; confira a lista do acordo' if allowed is None else 'consta na lista deste grupo; demais requisitos pendentes'))
            for column in ('Situação da lista', 'Observações', 'Observação'):
                if column in row and str(row[column]).strip():
                    st.write(str(row[column]))
            if accepted is not None:
                st.write(acceptance_status(row['Editora'], accepted))
            url = str(row.get('URL', ''))
            parsed = urlparse(url)
            if parsed.scheme == 'https' and parsed.netloc and not parsed.username:
                st.link_button('Abrir página de referência da revista', url)
            st.caption('Confira o escopo, os tipos de artigo aceitos e as condições oficiais de publicação. Fator de impacto, prazo editorial e probabilidade de aceite não são estimados por este motor.')