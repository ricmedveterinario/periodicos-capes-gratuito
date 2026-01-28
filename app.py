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
    
    /* ==================== OCULTAR FOOTER EM MODO EMBED ==================== */
    
    /* Ocultar footer "Built with Streamlit" e botão "Fullscreen" */
    .stApp > footer,
    footer[data-testid="stFooter"],
    [data-testid="stAppViewBlockContainer"] > footer,
    div[class*="stFooter"],
    footer {
        display: none !important;
        visibility: hidden !important;
        opacity: 0 !important;
        height: 0 !important;
    }
    
    /* Ocultar especificamente em modo embed */
    .embedded footer,
    iframe footer,
    [data-is-embedded="true"] footer {
        display: none !important;
    }
    
    /* Remover espaço onde footer ficaria */
    .main {
        padding-bottom: 0 !important;
    }
    
    /* Ocultar qualquer link do Streamlit no footer */
    footer a[href*="streamlit"],
    footer a[href*="Streamlit"] {
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
        if (window.location.hash) {
            scrollToSection(window.location.hash);
        }
    });
    
    // Observar mudanças no DOM
    setTimeout(function() {
        const targetNode = document.querySelector('.main');
        if (targetNode) {
            observer2.observe(targetNode, { childList: true, subtree: true });
        }
    }, 1000);
</script>
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
🎯 **Como funciona:** Este sistema tem DUAS funções essenciais:
1. **🏛️ Verificar se SUA INSTITUIÇÃO é elegível** (primeiro passo - faça isso abaixo!)
2. **📚 Buscar o PERIÓDICO** onde você quer publicar (segundo passo)

Se AMBOS estiverem listados → **Você pode publicar GRATUITAMENTE!** 🎉
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
        • É afiliado a uma instituição brasileira elegível nos acordos<br>
        • Sua instituição tem acesso ao Portal de Periódicos CAPES<br>
        • O periódico está listado nos acordos da editora<br>
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
        <strong>Coordenação:</strong> Prof. Dr. Richard Costa Polveiro
    </p>
    <p style="margin-bottom: 0; font-size: 0.9rem; color: #6b7280;">
        ℹ️ Dados extraídos dos acordos transformativos CAPES vigentes • Atualizado periodicamente<br>
        💡 Acesse a barra lateral para links de contato e recursos do GOBIOTA
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
            # CORREÇÃO: skiprows=1 para pular a primeira linha (metadados da aba)
            df = pd.read_excel(file_path, sheet_name=sheet_name, skiprows=1)
            df = df.dropna(how='all')
            df = df.reset_index(drop=True)
            data[publisher] = df
        except Exception as e:
            st.warning(f"Não foi possível carregar dados de {publisher}: {str(e)}")
    
    try:
        # CORREÇÃO: skiprows=1 também para ÍNDICE
        data['INDICE'] = pd.read_excel(file_path, sheet_name='📊 ÍNDICE', skiprows=1).dropna(how='all')
    except:
        data['INDICE'] = None
    
    try:
        # CORREÇÃO: skiprows=1 também para REQUISITOS
        data['REQUISITOS'] = pd.read_excel(file_path, sheet_name='✅ REQUISITOS', skiprows=1).dropna(how='all')
    except:
        data['REQUISITOS'] = None
    
    return data

# Carregar dados de instituições
@st.cache_data(ttl=3600)
def load_institutions_data():
    """Carrega dados de instituições elegíveis do Google Sheets"""
    
    # IDs do Google Sheets
    spreadsheet_id = "1O4EdZXxdiZDg9-GpSpV5FlaxwgLMWdctOrXMBA5z3es"
    sheet_id = "1086382440"  # gid da aba específica
    
    # URL de exportação CSV
    url = f"https://docs.google.com/spreadsheets/d/{spreadsheet_id}/export?format=csv&gid={sheet_id}"
    
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
    'Royal Society Publishing (RSP)': 'https://www.periodicos.capes.gov.br/images/documents/Acordo%20CAPES–Royal%20Society_%20Publicação%20em%20Acesso%20Aberto%20Sem%20Custos%20_%20Royal%20Society.pdf',
    'Wiley': 'https://www.wiley.com/en-br/publish/article/open-access/oa-agreement/',
    'IEEE': 'https://open.ieee.org/partners/capes-transformative-agreement/',
    'ACS': 'https://acsopenscience.org/customers/capes/'
}

