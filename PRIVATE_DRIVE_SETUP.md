# Ativar as planilhas privadas no Streamlit

As planilhas permanecem restritas. O servidor do aplicativo acessa somente
os dois arquivos configurados, em modo de leitura. As consultas no site
continuam públicas; os arquivos completos e a chave não entram no GitHub.

## Configuração do proprietário

1. No Google Cloud Console, selecione ou crie um projeto e ative a
   **Google Drive API**. São arquivos Excel armazenados no Drive, portanto
   o aplicativo usa download pela Drive API, sem exigir conversão para Sheets.
2. Em **IAM e administrador → Contas de serviço**, crie uma conta dedicada
   ao Publica Aberto. Não conceda papéis administrativos no projeto nem
   delegação de acesso a todo o domínio.
3. Na conta de serviço, abra **Chaves → Adicionar chave → Criar nova chave → JSON**.
   Guarde o arquivo somente no seu computador. Não envie a chave pelo chat
   nem a coloque no repositório.
4. No Drive, compartilhe apenas as duas planilhas v2 com o `client_email`
   dessa conta de serviço, como **Leitor**. Preserve o acesso geral como
   **Restrito**. Não compartilhe a pasta inteira.
5. No painel Streamlit do aplicativo, abra **Settings → Secrets** e crie
   a seção `[gcp_service_account]`, preenchida com os campos da chave JSON.
   Use o exemplo abaixo como estrutura. Para `private_key`, preserve as
   quebras de linha do campo original, usando aspas triplas.

```toml
[gcp_service_account]
type = "service_account"
project_id = "ID_DO_PROJETO"
private_key_id = "ID_DA_CHAVE"
private_key = """CONTEUDO_DO_CAMPO_PRIVATE_KEY_DA_CHAVE_JSON"""
client_email = "EMAIL_DA_CONTA_DE_SERVICO"
token_uri = "https://oauth2.googleapis.com/token"
```

6. Salve a configuração. Valide a revisão em uma implantação de teste
   usando o ramo da proposta antes de atualizar o aplicativo principal.
   O catálogo esperado tem 5.936 registros e o grupo Nature Portfolio tem
   41 títulos. A busca por UFU deve mostrar Springer e Nature separadamente.
7. Somente após confirmar o acesso e as buscas, integre a revisão ao ramo
   de produção. O botão Atualizar Dados permite conferir alterações
   posteriores nos mesmos arquivos do Drive.

Sem credenciais ou permissão de leitura, esta revisão informa que as bases
privadas estão indisponíveis. Não publica as planilhas nem amplia o acesso
automaticamente. O arquivo `.streamlit/secrets.toml` e os arquivos `.xlsx`
locais estão excluídos do Git pelo `.gitignore`.

Referências:
- https://developers.google.com/workspace/drive/api/guides/manage-downloads
- https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/secrets-management
- https://docs.cloud.google.com/iam/docs/service-accounts-create
