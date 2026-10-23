# Métricas abertas e exploração de revistas

A busca simples permite pesquisar nome, ISSN, área e editora e ordenar por título,
média de citações em dois anos ou índice h. A busca avançada combina instituição,
cobertura registrada, presença e mínimo de métrica e data de aceite, ou abre o
recomendador por manuscrito. O cabeçalho e a identidade GOBIOTA são preservados.

## Dados e correspondência

`data/openalex_metrics.json.gz.b64` contém apenas metadados públicos obtidos diretamente
da API OpenAlex Sources, sob CC0, em 23/10/2026. Não contém as planilhas restritas,
listas institucionais, credenciais, manuscritos ou condições APC copiadas do Drive.
Foram obtidos 5.913 registros públicos de revistas, com 80 consultas em lote e
nenhum lote com falha. O número de correspondências no catálogo pode diferir por
duplicidades, grupos de acordo e ISSNs ausentes ou ambíguos.

As métricas são associadas somente por ISSN exato. Não há correspondência por
semelhança de título. Um ISSN associado a mais de uma fonte não recebe métrica.
Revistas sem métrica permanecem na lista com travessão; zero continua sendo zero.
Links usam a URL existente da revista ou a homepage do mesmo registro OpenAlex.
O gráfico deduplica ISSNs e apresenta somente valores disponíveis.

## Interpretação

- `summary_stats.2yr_mean_citedness`: média de citações em dois anos do OpenAlex.
- `summary_stats.h_index`: índice h da fonte no OpenAlex.
- Área: campo do tópico predominante de cada fonte no OpenAlex, traduzido para
  português quando disponível. Não representa classificação oficial de escopo.
- A data mostrada é a data de consulta; não é um ano JCR nem uma edição de JIF.

Essas medidas **não são Journal Impact Factor (JIF/JCR), CiteScore ou quartis**.
Não há Q1–Q4 inferidos. A média não é normalizada entre áreas, portanto diferenças
entre disciplinas não implicam qualidade editorial ou probabilidade de aceite.
A origem estatística não substitui a lista de títulos e instituições do acordo CAPES.

O gráfico usa valores locais e links próprios por ISSN, sem chamadas externas
durante o carregamento. Atualizar Dados relê as planilhas privadas, mas não
atualiza automaticamente a fotografia de métricas: é necessária nova coleta.
O arquivo comprimido e codificado em base64 é lido localmente para reduzir tamanho
de transferência sem depender da API durante o uso do site.

## Fontes

- https://help.openalex.org/data/sources/attributes/
- https://help.openalex.org/api/
- https://explore.openalex.org/about

O cliente https://github.com/clarivate/wosjournals-javascript-client poderá ser
avaliado separadamente se houver aprovação de API e condições de exibição dos
dados Clarivate. A licença do código não concede acesso ou licença dos dados JCR.
