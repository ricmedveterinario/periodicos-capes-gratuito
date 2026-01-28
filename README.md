# 💰 Publique Gratuitamente - Acordos CAPES

Sistema web para descobrir se você pode **publicar gratuitamente** em periódicos científicos através dos acordos transformativos CAPES.

🔗 **Acesse:** https://publicaberto.gobiota.com.br/

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

1. Acesse: https://publicaberto.gobiota.com.br/
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
- **ACM:** 207 instituições (100% com sigla)
- **Elsevier:** 434 instituições (100% com sigla)
- **IEEE:** 162 instituições (100% com sigla)
- **Wiley:** 434 instituições (100% com sigla)
- **Springer Nature:** 435 instituições (100% com sigla)
- **ACS:** 291 instituições (100% com sigla)
- **Royal Society:** 260 instituições (100% com sigla)

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

## 📚 Desenvolvido por

**Grupo GOBIOTA**  
*Grupo de Pesquisa e Inovação em Microbiologia e Inteligência Biotecnológica*

**Instituição:** Faculdade de Medicina Veterinária e Zootecnia (FMVZ)  
Universidade Federal de Uberlândia (UFU)

**Coordenação:** Professores Dr.Richard Costa Polveiro & Dr.Flávio Tetsuo Sassaki & Dra.Roberta Torres de Melo

