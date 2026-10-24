"""Simple and advanced journal discovery with separately labeled open metrics."""
import streamlit as st
import pandas as pd
from open_metrics import (METRIC, H_INDEX, AREA, enrich_catalog, read_snapshot,
                          filter_catalog, chart_records, safe_url, SNAPSHOT_PATH)
from capes_catalog import acceptance_status
from recommender_ui import render_recommender
from metric_visuals import metric_panel, journal_chips
from discovery_links import OPENALEX_ABOUT, scholar_journal_url, scholar_topic_url, summary_cards
from scholar_metrics import lookup as scholar_lookup, snapshot as scholar_snapshot


@st.cache_data(show_spinner=False, max_entries=2)
def prepare_explorer(catalog, snapshot_version=0):
    snapshot = read_snapshot()
    return enrich_catalog(catalog, snapshot), snapshot.get('retrieved_at', '')[:10]


def render_chart(frame, chart_metric, key='simple'):
    import altair as alt
    records = chart_records(frame, chart_metric)
    if not records:
        st.info('Não há métricas OpenAlex disponíveis para os filtros atuais. As revistas continuam na lista.')
        return
    areas = len({record['Área'] for record in records})
    chart = alt.Chart(alt.Data(values=records)).mark_circle(size=44, opacity=0.65).encode(
        x=alt.X('Valor:Q', title=chart_metric, scale=alt.Scale(type='symlog', constant=1, zero=True)),
        y=alt.Y('Área:N', title=None, axis=alt.Axis(labelLimit=220)),
        yOffset=alt.YOffset('Faixa:N', sort=list(range(9))),
        color=alt.Color('Área:N', legend=None, scale=alt.Scale(scheme='tableau20')),
        href=alt.Href('Página:N'),
        tooltip=[alt.Tooltip('Revista:N'), alt.Tooltip('ISSN:N'), alt.Tooltip('Editora:N'),
                 alt.Tooltip('Área:N'), alt.Tooltip('Valor:Q', title=chart_metric, format='.2f'),
                 alt.Tooltip('Consulta:N')],
    )
    median = alt.Chart(alt.Data(values=records)).transform_aggregate(
        Mediana='median(Valor)', groupby=['Área']
    ).mark_point(shape='diamond', filled=True, size=85, color='#173c53').encode(
        x=alt.X('Mediana:Q', scale=alt.Scale(type='symlog', constant=1, zero=True)),
        y=alt.Y('Área:N'),
        tooltip=[alt.Tooltip('Área:N'), alt.Tooltip('Mediana:Q', format='.2f')],
    )
    chart = (chart + median).properties(height=max(260, areas * 35), usermeta={"embedOptions": {"loader": {"target": "_blank"}}}).configure_view(stroke=None).configure_axis(
        labelFont='Arial', labelFontSize=14, titleFont='Arial', titleFontSize=16,
        labelColor='#475569', titleColor='#1f2937',
    )
    with st.container(key='pa_plot_' + key):
        st.altair_chart(chart, width="stretch")
    st.markdown('<span class="pa-mobile-hint">Deslize dentro do gráfico para explorar. Os botões das revistas abaixo também abrem os links.</span>', unsafe_allow_html=True)
    st.caption(f'{len(records):,} revistas com valor disponível. Passe o mouse para ver detalhes; clique no ponto para abrir a revista em nova aba quando houver link. Losangos mostram a mediana dos resultados de cada área. Áreas representam o campo do tópico predominante no OpenAlex. Eixo em escala simétrica logarítmica.')


