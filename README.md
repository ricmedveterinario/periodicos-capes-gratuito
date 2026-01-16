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

```bibtex
@misc{gobiota2025acordoscapes,
  author = {Grupo GOBIOTA},
  title = {Sistema de Consulta de Periódicos CAPES - Acordos Transformativos},
  year = {2025},
  publisher = {FMVZ - Universidade Federal de Uberlândia},
  url = {https://publica-gratis-capes.streamlit.app}
}
```

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