# ==================== CARREGAR DADOS E CRIAR SIDEBAR ====================

# Carregar dados PRIMEIRO
try:
    publisher_data = load_data()
    publishers_list = [k for k in publisher_data.keys() if k not in ['INDICE', 'REQUISITOS']]
except Exception as e:
    st.error(f"❌ **Erro ao carregar os dados**\n\nDetalhes técnicos: {str(e)}")
    st.stop()

# ==================== SIDEBAR ====================

# Sidebar - Logo e informações GOBIOTA
try:
    st.sidebar.image("logo.png", use_column_width=True)
except:
    pass

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

# ==================== NAVEGAÇÃO RÁPIDA ====================
st.sidebar.header("🧭 Navegação Rápida")

st.sidebar.markdown("""
<div style="background-color: #f0f9ff; 
            padding: 0.8rem; 
            border-radius: 8px; 
            border-left: 4px solid #3b82f6;
            margin-bottom: 1rem;">
    <p style="margin: 0; color: #1e40af; font-size: 0.85rem; line-height: 1.5;">
        Use os links abaixo para navegar rapidamente entre as seções:
    </p>
</div>
""", unsafe_allow_html=True)

# Links de navegação usando markdown
st.sidebar.markdown("""
<style>
    .nav-button {
        display: block;
        background: linear-gradient(135deg, #10b981 0%, #059669 100%);
        color: white !important;
        padding: 0.75rem;
        text-align: center;
        text-decoration: none;
        border-radius: 8px;
        margin-bottom: 0.5rem;
        font-weight: bold;
        transition: transform 0.2s;
        cursor: pointer;
    }
    .nav-button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .nav-button-blue {
        background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
    }
</style>

<a href="#passo-1-instituicao" class="nav-button" onclick="scrollToElement('passo-1-instituicao'); return false;">
    🏛️ Verificar Instituição
</a>

<a href="#passo-2-periodico" class="nav-button nav-button-blue" onclick="scrollToElement('passo-2-periodico'); return false;">
    📚 Buscar Periódico
</a>

<script>
function scrollToElement(elementId) {
    // Tentar encontrar o elemento pelo ID
    const element = document.getElementById(elementId);
    if (element) {
        // Rolar suavemente até o elemento
        element.scrollIntoView({ 
            behavior: 'smooth', 
            block: 'start' 
        });
        
        // Atualizar URL sem recarregar página
        if (history.pushState) {
            history.pushState(null, null, '#' + elementId);
        }
    } else {
        // Se não encontrar, tentar novamente após delay (Streamlit pode estar renderizando)
        setTimeout(function() {
            const el = document.getElementById(elementId);
            if (el) {
                el.scrollIntoView({ 
                    behavior: 'smooth', 
                    block: 'start' 
                });
            }
        }, 500);
    }
}

// Verificar se há hash na URL ao carregar
window.addEventListener('load', function() {
    if (window.location.hash) {
        const targetId = window.location.hash.substring(1);
        setTimeout(function() {
            scrollToElement(targetId);
        }, 1000);
    }
});
</script>
""", unsafe_allow_html=True)

st.sidebar.markdown("---")

# Espaço para futuros links do GOBIOTA
st.sidebar.header("🔗 Links GOBIOTA")

