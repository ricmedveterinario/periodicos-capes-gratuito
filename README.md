# 💰 Publique Gratuitamente - Acordos CAPES

Sistema web para descobrir se você pode **publicar gratuitamente** em periódicos científicos através dos acordos transformativos CAPES.

🔗 **Acesse:** https://publica-gratis-capes.streamlit.app

---

## 🎯 O que faz?

Ajuda pesquisadores brasileiros a economizar **US$ 1.500 a US$ 11.000** por artigo, verificando se podem publicar sem custos (sem APCs) através dos acordos CAPES.

### ✅ Você pode publicar gratuitamente se:

- É afiliado a uma instituição brasileira
- Instituição tem acesso ao Portal CAPES
- Periódico está nos acordos CAPES
- Você é o corresponding author

---

## 🎓 Editoras Cobertas

- 🟡 **Elsevier** - The Lancet, Cell, etc.
- 🟢 **Springer Nature** - Nature, BMC, Scientific Reports
- 🟡 **Wiley** - Diversas áreas científicas
- 🟢 **ACM** - Computação e tecnologia
- 🔵 **IEEE** - Engenharia e tecnologia
- 💎 **ACS** - Química e ciências relacionadas

**Total:** Mais de 8.000 periódicos cobertos

---

## 🚀 Como Usar

1. Acesse: https://publica-gratis-capes.streamlit.app
2. Selecione a editora do seu periódico
3. Busque pelo nome ou ISSN
4. **Encontrou?** → Você pode publicar grátis! 🎉

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

## 🛠️ Tecnologia

- **Frontend:** Streamlit
- **Dados:** Acordos transformativos CAPES (atualizados periodicamente)
- **Hospedagem:** Streamlit Cloud (gratuito)
- **Código:** Python + Pandas

---

## 📖 Documentação

- [Guia Rápido](INICIO_RAPIDO.md) - Como usar em 2 minutos
- [Guia Completo](GUIA_PUBLICACAO_GRATUITA.md) - Tudo sobre acordos transformativos
- [Deployment](GUIA_DEPLOYMENT.md) - Como fazer deploy próprio

---

## 💻 Rodar Localmente

```bash
# Clonar repositório
git clone https://github.com/ricmedveterinario/periodicos-capes-gratuito.git
cd periodicos-capes-gratuito

# Instalar dependências
pip install -r requirements.txt

# Executar
streamlit run app.py
```

Abre em: http://localhost:8501

---

## 🔄 Atualização de Dados

Os dados são carregados do Google Drive e atualizam automaticamente a cada 1 hora.

Para forçar atualização manual:
- Clique no botão "🔄 Atualizar Dados" na sidebar do app

---

## 🤝 Contribuir

Sugestões e contribuições são bem-vindas!

1. Fork este repositório
2. Crie uma branch (`git checkout -b feature/melhoria`)
3. Commit suas mudanças (`git commit -m 'Adiciona melhoria'`)
4. Push para a branch (`git push origin feature/melhoria`)
5. Abra um Pull Request

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

**Links de referência:**
- 📦 Repositório: https://github.com/ricmedveterinario/periodicos-capes-gratuito  
- 🌐 Aplicação (Streamlit): https://publica-gratis-capes.streamlit.app

---

### ABNT (NBR 6023:2018)

```
GRUPO GOBIOTA. Publique Gratuitamente – Acordos CAPES: sistema para 
verificar publicação sem APC via acordos transformativos. Versão vX.Y.Z. 
Uberlândia: FMVZ/UFU, 2026. Disponível em: 
https://github.com/ricmedveterinario/periodicos-capes-gratuito. 
Acesso em: DD mmm. AAAA.
```

**Notas:**
- Substitua `vX.Y.Z` pela versão utilizada (ex: v1.0.0)
- Se não há release, use: "Versão [hash do commit]"
- Substitua `DD mmm. AAAA` pela data de acesso (ex: 16 jan. 2026)

---

### APA 7

```
Grupo GOBIOTA. (2026). Publique Gratuitamente – Acordos CAPES 
(Version vX.Y.Z) [Software]. FMVZ, Universidade Federal de Uberlândia. 
https://github.com/ricmedveterinario/periodicos-capes-gratuito
```

**Notas:**
- Substitua `vX.Y.Z` pela versão (ex: v1.0.0)
- Se não há release: `(Commit abc1234)` no lugar de `(Version vX.Y.Z)`

---

### BibTeX (LaTeX/Overleaf) — Recomendado

```bibtex
@software{gobiota_publica_gratis_capes_2026,
  author    = {{Grupo GOBIOTA}},
  title     = {Publique Gratuitamente -- Acordos CAPES},
  year      = {2026},
  version   = {vX.Y.Z},
  publisher = {FMVZ -- Universidade Federal de Uberl{\^a}ndia (UFU)},
  url       = {https://github.com/ricmedveterinario/periodicos-capes-gratuito},
  note      = {Acesso em: DD mmm AAAA}
}
```

**Notas:**
- Substitua `vX.Y.Z` pela versão (ex: v1.0.0)
- Se não há release, adicione no `note`: "Commit: [hash]"
- No LaTeX, use: `\cite{gobiota_publica_gratis_capes_2026}`

---

### 💡 Dica: Use o botão "Cite this repository"

Este repositório possui um arquivo `CITATION.cff` que permite citar automaticamente:

1. Vá para: https://github.com/ricmedveterinario/periodicos-capes-gratuito
2. Clique no botão **"Cite this repository"** (lado direito)
3. Escolha o formato (APA, BibTeX, etc.)
4. Clique em **[Copy]**
5. Cole na sua referência!

**1 clique → citação pronta!** ✨

---

## 📞 Suporte

**Tem dúvidas?**
- 📧 E-mail: richard.polveiro@ufu.br
- 📱 Instagram: [@gobiota2025](https://instagram.com/gobiota2025)
- 🐛 Issues: [GitHub Issues](https://github.com/ricmedveterinario/periodicos-capes-gratuito/issues)

---

## 🌟 Impacto

Ajudando pesquisadores brasileiros a:
- 💰 Economizar milhões em APCs
- 📖 Publicar em acesso aberto
- 🌍 Aumentar visibilidade de suas pesquisas
- 🇧🇷 Fortalecer a ciência brasileira

---

**Desenvolvido com ❤️ pelo [Grupo GOBIOTA](http://dgp.cnpq.br/dgp/espelhogrupo/5786031102053722)**  
FMVZ - Universidade Federal de Uberlândia

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://publica-gratis-capes.streamlit.app)
