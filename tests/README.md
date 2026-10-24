# Testes automáticos

Esta pasta reúne as verificações das bases CAPES, buscas, recomendações, links, métricas e leitura privada do Drive.

Na raiz do repositório, execute:

```shell
python -m unittest discover -s tests -t . -v
```

Os testes usam exemplos locais e simulações de autenticação. Não precisam das credenciais do Google Drive e não fazem a coleta de indicadores no Google Scholar.