st.sidebar.markdown("""
<style>
    .sidebar-link {
        display: block;
        padding: 0.5rem 0.75rem;
        margin-bottom: 0.25rem;
        border-radius: 6px;
        text-decoration: none;
        color: #374151;
        background-color: #f9fafb;
        border-left: 3px solid #3b82f6;
        transition: all 0.2s;
        font-size: 0.9rem;
    }
    .sidebar-link:hover {
        background-color: #eff6ff;
        transform: translateX(4px);
        color: #1e40af;
    }
    .sidebar-link-disabled {
        opacity: 0.5;
        cursor: not-allowed;
        border-left: 3px solid #9ca3af;
    }
    .sidebar-section-title {
        font-size: 0.75rem;
        font-weight: bold;
        color: #6b7280;
        text-transform: uppercase;
        margin: 1rem 0 0.5rem 0;
        letter-spacing: 0.05em;
    }
</style>

<div class="sidebar-section-title">📞 Contato</div>

<a href="mailto:gobiota2025@gmail.com" class="sidebar-link" target="_blank">
    📧 E-mail Institucional
</a>

<a href="mailto:richard.polveiro@ufu.br" class="sidebar-link" target="_blank">
    📧 E-mail Coordenação
</a>

<a href="https://instagram.com/gobiota2025" class="sidebar-link" target="_blank">
    📱 Instagram @gobiota2025
</a>

<div class="sidebar-section-title">🔬 Pesquisa</div>

<a href="http://dgp.cnpq.br/dgp/espelhogrupo/815660" class="sidebar-link" target="_blank">
    🔗 Grupo CNPq (DGP)
</a>

<div class="sidebar-section-title">🚀 Em Desenvolvimento</div>

<span class="sidebar-link sidebar-link-disabled">
    🔬 Sistemas de Análise
</span>

<span class="sidebar-link sidebar-link-disabled">
    📊 Banco de Dados
</span>

<span class="sidebar-link sidebar-link-disabled">
    📚 Publicações
</span>

<span class="sidebar-link sidebar-link-disabled">
    👥 Equipe
</span>
""", unsafe_allow_html=True)

# ==================== VALORES PADRÃO (anteriormente da sidebar) ====================
# Estes valores serão sobrescritos pelos campos do centro da página
institution_search = ""
institution_publisher_filter = []
selected_publisher = "Todas"
search_term = ""
view_option = "Paginada (Recomendado)"
rows_per_page = 25

# ==================== NOVA SEÇÃO: VERIFICAR INSTITUIÇÃO ====================

st.markdown("---")

# Âncora para navegação
st.markdown('<div id="passo-1-instituicao"></div>', unsafe_allow_html=True)

# CABEÇALHO GRANDE DO PASSO 1
st.markdown("""
<div style="background: linear-gradient(135deg, #10b981 0%, #059669 100%); 
            padding: 1.5rem; 
            border-radius: 10px; 
            margin-bottom: 1rem;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
    <h2 style="color: white; margin: 0; font-size: 1.8rem;">
        🏛️ PASSO 1: Verifique se sua Instituição é Elegível
    </h2>
    <p style="color: white; margin: 0.5rem 0 0 0; font-size: 1rem; opacity: 0.95;">
        Primeiro passo essencial: descubra em quais editoras você pode publicar gratuitamente
    </p>
</div>
""", unsafe_allow_html=True)

