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
    .warning-box {
        background-color: #fef3c7;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #f59e0b;
        margin: 1rem 0;
    }
    .info-box {
        background-color: #dbeafe;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #3b82f6;
        margin: 1rem 0;
    }
    .diamond-box {
        background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
        padding: 1.5rem;
        border-radius: 10px;
        border: 2px solid #f59e0b;
        margin: 1rem 0;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .danger-box {
        background-color: #fee2e2;
        padding: 1.5rem;
        border-radius: 8px;
        border-left: 4px solid #ef4444;
        margin: 1rem 0;
    }
    
    /* ==================== OCULTAR DOWNLOADS - REGRAS MÁXIMAS ==================== */
    
    /* Ocultar botão "Download as CSV" por múltiplos seletores */
    button[title="Download as CSV"],
    button[title="Download"],
    button[title="Baixar como CSV"],
    button[kind="header"],
    button[data-testid*="download"],
    button[data-testid*="Download"],
    [data-testid="stDataFrameDownloadButton"],
    [data-testid="stDownloadButton"],
    [data-testid="stElementToolbar"] button,
    div[data-testid="stDataFrame"] button[kind="header"],
    div[data-testid="stDataFrame"] button,
    .stDataFrame button {
        display: none !important;
        visibility: hidden !important;
        opacity: 0 !important;
        pointer-events: none !important;
        width: 0 !important;
        height: 0 !important;
        margin: 0 !important;
        padding: 0 !important;
    }
    
    /* Ocultar toolbar inteiro dos dataframes */
    [data-testid="stElementToolbar"],
    div[data-testid="stDataFrame"] [data-testid="stElementToolbar"],
    .stDataFrame [data-testid="stElementToolbar"] {
        display: none !important;
        visibility: hidden !important;
        opacity: 0 !important;
    }
    
    /* Remover QUALQUER botão dentro de dataframes */
    div[data-testid="stDataFrame"] button,
    div[data-testid="stDataFrame"] div button,
    [class*="dataframe"] button,
    [class*="DataFrame"] button {
        display: none !important;
    }
</style>

<script>
    // JavaScript AGRESSIVO para remover botões de download
    function removeDownloadButtons() {
        // Remover por título
        document.querySelectorAll('button[title*="Download"], button[title*="CSV"], button[title*="Baixar"]').forEach(btn => {
            btn.style.display = 'none';
            btn.style.visibility = 'hidden';
            btn.style.opacity = '0';
            btn.remove();
        });
        
        // Remover por atributos data
        document.querySelectorAll('[data-testid*="download"], [data-testid*="Download"]').forEach(el => {
            el.style.display = 'none';
            el.remove();
        });
        
        // Remover toolbar inteiro
        document.querySelectorAll('[data-testid="stElementToolbar"]').forEach(toolbar => {
            toolbar.style.display = 'none';
            toolbar.remove();
        });
        
        // Remover TODOS os botões dentro de dataframes
        document.querySelectorAll('div[data-testid="stDataFrame"] button').forEach(btn => {
            btn.style.display = 'none';
            btn.remove();
        });
        
        // Remover por texto do botão
        document.querySelectorAll('button').forEach(button => {
            const text = button.textContent.toLowerCase();
            if (text.includes('download') || text.includes('csv') || text.includes('baixar')) {
                button.style.display = 'none';
                button.remove();
            }
        });
    }
    
    // Executar ao carregar
    document.addEventListener('DOMContentLoaded', removeDownloadButtons);
    
    // Executar MUITO frequentemente (a cada 100ms) para pegar elementos dinâmicos
    setInterval(removeDownloadButtons, 100);
    
    // Observer para novos elementos (mais agressivo)
    const observer = new MutationObserver(function(mutations) {
        removeDownloadButtons();
    });
    
    // Observar o body inteiro
    setTimeout(function() {
        observer.observe(document.body, { 
            childList: true, 
            subtree: true,
            attributes: true
        });
    }, 500);
    
    // Backup: remover a cada segundo também
    setInterval(removeDownloadButtons, 1000);
</script>

<script>
    // Função para rolagem suave ao clicar nos links de navegação
    document.addEventListener('DOMContentLoaded', function() {
        // Aguardar um pouco para garantir que o Streamlit terminou de renderizar
        setTimeout(function() {
            // Verificar se há hash na URL
            if (window.location.hash) {
                scrollToSection(window.location.hash);
            }
            
            // Adicionar listeners aos links de navegação
            document.querySelectorAll('a[href^="#"]').forEach(anchor => {
                anchor.addEventListener('click', function (e) {
                    e.preventDefault();
                    const targetId = this.getAttribute('href');
                    scrollToSection(targetId);
                });
            });
        }, 1000);
    });
    
    // Função para rolar até a seção
    function scrollToSection(targetId) {
        // Remover o # do início
        const sectionId = targetId.replace('#', '');
        
        // Tentar encontrar elemento pelo ID exato
        let targetElement = document.getElementById(sectionId);
        
        // Se não encontrar, procurar por texto do header
        if (!targetElement) {
            const headers = document.querySelectorAll('h1, h2, h3');
            headers.forEach(header => {
                const headerText = header.textContent.toLowerCase()
                    .replace(/[^a-z0-9]+/g, '-')
                    .replace(/^-+|-+$/g, '');
                
                if (sectionId.includes(headerText) || headerText.includes(sectionId.split('-')[0])) {
                    targetElement = header;
                }
            });
        }
        
        // Rolar até o elemento encontrado
        if (targetElement) {
            targetElement.scrollIntoView({ 
                behavior: 'smooth', 
                block: 'start'
            });
        }
    }
    
    // Observer para quando o Streamlit adiciona novo conteúdo
    const observer2 = new MutationObserver(function(mutations) {
        // Re-adicionar listeners quando novo conteúdo é adicionado
        document.querySelectorAll('a[href^="#"]').forEach(anchor => {
            anchor.removeEventListener('click', null);
            anchor.addEventListener('click', function (e) {
                e.preventDefault();
                const targetId = this.getAttribute('href');
                scrollToSection(targetId);
            });
        });
    });
    
    // Observar o container principal do Streamlit
    setTimeout(function() {
        const container = document.querySelector('.main');
        if (container) {
            observer2.observe(container, { 
                childList: true, 
                subtree: true 
            });
        }
    }, 1000);
</script>
""", unsafe_allow_html=True)

# Função para normalizar texto (remover acentos)
def normalize_text(text):
    if pd.isna(text):
        return ""
    text = str(text)
    return ''.join(c for c in unicodedata.normalize('NFD', text) 
                   if unicodedata.category(c) != 'Mn').lower()

# Cache da URL do Google Sheets
@st.cache_data(ttl=3600)  # Cache por 1 hora
def load_data_from_google_sheets():
    """
    Carrega dados do Google Sheets publicado
    """
    # URL do Google Sheets exportado como Excel
    sheet_id = "10Q3uNZARR3eJFr4XsZOF5FvytUBKCnWX"
    url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=xlsx"
    
    try:
        # Carregar todas as abas
        excel_file = pd.ExcelFile(url)
        
        # Dicionário para armazenar os dados
        data = {}
        
        # Carregar cada aba
        for sheet_name in excel_file.sheet_names:
            df = pd.read_excel(excel_file, sheet_name=sheet_name)
            data[sheet_name.replace('📊 ', '').replace('🟢 ', '').replace('🟡 ', '')\
                .replace('🔵 ', '').replace('💎 ', '').replace('🔴 ', '')\
                .replace('✅ ', '').replace('⚠️ ', '').strip()] = df
        
        return data
    except Exception as e:
        st.error(f"Erro ao carregar dados: {str(e)}")
        return None

# Função para criar lista de instituições a partir dos dados de editoras
def extract_institutions(publisher_data):
    """
    Extrai lista única de instituições de todas as editoras
    """
    institutions_set = set()
    
    # Lista de editoras que podem ter dados de instituições
    publisher_keys = ['Springer Nature', 'Elsevier', 'Wiley', 'ACM', 'IEEE', 'ACS', 'RSP']
    
    for key in publisher_keys:
        if key in publisher_data:
            df = publisher_data[key]
            # Tentar encontrar coluna de instituição
            inst_cols = [col for col in df.columns if 'instituição' in col.lower() or 'institution' in col.lower()]
            for col in inst_cols:
                institutions_set.update(df[col].dropna().unique())
    
    return sorted(list(institutions_set))

# Carregar dados
with st.spinner("Carregando dados atualizados..."):
    publisher_data = load_data_from_google_sheets()

if publisher_data is None:
    st.error("Não foi possível carregar os dados. Por favor, tente novamente mais tarde.")
    st.stop()

# ==================== CABEÇALHO ====================

col_logo, col_title = st.columns([1, 3])

with col_logo:
    st.markdown("""
    <div style="text-align: center; padding: 1rem;">
        <div style="background-color: #1e3a8a; border-radius: 50%; width: 120px; height: 120px; 
                    display: flex; align-items: center; justify-content: center; margin: 0 auto;">
            <span style="font-size: 3rem;">📚</span>
        </div>
        <p style="margin-top: 0.5rem; font-weight: bold; color: #1e40af;">GOBIOTA</p>
        <p style="font-size: 0.8rem; color: #6b7280; line-height: 1.2;">
            Grupo de Pesquisa e Inovação em<br>
            Microbiologia e Inteligência<br>
            Biotecnológica
        </p>
        <p style="font-size: 0.75rem; color: #9ca3af;">FMVZ • UFU</p>
    </div>
    """, unsafe_allow_html=True)

with col_title:
    st.markdown("""
    <div class="main-header">
        <h1 style="margin: 0; font-size: 2.5rem;">📚 Publique Gratuitamente - Acordos CAPES</h1>
        <p style="margin-top: 0.5rem; font-size: 1.1rem; opacity: 0.9;">
            Descubra se você pode publicar sem custos através dos acordos transformativos
        </p>
    </div>
    """, unsafe_allow_html=True)

# Botão de atualização
col_btn, col_info = st.columns([1, 4])

with col_btn:
    if st.button("🔄 Atualizar Dados", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

with col_info:
    st.info("ℹ️ Dados atualizados automaticamente a cada 1 hora")

st.markdown("---")

# ==================== COMO FUNCIONA ====================

st.markdown("""
<div class="info-box">
    <h3 style="margin-top: 0;">🎯 Como funciona: Este sistema tem DUAS funções essenciais:</h3>
    <ol style="font-size: 1.05rem; line-height: 1.8;">
        <li><strong>🏛 Verificar se SUA INSTITUIÇÃO é elegível</strong> (primeiro passo - faça isso abaixo!)</li>
        <li><strong>📚 Buscar o PERIÓDICO</strong> onde você quer publicar (segundo passo)</li>
    </ol>
    <p style="font-size: 1.1rem; margin-bottom: 0; margin-top: 1rem;">
        <strong>Se AMBOS estiverem listados → Você pode publicar GRATUITAMENTE! 🎉</strong>
    </p>
</div>
""", unsafe_allow_html=True)

# ==================== NAVEGAÇÃO RÁPIDA ====================

st.markdown("""
<div style="background-color: #f0fdf4; padding: 1rem; border-radius: 8px; border-left: 4px solid #10b981; margin: 1rem 0;">
    <h4 style="margin-top: 0;">🧭 Navegação Rápida</h4>
    <p style="margin-bottom: 0.5rem;">Use os links abaixo para navegar rapidamente entre as seções:</p>
    <div style="display: flex; gap: 1rem; flex-wrap: wrap;">
        <a href="#verificar-instituicao" style="padding: 0.5rem 1rem; background-color: #10b981; color: white; 
           text-decoration: none; border-radius: 5px; font-weight: bold;">🏛 Verificar Instituição</a>
        <a href="#buscar-periodico" style="padding: 0.5rem 1rem; background-color: #3b82f6; color: white; 
           text-decoration: none; border-radius: 5px; font-weight: bold;">📚 Buscar Periódico</a>
    </div>
</div>
""", unsafe_allow_html=True)

# ==================== O QUE SÃO ACORDOS TRANSFORMATIVOS ====================

with st.expander("💰 O que são Acordos Transformativos?", expanded=False):
    st.markdown("""
    São acordos entre a CAPES e grandes editoras científicas que permitem a **pesquisadores brasileiros 
    publicarem gratuitamente em acesso aberto**, sem pagar APCs (Article Processing Charges - taxas 
    de processamento de artigos que podem custar milhares de dólares).
    
    ### 🎯 Benefícios:
    - ✅ Publicação 100% gratuita em acesso aberto
    - ✅ Visibilidade mundial imediata
    - ✅ Economia de US$ 1.500 a US$ 11.000 por artigo
    - ✅ Cumprimento de requisitos de acesso aberto
    
    ### 📊 Números desta atualização:
    - **5.863 periódicos** disponíveis
    - **8 editoras** parceiras
    - **Período:** 2026-2028
    - **Última atualização:** 13 de Fevereiro de 2026
    """)

st.markdown("---")
st.markdown("<div id='verificar-instituicao'></div>", unsafe_allow_html=True)

# ==================== PASSO 1: VERIFICAR INSTITUIÇÃO ====================

st.markdown("## 🏛 PASSO 1: Verificar sua Instituição")

st.markdown("""
<div class="warning-box">
    <strong>⚠️ IMPORTANTE:</strong> Antes de buscar periódicos, verifique se sua instituição é elegível!
    <br><br>
    Cada editora tem sua própria lista de instituições. Sua instituição pode estar em algumas 
    editoras mas não em outras.
</div>
""", unsafe_allow_html=True)

# Input de busca de instituição
institution_search = st.text_input(
    "Digite o nome da sua instituição:",
    placeholder="Ex: Universidade Federal de Uberlândia",
    help="Digite pelo menos 3 caracteres para buscar"
)

if institution_search and len(institution_search) >= 3:
    search_normalized = normalize_text(institution_search)
    
    # Buscar em todas as editoras
    found_institutions = {}
    
    # Lista de editoras para verificar
    publishers_to_check = {
        'Springer Nature': '🟢 Springer Nature',
        'Elsevier': '🟡 Elsevier',
        'Wiley OnlineOpen': '🟢 Wiley OnlineOpen',
        'Wiley Gold': '🟡 Wiley Gold',
        'ACM': '🟢 ACM',
        'IEEE': '🔵 IEEE',
        'ACS': '💎 ACS',
        'RSP': '🔴 RSP'
    }
    
    for publisher, display_name in publishers_to_check.items():
        if publisher in publisher_data:
            df = publisher_data[publisher]
            # Buscar em todas as colunas por instituições
            matches = []
            for col in df.columns:
                if df[col].dtype == 'object':
                    df_search = df[col].dropna().astype(str)
                    df_normalized = df_search.apply(normalize_text)
                    matches.extend(df_search[df_normalized.str.contains(search_normalized, na=False)].unique())
            
            if matches:
                found_institutions[display_name] = list(set(matches))
    
    if found_institutions:
        st.success(f"✅ Encontramos sua instituição em {len(found_institutions)} editora(s)!")
        
        for publisher, institutions in found_institutions.items():
            with st.expander(f"{publisher} - {len(institutions)} instituição(ões) encontrada(s)", expanded=True):
                for inst in institutions:
                    st.markdown(f"- {inst}")
        
        st.markdown("""
        <div class="institution-card">
            <strong>✅ Próximo passo:</strong> Busque periódicos nas editoras onde sua instituição é elegível!
        </div>
        """, unsafe_allow_html=True)
    else:
        st.warning(f"⚠️ Não encontramos '{institution_search}' nas listas. Tente:")
        st.markdown("""
        - Verificar a ortografia
        - Usar nome completo da instituição
        - Tentar variações (siglas, por extenso)
        - Contatar sua biblioteca para confirmar
        """)

st.markdown("---")
st.markdown("<div id='buscar-periodico'></div>", unsafe_allow_html=True)

# ==================== PASSO 2: BUSCAR PERIÓDICO ====================

st.markdown("## 📚 PASSO 2: Buscar Periódico")

# Sidebar para filtros
with st.sidebar:
    st.markdown("### 🔍 Filtros de Busca")
    
    # Seletor de editora
    publisher_options = ["Todas as editoras"] + list(publisher_data.keys())
    # Remover abas especiais
    publisher_options = [p for p in publisher_options if p not in ['INDICE', 'ÍNDICE', 'REQUISITOS', 'AVISOS']]
    
    selected_publisher = st.selectbox(
        "Editora:",
        publisher_options,
        help="Selecione uma editora específica ou busque em todas"
    )
    
    # Tipo de visualização
    view_type = st.radio(
        "Tipo de Visualização:",
        ["Resultados da Busca", "Tabela Completa", "Resumo Estatístico"],
        help="Escolha como visualizar os dados"
    )

# Busca de periódico
col1, col2 = st.columns([3, 1])

with col1:
    journal_search = st.text_input(
        "🔍 Digite o nome do periódico ou ISSN:",
        placeholder="Ex: Nature, Science, 1234-5678",
        help="Busca por título ou ISSN"
    )

with col2:
    st.markdown("<br>", unsafe_allow_html=True)
    search_button = st.button("🔍 Buscar", use_container_width=True, type="primary")

# Preparar dados para busca
all_journals = []

if selected_publisher == "Todas as editoras":
    publishers_to_search = [p for p in publisher_data.keys() if p not in ['INDICE', 'ÍNDICE', 'REQUISITOS', 'AVISOS']]
else:
    publishers_to_search = [selected_publisher]

for publisher in publishers_to_search:
    if publisher in publisher_data:
        df = publisher_data[publisher].copy()
        if 'Editora' not in df.columns:
            df['Editora'] = publisher
        all_journals.append(df)

if all_journals:
    df_all = pd.concat(all_journals, ignore_index=True)
else:
    st.error("Não foi possível carregar os dados das editoras.")
    st.stop()

# Aplicar busca
if journal_search:
    search_normalized = normalize_text(journal_search)
    
    # Criar máscara de busca
    mask = pd.Series([False] * len(df_all))
    
    # Buscar em título
    if 'Título da Revista' in df_all.columns:
        mask |= df_all['Título da Revista'].apply(normalize_text).str.contains(search_normalized, na=False)
    
    # Buscar em ISSN
    issn_columns = [col for col in df_all.columns if 'issn' in col.lower()]
    for col in issn_columns:
        mask |= df_all[col].astype(str).str.replace('-', '').str.contains(
            journal_search.replace('-', ''), na=False, case=False
        )
    
    df_filtered = df_all[mask].copy()
    
    if len(df_filtered) > 0:
        st.success(f"✅ Encontramos {len(df_filtered)} periódico(s)!")
        
        # Mostrar resultados
        for idx, row in df_filtered.iterrows():
            with st.container():
                # Verificar avisos especiais
                is_wiley_gold = 'Wiley Gold' in str(row.get('Editora', ''))
                is_diamond = 'DIAMANTE' in str(row.get('Modelo', '')).upper() or \
                            'ACS Central Science' in str(row.get('Título da Revista', ''))
                cobertura = str(row.get('Cobertura APC', '100%'))
                
                # Título do periódico
                st.markdown(f"### 📖 {row.get('Título da Revista', 'N/A')}")
                
                # Card especial para DIAMANTE
                if is_diamond:
                    st.markdown("""
                    <div class="diamond-box">
                        <h4 style="margin-top: 0; color: #92400e;">💎 PERIÓDICO DIAMANTE!</h4>
                        <p style="margin-bottom: 0; font-size: 1.05rem;">
                            <strong>Totalmente GRATUITO para TODOS!</strong><br>
                            Este periódico não cobra APC de ninguém, independente de acordo.<br>
                            É uma escolha PREMIUM para suas publicações! 🌟
                        </p>
                    </div>
                    """, unsafe_allow_html=True)
                
                # Aviso para Wiley Gold
                elif is_wiley_gold or '55%' in cobertura:
                    st.markdown("""
                    <div class="danger-box">
                        <h4 style="margin-top: 0; color: #b91c1c;">⚠️ ATENÇÃO - CUSTO PARCIAL!</h4>
                        <p style="font-size: 1.05rem; margin-bottom: 0.5rem;">
                            <strong>Wiley Gold oferece apenas 55% de desconto.</strong><br>
                            <strong style="color: #dc2626;">VOCÊ AINDA PAGARÁ 45% DO APC!</strong>
                        </p>
                        <p style="margin-bottom: 0; font-size: 0.95rem;">
                            <strong>Exemplo:</strong><br>
                            • APC total: $3.000<br>
                            • Desconto CAPES (55%): $1.650<br>
                            • <strong style="color: #dc2626;">VOCÊ PAGA: $1.350</strong>
                        </p>
                        <p style="margin-top: 0.5rem; margin-bottom: 0; font-size: 0.9rem; font-style: italic;">
                            💡 Recomendação: Prefira Wiley OnlineOpen (100% grátis)
                        </p>
                    </div>
                    """, unsafe_allow_html=True)
                
                # Informações do periódico
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.markdown(f"**Editora:** {row.get('Editora', 'N/A')}")
                    if 'ISSN' in row:
                        st.markdown(f"**ISSN:** {row.get('ISSN', 'N/A')}")
                    elif 'ISSN Online' in row:
                        st.markdown(f"**ISSN:** {row.get('ISSN Online', 'N/A')}")
                
                with col2:
                    modelo = row.get('Modelo', 'N/A')
                    st.markdown(f"**Modelo:** {modelo}")
                    st.markdown(f"**Cobertura:** {cobertura}")
                
                with col3:
                    # Mostrar APC se disponível
                    if 'APC (USD)' in row and pd.notna(row.get('APC (USD)')):
                        apc_usd = row.get('APC (USD)')
                        st.markdown(f"**APC:** ${apc_usd:,.2f} USD" if isinstance(apc_usd, (int, float)) else f"**APC:** {apc_usd}")
                    
                    # Mostrar área se disponível
                    if 'Área' in row and pd.notna(row.get('Área')):
                        st.markdown(f"**Área:** {row.get('Área')}")
                
                # Informações adicionais
                if 'URL' in row and pd.notna(row.get('URL')):
                    st.markdown(f"🔗 [Visitar site do periódico]({row.get('URL')})")
                
                # Avisos específicos por editora
                editora = str(row.get('Editora', ''))
                
                if 'Elsevier' in editora:
                    st.info("""
                    ℹ️ **Requisitos Elsevier:**
                    - Licença CC BY obrigatória
                    - ORCID registrado na Plataforma Sucupira
                    - Verificar elegibilidade em: https://agreements.journals.elsevier.com/capes
                    """)
                
                st.markdown("---")
    else:
        st.warning(f"⚠️ Nenhum periódico encontrado para '{journal_search}'")
        st.markdown("""
        **Dicas:**
        - Verifique a ortografia
        - Tente termos mais genéricos
        - Use apenas palavras-chave principais
        - Tente o ISSN do periódico
        """)

elif view_type == "Tabela Completa":
    st.info(f"📊 Mostrando {len(df_all):,} periódicos de {selected_publisher}")
    
    # Selecionar colunas principais para exibição
    display_cols = []
    for col in ['Título da Revista', 'ISSN', 'ISSN Online', 'Editora', 'Modelo', 'Cobertura APC']:
        if col in df_all.columns:
            display_cols.append(col)
    
    st.dataframe(
        df_all[display_cols] if display_cols else df_all,
        use_container_width=True,
        hide_index=True,
        height=600
    )

elif view_type == "Resumo Estatístico":
    st.markdown("### 📊 Estatísticas Gerais")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        total = len(df_all)
        st.metric("Total de Periódicos", f"{total:,}")
    
    with col2:
        if 'Editora' in df_all.columns:
            editoras = df_all['Editora'].nunique()
            st.metric("Editoras", editoras)
    
    with col3:
        if 'Cobertura APC' in df_all.columns:
            gratuitos = df_all[df_all['Cobertura APC'].astype(str).str.contains('100%', na=False)]
            st.metric("100% Gratuitos", f"{len(gratuitos):,}")
    
    # Distribuição por editora
    if 'Editora' in df_all.columns:
        st.markdown("#### Periódicos por Editora")
        dist = df_all['Editora'].value_counts().sort_values(ascending=False)
        for editora, count in dist.items():
            st.markdown(f"- **{editora}:** {count:,} periódicos")

# ==================== INFORMAÇÕES ADICIONAIS ====================
st.markdown("---")

st.markdown("### 📚 Informações Complementares")

# Exibir ÍNDICE
if 'INDICE' in publisher_data or 'ÍNDICE' in publisher_data:
    indice_key = 'INDICE' if 'INDICE' in publisher_data else 'ÍNDICE'
    with st.expander("📊 Resumo Geral - Índice de Periódicos", expanded=False):
        st.markdown("### Visão Geral dos Acordos CAPES (2026-2028)")
        st.dataframe(
            publisher_data[indice_key],
            use_container_width=True,
            hide_index=True
        )
        st.caption("💡 Este é um resumo consolidado de todos os acordos transformativos CAPES")
        st.caption("✅ Listas oficiais atualizadas em 13/02/2026")

# Exibir REQUISITOS
if 'REQUISITOS' in publisher_data:
    with st.expander("✅ Requisitos para Publicação Gratuita", expanded=False):
        st.markdown("### O que você precisa para publicar gratuitamente")
        st.dataframe(
            publisher_data['REQUISITOS'],
            use_container_width=True,
            hide_index=True
        )
        st.caption("⚠️ Verifique estes requisitos antes de submeter seu artigo")

# FAQ
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
    - ✅ Você é afiliado a uma instituição brasileira elegível
    - ✅ Sua instituição está nos acordos da editora específica
    - ✅ Você é o autor correspondente (corresponding author)
    
    **💡 Use a seção "PASSO 1: Verificar Instituição" no topo para confirmar!**
    
    ### 3. Por que preciso verificar minha instituição?
    
    Nem todas as instituições brasileiras estão em todos os acordos. Cada editora tem 
    sua própria lista de instituições elegíveis. Sua instituição pode estar em algumas 
    editoras, mas não em outras. Por isso é essencial verificar ANTES de escolher o periódico.
    
    ### 4. Como usar este sistema?
    
    **Passo a passo:**
    1. Use a seção "PASSO 1" para verificar se sua instituição é elegível
    2. Anote em quais editoras sua instituição está
    3. Use a seção "PASSO 2" para buscar periódicos nessas editoras
    4. Se encontrar o periódico em uma editora onde sua instituição é elegível → Você pode publicar grátis! 🎉
    
    ### 5. Quanto eu economizo?
    
    APCs típicos variam de:
    - **US$ 1.500 a US$ 3.000** em periódicos convencionais
    - **US$ 3.000 a US$ 11.000** em periódicos de alto impacto
    
    Com os acordos CAPES, você publica **totalmente grátis** em acesso aberto!
    
    **⚠️ EXCETO:** Wiley Gold oferece apenas 55% de desconto (você paga 45%)
    
    ### 6. O que é um periódico DIAMANTE?
    
    Periódicos DIAMANTE (como **ACS Central Science**) são totalmente gratuitos para TODOS, 
    independente de acordos. Eles não cobram APC de ninguém. São uma escolha premium!
    
    ### 7. Onde encontro mais informações?
    
    - **Portal CAPES:** https://www.periodicos.capes.gov.br
    - **Biblioteca da sua instituição:** Entre em contato para suporte
    - **Listas oficiais:** Use os links nas seções de cada editora
    """)

