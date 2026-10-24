import streamlit as st
import pandas as pd
from datetime import datetime
import io
import unicodedata
import os
import base64
from pathlib import Path
from capes_catalog import load_catalog, search_catalog, acceptance_status, REVISION
from explorer_ui import render_explorer
from scholar_metrics import configure_snapshot

# Configuração da página
st.set_page_config(
    page_title="Publique Gratuitamente - Acordos CAPES",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="auto"
)

st.markdown('<style>' + (Path(__file__).parent / 'typography.css').read_text(encoding='utf-8') + '</style>', unsafe_allow_html=True)

# CSS customizado
st.markdown("""
<style>
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
    <div class="pa-eyebrow">GOBIOTA / UFU</div>
    <h1>Publica Aberto</h1>
    <p style="font-size: 1.1rem; margin-bottom: 0;">
        Sua pesquisa, a revista certa. Descubra oportunidades nos acordos CAPES.
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

# Excel privado: uma leitura de cada arquivo por período de cache.
@st.cache_data(ttl=3600)
def load_sources():
    local_dir = os.environ.get('PUBLICA_ABERTO_LOCAL_DATA_DIR')
    if local_dir:
        return load_catalog(data_dir=local_dir)
    try:
        account = dict(st.secrets['gcp_service_account'])
    except (KeyError, FileNotFoundError):
        from drive_workbooks import PrivateDriveConfigurationError
        raise PrivateDriveConfigurationError('O acesso privado às bases precisa ser configurado no servidor.') from None
    return load_catalog(service_account_info=account, drive_files=dict(st.secrets.get('private_workbooks', {})) or None)

def load_data():
    return load_sources()[0]

def load_institutions_data():
    return load_sources()[1]

@st.cache_data(ttl=3600, show_spinner=False)
def load_scholar_data():
    local_dir = os.environ.get('PUBLICA_ABERTO_LOCAL_DATA_DIR')
    if local_dir:
        import json
        return json.loads((Path(local_dir)/'scholar_metrics_pilot.json').read_text(encoding='utf-8'))
    from drive_workbooks import read_private_json
    return read_private_json(dict(st.secrets['gcp_service_account']),
                             '1WIcG_a4Iabh9wWzqBujHaex359mjyNlv')

# URLs oficiais das editoras
URLS_INSTITUICOES = {
    'Elsevier': 'https://view.highspot.com/viewer/c53fae46a21769209f110f21afcc6504#1',
    'Springer Nature': 'https://cms-resources.apps.public.k8s.springernature.io/springer-cms/rest/v1/content/27829128/data/v6',
    'Nature Portfolio': 'https://cms-resources.apps.public.k8s.springernature.io/springer-cms/rest/v1/content/52896924/data/v3',
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
    # Criar lista de editoras separando Wiley OnlineOpen e Wiley Gold
    publishers_list_raw = [k for k in publisher_data.keys() if k not in ['INDICE', 'REQUISITOS', 'AVISOS']]
    
    # Reordenar para melhor visualização
    publishers_list = []
    for pub in publishers_list_raw:
        if pub not in publishers_list:
            publishers_list.append(pub)
    
    # Adicionar opção combinada de Wiley
    # Inserir "Wiley (Todas)" após os Wiley individuais
    wiley_index = None
    for i, pub in enumerate(publishers_list):
        if 'Wiley' in pub:
            wiley_index = i
            break
    
    if wiley_index is not None:
        # Encontrar onde inserir "Wiley (Todas)"
        insert_pos = wiley_index
        for i in range(wiley_index, len(publishers_list)):
            if 'Wiley' in publishers_list[i]:
                insert_pos = i + 1
            else:
                break
        publishers_list.insert(insert_pos, 'Wiley (Todas)')

except Exception:
    st.error("Não foi possível carregar as bases privadas. A equipe responsável precisa conferir o acesso do aplicativo no Google Drive.")
    st.stop()

# ==================== SIDEBAR ====================

# Sidebar - Logo e informações GOBIOTA
try:
    logo_data = base64.b64encode((Path(__file__).resolve().parent / "logo.png").read_bytes()).decode('ascii')
    st.sidebar.markdown('<div class="pa-brand"><img src="data:image/png;base64,' + logo_data + '" alt="Logotipo GOBIOTA — Universidade Federal de Uberlândia"></div>', unsafe_allow_html=True)
except:
    pass

st.sidebar.markdown("""
<div style="text-align: center; margin-top: -10px; margin-bottom: 20px;">
    <p style="margin: 0; font-size: 0.875rem; color: #475569; line-height: 1.3;">
        <strong>G</strong>rupo de Pesquisa e Inovação em<br>
        <strong>O</strong>rganismos, <strong>Bio</strong>informática e<br>
        <strong>T</strong>ecnologias <strong>A</strong>plicadas
    </p>
    <p style="margin: 10px 0 0 0; font-size: 0.875rem; color: #475569;">
        PPGCVET • FMVZ • UFU
    </p>
</div>
""", unsafe_allow_html=True)

st.sidebar.markdown("---")

# Botão para forçar atualização
if st.sidebar.button("🔄 Atualizar Dados", help="Recarrega a versão de dados publicada no aplicativo"):
    st.cache_data.clear()
    st.rerun()

st.sidebar.caption('Bases v2.1 • Revisão de 24/10/2026 • Nature: 41 títulos incluídos' if st.secrets.get('private_workbooks') else 'Bases v2 • Revisão de 19/10/2026 • Nature: lista de setembro/2026')
st.sidebar.caption("Atualizar Dados consulta novamente a base de periódicos e instituições.")

st.sidebar.markdown("---")

st.sidebar.caption("Encontre sugestões pelo manuscrito ou consulte uma revista na navegação principal.")

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
        border-left: 3px solid #475569;
    }
    .sidebar-section-title {
        font-size: 0.875rem;
        font-weight: bold;
        color: #475569;
        text-transform: uppercase;
        margin: 1rem 0 0.5rem 0;
        letter-spacing: 0.05em;
    }
</style>

<div class="sidebar-section-title">📞 Contato GOBIOTA</div>

<a href="mailto:gobiota2025@gmail.com" class="sidebar-link" target="_blank">
    📧 gobiota2025@gmail.com
</a>

<a href="mailto:richard.polveiro@ufu.br" class="sidebar-link" target="_blank">
    📧 richard.polveiro@ufu.br
</a>

<a href="https://instagram.com/gobiota2025" class="sidebar-link" target="_blank">
    📱 @gobiota2025
</a>

<div class="sidebar-section-title">🏛️ Links Institucionais</div>

<a href="https://fmvz.ufu.br" class="sidebar-link" target="_blank">
    🎓 FMVZ/UFU
</a>

<a href="https://ppgcv.fmvz.ufu.br/" class="sidebar-link" target="_blank">
    📚 PPGCVET/UFU
</a>

<a href="http://dgp.cnpq.br/dgp/espelhogrupo/815660" class="sidebar-link" target="_blank">
    🔬 Grupo CNPq (DGP)
</a>

<div class="sidebar-section-title">📊 Recursos CAPES</div>

<a href="https://www.periodicos.capes.gov.br" class="sidebar-link" target="_blank">
    📖 Portal CAPES
</a>

<a href="https://www.periodicos.capes.gov.br/index.php/acessoaberto/acordos-transformativos.html" class="sidebar-link" target="_blank">
    📚 Lista de Editoras
</a>

""", unsafe_allow_html=True)