📧 richard.polveiro@ufu.br  
📧 gobiota2025@gmail.com
📱 [@gobiota2025](https://instagram.com/gobiota2025)  
🔗 [CNPq - Espelho do Grupo](http://dgp.cnpq.br/dgp/espelhogrupo/5786031102053722)

---

## 🔄 Atualização de Dados

### Periódicos e Instituições:
- Atualização automática a cada 1 hora se houver necessidade.
- Botão manual: "🔄 Atualizar Dados" na sidebar

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
- Mantenha os créditos ao Grupo GOBIOTA e FMVZ/UFU e PPGCVET/UFU
- Cite adequadamente em publicações acadêmicas
- Não redistribua os dados sem autorização

---

## 🎯 Como Citar

Se você utilizou este projeto em um artigo, TCC, dissertação, tese ou relatório, cite o **software** (este repositório). Sempre que possível, cite uma **versão (release)**. Se você não usou uma release, cite o **hash do commit**.

Repositório: https://github.com/ricmedveterinario/periodicos-capes-gratuito  
Aplicação (Streamlit): https://publicaberto.gobiota.com.br/

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
https://publicaberto.gobiota.com.br/

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
- 📧 E-mail: gobiota2025@gmail.com
- 📱 Instagram: [@gobiota2025](https://instagram.com/gobiota2025)
- 🐛 Issues: [GitHub Issues](https://github.com/ricmedveterinario/periodicos-capes-gratuito/issues)

---

## 🌟 Impacto

### Números:
- 🏛️ **2.223 instituições** catalogadas
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

### v2.7 - Verificação de Instituições
- ✨ **NOVO:** Busca de instituições elegíveis
- ✨ **NOVO:** Verificação por editora
- ✨ **NOVO:** 2.223 instituições catalogadas
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
- [ ] Histórico de buscas
- [ ] Notificações de novos acordos
- [ ] API para integração
- [ ] App mobile

---

## ⚖️ Licença e Direitos

### Licença do Código

Este projeto é licenciado sob os termos da **Licença MIT**. Consulte o arquivo [LICENSE](LICENSE) para mais detalhes.

### Direitos Autorais

**© 2026 Richard Costa Polveiro - Grupo GOBIOTA**

Todos os direitos sobre o código, interface e lógica desta aplicação são reservados ao autor e ao Grupo GOBIOTA - FMVZ/UFU.

### Fonte dos Dados

As informações sobre periódicos, instituições elegíveis e acordos transformativos são baseadas em:
- **Portal de Periódicos da CAPES** - Documentos e páginas oficiais
- **Editoras participantes** - Listas oficiais de periódicos e instituições
- **Acordos transformativos vigentes** - Informações públicas divulgadas pela CAPES

**Links oficiais:**
- CAPES: https://www.periodicos.capes.gov.br
- Elsevier: https://www.elsevier.com/open-access/agreements
- Springer Nature: https://www.springernature.com/gp/open-research/transformative-journals
- Wiley: https://www.wiley.com/en-br/publish/article/open-access/oa-agreement
- ACM: https://www.acm.org/publications/openaccess
- IEEE: https://open.ieee.org/partners/capes-transformative-agreement
- ACS: https://acsopenscience.org/customers/capes

---

## ⚠️ Aviso Legal e Disclaimer

### Natureza da Aplicação

Esta aplicação é uma **ferramenta independente** desenvolvida para fins **exclusivamente informativos e acadêmicos**. Organiza e apresenta informações públicas sobre acordos transformativos CAPES–editoras para facilitar a consulta por pesquisadores brasileiros.

### Ausência de Vínculo Oficial

**IMPORTANTE:** Esta ferramenta **NÃO possui vínculo oficial** com:
- Coordenação de Aperfeiçoamento de Pessoal de Nível Superior (CAPES)
- Editoras participantes dos acordos (Elsevier, Springer Nature, Wiley, ACM, IEEE, ACS, Royal Society)
- Periódicos científicos listados

### Limitações e Responsabilidades

- ⚠️ **Verificação obrigatória:** Sempre consulte os documentos oficiais da CAPES e das editoras antes de tomar decisões de submissão de artigos.
- ⚠️ **Dados atualizados:** Embora nos esforcemos para manter os dados atualizados, os acordos podem mudar sem aviso prévio. A data da última atualização está indicada no sistema.
- ⚠️ **Sem garantias:** Esta ferramenta é fornecida "como está", sem garantias de qualquer tipo. Não nos responsabilizamos por decisões tomadas com base nas informações aqui apresentadas.
- ⚠️ **Verifique elegibilidade:** A elegibilidade final para publicação gratuita depende de verificação junto à sua instituição e à editora do periódico.

### Direitos de Terceiros

Os direitos sobre:
- **Dados dos acordos:** Pertencem à CAPES e às editoras
- **Nomes e logotipos:** Pertencem aos respectivos titulares (CAPES, editoras, periódicos)
- **Marcas registradas:** Pertencem aos seus proprietários

Este projeto **não reivindica propriedade** sobre esses elementos, utilizando-os apenas de forma descritiva e informativa, conforme permitido para fins acadêmicos e de referência.

### Uso Acadêmico

Esta ferramenta foi desenvolvida como parte das atividades do **Grupo GOBIOTA** da **FMVZ/UFU** para apoiar a comunidade científica brasileira no acesso à publicação em acesso aberto.

**Citação recomendada:**
Se você utilizar esta ferramenta em seu trabalho acadêmico, considere citá-la conforme as orientações na seção [Como Citar](#-como-citar).

### Contato para Questões Legais

Para questões relacionadas a direitos autorais, licenciamento ou uso da aplicação:

📧 **E-mail:** gobiota2025@gmail.com
📧 **E-mail:** richard.polveiro@ufu.br  
🏛️ **Instituição:** FMVZ - Universidade Federal de Uberlândia  
🔗 **GitHub:** https://github.com/ricmedveterinario/periodicos-capes-gratuito

---

## 📝 Política de Privacidade

### Coleta de Dados

Esta aplicação **NÃO coleta, armazena ou compartilha** dados pessoais dos usuários:
- ✅ Não requer login ou cadastro
- ✅ Não utiliza cookies de rastreamento
- ✅ Não armazena histórico de buscas
- ✅ Não coleta informações identificáveis

### Dados de Uso

O **Streamlit Community Cloud** (plataforma de hospedagem) pode coletar estatísticas agregadas e anônimas de uso para fins de infraestrutura, conforme seus próprios [Termos de Serviço](https://streamlit.io/terms-of-use).

### Cache Local

A aplicação utiliza cache temporário (1 hora) para melhorar a performance, mas **nenhum dado pessoal** é armazenado.

---

## 🤝 Termos de Uso

Ao utilizar esta aplicação, você concorda que:

1. **Uso responsável:** Utilizará a ferramenta apenas para fins legítimos de consulta acadêmica e informativa
2. **Verificação oficial:** Consultará sempre as fontes oficiais (CAPES/editoras) antes de tomar decisões
3. **Sem redistribuição de dados:** Não copiará ou redistribuirá em massa os dados sem autorização
4. **Citação apropriada:** Citará adequadamente o sistema caso o utilize em trabalhos acadêmicos
5. **Respeito aos direitos:** Respeitará os direitos autorais e marcas de terceiros mencionados

### Modificações nos Termos

Reservamo-nos o direito de modificar estes termos a qualquer momento. As alterações entrarão em vigor imediatamente após publicação no repositório.

---

## 📚 Referências Legais e Normativas

### Legislação Aplicável

Este projeto está sujeito a:
- **Lei 9.610/98** (Lei de Direitos Autorais - Brasil)
- **Lei 9.279/96** (Lei de Propriedade Industrial - Brasil)
- **Marco Civil da Internet** (Lei 12.965/2014)
- **LGPD** (Lei 13.709/2018) - não aplicável, pois não há coleta de dados pessoais

### Acordos Transformativos CAPES

Para informações oficiais sobre os acordos:
- [Portal de Periódicos CAPES](https://www.periodicos.capes.gov.br)
- [Guias de Publicação em Acesso Aberto](https://www.periodicos.capes.gov.br/index.php/publicacoes-acesso-aberto.html)

---

**Desenvolvido com ❤️ pelo [Grupo GOBIOTA](http://dgp.cnpq.br/dgp/espelhogrupo/5786031102053722)**  
FMVZ - Universidade Federal de Uberlândia

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://publica-gratis-capes.streamlit.app)

---

**Última atualização:** Janeiro 2026  
**Versão:** 2.7 (Com verificação de instituições)