with st.expander("ℹ️ Sobre este Sistema"):
    st.markdown(f"""
    ### Objetivo
    
    Facilitar a busca de periódicos e verificação de instituições elegíveis nos acordos CAPES.
    
    ### Como funciona:
    
    **PASSO 1:** Verifica se sua instituição está nos acordos  
    **PASSO 2:** Busca periódicos nas editoras onde você é elegível  
    
    ### Última Atualização:
    
    **Data:** 13 de Fevereiro de 2026  
    **Fonte:** Listas oficiais das editoras (2025-2026)  
    **Total:** 5.863 periódicos validados  
    **Período:** Acordos 2026-2028  
    
    ### Desenvolvido por:
    
    **Grupo GOBIOTA** - Genômica, Bioinformática e Tecnologias Aplicadas  
    FMVZ/UFU
    
    ---
    *Versão 3.0.0 - Atualização Completa*
    """)

# ==================== AGÊNCIAS DE FOMENTO ====================

st.markdown("""
<div style="background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%); 
            padding: 1.5rem; 
            border-radius: 10px; 
            border-left: 4px solid #0284c7;
            margin: 2rem 0;">
    <p style="text-align: center; margin: 0; color: #0c4a6e; font-size: 0.95rem; line-height: 1.6;">
        <strong>🔬 Apoio à Pesquisa</strong><br><br>
        Esta iniciativa é fortalecida pelo apoio de agências de fomento à pesquisa no Brasil, 
        em especial <strong>CNPq</strong>, <strong>CAPES</strong> e <strong>FAPEMIG</strong>, 
        por meio de diferentes projetos e bolsas associados ao <strong>Grupo GOBIOTA – FMVZ/UFU</strong>.
    </p>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div style="background-color: #fef3c7; 
            padding: 1rem; 
            border-radius: 8px; 
            border-left: 4px solid #f59e0b;
            margin-bottom: 2rem;">
    <p style="margin: 0; color: #92400e; font-size: 0.85rem; text-align: center;">
        ⚠️ <strong>Disclaimer:</strong> As opiniões, hipóteses e conclusões ou recomendações 
        expressas neste site são de responsabilidade dos autores e não necessariamente 
        refletem a visão das agências de fomento.
    </p>
</div>
""", unsafe_allow_html=True)