# Descoberta de revistas com dois níveis de complexidade.
try:
    configure_snapshot(load_scholar_data())
except Exception:
    configure_snapshot({'records':[], 'edition':2025, 'period':'2020–2024'})
    st.warning('Os indicadores Google Scholar estão temporariamente indisponíveis. As demais consultas continuam disponíveis.')
active_section = render_explorer(publisher_data, load_institutions_data())

if active_section == 'Entenda os índices':
    with st.expander('Sobre o projeto, acordos e condições de uso'):
        with st.expander("Como usar o Publica Aberto e equipe GOBIOTA", expanded=False):
            # Alerta informativo
            st.info("""
            🎯 **Como funciona:** Consulte os acordos e escolha o nível de busca:
            1. **🏛️ Verificar se SUA INSTITUIÇÃO é elegível** (primeiro passo - faça isso abaixo!)
            2. **📚 Buscar o PERIÓDICO** onde você quer publicar (segundo passo)
        
            Se ambos estiverem listados, confira também o modelo do periódico, a data de aceite e os requisitos do autor. O custeio depende de validação pela CAPES.
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
                    <strong>Verificação preliminar:</strong><br>
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
                    <strong>Programa de Pós-graduação:</strong> Programa de Pós-graduação em Ciências Veterinárias (PPGCVET)<br>
                    <strong>Universidade:</strong> Universidade Federal de Uberlândia (UFU)
                </p>
                <p style="margin-bottom: 0.5rem; font-size: 0.875rem; color: #4b5563;">
                    <strong>Coordenação:</strong> Prof. Dr. Richard Costa Polveiro
                </p>
                <p style="margin-bottom: 0; font-size: 0.9rem; color: #475569;">
                    ℹ️ Dados extraídos dos acordos transformativos CAPES vigentes • Atualizado periodicamente<br>
                    💡 Acesse a barra lateral para links de contato e recursos do GOBIOTA
                </p>
            </div>
            """, unsafe_allow_html=True)
        
        
        # ==================== INFORMAÇÕES ADICIONAIS ====================
        st.markdown("---")
        
        st.markdown("### 📚 Informações Complementares")
        
        # Exibir ÍNDICE
        if publisher_data.get('INDICE') is not None:
            with st.expander("📊 Resumo Geral - Índice de Periódicos", expanded=False):
                st.markdown("### Visão Geral dos Acordos CAPES")
                overview = publisher_data['INDICE'].copy()
                overview['Editora'] = overview['Editora'].astype(str).str.strip()
                overview['Ícone'] = '📚'
                st.dataframe(
                    overview,
                    width="stretch",
                    hide_index=True,
                    column_config={
                        'Ícone': st.column_config.TextColumn('Ícone', width='small'),
                        'Editora': st.column_config.TextColumn('Editora', width='medium'),
                    },
                )
                st.caption("💡 Este é um resumo consolidado de todos os acordos transformativos CAPES")
                st.caption("ℹ️ OA = OPEN ACCESS")
            
        # Exibir REQUISITOS
        if publisher_data.get('REQUISITOS') is not None:
            with st.expander("✅ Requisitos para Publicação Gratuita", expanded=False):
                st.markdown("### O que você precisa para publicar gratuitamente")
                st.dataframe(
                    publisher_data['REQUISITOS'],
                    width="stretch",
                    hide_index=True
                )
                st.caption("⚠️ Verifique estes requisitos antes de submeter seu artigo")
        
        # NOVO: Exibir AVISOS
        if publisher_data.get('AVISOS') is not None:
            with st.expander("⚠️ AVISOS IMPORTANTES - Leia antes de submeter!", expanded=False):
                st.markdown("### Avisos e Observações sobre os Acordos")
                st.dataframe(
                    publisher_data['AVISOS'],
                    width="stretch",
                    hide_index=True
                )
                st.caption("⚠️ Atenção especial para Elsevier e Wiley Gold!")
        
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
                
            **Condições preliminares para solicitar custeio:**
            - ✅ O periódico está listado neste sistema
            - ✅ Você é afiliado a uma instituição brasileira elegível
            - ✅ Sua instituição está nos acordos da editora específica
            - ✅ Você é o autor correspondente (corresponding author)
                
            **A busca não confirma o perfil do autor, a cobertura por título ou a autorização da CAPES.**
                
            ### 3. Por que preciso verificar minha instituição?
                
            Nem todas as instituições brasileiras estão em todos os acordos. Cada editora tem 
            sua própria lista de instituições elegíveis. Sua instituição pode estar em algumas 
            editoras, mas não em outras. Por isso é essencial verificar ANTES de escolher o periódico.
                
            ### 4. Como usar este sistema?
                
            **Passo a passo:**
            1. Use a seção "Busca avançada" para verificar se sua instituição é elegível
            2. Anote em quais editoras sua instituição está
            3. Use a seção "Busca simples" para buscar periódicos nessas editoras
            4. Se encontrar o periódico em uma editora onde sua instituição é elegível → Confira a cobertura e os requisitos antes de submeter.
                
            ### 5. Quanto eu economizo?
                
            APCs típicos variam de:
            - **US$ 1.500 a US$ 3.000** em periódicos convencionais
            - **US$ 3.000 a US$ 11.000** em periódicos de alto impacto
                
            O custeio de APC depende do acordo e da validação. Serviços editoriais adicionais podem gerar cobrança.
                
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
            PPGCVET/FMVZ/UFU
                
            ---
            *Revisão das bases: 19/10/2026. Outras listas editoriais permanecem em revisão.*
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
                por meio de diferentes projetos e bolsas associados ao <strong>Grupo GOBIOTA – PPGCVET/FMVZ/UFU</strong>.
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div style="background-color: #fef3c7; 
                    padding: 1rem; 
                    border-radius: 8px; 
                    border-left: 4px solid #f59e0b;
                    margin-bottom: 2rem;">
            <p style="margin: 0; color: #92400e; font-size: 0.875rem; text-align: center;">
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
            <p style="margin: 0.25rem 0; font-size: 0.875rem; color: #475569;">
                Programa de Pós-graduação em Ciências Veterinárias (PPGCVET)<br>
                Faculdade de Medicina Veterinária e Zootecnia (FMVZ)<br>
                Universidade Federal de Uberlândia (UFU)
            </p>
            <hr style="margin: 1rem auto; width: 50%; border: none; border-top: 1px solid #e5e7eb;">
            <p style="margin: 0.5rem 0 0 0; font-size: 0.875rem; color: #475569;">
                💰 Ajudando pesquisadores brasileiros a publicarem em acesso aberto
            </p>
            <p style="margin: 0.5rem 0 0 0; font-size: 0.875rem; color: #475569;">
                Licenciado sob MIT License | Versão 1.0 | Interface de 23/10/2026
            </p>
        </div>
        """, unsafe_allow_html=True)