with st.expander("📋 Clique aqui para buscar sua instituição", expanded=True):
    st.markdown("""
    <div class="institution-card">
        <h3 style="margin-top: 0; color: #065f46;">✅ Por que verificar sua instituição?</h3>
        <p style="margin-bottom: 0.5rem;">
            <strong>Nem todas as instituições brasileiras estão nos acordos!</strong> Mesmo que o periódico esteja 
            listado, você só pode publicar gratuitamente se sua instituição estiver nos acordos específicos de cada editora.
        </p>
        <p style="margin-bottom: 0.5rem;">
            <strong>💡 O que isso significa?</strong><br>
            • Cada editora tem sua própria lista de instituições elegíveis<br>
            • Sua instituição pode estar em ALGUMAS editoras, mas não em todas<br>
            • Por exemplo: UFU está nas 7 editoras, mas algumas instituições estão em apenas 2 ou 3<br>
            • Você precisa verificar se está na editora do periódico que escolher
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="warning-box">
        <strong>⚠️ IMPORTANTE - Como funciona a busca:</strong><br>
        • Você pode buscar pelo <strong>NOME COMPLETO</strong> (ex: "Universidade Federal de Uberlândia")<br>
        • Ou pela <strong>SIGLA</strong> (ex: "UFU", "UNESP", "USP")<br>
        • Ou por <strong>PARTE DO NOME</strong> (ex: "Federal Uberlândia" encontra UFU)<br>
        • A busca funciona com ou sem acentos<br><br>
        <strong>💡 Dica:</strong> Se não encontrar pela sigla, tente pelo nome completo ou parte dele!
    </div>
    """, unsafe_allow_html=True)
    
    # Carregar dados
    df_inst = load_institutions_data()
    
    if df_inst is not None:
        # Detectar nomes de colunas
        colunas = df_inst.columns.tolist()
        
        # Verificar se tem as colunas necessárias
        col_editora = None
        col_nome = None
        col_sigla = None
        col_busca = None
        
        # Mapear colunas possíveis
        for col in colunas:
            col_lower = col.lower()
            if 'editora' in col_lower or 'publisher' in col_lower:
                col_editora = col
            elif 'nome' in col_lower and 'instituição' in col_lower:
                col_nome = col
            elif 'sigla' in col_lower or 'acronym' in col_lower:
                col_sigla = col
            elif 'busca' in col_lower or 'normalized' in col_lower:
                col_busca = col
        
        if not col_editora or not col_nome:
            st.error("❌ Estrutura da planilha não reconhecida. Verifique as colunas.")
            st.write("**Colunas encontradas:**", colunas)
        else:
            # Campo de busca - combinar com sidebar
            st.markdown("### 🔍 Buscar minha instituição:")
            
            col1, col2 = st.columns([3, 1])
            
            with col1:
                instituicao_busca = st.text_input(
                    "Digite o nome da sua instituição ou sigla:",
                    placeholder="Ex: UFU, Universidade Federal de Uberlândia, Federal Uberlândia...",
                    key="busca_instituicao",
                    help="Busque pelo nome completo, sigla ou parte do nome - funciona sem acentos."
                )
            
            with col2:
                st.markdown("<br>", unsafe_allow_html=True)
                if st.button("🔍 Buscar", type="primary", use_container_width=True):
                    pass  # Trigger de atualização
            
            # Filtro de editoras
            st.markdown("### 📚 Filtrar por editoras:")
            
            st.markdown("""
            <div class="info-box">
                <strong>💡 Por que filtrar por editoras?</strong><br>
                Cada editora tem acordos diferentes com instituições específicas. Filtre pelas editoras 
                onde você pretende publicar para ver se sua instituição está elegível especificamente nelas.
            </div>
            """, unsafe_allow_html=True)
            
            editoras_disponiveis = sorted(df_inst[col_editora].unique())
            
            # Checkboxes
            cols = st.columns(4)
            editoras_selecionadas = []
            
            for i, editora in enumerate(editoras_disponiveis):
                with cols[i % 4]:
                    checked = st.checkbox(
                        editora,
                        value=True,  # Todas marcadas por padrão
                        key=f"check_inst_ed_{i}"
                    )
                    if checked:
                        editoras_selecionadas.append(editora)
            
            # Realizar busca
            if not editoras_selecionadas:
                st.warning("⚠️ Selecione pelo menos uma editora")
            else:
                # Usar campo local apenas
                busca_ativa = instituicao_busca
                
                # Filtrar resultados
                if busca_ativa:
                    termo_norm = normalizar_busca(busca_ativa)
                    
                    # Buscar em todas as colunas relevantes
                    mask = pd.Series([False] * len(df_inst))
                    
                    if col_busca:
                        mask = mask | df_inst[col_busca].astype(str).str.contains(termo_norm, case=False, na=False)
                    if col_sigla:
                        mask = mask | df_inst[col_sigla].astype(str).str.upper().str.contains(termo_norm, na=False)
                    mask = mask | df_inst[col_nome].astype(str).str.upper().str.contains(termo_norm, na=False)
                    
                    resultados = df_inst[mask & df_inst[col_editora].isin(editoras_selecionadas)]
                else:
                    resultados = df_inst[df_inst[col_editora].isin(editoras_selecionadas)]
                
                # Mostrar resultados
                if busca_ativa:
                    st.markdown("---")
                
                if len(resultados) > 0:
                    editoras_encontradas = sorted(resultados[col_editora].unique())
                    
                    if busca_ativa:
                        st.success(f"✅ **Sua instituição é elegível em {len(editoras_encontradas)} editora(s)!**")
                        
                        st.markdown("""
                        <div class="info-box">
                            <strong>🎉 Ótima notícia!</strong> Sua instituição está nos acordos. Agora:<br>
                            1. ✅ Anote em quais editoras você pode publicar (veja abaixo)<br>
                            2. 📚 Role a página para baixo até "Lista de Periódicos Elegíveis"<br>
                            3. 🔍 Busque o periódico específico onde quer publicar<br>
                            4. ✅ Se o periódico estiver em uma editora onde sua instituição é elegível → <strong>Você pode publicar GRÁTIS!</strong>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # Cards de resumo
                        cols_resumo = st.columns(min(len(editoras_encontradas), 4))
                        for i, ed in enumerate(editoras_encontradas):
                            with cols_resumo[i % 4]:
                                st.metric(
                                    label=ed,
                                    value="Elegível",
                                    delta="✓"
                                )
                        
                        st.markdown("---")
                    
                    # Detalhes por editora
                    for editora in editoras_encontradas:
                        df_editora = resultados[resultados[col_editora] == editora]
                        
                        expandido = (len(editoras_encontradas) <= 2 and busca_ativa != "")
                        
                        with st.expander(
                            f"**{editora}** ({len(df_editora)} instituições)",
                            expanded=expandido
                        ):
                            # Link oficial
                            if editora in URLS_INSTITUICOES:
                                st.markdown(f"🔗 [Consultar lista oficial da {editora}]({URLS_INSTITUICOES[editora]})")
                            
                            # Preparar display
                            cols_display = []
                            if col_sigla:
                                cols_display.append(col_sigla)
                            cols_display.append(col_nome)
                            
                            df_display = df_editora[cols_display].copy()
                            df_display = df_display.sort_values(col_nome)
                            df_display = df_display.reset_index(drop=True)
                            
                            st.dataframe(
                                df_display,
                                use_container_width=True,
                                hide_index=True,
                                height=min(400, len(df_display) * 35 + 38)
                            )
                            
                            st.caption(f"📊 {len(df_editora)} instituições encontradas")
                else:
                    if busca_ativa:
                        st.warning("🔍 Nenhuma instituição encontrada com os critérios selecionados")
                        st.markdown("""
                        <div class="warning-box">
                            <strong>💡 Não encontrou sua instituição? Tente:</strong><br>
                            • <strong>Buscar pela sigla</strong> (ex: "UFU" em vez de nome completo)<br>
                            • <strong>Buscar por parte do nome</strong> (ex: "Federal Uberlândia" em vez de nome completo)<br>
                            • <strong>Verificar se digitou corretamente</strong> (a busca funciona sem acentos)<br>
                            • <strong>Verificar todas as editoras</strong> (marque todas os checkboxes)<br>
                            • <strong>Consultar as listas oficiais</strong> das editoras (links acima)<br><br>
                            <strong>⚠️ Sua instituição pode não estar nos acordos.</strong> Neste caso, você precisará 
                            pagar APCs ou buscar periódicos com outros modelos de acesso aberto.
                        </div>
                        """, unsafe_allow_html=True)
    else:
        st.error("❌ Não foi possível carregar os dados de instituições. Tente novamente mais tarde.")

st.markdown("---")

# Âncora para navegação
st.markdown('<div id="passo-2-periodico"></div>', unsafe_allow_html=True)

# ==================== CÓDIGO ORIGINAL DE PERIÓDICOS ====================

# CABEÇALHO GRANDE DO PASSO 2
st.markdown("""
<div style="background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%); 
            padding: 1.5rem; 
            border-radius: 10px; 
            margin-bottom: 1rem;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
    <h2 style="color: white; margin: 0; font-size: 1.8rem;">
        📚 PASSO 2: Buscar o Periódico
    </h2>
    <p style="color: white; margin: 0.5rem 0 0 0; font-size: 1rem; opacity: 0.95;">
        Agora busque o periódico específico onde deseja publicar
    </p>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class="info-box">
    <p style="margin-bottom: 0;">
        <strong>💡 Como funciona:</strong> Se o periódico estiver listado em uma editora onde sua instituição é elegível → 
        <strong>Você pode publicar GRATUITAMENTE!</strong>
    </p>
</div>
""", unsafe_allow_html=True)

# ==================== BUSCA INTERATIVA DE PERIÓDICOS ====================

with st.expander("📋 Clique aqui para buscar seu periódico", expanded=True):
    st.markdown("""
    <div class="info-box">
        <h3 style="margin-top: 0; color: #1e40af;">🔍 Busque o periódico onde deseja publicar</h3>
        <p style="margin-bottom: 0.5rem;">
            <strong>Como usar esta busca:</strong><br>
            • Digite o <strong>nome do periódico</strong> (completo ou parcial)<br>
            • Ou digite o <strong>ISSN</strong> (identificador único do periódico)<br>
            • Selecione a <strong>editora específica</strong> ou busque em todas<br>
            • A busca funciona em tempo real e ignora acentos
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("### 🔍 Buscar periódico:")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        periodico_busca = st.text_input(
            "Digite o nome do periódico ou ISSN:",
            placeholder="Ex: Nature, Science, Cell, 0036-8075...",
            key="busca_periodico_page",
            help="Busque pelo nome do periódico ou ISSN. A busca funciona com palavras parciais."
        )
    
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🔍 Buscar Periódico", type="primary", use_container_width=True, key="btn_buscar_periodico"):
            pass  # Trigger de atualização
    
    # Filtro de editoras
    st.markdown("### 📚 Filtrar por editora:")
    
    st.markdown("""
    <div class="warning-box">
        <strong>💡 Por que filtrar por editora?</strong><br>
        Se você já verificou sua instituição no PASSO 1 e sabe em quais editoras é elegível, 
        filtre apenas essas editoras para ver os periódicos disponíveis especificamente para você!
    </div>
    """, unsafe_allow_html=True)
    
    # Seleção de editora na página
    editora_selecionada_page = st.selectbox(
        "Escolha uma editora específica ou busque em todas:",
        ["Todas as Editoras"] + publishers_list,
        index=0,
        key="editora_select_page",
        help="Selecione a editora onde sua instituição é elegível (verificada no PASSO 1)"
    )
    
    st.markdown("---")
    
    # Usar busca da página
    busca_ativa_periodico = periodico_busca
    editora_ativa = editora_selecionada_page if editora_selecionada_page != "Todas as Editoras" else "Todas"
    
    # Mostrar resumo da busca
    if busca_ativa_periodico or editora_ativa != "Todas":
        st.markdown("""
        <div style="background-color: #dbeafe; 
                    padding: 1rem; 
                    border-radius: 8px; 
                    border-left: 4px solid #3b82f6;
                    margin-bottom: 1rem;">
            <p style="margin: 0; color: #1e40af;">
                <strong>🔍 Filtros ativos:</strong><br>
        """, unsafe_allow_html=True)
        
        if busca_ativa_periodico:
            st.markdown(f"**Busca:** {busca_ativa_periodico}", unsafe_allow_html=True)
        if editora_ativa != "Todas":
            st.markdown(f"**Editora:** {editora_ativa}", unsafe_allow_html=True)
        
        st.markdown("</p></div>", unsafe_allow_html=True)

st.markdown("---")

# Área principal
st.markdown("### 🔍 Resultados da Busca:")
st.markdown("""
<div style="background-color: #f0f9ff; 
            padding: 0.8rem; 
            border-radius: 8px; 
            border-left: 4px solid #3b82f6;
            margin-bottom: 1rem;">
    <p style="margin: 0; color: #1e40af; font-size: 0.95rem;">
        💡 <strong>Dica:</strong> Use as opções abaixo para personalizar a visualização dos resultados.
    </p>
</div>
""", unsafe_allow_html=True)

# ==================== OPÇÕES DE VISUALIZAÇÃO (MOVIDAS PARA O CENTRO) ====================
st.markdown("### ⚙️ Opções de Visualização")

col_viz1, col_viz2 = st.columns([2, 1])

with col_viz1:
    view_option = st.radio(
        "Escolha o modo de visualização:",
        ["Paginada (Recomendado)", "Tabela Completa", "Resumo Estatístico"],
        help="Escolha como deseja visualizar os dados",
        horizontal=True
    )

with col_viz2:
    if view_option == "Paginada (Recomendado)":
        rows_per_page = st.slider(
            "Linhas por página:",
            min_value=10,
            max_value=100,
            value=25,
            step=5,
            help="Número de periódicos exibidos por página"
        )
    else:
        rows_per_page = 25  # Valor padrão

st.markdown("---")
    
# Preparar dados - USAR BUSCA DA PÁGINA
search_term_final = busca_ativa_periodico if 'busca_ativa_periodico' in locals() else ""
selected_publisher_final = editora_ativa if 'editora_ativa' in locals() else "Todas"

if selected_publisher_final == "Todas" or selected_publisher_final == "Todas as Editoras":
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
    df_display = publisher_data[selected_publisher_final].copy()
    df_display.insert(0, 'Editora', selected_publisher_final)
    
# Filtrar - USAR BUSCA DA PÁGINA
if search_term_final:
    mask = pd.Series([False] * len(df_display))
    for col in df_display.select_dtypes(include=['object']).columns:
        mask = mask | df_display[col].astype(str).str.contains(search_term_final, case=False, na=False)
        
    df_filtered = df_display[mask]
else:
    df_filtered = df_display
    
total_rows = len(df_filtered)
    
if search_term_final:
    st.success(f"✅ Encontrados **{total_rows}** periódicos contendo '{search_term_final}'")
else:
    st.info(f"📊 Mostrando **{total_rows}** periódicos")
    
# Exibir
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
    
# ==================== INFORMAÇÕES ADICIONAIS ====================
st.markdown("---")

st.markdown("### 📚 Informações Complementares")

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
        
    ### 6. Onde encontro mais informações?
        
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
        
    ### Desenvolvido por:
        
    **Grupo GOBIOTA** - Genômica, Bioinformática e Tecnologias Aplicadas  
    FMVZ/UFU
        
    ---
    *Última atualização: {datetime.now().strftime('%d/%m/%Y')}*
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

# Aviso Legal e Direitos (usando st.info - componente nativo)
st.info("""
**⚖️ Aviso Legal e Direitos**

**© Direitos Autorais**  
© 2026 Richard Costa Polveiro - Grupo GOBIOTA  
Todos os direitos sobre o código e interface são reservados.  
Licenciado sob [Licença MIT](https://github.com/ricmedveterinario/periodicos-capes-gratuito/blob/main/LICENSE).

**📊 Fonte dos Dados**  
Informações baseadas em documentos oficiais do [Portal CAPES](https://www.periodicos.capes.gov.br) e das editoras participantes.

**⚠️ Disclaimer**  
**Ferramenta independente sem vínculo oficial com CAPES ou editoras.**  
Desenvolvida para fins informativos e acadêmicos. Verifique sempre documentos oficiais antes de decisões.  
Direitos sobre dados e marcas pertencem aos respectivos titulares.

**🔒 Privacidade**  
Esta aplicação **não coleta, armazena ou compartilha dados pessoais**.  
Não requer login, não usa cookies e não armazena histórico.
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
        Licenciado sob MIT License | Versão 2.2.1 | Janeiro 2026
    </p>
</div>
""", unsafe_allow_html=True)