# ==================== RODAPÉ LEGAL ====================

st.markdown("---")

# Proteção de Dados
st.warning("""
**⚠️ Proteção de Dados**

**📊 Os dados desta plataforma são protegidos por direitos autorais.**

**🚫 Proibido:**
- Download em massa dos dados
- Extração automatizada (web scraping)
- Reprodução não autorizada da base de dados
- Criação de cópias ou sistemas derivados

**✅ Permitido:**
- Consulta individual para fins de pesquisa acadêmica
- Busca de periódicos e instituições específicas
- Uso pessoal e não comercial

**⚖️ Importante:** Este sistema é apenas para consulta. A violação destes termos pode resultar em ações legais.
""")

# Aviso Legal e Direitos
st.info("""
**⚖️ Aviso Legal e Direitos**

**© Direitos Autorais**  
© 2026 Richard Costa Polveiro - Grupo GOBIOTA  
Todos os direitos sobre o código e interface são reservados.  
Licenciado sob [Licença MIT](https://github.com/ricmedveterinario/periodicos-capes-gratuito/blob/main/LICENSE).

**📊 Fonte dos Dados**  
Informações baseadas em documentos oficiais do [Portal CAPES](https://www.periodicos.capes.gov.br) e das editoras participantes.  
Listas oficiais atualizadas em **13/02/2026** (período 2026-2028).

**⚠️ Disclaimer**  
**Ferramenta independente sem vínculo oficial com CAPES ou editoras.**  
Desenvolvida para fins informativos e acadêmicos. Verifique sempre documentos oficiais antes de decisões.  
Direitos sobre dados e marcas pertencem aos respectivos titulares.

**🔒 Privacidade**  
Esta aplicação **não requer login**.  
O que você digita é usado apenas durante o uso e não é armazenado pelo aplicativo.  
A hospedagem pode registrar logs técnicos para segurança e diagnóstico.  
Usamos Google Analytics.
""")

