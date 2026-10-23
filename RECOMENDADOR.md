# Recomendador temático de revistas

O formulário aceita título, resumo e palavras-chave e ordena revistas do catálogo
Publica Aberto por correspondência temática. O índice usa títulos e campos de área
disponíveis, expansão por vocabulário português–inglês e BM25 (k1=1.5, b=0.75).
Cada termo pesa 3 no título, 4 nas palavras-chave e 1 no resumo. Repetição no
manuscrito não aumenta esses pesos. A lista mostra os termos que contribuíram.

A seleção exata da instituição limita os grupos aos presentes em sua lista.
Springer e Nature são separados. O rótulo institucional Wiley inclui seus dois
grupos; o filtro padrão de cobertura integral exclui Wiley Gold, descontos,
cobertura pendente e títulos de assinatura sem publicação indicada.
Esses filtros são preliminares: não autorizam custeio e não substituem CAPES.

A pontuação não é porcentagem, probabilidade de aceite, prestígio ou qualidade.
Não há fator de impacto estimado. A falta de escopos completos e de artigos no
índice limita a recomendação, especialmente em títulos multidisciplinares e nos
grupos sem áreas estruturadas. Não encontrar uma revista não indica inelegibilidade.

O texto é processado no próprio servidor, sem chamada de API externa nem gravação
pelo recomendador. O formulário conserva valores na sessão Streamlit. O cache de
recursos contém apenas o índice do catálogo; consultas e manuscritos não são
armazenados no cache compartilhado. Nenhuma credencial ou planilha privada é
incluída nesta alteração, e não há novas dependências de produção.
