# Otimização de carregamento — 19/10/2026

Base: Publica Aberto v0.8.0, commit original
83f469f591bc71ee8309de5f1ab981a062e78099.

## Alteração preparada

O carregamento dos periódicos chamava `pd.read_excel` com a mesma URL
11 vezes: oito editoras e três abas auxiliares. Cada chamada podia baixar
novamente a planilha inteira. Agora o aplicativo baixa uma vez, abre o
arquivo Excel uma vez e reutiliza a mesma pasta de trabalho para as abas.
A consulta de instituições também usa o carregador com espera de rede
limitada a 30 segundos. O cache existente de uma hora foi preservado.

Arquivos alterados/adicionados para implantação: `app.py` e
`workbook_loader.py`. A dependência openpyxl já estava declarada.

## Limite desta melhoria

A redução de downloads se aplica ao carregamento sem cache. O tempo real
em produção ainda precisa ser medido; não foi atribuída uma porcentagem
de ganho sem medição.

A hibernação após inatividade pertence à hospedagem Streamlit Community
Cloud. Esta mudança não elimina a tela de aplicativo dormindo. Para
disponibilidade contínua, avaliar hospedagem sem hibernação, custos e
configuração do domínio antes de migrar.

Documentação: https://docs.streamlit.io/deploy/streamlit-community-cloud/manage-your-app

## Verificação

`tests/test_workbook_loader.py` constrói uma planilha de teste com as onze abas
e verifica um único download, os dados das oito editoras, a remoção da
coluna duplicada Editora, os cabeçalhos auxiliares e a propagação de
falhas de conexão. Não consulta nem modifica as planilhas de produção.

As URLs de dados foram mantidas. A pasta do Drive indicada pelo usuário
ainda precisa ser conferida contra essas URLs.

Nenhuma publicação no GitHub ou no site foi feita nesta etapa.
