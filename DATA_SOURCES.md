# Bases do Publica Aberto — revisão de 19/10/2026

Esta revisão lê as duas planilhas privadas pelo Google Drive API, com uma
conta de serviço configurada somente nos Secrets do Streamlit. Nenhuma
planilha Excel é publicada no repositório. Cada arquivo é baixado uma
vez por carregamento sem cache. O cache conserva os dados por uma hora;
o botão Atualizar Dados força a releitura dos arquivos do Drive.

A implantação depende da configuração descrita em PRIVATE_DRIVE_SETUP.md.
Não ativar esta revisão em produção antes de validar o acesso privado.

## Arquivos

- No Drive, `PUBLICA_ABERTO_CAPES_2026_2028_SITE_12_02_2026_v2.xlsx`: oito abas com
  5.895 registros e as abas auxiliares existentes. Contagens e requisitos
  foram corrigidos, ISSNs numéricos válidos da Wiley foram formatados,
  e situações Springer sem publicação ou pendentes foram identificadas.
- No Drive, `instituicoes_elegiveis_FINAL_v2.xlsx`: base anterior de instituições,
  preservada. A camada de consulta substitui apenas o grupo Springer
  pela lista oficial e acrescenta Nature como grupo independente.
- No repositório, `data/nature_2026.json`: dados obtidos diretamente das
  fontes públicas da Springer Nature, com 41 títulos híbridos Nature e listas de
  435 instituições Springer e 299 Nature. A pesquisa apresenta 5.936
  registros de periódicos no total. Esses números não representam
  aprovação individual de custeio.

Os arquivos v2 enviados pelo proprietário ao Drive foram identificados
pelos IDs abaixo. Na implantação desta revisão, ambos estavam restritos
ao proprietário. Não houve alteração de conteúdo ou compartilhamento:

- Periódicos: `1PysXi6_kp7TL4fXmw8jlZe5aFjRrWsSo`
- Instituições: `1zgE4_LshjeP75SqGzckP9bV36p_M_SS_`

## Escopo e limitações

Springer e Nature usam listas institucionais separadas. A conferência da
data informa somente se o aceite está no período do respectivo acordo.
O aplicativo não verifica o perfil pessoal do autor nem substitui a
validação pela CAPES. As listas das demais editoras foram preservadas
da versão anterior e estão identificadas para confirmação na editora.

Os 13 registros Springer não híbridos assinalados Publish na planilha
oficial continuam pendentes de confirmação por divergência de escopo.
Os 38 registros sem indicação de publicação não são rotulados como APC
integral. Scientific Reports e Nature Communications não foram inseridos
na lista Nature, pois não constam na lista específica consultada.

## Fontes oficiais

- [Lista Springer](https://cms-resources.apps.public.k8s.springernature.io/springer-cms/rest/v1/content/27829124/data/v5)
- [Lista Nature, setembro/2026](https://cms-resources.apps.public.k8s.springernature.io/springer-cms/rest/v1/content/52896256/data/v7)
- [Instituições Springer](https://cms-resources.apps.public.k8s.springernature.io/springer-cms/rest/v1/content/27829128/data/v6)
- [Instituições Nature](https://cms-resources.apps.public.k8s.springernature.io/springer-cms/rest/v1/content/52896924/data/v3)
- [Acordo e períodos de aceite](https://www.springernature.com/br/open-science/oa-agreements/brazil/capes)
- [Orientação CAPES e Portaria 224/2026](https://www.gov.br/capes/pt-br/acesso-a-informacao/acoes-e-programas/carta-de-servicos-ao-usuario/obter-acesso-ao-portal-de-periodicos-da-capes)

Esta revisão não altera a política de hibernação do Streamlit Community Cloud.
