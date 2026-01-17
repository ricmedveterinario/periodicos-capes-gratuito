# 💰 Publique Gratuitamente - Acordos CAPES

Sistema web para descobrir se você pode **publicar gratuitamente** em periódicos científicos através dos acordos transformativos CAPES.

🔗 **Acesse:** https://publica-gratis-capes.streamlit.app

---

## 🎯 O que faz?

Ajuda pesquisadores brasileiros a economizar **US$ 1.500 a US$ 11.000** por artigo, verificando:

1. **🏛️ Se sua INSTITUIÇÃO é elegível** nos acordos CAPES
2. **📚 Se o PERIÓDICO está na lista** de cada editora

**Se AMBOS estiverem listados → Você pode publicar GRATUITAMENTE!** 🎉

---

## ✨ Funcionalidades

### 🏛️ Verificação de Instituições (NOVO!)

- Busque por **nome completo**, **sigla** ou **parte do nome**
- Veja em **quais editoras** sua instituição é elegível
- **2.222 instituições** catalogadas em **7 editoras**
- Busca inteligente (funciona sem acentos)
- Links diretos para listas oficiais

### 📚 Busca de Periódicos

- Mais de **8.600 periódicos** cobertos
- Busca por **nome** ou **ISSN**
- Filtros por **editora**
- Visualização **paginada**, **completa** ou **resumida**

---

## 📋 Como Usar (2 Passos)

### **PASSO 1:** Verificar Instituição

1. Acesse: https://publica-gratis-capes.streamlit.app
2. Expanda: **"🏛️ PASSO 1: Verifique se sua Instituição é Elegível"**
3. Digite sua instituição (nome ou sigla)
4. Anote em quais editoras você é elegível

**Por quê?** Nem todas as instituições estão em todas as editoras. Você precisa saber onde pode publicar ANTES de escolher o periódico.

### **PASSO 2:** Buscar Periódico

1. Role até: **"📚 PASSO 2: Buscar o Periódico"**
2. Selecione a editora (use uma onde você é elegível)
3. Busque pelo nome do periódico
4. **Encontrou?** → Você pode publicar grátis! 🎉

---

## 🎓 Editoras Cobertas

### Periódicos:
- 🟡 **Elsevier** - The Lancet, Cell, etc. (434 periódicos)
- 🟢 **Springer Nature** - Nature, BMC (435 periódicos)
- 🟡 **Wiley** - Diversas áreas (434 periódicos)
- 🟢 **ACM** - Computação (206 periódicos)
- 🔵 **IEEE** - Engenharia (162 periódicos)
- 💎 **ACS** - Química (291 periódicos)

### Instituições Elegíveis:
- **ACM:** 206 instituições (100% com sigla)
- **Elsevier:** 434 instituições (100% com sigla)
- **IEEE:** 162 instituições (100% com sigla)
- **Wiley:** 434 instituições (100% com sigla)
- **Springer Nature:** 435 instituições (99,5% com sigla)
- **ACS:** 291 instituições (97,6% com sigla)
- **Royal Society:** 260 instituições (95% com sigla)

**Total:** 2.222 instituições elegíveis

---

## 📊 Exemplos de Uso

### Exemplo 1: Pesquisador da UFU

1. **PASSO 1:** Busca "UFU"
   - ✅ Resultado: Elegível em **7 editoras**
   
2. **PASSO 2:** Quer publicar na "Nature Communications"
   - Busca o periódico
   - ✅ Encontrou na Springer Nature
   - ✅ UFU é elegível na Springer Nature
   - **Resultado:** Pode publicar GRÁTIS! 🎉

### Exemplo 2: Pesquisador de Instituição Pequena

1. **PASSO 1:** Busca sua instituição
   - ✅ Resultado: Elegível em **2 editoras** (ACM e IEEE)
   
2. **PASSO 2:** Quer publicar na "Cell"
   - Busca o periódico
   - ✅ Encontrou na Elsevier
   - ❌ Instituição NÃO é elegível na Elsevier
   - **Resultado:** Precisa pagar APC ou escolher outro periódico

---

## 🔍 Dicas de Busca

### Para Instituições:

✅ **Funciona:**
- Nome completo: "Universidade Federal de Uberlândia"
- Sigla: "UFU"
- Parte do nome: "Federal Uberlândia"
- Sem acentos: "Federal Uberlandia"

### Para Periódicos:

✅ **Funciona:**
- Nome completo: "Nature Communications"
- Parte do nome: "Nature"
- ISSN: "2041-1723"
- Áreas temáticas: "Cell Biology"

