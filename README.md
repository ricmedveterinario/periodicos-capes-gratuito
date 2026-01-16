# 📊 Publique Gratuitamente - Acordos Transformativos CAPES

Sistema web interativo para consulta de periódicos científicos com **publicação gratuita** através dos acordos transformativos CAPES.

## 🎯 Para que serve?

Este sistema ajuda pesquisadores brasileiros a descobrir se podem **publicar sem custos** (sem pagar APCs - Article Processing Charges) em periódicos científicos de alto impacto através dos acordos transformativos entre CAPES e grandes editoras.

**Economia típica:** US$ 1.500 a US$ 11.000 por artigo! 💰

## ✅ Você pode publicar gratuitamente se:

- É afiliado a uma instituição brasileira
- Sua instituição tem acesso ao Portal de Periódicos CAPES
- O periódico está listado neste sistema
- Você é o autor correspondente (corresponding author)

---

**Grupo GOBIOTA** - Genômica, Bioinformática e Tecnologias Aplicadas  
Programa de Pós-Graduação  
Faculdade de Medicina Veterinária e Zootecnia (FMVZ)  
Universidade Federal de Uberlândia (UFU)

---

## 🚀 Deploy no Streamlit Cloud (GRATUITO)

### Passo 1: Preparar o Repositório GitHub

1. Crie um repositório público no GitHub
2. Faça upload dos seguintes arquivos:
   - `app.py` (script principal)
   - `requirements.txt` (dependências)
   - `CAPES_6_ACORDOS_DINAMICO.xlsx` (arquivo de dados)
   - `README.md` (este arquivo)

**Estrutura do repositório:**
```
periódicos-capes/
├── app.py
├── requirements.txt
├── CAPES_6_ACORDOS_DINAMICO.xlsx
└── README.md
```

### Passo 2: Deploy no Streamlit Cloud

1. Acesse: https://streamlit.io/cloud
2. Faça login com sua conta GitHub
3. Clique em "New app"
4. Selecione:
   - **Repository:** seu-usuario/periódicos-capes
   - **Branch:** main
   - **Main file path:** app.py
5. Clique em "Deploy!"

**Pronto!** Seu app estará online em poucos minutos em:
`https://seu-usuario-periódicos-capes.streamlit.app`

### Passo 3: Personalizar URL (Opcional)

Você pode personalizar a URL nas configurações do app no Streamlit Cloud.

---

## 💻 Executar Localmente

### Requisitos

- Python 3.8 ou superior
- pip (gerenciador de pacotes Python)

### Instalação

1. Clone o repositório ou baixe os arquivos
2. Navegue até o diretório do projeto
3. Instale as dependências:

```bash
pip install -r requirements.txt
```

### Execução

```bash
streamlit run app.py
```

O app abrirá automaticamente no navegador em: `http://localhost:8501`

---

## 📁 Estrutura de Arquivos

### app.py
Script principal do Streamlit com:
- Interface interativa
- Sistema de busca e filtros
- Visualização de dados por editora
- Créditos e informações institucionais

### requirements.txt
Dependências do projeto:
- `streamlit`: Framework web
- `pandas`: Manipulação de dados
- `openpyxl`: Leitura de arquivos Excel

### CAPES_6_ACORDOS_DINAMICO.xlsx
Arquivo de dados consolidados contendo:
- Periódicos de 6 editoras principais
- Informações sobre acordos transformativos
- Dados organizados por editora

---

## 🎨 Recursos do Sistema

### ✅ Funcionalidades

- **Busca textual** em todos os campos
- **Filtros por editora** (Elsevier, Springer Nature, Wiley, ACM, IEEE, ACS)
- **Múltiplos modos de visualização** (Interativa, Completa, Estatística)
- **Paginação** de resultados
- **Estatísticas em tempo real**
- **Interface responsiva** (funciona em desktop e mobile)

### 📊 Editoras Disponíveis

