import streamlit as st
import pandas as pd
from datetime import datetime
import io

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
🎯 **Como funcionar:** Pesquise o periódico desejado abaixo. Se ele estiver listado, **você pode publicar gratuitamente** 
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
        <strong>Grupo GOBIOTA</strong> - Genômica, Bioinformática e Tecnologias Aplicadas<br>
        <strong>Programa de Pós-Graduação</strong><br>
        Faculdade de Medicina Veterinária e Zootecnia (FMVZ)<br>
        Universidade Federal de Uberlândia (UFU)
    </p>
    <p style="margin-bottom: 0; font-size: 0.9rem; color: #6b7280;">
        ℹ️ Dados extraídos dos acordos transformativos CAPES vigentes • Atualizado periodicamente
    </p>
</div>
""", unsafe_allow_html=True)

# Carregar dados
@st.cache_data
def load_data():
    """Carrega os dados do arquivo Excel"""
    file_path = 'https://drive.google.com/uc?export=download&id=1iOxbUE2vwWrtzIIgeydGdpYueoHnMVHY'
    
    # Carregar todas as abas
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
            # Remover linhas completamente vazias
            df = df.dropna(how='all')
            # Resetar índice
            df = df.reset_index(drop=True)
            data[publisher] = df
        except Exception as e:
            st.warning(f"Não foi possível carregar dados de {publisher}: {str(e)}")
    
    return data

# Carregar dados
try:
    publisher_data = load_data()
    
    # Sidebar - Seleção de editora
    st.sidebar.header("🔍 Filtros de Busca")
    
    selected_publisher = st.sidebar.selectbox(
        "Selecione a Editora:",
        options=list(publisher_data.keys()),
        index=0
    )
    
    # Obter dados da editora selecionada
    df = publisher_data[selected_publisher]
    
    # Estatísticas gerais
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 📈 Estatísticas Gerais")
    
    total_journals = 0
    for publisher, data in publisher_data.items():
        count = len(data)
        total_journals += count
        st.sidebar.metric(publisher, f"{count:,}")
    
    st.sidebar.markdown(f"**Total:** {total_journals:,} periódicos")
    
    # Área principal - Dados da editora selecionada
    st.header(f"📖 {selected_publisher}")
    
    # Métricas da editora
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <h3 style="margin: 0; color: #1e40af;">{len(df):,}</h3>
            <p style="margin: 0; color: #6b7280;">Total de Periódicos</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <h3 style="margin: 0; color: #1e40af;">{len(df.columns)}</h3>
            <p style="margin: 0; color: #6b7280;">Campos de Dados</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <h3 style="margin: 0; color: #1e40af;">{selected_publisher}</h3>
            <p style="margin: 0; color: #6b7280;">Editora Selecionada</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Filtro de busca textual
    st.markdown("### 🔍 Busque seu periódico")
    st.markdown("Digite o nome do periódico, ISSN ou editor para verificar se você pode publicar gratuitamente:")
    
    search_term = st.text_input(
        "Buscar periódico:",
        placeholder="Ex: Nature, Science, 1234-5678, etc.",
        label_visibility="collapsed"
    )
    
    # Aplicar filtro se houver termo de busca
    if search_term:
        # Criar máscara de busca em todas as colunas
        mask = df.astype(str).apply(
            lambda x: x.str.contains(search_term, case=False, na=False)
        ).any(axis=1)
        df_filtered = df[mask]
        
        if len(df_filtered) > 0:
            st.success(f"""
            ✅ **ÓTIMA NOTÍCIA!** Encontrados **{len(df_filtered)} periódico(s)** para '{search_term}'
            
            🎉 Você pode publicar **GRATUITAMENTE** (sem pagar APCs) se for o corresponding author 
            afiliado a uma instituição brasileira com acesso ao Portal CAPES!
            """)
        else:
            st.warning(f"""
            ⚠️ Nenhum periódico encontrado para '{search_term}' nesta editora.
            
            **Tente:**
            - Verificar a ortografia
            - Buscar por ISSN
            - Selecionar outra editora na barra lateral
            - Procurar variações do nome (com/sem 'The', 'Journal of', etc.)
            """)
    else:
        df_filtered = df
    
    # Opções de visualização
    st.subheader("📋 Dados dos Periódicos")
    
    view_option = st.radio(
        "Modo de visualização:",
        ["Tabela Interativa", "Tabela Completa", "Resumo Estatístico"],
        horizontal=True
    )
    
    if view_option == "Tabela Interativa":
        # Mostrar número de linhas por página
        rows_per_page = st.slider(
            "Linhas por página:",
            min_value=10,
            max_value=100,
            value=25,
            step=5
        )
        
        # Paginação
        total_rows = len(df_filtered)
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
        
        Se sua instituição tem acesso ao Portal CAPES, você está elegível!
        
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
    
    # Rodapé atualizado
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
            📧 Dúvidas ou sugestões? Entre em contato através da sua biblioteca institucional
        </p>
    </div>
    """, unsafe_allow_html=True)

except Exception as e:
    st.error(f"""
    ❌ **Erro ao carregar os dados**
    
    Certifique-se de que o arquivo 'CAPES_6_ACORDOS_DINAMICO.xlsx' está no mesmo 
    diretório do script app.py
    
    Detalhes técnicos: {str(e)}
    """)
    st.info("""
    ### 📝 Instruções de uso:
    
    1. Coloque o arquivo Excel no mesmo diretório do app.py
    2. Renomeie o arquivo para: `CAPES_6_ACORDOS_DINAMICO.xlsx`
    3. Execute: `streamlit run app.py`
    """)
