"""Simple and advanced journal discovery with separately labeled open metrics."""
import streamlit as st
from open_metrics import (METRIC, H_INDEX, AREA, enrich_catalog, read_snapshot,
                          filter_catalog, chart_records, safe_url)
from capes_catalog import acceptance_status
from recommender_ui import render_recommender


@st.cache_data(show_spinner=False, max_entries=2)
def prepare_explorer(catalog):
    snapshot = read_snapshot()
    return enrich_catalog(catalog, snapshot), snapshot.get('retrieved_at', '')[:10]


def render_chart(frame, chart_metric):
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
    chart = (chart + median).properties(height=max(260, areas * 31)).configure_view(stroke=None)
    st.altair_chart(chart, use_container_width=True)
    st.caption(f'{len(records):,} revistas com valor disponível. Passe o mouse para ver detalhes; clique no ponto para abrir a revista quando houver link. Losangos mostram a mediana dos resultados de cada área. Áreas representam o campo do tópico predominante no OpenAlex. Eixo em escala simétrica logarítmica.')


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
            title_col, metric_col, h_col = st.columns([6, 2, 1])
            with title_col:
                st.markdown('**' + str(row['Título da Revista']) + '**')
                st.caption(str(row[AREA]) + ' · ' + str(row['Editora']))
                st.caption('ISSN ' + str(row['ISSN']) + ' · ' + str(row.get('Modelo', '')) + ' · APC: ' + str(row.get('Cobertura APC', 'Conferir')))
            with metric_col:
                value = row[METRIC]
                st.metric('Citações / 2 anos¹', '—' if value != value else f'{value:.2f}')
            with h_col:
                value = row[H_INDEX]
                st.metric('Índice h¹', '—' if value != value else str(int(value)))
            url = safe_url(row['Página da revista'])
            if url:
                st.link_button('Abrir revista ↗', url)
            with st.expander('Cobertura, fonte e vigência'):
                st.write(acceptance_status(row['Editora'], accepted))
                st.write(str(row.get('Situação da lista', 'Confira as condições oficiais do acordo.')))
                if row['Fonte OpenAlex']:
                    st.link_button('Conferir registro no OpenAlex', row['Fonte OpenAlex'])
                st.caption('Correspondência: ' + row['Correspondência'] + ' · consulta: ' + row['Consulta OpenAlex'])
                if not url:
                    st.caption('Link direto da revista não localizado.')


def render_explorer(catalog, institutions):
    frame, retrieved = prepare_explorer(catalog)
    st.markdown('<div id="explorar-revistas"></div>', unsafe_allow_html=True)
    st.caption('¹ Métricas abertas OpenAlex, consultadas em ' + (retrieved or 'data não disponível') + '. Não são JIF/JCR, CiteScore ou quartil. Não determinam elegibilidade CAPES ou qualidade individual do artigo.')
    simple, advanced = st.tabs(['🔎 Busca simples', '🎯 Busca avançada'])
    publishers = sorted(frame['Editora'].unique())
    areas = sorted(frame[AREA].unique())
    with simple:
        query = st.text_input('Buscar revista', placeholder='Nome, ISSN ou tema — ex.: microbiologia', key='simple_query')
        left, middle, right = st.columns(3)
        publisher = left.selectbox('Editora / acordo', ['Todas'] + publishers, key='simple_publisher')
        area = middle.selectbox('Área', ['Todas'] + areas, key='simple_area')
        order = right.selectbox('Ordenar por', ['Título', 'Citações em 2 anos', 'Índice h'], key='simple_order')
        filtered = filter_catalog(frame, query, [publisher] if publisher != 'Todas' else None,
                                  area if area != 'Todas' else None, order=order)
        with st.expander('Panorama visual por área', expanded=True):
            render_chart(filtered, METRIC if order != 'Índice h' else H_INDEX)
        render_cards(filtered, 'simple')
    with advanced:
        mode = st.radio('Como deseja buscar?', ['Combinar filtros', 'Recomendar pelo manuscrito'], horizontal=True)
        if mode == 'Recomendar pelo manuscrito':
            render_recommender(catalog, institutions)
        else:
            query = st.text_input('Nome, ISSN ou tema', key='advanced_query')
            left, right = st.columns(2)
            selected = left.multiselect('Editoras / acordos', publishers)
            area = right.selectbox('Área', ['Todas'] + areas, key='advanced_area')
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
            st.caption('O filtro institucional confere somente a presença no acordo. A autorização de custeio exige os demais requisitos CAPES.')
            with st.expander('Panorama visual dos resultados', expanded=False):
                render_chart(filtered, H_INDEX if order == 'Índice h' else METRIC)
            render_cards(filtered, 'advanced', accepted)
    with st.expander('Sobre as métricas e a classificação por área'):
        st.write('A média de citações em dois anos e o índice h são fornecidos pelo OpenAlex. A correspondência usa ISSN exato; casos ambíguos e métricas ausentes não recebem valores estimados. A data de consulta é uma fotografia da base, não um ano JCR.')
        st.write('A área vem do campo do tópico mais frequente associado à revista no OpenAlex, traduzido quando disponível. Revistas multidisciplinares podem aparecer sob uma área predominante; não é uma classificação oficial de escopo editorial.')
        st.markdown('[Fonte e definições OpenAlex](https://help.openalex.org/data/sources/attributes/) · Dados CC0. Quartis JCR não são calculados a partir dessas métricas.')