---

## 🛠️ Tecnologia

- **Frontend:** Streamlit
- **Backend:** Python + Pandas
- **Dados:** Google Sheets (atualizados em tempo real)
- **Hospedagem:** Streamlit Cloud (gratuito)
- **Performance:** Cache de 1 hora

---

## 💻 Rodar Localmente

```bash
# Clonar repositório
git clone https://github.com/ricmedveterinario/periodicos-capes-gratuito.git
cd periodicos-capes-gratuito

# Instalar dependências
pip install streamlit pandas openpyxl

# Executar
streamlit run app.py
```

Abre em: http://localhost:8501

---

## 📚 Desenvolvido por

**Grupo GOBIOTA**  
*Grupo de Pesquisa e Inovação em Microbiologia e Inteligência Biotecnológica*

**Instituição:** Faculdade de Medicina Veterinária e Zootecnia (FMVZ)  
Universidade Federal de Uberlândia (UFU)

**Coordenação:** Prof. Dr. Richard Costa Polveiro

📧 richard.polveiro@ufu.br  
📱 [@gobiota2025](https://instagram.com/gobiota2025)  
🔗 [CNPq - Espelho do Grupo](http://dgp.cnpq.br/dgp/espelhogrupo/5786031102053722)

---

## 🔄 Atualização de Dados

### Periódicos:
- Carregados do Google Drive
- Atualização automática a cada 1 hora
- Botão manual: "🔄 Atualizar Dados" na sidebar

### Instituições:
- Carregadas do Google Sheets
- Atualização em tempo real
- Siglas padronizadas (99% de cobertura)

---

## 📖 Estrutura do Projeto

```
periodicos-capes-gratuito/
├── app.py                      # Aplicação principal
├── logo.png                    # Logo GOBIOTA
├── requirements.txt            # Dependências Python
├── README.md                   # Este arquivo
├── dados/
│   ├── periódicos/            # Listas de periódicos por editora
│   └── instituições/          # Lista de instituições elegíveis
└── docs/
    ├── GUIA_USO.md            # Guia completo de uso
    ├── FAQ.md                 # Perguntas frequentes
    └── DEPLOYMENT.md          # Guia de deploy
```

---

## 🤝 Contribuir

Sugestões e contribuições são bem-vindas!

1. Fork este repositório
2. Crie uma branch (`git checkout -b feature/melhoria`)
3. Commit suas mudanças (`git commit -m 'Adiciona melhoria'`)
4. Push para a branch (`git push origin feature/melhoria`)
5. Abra um Pull Request

---

## ❓ Perguntas Frequentes

### Por que preciso verificar minha instituição?

Nem todas as instituições brasileiras estão em todos os acordos. Cada editora tem sua própria lista de instituições elegíveis.

### Minha instituição não aparece. E agora?

- Tente buscar por sigla em vez do nome completo
- Tente buscar por parte do nome
- Consulte as listas oficiais das editoras
- Entre em contato com a biblioteca da sua instituição

### Posso publicar em qualquer periódico?

Não. Você só pode publicar gratuitamente em periódicos que estão nos acordos E sua instituição é elegível naquela editora específica.

### Como submeter meu artigo?

1. Submeta normalmente pelo site do periódico
2. Selecione "Open Access" ou "Gold OA"
3. Informe sua afiliação brasileira
4. O sistema reconhece automaticamente o acordo CAPES
5. Não há cobrança de APCs!

---

## 📄 Licença

MIT License - veja [LICENSE](LICENSE) para detalhes.

**Ao usar este sistema:**
- Mantenha os créditos ao Grupo GOBIOTA e FMVZ/UFU
- Cite adequadamente em publicações acadêmicas
- Não redistribua os dados sem autorização

---

## 🎯 Como Citar

Se você utilizou este projeto em um artigo, TCC, dissertação, tese ou relatório, cite o **software** (este repositório). Sempre que possível, cite uma **versão (release)**. Se você não usou uma release, cite o **hash do commit**.

Repositório: https://github.com/ricmedveterinario/periodicos-capes-gratuito  
Aplicação (Streamlit): https://publica-gratis-capes.streamlit.app

### ABNT (NBR 6023:2018) — exemplo
GRUPO GOBIOTA. *Publique Gratuitamente – Acordos CAPES: sistema para verificar publicação sem APC via acordos transformativos*. Versão **vX.Y.Z**. Uberlândia: FMVZ/UFU, 2025. Disponível em: <https://github.com/ricmedveterinario/periodicos-capes-gratuito>. Acesso em: DD mmm. AAAA.

### APA 7 — exemplo
Grupo GOBIOTA. (2025). *Publique Gratuitamente – Acordos CAPES* (Version vX.Y.Z) [Software]. FMVZ/Universidade Federal de Uberlândia. https://github.com/ricmedveterinario/periodicos-capes-gratuito

### BibTeX (LaTeX/Overleaf) — recomendado
```bibtex
@software{gobiota_publica_gratis_capes_2025,
  author    = {Grupo GOBIOTA},
  title     = {Publique Gratuitamente -- Acordos CAPES},
  year      = {2025},
  version   = {vX.Y.Z},
  publisher = {FMVZ -- Universidade Federal de Uberl{\^a}ndia (UFU)},
  url       = {https://github.com/ricmedveterinario/periodicos-capes-gratuito},
  note      = {Acesso em: DD mmm AAAA. Se n{\~a}o houver release, informe o commit: <hash>.}
}
```

### Se você usou a aplicação online (opcional)
Inclua também, na metodologia, a referência do sistema acessado:
https://publica-gratis-capes.streamlit.app

### Fonte dos dados (quando aplicável)
Os resultados dependem das informações e acordos divulgados pelo Portal de Periódicos CAPES. Quando sua publicação exigir citar a fonte dos dados, cite também:
https://www.periodicos.capes.gov.br/

<details>
<summary><strong>Para facilitar a citação no GitHub: modelo de CITATION.cff</strong></summary>

Crie um arquivo <code>CITATION.cff</code> na raiz do repositório e ajuste <code>year</code> e <code>version</code>. Isso habilita o botão “Cite this repository”.

```yaml
cff-version: 1.2.0
message: "Se você usar este software em pesquisa acadêmica, cite-o conforme abaixo."
type: software
title: "Publique Gratuitamente – Acordos CAPES"
authors:
  - name: "Grupo GOBIOTA"
year: 2025
version: "vX.Y.Z"
url: "https://github.com/ricmedveterinario/periodicos-capes-gratuito"
publisher:
  name: "FMVZ – Universidade Federal de Uberlândia (UFU)"
```
</details>

---

## 📞 Suporte

**Tem dúvidas?**
- 📧 E-mail: richard.polveiro@ufu.br
- 📱 Instagram: [@gobiota2025](https://instagram.com/gobiota2025)
- 🐛 Issues: [GitHub Issues](https://github.com/ricmedveterinario/periodicos-capes-gratuito/issues)

---

## 🌟 Impacto

### Números:
- 🏛️ **2.222 instituições** catalogadas
- 📚 **8.600+ periódicos** cobertos
- 💰 **US$ 1.500-11.000** economizados por artigo
- 🎓 **7 editoras** com acordos ativos

### Ajudando pesquisadores brasileiros a:
- 💰 Economizar milhões em APCs
- 📖 Publicar em acesso aberto
- 🌍 Aumentar visibilidade de suas pesquisas
- 🇧🇷 Fortalecer a ciência brasileira

---

## 🆕 Novidades (Janeiro 2026)

### v2.0 - Verificação de Instituições
- ✨ **NOVO:** Busca de instituições elegíveis
- ✨ **NOVO:** Verificação por editora
- ✨ **NOVO:** 2.222 instituições catalogadas
- ✨ **NOVO:** Siglas padronizadas (99% cobertura)
- ✨ **NOVO:** Busca inteligente (funciona sem acentos)
- 🔄 **MELHORADO:** Interface com 2 passos claros
- 🔄 **MELHORADO:** Explicações e instruções
- 🔄 **MELHORADO:** Links para listas oficiais

### v1.0 - Versão Inicial
- Busca de periódicos por editora
- Sistema de paginação
- Filtros e visualizações
- 8.600+ periódicos cobertos

---

## 🔮 Roadmap

### Próximas Melhorias:
- [ ] Busca por área de conhecimento
- [ ] Comparação de periódicos
- [ ] Histórico de buscas
- [ ] Exportação de listas
- [ ] Notificações de novos acordos
- [ ] API para integração
- [ ] App mobile

---

**Desenvolvido com ❤️ pelo [Grupo GOBIOTA](http://dgp.cnpq.br/dgp/espelhogrupo/5786031102053722)**  
FMVZ - Universidade Federal de Uberlândia

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://publica-gratis-capes.streamlit.app)

---

**Última atualização:** Janeiro 2026  
**Versão:** 2.0 (Com verificação de instituições)
