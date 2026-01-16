import streamlit as st
import pandas as pd
from datetime import datetime
import io
import unicodedata

# Configuração da página
st.set_page_config(
    page_title="Publique Gratuitamente - Acordos CAPES",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS customizado
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #1e3a8a 0%, #3b82f6 100%);
        padding: 2rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        color: white;
    }
    .credits {
        background-color: #f3f4f6;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #3b82f6;
        margin-top: 1rem;
    }
    .publisher-card {
        background-color: #ffffff;
        padding: 1rem;
        border-radius: 8px;
        border: 1px solid #e5e7eb;
        margin-bottom: 1rem;
    }
    .metric-card {
        background-color: #eff6ff;
        padding: 1rem;
        border-radius: 8px;
        text-align: center;
    }
    .institution-card {
        background-color: #f0fdf4;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #10b981;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# Cabeçalho
st.markdown("""
<div class="main-header">
    <h1>📊 Publique Gratuitamente - Acordos CAPES</h1>
    <p style="font-size: 1.1rem; margin-bottom: 0;">
        Descubra se você pode publicar sem custos através dos acordos transformativos
    </p>
</div>
""", unsafe_allow_html=True)

# Alerta informativo
st.info("""
🎯 **Como funciona:** Pesquise o periódico desejado abaixo. Se ele estiver listado, **você pode publicar gratuitamente** 
(sem pagar APCs) se for afiliado a uma instituição brasileira participante do Portal de Periódicos CAPES!
""")

# Créditos
st.markdown("""
<div class="credits">
    <h3 style="margin-top: 0; color: #1e40af;">💰 O que são Acordos Transformativos?</h3>
    <p style="margin-bottom: 1rem;">
        São acordos entre a CAPES e grandes editoras científicas que permitem a <strong>pesquisadores brasileiros 
        publicarem gratuitamente em acesso aberto</strong>, sem pagar APCs (Article Processing Charges - taxas de 
        processamento de artigos que podem custar milhares de dólares).
    </p>
    <p style="margin-bottom: 1rem;">
        <strong>✅ Você está elegível se:</strong><br>
        • É afiliado a uma instituição brasileira<br>
        • Sua instituição tem acesso ao Portal de Periódicos CAPES<br>
        • O periódico está listado neste sistema<br>
        • Você é o autor correspondente (corresponding author)
    </p>
    <hr style="margin: 1rem 0;">
    <h3 style="margin-top: 1rem; color: #1e40af;">📚 Desenvolvido por:</h3>
    <p style="margin-bottom: 0.5rem;">
        <strong>Grupo GOBIOTA</strong><br>
        <em>Grupo de Pesquisa e Inovação em Microbiologia e Inteligência Biotecnológica</em>
    </p>
    <p style="margin-bottom: 0.5rem; font-size: 0.9rem;">
        <strong>Instituição:</strong> Faculdade de Medicina Veterinária e Zootecnia (FMVZ)<br>
        Universidade Federal de Uberlândia (UFU)
    </p>
    <p style="margin-bottom: 0.5rem; font-size: 0.85rem; color: #4b5563;">
        <strong>Coordenação:</strong> Prof. Dr. Richard Costa Polveiro<br>
        <strong>CNPq:</strong> <a href="http://dgp.cnpq.br/dgp/espelhogrupo/5786031102053722" target="_blank" style="color: #3b82f6;">Espelho do Grupo</a><br>
        <strong>Instagram:</strong> <a href="https://instagram.com/gobiota2025" target="_blank" style="color: #3b82f6;">@gobiota2025</a>
    </p>
    <p style="margin-bottom: 0; font-size: 0.9rem; color: #6b7280;">
        ℹ️ Dados extraídos dos acordos transformativos CAPES vigentes • Atualizado periodicamente
    </p>
</div>
""", unsafe_allow_html=True)

# ==================== FUNÇÕES AUXILIARES ====================

def normalizar_busca(texto):
    """Remove acentos para busca"""
    if pd.isna(texto):
        return ""
    texto = unicodedata.normalize('NFKD', str(texto))
    texto = ''.join([c for c in texto if not unicodedata.combining(c)])
    return texto.upper()

# Carregar dados de periódicos
@st.cache_data(ttl=3600)
def load_data():
    """Carrega os dados do arquivo Excel hospedado no Google Drive"""
    file_path = 'https://drive.google.com/uc?export=download&id=1iOxbUE2vwWrtzIIgeydGdpYueoHnMVHY'
    
    xl_file = pd.ExcelFile(file_path)
    data = {}
    
    publishers = {
        '🟡 Elsevier': 'Elsevier',
        '🟢 Springer Nature': 'Springer Nature',
        '🟡⚠️ Wiley': 'Wiley',
        '🟢 ACM': 'ACM',
        '🔵 IEEE': 'IEEE',
        '💎 ACS': 'ACS'
    }
    
    for sheet_name, publisher in publishers.items():
        try:
            df = pd.read_excel(file_path, sheet_name=sheet_name)
            df = df.dropna(how='all')
            df = df.reset_index(drop=True)
            data[publisher] = df
        except Exception as e:
            st.warning(f"Não foi possível carregar dados de {publisher}: {str(e)}")
    
    try:
        data['INDICE'] = pd.read_excel(file_path, sheet_name='📊 ÍNDICE').dropna(how='all')
    except:
        data['INDICE'] = None
    
    try:
        data['REQUISITOS'] = pd.read_excel(file_path, sheet_name='✅ REQUISITOS').dropna(how='all')
    except:
        data['REQUISITOS'] = None
    
    return data

# Carregar dados de instituições
@st.cache_data(ttl=3600)
def load_institutions_data():
    """Carrega dados de instituições elegíveis do Google Drive"""
    # Link direto de download do Google Drive
    # Converter: https://drive.google.com/file/d/FILE_ID/view?usp=drive_link
    # Para: https://drive.google.com/uc?export=download&id=FILE_ID
    
    file_id = '1YYKD7zrTZNpIFIXMlDlFcRtYjRn5IYYq'
    url = f'https://drive.google.com/uc?export=download&id={file_id}'
    
    try:
        df = pd.read_csv(url)
        return df
    except Exception as e:
        st.error(f"Erro ao carregar dados de instituições: {str(e)}")
        return None

# URLs oficiais das editoras
URLS_INSTITUICOES = {
    'Elsevier': 'https://view.highspot.com/viewer/c53fae46a21769209f110f21afcc6504#1',
    'Springer Nature': 'https://resource-preview-cms.springernature.com/springer-cms/rest/v1/content/27829128/data/v7',
    'ACM': 'https://www.periodicos.capes.gov.br/images/documents/Lista%20de%20IES_ACM.pdf',
    'Royal Society': 'https://www.periodicos.capes.gov.br/images/documents/Acordo%20CAPES–Royal%20Society_%20Publicação%20em%20Acesso%20Aberto%20Sem%20Custos%20_%20Royal%20Society.pdf',
    'Wiley': 'https://www.wiley.com/en-br/publish/article/open-access/oa-agreement/',
    'IEEE': 'https://open.ieee.org/partners/capes-transformative-agreement/',
    'ACS': 'https://acsopenscience.org/customers/capes/'
}

# ==================== NOVA SEÇÃO: VERIFICAR INSTITUIÇÃO ====================

st.markdown("---")

with st.expander("🏛️ Verifique se sua Instituição é Elegível", expanded=False):
    st.markdown("""
    <div class="institution-card">
        <h3 style="margin-top: 0; color: #065f46;">✅ Confirme a elegibilidade da sua instituição</h3>
        <p style="margin-bottom: 0.5rem;">
            Use esta ferramenta para verificar em quais editoras sua instituição pode publicar 
            <strong>sem custos de APC</strong> através dos acordos CAPES.
        </p>
        <p style="margin-bottom: 0; font-size: 0.9rem; color: #6b7280;">
            💡 <strong>Total:</strong> 2.461 instituições elegíveis em 7 editoras
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Carregar dados
    df_inst = load_institutions_data()
    
    if df_inst is not None:
        # Campo de busca
        col1, col2 = st.columns([3, 1])
        
        with col1:
            instituicao_busca = st.text_input(
                "🔍 Digite sua instituição (nome ou sigla):",
                placeholder="Ex: UFU, Universidade Federal de Uberlândia, UNESP...",
                key="busca_instituicao",
                help="Você pode buscar pelo nome completo, sigla ou parte do nome"
            )
        
        # Filtro de editoras
        st.markdown("### 📚 Filtrar por editoras:")
        
        editoras_disponiveis = sorted(df_inst['editora'].unique())
        
        # Seleção rápida
        col_select = st.columns([1, 3])
        with col_select[0]:
            selecionar_todas = st.checkbox("Selecionar todas", value=True, key="select_all_ed")
        
        # Checkboxes
        cols = st.columns(4)
        editoras_selecionadas = []
        
        for i, editora in enumerate(editoras_disponiveis):
            with cols[i % 4]:
                checked = st.checkbox(
                    editora,
                    value=selecionar_todas,
                    key=f"check_inst_ed_{i}"
                )
                if checked:
                    editoras_selecionadas.append(editora)
        
        # Realizar busca
        if not editoras_selecionadas:
            st.warning("⚠️ Selecione pelo menos uma editora")
        else:
            # Filtrar resultados
            if instituicao_busca:
                termo_norm = normalizar_busca(instituicao_busca)
                
                mask = (
                    df_inst['nome_normalizado'].str.contains(termo_norm, na=False) |
                    df_inst['acronimo_normalizado'].str.contains(termo_norm, na=False)
                )
                
                resultados = df_inst[mask & df_inst['editora'].isin(editoras_selecionadas)]
            else:
                resultados = df_inst[df_inst['editora'].isin(editoras_selecionadas)]
            
            # Mostrar resultados
            st.markdown("---")
            
            if len(resultados) > 0:
                editoras_encontradas = sorted(resultados['editora'].unique())
                
                if instituicao_busca:
                    st.success(f"✅ **Sua instituição é elegível em {len(editoras_encontradas)} editora(s)!**")
                    
                    # Cards de resumo
                    cols_resumo = st.columns(min(len(editoras_encontradas), 4))
                    for i, ed in enumerate(editoras_encontradas):
                        with cols_resumo[i % 4]:
                            st.metric(
                                label=ed,
                                value="Elegível",
                                delta="✓"
                            )
                else:
                    st.info(f"Mostrando {len(resultados)} instituições de {len(editoras_encontradas)} editora(s)")
                
                st.markdown("---")
                
                # Detalhes por editora
                for editora in editoras_encontradas:
                    df_editora = resultados[resultados['editora'] == editora]
                    
                    with st.expander(
                        f"**{editora}** ({len(df_editora)} instituições)",
                        expanded=(len(editoras_encontradas) <= 2 and instituicao_busca != "")
                    ):
                        # Link oficial
                        if editora in URLS_INSTITUICOES:
                            st.markdown(f"🔗 [Consultar lista oficial da {editora}]({URLS_INSTITUICOES[editora]})")
                        
                        # Tabela
                        df_display = df_editora[['acronimo', 'nome']].copy()
                        df_display.columns = ['Sigla', 'Nome da Instituição']
                        df_display = df_display.sort_values('Nome da Instituição')
                        df_display = df_display.reset_index(drop=True)
                        
                        st.dataframe(
                            df_display,
                            use_container_width=True,
                            hide_index=True,
                            height=min(400, len(df_display) * 35 + 38)
                        )
                
                # Download
                st.markdown("---")
                st.markdown("### 💾 Exportar Resultados")
                
                df_export = resultados[['editora', 'acronimo', 'nome']].copy()
                df_export.columns = ['Editora', 'Sigla', 'Nome da Instituição']
                
                csv = df_export.to_csv(index=False, encoding='utf-8-sig')
                
                nome_arquivo = f"instituicoes_{instituicao_busca if instituicao_busca else 'todas'}.csv"
                
                st.download_button(
                    label="📥 Download CSV",
                    data=csv,
                    file_name=nome_arquivo,
                    mime="text/csv"
                )
            else:
                st.info("🔍 Nenhuma instituição encontrada com os critérios selecionados")
                st.markdown("""
                **💡 Sugestões:**
                - Verifique a ortografia
                - Tente usar apenas parte do nome (ex: "Federal Uberlândia")
                - Use a sigla (ex: "UFU")
                - Verifique se selecionou as editoras corretas
                """)
    else:
        st.error("❌ Não foi possível carregar os dados de instituições. Tente novamente mais tarde.")

st.markdown("---")

# ==================== CÓDIGO ORIGINAL DE PERIÓDICOS ====================

# Carregar dados
try:
    publisher_data = load_data()
    
    publishers_list = [k for k in publisher_data.keys() if k not in ['INDICE', 'REQUISITOS']]
    
    # Exibir ÍNDICE
    if publisher_data.get('INDICE') is not None:
        with st.expander("📊 Resumo Geral - Índice de Periódicos", expanded=False):
            st.markdown("### Visão Geral dos Acordos CAPES")
            st.dataframe(
                publisher_data['INDICE'],
                use_container_width=True,
                hide_index=True
            )
            st.caption("💡 Este é um resumo consolidado de todos os acordos transformativos CAPES")
    
    # Exibir REQUISITOS
    if publisher_data.get('REQUISITOS') is not None:
        with st.expander("✅ Requisitos para Publicação Gratuita", expanded=False):
            st.markdown("### O que você precisa para publicar gratuitamente")
            st.dataframe(
                publisher_data['REQUISITOS'],
                use_container_width=True,
                hide_index=True
            )
            st.caption("⚠️ Verifique estes requisitos antes de submeter seu artigo")
    
    st.markdown("---")
    
    # Sidebar - Logo e informações GOBIOTA
    st.sidebar.image("logo.png", use_column_width=True)
    
    st.sidebar.markdown("""
    <div style="text-align: center; margin-top: -10px; margin-bottom: 20px;">
        <h3 style="margin: 5px 0; color: #1e40af; font-size: 1.1rem;">GOBIOTA</h3>
        <p style="margin: 0; font-size: 0.75rem; color: #6b7280; line-height: 1.3;">
            <strong>G</strong>rupo de Pesquisa e Inovação em<br>
            <strong>O</strong>rganismos, <strong>Bio</strong>informática e<br>
            <strong>T</strong>ecnologias <strong>A</strong>plicadas
        </p>
        <p style="margin: 10px 0 0 0; font-size: 0.7rem; color: #9ca3af;">
            FMVZ • UFU
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    st.sidebar.markdown("---")
    
    # Botão para forçar atualização
    if st.sidebar.button("🔄 Atualizar Dados", help="Recarrega os dados da planilha CAPES"):
        st.cache_data.clear()
        st.rerun()
    
    st.sidebar.caption("ℹ️ Dados atualizados automaticamente a cada 1 hora")
    
    st.sidebar.markdown("---")
    
    # Sidebar - Seleção de editora
    st.sidebar.header("🔍 Filtros de Busca")
    
    # Seleção de editora
    selected_publisher = st.sidebar.selectbox(
        "Escolha a Editora:",
        ["Todas"] + publishers_list,
        help="Selecione uma editora específica ou 'Todas' para buscar em todas as editoras"
    )
    
    # Campo de busca
    search_term = st.sidebar.text_input(
        "🔎 Buscar Periódico:",
        placeholder="Digite o nome do periódico...",
        help="Digite parte do nome do periódico para filtrar os resultados"
    )
    
    st.sidebar.markdown("---")
    
    # Opções de visualização
    st.sidebar.header("⚙️ Opções de Visualização")
    
    view_option = st.sidebar.radio(
        "Escolha o modo de visualização:",
        ["Paginada (Recomendado)", "Tabela Completa", "Resumo Estatístico"],
        help="Escolha como deseja visualizar os dados"
    )
    
    if view_option == "Paginada (Recomendado)":
        rows_per_page = st.sidebar.slider(
            "Linhas por página:",
            min_value=10,
            max_value=100,
            value=25,
            step=5,
            help="Número de periódicos exibidos por página"
        )
    
    # Área principal
    st.header("📋 Lista de Periódicos Elegíveis")
    
    # Preparar dados para exibição
    if selected_publisher == "Todas":
        # Combinar dados de todas as editoras
        all_data = []
        for pub, df in publisher_data.items():
            if pub not in ['INDICE', 'REQUISITOS']:
                df_temp = df.copy()
                df_temp.insert(0, 'Editora', pub)
                all_data.append(df_temp)
        
        if all_data:
            df_display = pd.concat(all_data, ignore_index=True)
        else:
            df_display = pd.DataFrame()
    else:
        df_display = publisher_data[selected_publisher].copy()
        df_display.insert(0, 'Editora', selected_publisher)
    
    # Aplicar filtro de busca
    if search_term:
        # Criar máscara de busca em todas as colunas de texto
        mask = pd.Series([False] * len(df_display))
        for col in df_display.select_dtypes(include=['object']).columns:
            mask = mask | df_display[col].astype(str).str.contains(search_term, case=False, na=False)
        
        df_filtered = df_display[mask]
    else:
        df_filtered = df_display
    
    # Informações sobre os resultados
    total_rows = len(df_filtered)
    
    if search_term:
        st.success(f"✅ Encontrados **{total_rows}** periódicos contendo '{search_term}'")
    else:
        st.info(f"📊 Mostrando **{total_rows}** periódicos")
    
    # Exibir dados conforme opção escolhida
    if total_rows == 0:
        st.warning("⚠️ Nenhum periódico encontrado com os critérios de busca especificados.")
    
    elif view_option == "Paginada (Recomendado)":
        total_pages = (total_rows - 1) // rows_per_page + 1
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            page = st.number_input(
                f"Página (1-{total_pages}):",
                min_value=1,
                max_value=max(1, total_pages),
                value=1
            )
        
        start_idx = (page - 1) * rows_per_page
        end_idx = start_idx + rows_per_page
        
        st.dataframe(
            df_filtered.iloc[start_idx:end_idx],
            use_container_width=True,
            hide_index=True
        )
        
        st.caption(f"Mostrando linhas {start_idx + 1} a {min(end_idx, total_rows)} de {total_rows}")
    
    elif view_option == "Tabela Completa":
        st.dataframe(
            df_filtered,
            use_container_width=True,
            hide_index=True,
            height=600
        )
    
    else:  # Resumo Estatístico
        st.write("### 📊 Informações da Base de Dados")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Estrutura dos Dados:**")
            st.write(f"- Total de registros: {len(df_filtered):,}")
            st.write(f"- Total de colunas: {len(df_filtered.columns)}")
            st.write(f"- Tipos de dados:")
            for dtype in df_filtered.dtypes.unique():
                count = (df_filtered.dtypes == dtype).sum()
                st.write(f"  - {dtype}: {count} coluna(s)")
        
        with col2:
            st.write("**Colunas Disponíveis:**")
            for i, col in enumerate(df_filtered.columns, 1):
                st.write(f"{i}. {col}")
    
    # Informações adicionais
    st.markdown("---")
    
    with st.expander("❓ Perguntas Frequentes - Como publicar gratuitamente"):
        st.markdown("""
        ### 1. O que são Acordos Transformativos?
        
        São contratos entre a CAPES e grandes editoras científicas que permitem:
        - **Acesso aberto (Open Access)** às publicações
        - **Sem custos de APC** para autores brasileiros elegíveis
        - Publicações imediatamente disponíveis para todo o mundo
        
        ### 2. Como sei se posso publicar gratuitamente?
        
        **Você pode publicar sem custos se:**
        - ✅ O periódico está listado neste sistema
        - ✅ Você é afiliado a uma instituição brasileira
        - ✅ Sua instituição tem acesso ao Portal CAPES
        - ✅ Você é o autor correspondente (corresponding author)
        
        **Importante:** O benefício vale para o **corresponding author** afiliado a instituição brasileira.
        
        ### 3. Como usar este sistema?
        
        **Passo a passo:**
        1. Escolha a editora do periódico na barra lateral
        2. Use a busca para encontrar o periódico desejado
        3. Se o periódico aparecer na lista → Você pode publicar gratuitamente! 🎉
        4. Se não aparecer → Você precisará pagar APCs ou buscar outras opções
        
        ### 4. Quanto eu economizo?
        
        APCs típicos variam de:
        - **US$ 1.500 a US$ 3.000** em periódicos convencionais
        - **US$ 3.000 a US$ 11.000** em periódicos de alto impacto (Nature, Science, Cell, etc.)
        
        Com os acordos CAPES, você publica **totalmente grátis** em acesso aberto!
        
        ### 5. Quais editoras estão cobertas?
        
        Este sistema cobre 6 grandes editoras:
        - **🟡 Elsevier** - Maior editora científica (The Lancet, Cell, etc.)
        - **🟢 Springer Nature** - Nature, BMC, Scientific Reports
        - **🟡⚠️ Wiley** - Diversas áreas científicas
        - **🟢 ACM** - Computação e tecnologia
        - **🔵 IEEE** - Engenharia e tecnologia
        - **💎 ACS** - Química e ciências relacionadas
        
        ### 6. Como faço para publicar depois de encontrar o periódico?
        
        1. **Submeta seu artigo** normalmente pelo site do periódico
        2. **Durante a submissão**, selecione a opção "Open Access" ou "Gold OA"
        3. **Informe sua afiliação brasileira** corretamente
        4. O sistema reconhece automaticamente o acordo CAPES
        5. Não há cobrança de APCs!
        
        **Dica:** Em caso de dúvida, entre em contato com a editora mencionando o acordo CAPES.
        
        ### 7. Minha instituição participa?
        
        Praticamente todas as instituições brasileiras de ensino e pesquisa participam através do 
        **Portal de Periódicos CAPES**. Isso inclui:
        - Universidades federais, estaduais e privadas
        - Institutos federais
        - Centros de pesquisa
        
        **💡 Use a seção "Verifique se sua Instituição é Elegível" no topo da página para confirmar!**
        
        ### 8. Os acordos têm prazo de validade?
        
        Sim, os acordos são renovados periodicamente. Este sistema é atualizado conforme:
        - Novos acordos são assinados
        - Acordos existentes são renovados
        - Novos periódicos são adicionados aos acordos
        
        ### 9. Posso publicar em co-autoria com estrangeiros?
        
        **Sim!** O que importa é que o **corresponding author** seja afiliado a uma instituição 
        brasileira elegível. Os demais co-autores podem ser de qualquer país.
        
        ### 10. Onde encontro mais informações oficiais?
        
        - **Portal CAPES:** https://www.periodicos.capes.gov.br
        - **Acordo com cada editora:** Consulte a página de Open Access da editora
        - **Biblioteca da sua instituição:** Entre em contato para suporte
        
        ---
        
        ### 📞 Precisa de ajuda?
        
        Entre em contato com a **biblioteca da sua instituição** - eles têm especialistas 
        em acordos transformativos que podem ajudar!
        """)
    
    with st.expander("ℹ️ Sobre este Sistema"):
        st.markdown("""
        ### Objetivo
        
        Facilitar a busca de periódicos cobertos pelos acordos transformativos CAPES, 
        ajudando pesquisadores brasileiros a:
        - Economizar milhares de dólares em APCs
        - Publicar em acesso aberto sem custos
        - Aumentar o impacto de suas pesquisas
        
        ### Como usar:
        
        1. **Selecione a Editora** na barra lateral (se souber qual é)
        2. **Use o campo de busca** para encontrar seu periódico
        3. **Verifique se está na lista** = Publicação gratuita! 🎉
        
        ### Dados:
        
        Os dados são extraídos e consolidados dos acordos oficiais CAPES com cada editora.
        Atualizações são feitas periodicamente conforme novos acordos ou renovações.
        
        ### Desenvolvido por:
        
        **Grupo GOBIOTA** - Genômica, Bioinformática e Tecnologias Aplicadas  
        Programa de Pós-Graduação - FMVZ/UFU
        
        **Objetivo:** Democratizar o acesso à informação sobre publicação científica gratuita 
        para toda a comunidade acadêmica brasileira.
        
        ---
        *Última atualização: {datetime.now().strftime('%d/%m/%Y')}*
        """)
    
    # Rodapé
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #6b7280; padding: 1rem;">
        <p style="margin-bottom: 0.5rem;">
            <strong>Grupo GOBIOTA</strong> | FMVZ - Universidade Federal de Uberlândia
        </p>
        <p style="margin: 0; font-size: 0.9rem;">
            💰 Ajudando pesquisadores brasileiros a publicarem gratuitamente em acesso aberto
        </p>
        <p style="margin-top: 0.5rem; font-size: 0.85rem;">
            📧 <a href="mailto:richard.polveiro@ufu.br" style="color: #3b82f6; text-decoration: none;">richard.polveiro@ufu.br</a> | 
            📱 <a href="https://instagram.com/gobiota2025" target="_blank" style="color: #3b82f6; text-decoration: none;">@gobiota2025</a> | 
            🔗 <a href="http://dgp.cnpq.br/dgp/espelhogrupo/5786031102053722" target="_blank" style="color: #3b82f6; text-decoration: none;">CNPq</a>
        </p>
        <p style="margin-top: 0.5rem; font-size: 0.8rem; color: #9ca3af;">
            Grupo de Pesquisa e Inovação em Microbiologia e Inteligência Biotecnológica
        </p>
    </div>
    """, unsafe_allow_html=True)

except Exception as e:
    st.error(f"""
    ❌ **Erro ao carregar os dados**
    
    Certifique-se de que o arquivo está acessível no Google Drive.
    
    Detalhes técnicos: {str(e)}
    """)
