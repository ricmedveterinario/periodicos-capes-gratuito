# Recomendação temática local

O motor modular combina normalização português–inglês, análise por regras do
manuscrito, recuperação textual e reordenação contextual. Não é um modelo de
linguagem treinado, não prevê aceite e não envia o texto a serviços externos.

O índice considera nomes, áreas, temas, palavras-chave e escopo quando disponível.
Campos da editora e do OpenAlex são combinados sem duplicar valores idênticos.
As frequências dos campos são ponderadas antes da saturação BM25; esta é uma
aproximação de BM25F, sem normalização independente por campo.

Expressões como deep learning recebem tratamento contextual. Doença e população
ajudam a distinguir o problema estudado de métodos auxiliares. Especialismos
explícitos incompatíveis são tratados por regras de domínio, sem lista de títulos
preferidos. Essas regras continuam sujeitas a falhas e não substituem a leitura
do escopo. Revistas multidisciplinares e temas raros podem ter metadados escassos.

Filtros CAPES são aplicados separadamente. Métricas de citação não aumentam a
pontuação. Evidência é uma heurística; cobertura temática é a fração ponderada
dos termos de consulta representados, incluindo expansões. Nenhuma é probabilidade.

O módulo semântico de coocorrências permanece desligado por padrão. Não há nova
dependência de produção. Índice reutilizado em cache; entradas limitadas a 500
caracteres de título, 1.000 de palavras-chave e 12.000 de resumo, até 30 resultados.

Validação local inclui testes de regressão, comparações com o catálogo real e
execução do formulário Streamlit. Comparações de títulos sugeridos não constituem
avaliação editorial independente nem comprovam superioridade universal.

Para retorno ao motor anterior, importe `LegacyJournalRecommender` de
`journal_recommender` no lugar de `JournalRecommender` e limpe o cache do aplicativo.