def render_cards(frame, key, accepted=None):
    signature = tuple((str(row['ISSN']), str(row['Editora'])) for _, row in frame.iterrows())
    page_key = key + '_page'
    if st.session_state.get(key + '_signature') != signature:
        st.session_state[key + '_signature'] = signature
        st.session_state[page_key] = 1
    total = len(frame)
    st.caption(f'{total:,} registros · {int(frame[METRIC].notna().sum()):,} com média de citações disponível')
    if not total:
        st.info('Nenhuma revista encontrada. Revise o termo e os filtros.')
        return
    pages = max(1, (total + 9) // 10)
    page = st.number_input('Página de resultados', min_value=1, max_value=pages, step=1, key=page_key)
    for _, row in frame.iloc[(page-1)*10:page*10].iterrows():
        with st.container(border=True):
            st.markdown('**' + str(row['Título da Revista']) + '**')
            st.markdown(journal_chips(row[AREA], row['Editora'], row['_full_coverage']), unsafe_allow_html=True)
            st.markdown(metric_panel(row), unsafe_allow_html=True)
            if pd.isna(row[METRIC]) and pd.isna(row[H_INDEX]):
                st.caption('Métricas não disponíveis nesta consulta.')
            url = safe_url(row['Página da revista'])
            if url:
                st.link_button('Abrir revista ↗', url, width='stretch')
            st.link_button('Pesquisar artigos no Google Acadêmico ↗', scholar_journal_url(row['Título da Revista']), width='stretch')
            with st.expander('Cobertura, fonte e vigência'):
                st.write('**ISSN:** ' + str(row['ISSN']))
                for column in ('Modelo', 'Cobertura APC'):
                    value = str(row.get(column, '')).strip()
                    if value and value not in {'None', 'nan'}:
                        st.write(f'**{column}:** {value}')
                if accepted is not None:
                    st.write(acceptance_status(row['Editora'], accepted))
                if row['Fonte OpenAlex']:
                    st.link_button('Conferir registro no OpenAlex', row['Fonte OpenAlex'])
                if row['Fonte OpenAlex']:
                    st.caption('Métricas associadas pelo ISSN · consulta: ' + row['Consulta OpenAlex'])
                if not url:
                    st.caption('Link direto da revista não localizado.')


def render_explorer(catalog, institutions):
    from metrics_guide import render_metrics_guide
    from catalog_summary import catalog_counts
    version = SNAPSHOT_PATH.stat().st_mtime_ns if SNAPSHOT_PATH.exists() else 0
    frame, retrieved = prepare_explorer(catalog, version)
    counts = catalog_counts(frame, scholar_lookup)
    st.markdown(summary_cards(counts), unsafe_allow_html=True)
    st.caption(f"Segundo nossa base: {format(counts['full'], ',').replace(',', '.')} registros com cobertura integral indicada; {counts['partial']:,} com desconto parcial; {counts['other']:,} com outras condições ou confirmação pendente. A autorização depende dos requisitos do acordo. OpenAlex e Google não definem essa cobertura.")
    section = st.radio('Navegação', ['Encontrar revistas', 'Busca direta', 'Análise avançada', 'Entenda os índices'], horizontal=True, label_visibility='collapsed', key='main_section')
    if section == 'Entenda os índices':
        render_metrics_guide()
        return section
    if section == 'Encontrar revistas':
        st.subheader('Seu próximo artigo começa com uma boa escolha')
        st.write('Informe o título, o resumo ou palavras-chave. Explore sugestões e confira o escopo de cada revista.')
        render_recommender(catalog, institutions)
        return section
    publishers = sorted(frame['Editora'].unique())
    areas = sorted(frame[AREA].unique())
    if section == 'Busca direta':
        st.subheader('Encontre uma revista no catálogo')
        query = st.text_input('Buscar revista', placeholder='Nome, ISSN ou tema', key='simple_query')
        left, middle, right = st.columns(3)
        publisher = left.selectbox('Editora / acordo', ['Todas'] + publishers, key='simple_publisher')
        area = middle.selectbox('Área OpenAlex', ['Todas'] + areas, key='simple_area')
        order = right.selectbox('Ordenar por', ['Título', 'Citações em 2 anos', 'Índice h'], key='simple_order')
        filtered = filter_catalog(frame, query, [publisher] if publisher != 'Todas' else None,
                                  area if area != 'Todas' else None, order=order)
        google_only = st.checkbox('Somente revistas com h5 Google disponível', key='simple_google_only')
        if google_only:
            mask = filtered.apply(lambda row: scholar_lookup(row['Título da Revista'], issn=row['ISSN']) is not None, axis=1)
            filtered = filtered.loc[mask]
        render_cards(filtered, 'simple')
        return section
    st.subheader('Cruze filtros e explore o panorama')
    query = st.text_input('Nome, ISSN ou tema', key='advanced_query')
    left, right = st.columns(2)
    selected = left.multiselect('Editoras / acordos', publishers)
    area = right.selectbox('Área OpenAlex', ['Todas'] + areas, key='advanced_area')
    names = sorted(institutions['Nome da Instituição'].dropna().unique())
    institution = st.selectbox('Instituição do autor correspondente', ['Sem filtro institucional'] + names, key='advanced_institution')
    left, right = st.columns(2)
    full = left.checkbox('Somente cobertura integral indicada na base', value=True, key='advanced_full')
    metric_only = right.checkbox('Somente revistas com métrica OpenAlex', value=False)
    left, middle, right = st.columns(3)
    minimum = left.number_input('Média de citações mínima', min_value=0.0, value=0.0, step=0.5)
    accepted = middle.date_input('Data de aceite (opcional)', value=None, key='advanced_date')
    order = right.selectbox('Ordenar por', ['Citações em 2 anos', 'Índice h', 'Título'], key='advanced_order')
    filtered = filter_catalog(frame, query, selected, area if area != 'Todas' else None,
                              institutions, institution if institution != 'Sem filtro institucional' else None,
                              full, metric_only, minimum, order)
    show_chart = st.checkbox('Carregar gráfico interativo', value=False, key='load_chart')
    if show_chart:
        render_chart(filtered, H_INDEX if order == 'Índice h' else METRIC, key='advanced')
    else:
        st.caption('O gráfico só é carregado quando solicitado, para manter a navegação mais leve.')
    render_cards(filtered, 'advanced', accepted)
    return section