1. **🟡 Elsevier** - Ampla cobertura em ciências
2. **🟢 Springer Nature** - Publicações de alto impacto
3. **🟡⚠️ Wiley** - Diversas áreas do conhecimento
4. **🟢 ACM** - Computação e tecnologia
5. **🔵 IEEE** - Engenharia e tecnologia
6. **💎 ACS** - Química e ciências relacionadas

---

## 🔒 Segurança e Privacidade

### Proteção de Dados

- ✅ Código executado no servidor (não no navegador do usuário)
- ✅ Dados não podem ser baixados diretamente pelos usuários
- ✅ Sem necessidade de API keys ou credenciais
- ✅ Acesso controlado pelo Streamlit Cloud

### Limitações de Download

O sistema **não permite** download direto dos dados completos. Usuários podem apenas:
- Visualizar dados na interface
- Fazer buscas e filtros
- Copiar texto selecionado manualmente (uma linha por vez)

---

## 🔄 Atualização de Dados

Para atualizar os dados do sistema:

1. Substitua o arquivo `CAPES_6_ACORDOS_DINAMICO.xlsx` no repositório
2. Faça commit das alterações no GitHub
3. O Streamlit Cloud detecta automaticamente e faz redeploy

**Nota:** O cache do Streamlit garante performance mesmo com arquivos grandes.

---

## 📝 Personalização

### Modificar Créditos

Edite a seção de créditos no arquivo `app.py`:

```python
st.markdown("""
<div class="credits">
    <h3>📚 Desenvolvido por:</h3>
    <p>
        <strong>Seu Nome/Grupo</strong><br>
        Sua Instituição
    </p>
</div>
""", unsafe_allow_html=True)
```

### Adicionar Logo

1. Adicione o arquivo de imagem ao repositório (ex: `logo.png`)
2. No `app.py`, adicione:

```python
st.sidebar.image("logo.png", use_column_width=True)
```

### Cores e Estilos

Modifique a seção CSS no `app.py` para personalizar:
- Cores do cabeçalho
- Estilo dos cards
- Fontes e espaçamentos

---

## 🆘 Suporte e Problemas

### Problemas Comuns

**Erro: "Cannot find file"**
- Verifique se o arquivo Excel está no mesmo diretório que app.py
- Confirme que o nome do arquivo está correto: `CAPES_6_ACORDOS_DINAMICO.xlsx`

**App não carrega dados**
- Verifique se todas as dependências estão instaladas
- Confirme que o arquivo Excel não está corrompido
- Veja os logs no Streamlit Cloud para detalhes do erro

**Performance lenta**
- O cache do Streamlit deve resolver isso automaticamente
- Se persistir, considere otimizar o tamanho do arquivo Excel

### Contato

Para questões ou sugestões:
- Abra uma issue no repositório GitHub
- Entre em contato com o Grupo GOBIOTA - FMVZ/UFU

---

## 📄 Licença

Este sistema foi desenvolvido para uso acadêmico e educacional pelo Grupo GOBIOTA.

**Uso permitido:**
- Consulta acadêmica
- Fins educacionais
- Pesquisa científica

**Ao usar este sistema, por favor:**
- Mantenha os créditos ao Grupo GOBIOTA e FMVZ/UFU
- Cite adequadamente se usar em publicações
- Não redistribua os dados sem autorização

---

## 🎓 Como Citar

Se você usar este sistema em trabalhos acadêmicos, utilize:

```
Grupo GOBIOTA. (2025). Sistema de Consulta de Periódicos CAPES - 
Acordos Transformativos. Faculdade de Medicina Veterinária e Zootecnia, 
Universidade Federal de Uberlândia. 
Disponível em: [URL do seu app]
```

---

## 🚀 Próximos Passos

Após o deploy:

1. ✅ Teste todas as funcionalidades
2. ✅ Compartilhe o link com colegas
3. ✅ Monitore estatísticas de uso no Streamlit Cloud
4. ✅ Colete feedback para melhorias
5. ✅ Atualize dados periodicamente

---

**Desenvolvido com ❤️ pelo Grupo GOBIOTA**  
*FMVZ - Universidade Federal de Uberlândia*
