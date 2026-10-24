# Google Scholar Metrics: importação da coleta de 24/10/2026

O site usa um arquivo estático de métricas e não consulta o Google durante as visitas.

O snapshot de 226 registros fica restrito no Google Drive, lido pela conta de serviço já utilizada no aplicativo e armazenado no cache do servidor por até uma hora. O botão Atualizar Dados limpa esse cache. O GitHub recebe somente o código. Os indicadores são exibidos nos cartões públicos, mas o arquivo consolidado não é disponibilizado como download público.

Foram aceitos 226 registros da edição 2025, período 2020–2024: 218 marcados na entrega como consulta direta e 8 secundários. Os dados da entrega foram comparados aos lotes JSON válidos ou aos registros anteriormente conferidos. Esta validação interna não é uma nova conferência online de cada revista.

O importador lê apenas JSON do ZIP. Não extrai nem executa os programas recebidos. Exclui lotes inválidos, verifica números, edição, URL e identificador do periódico Google, conflitos e títulos. Três aliases conhecidos e sufixos de sigla ACM são aceitos explicitamente; títulos genéricos semelhantes não são associados. No site, o título e o ISSN do catálogo precisam coincidir com o registro importado.

Para preparar futuras atualizações, execute `import_scholar_collection.py` offline com o ZIP, `--output` apontando para uma cópia do snapshot e `--report` para o relatório. Rejeições interrompem a substituição. Revise o relatório e os aliases antes de publicar o snapshot.

O ZIP, a planilha completa, checkpoints, dados pendentes e programas do painel local não devem ser incluídos no repositório público. Apenas os fatos bibliométricos públicos aceitos e sua procedência são usados pelo site.

## Avaliação do coletor recebido

Pontos úteis: checkpoint, lotes brutos preservados, edição e fonte por registro, interrupção em CAPTCHA/429 e ausência numérica representada por vazio.

Melhorias recomendadas antes de executar novamente: persistir o bloqueio como trava no servidor, retomar por ISSN e identificador de revista em vez de posição da linha, salvar e confirmar cada resultado antes de avançar, separar “não consultado após interrupção” de “bloqueio observado nesta consulta” e tratar HTTP 403, redirecionamentos para `/sorry/` e ausência da estrutura esperada como falha, nunca como busca vazia. O código do motor recebido não foi executado nesta integração.

A data de captura ou importação não muda a edição da métrica. O h5 do Google Scholar não é o índice h do OpenAlex nem fator de impacto JCR.