# Rodapé com créditos
st.markdown("""
<div style="text-align: center; padding: 1.5rem; background-color: #f9fafb; border-radius: 10px; margin-top: 2rem;">
    <h4 style="margin: 0 0 0.5rem 0; color: #1e40af;">Grupo GOBIOTA</h4>
    <p style="margin: 0.25rem 0; font-size: 0.9rem; color: #4b5563;">
        Grupo de Pesquisa e Inovação em Microbiologia e Inteligência Biotecnológica
    </p>
    <p style="margin: 0.25rem 0; font-size: 0.85rem; color: #6b7280;">
        Faculdade de Medicina Veterinária e Zootecnia (FMVZ)<br>
        Universidade Federal de Uberlândia (UFU)
    </p>
    <hr style="margin: 1rem auto; width: 50%; border: none; border-top: 1px solid #e5e7eb;">
    <p style="margin: 0.5rem 0 0 0; font-size: 0.8rem; color: #9ca3af;">
        💰 Ajudando pesquisadores brasileiros a publicarem em acesso aberto
    </p>
    <p style="margin: 0.5rem 0 0 0; font-size: 0.75rem; color: #9ca3af;">
        Licenciado sob MIT License | Versão 3.0.0 | Fevereiro 2026
    </p>
</div>
""", unsafe_allow_html=True)
