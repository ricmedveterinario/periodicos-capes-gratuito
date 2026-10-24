"""Read restricted XLSX files using server-side Google service credentials."""
from io import BytesIO


class PrivateDriveConfigurationError(RuntimeError):
    pass


def read_private_json(service_account_info, file_id):
    """Read a single explicitly configured JSON file without exposing credentials."""
    if not service_account_info:
        raise PrivateDriveConfigurationError('Configure o acesso privado às métricas no servidor.')
    from google.oauth2.service_account import Credentials
    from google.auth.transport.requests import AuthorizedSession
    credentials = Credentials.from_service_account_info(
        dict(service_account_info), scopes=['https://www.googleapis.com/auth/drive.readonly'])
    with AuthorizedSession(credentials) as session:
        response = session.get(f'https://www.googleapis.com/drive/v3/files/{file_id}',
                               params={'alt': 'media'}, timeout=30)
        if response.status_code != 200:
            raise PrivateDriveConfigurationError('Acesso privado às métricas Google indisponível.')
        try:
            result=response.json()
        except ValueError:
            raise PrivateDriveConfigurationError('Formato da base de métricas inválido.') from None
        if not isinstance(result,dict) or not isinstance(result.get('records'),list):
            raise PrivateDriveConfigurationError('Estrutura da base de métricas inválida.')
        return result


def read_private_workbooks(service_account_info, file_ids):
    if not service_account_info:
        raise PrivateDriveConfigurationError('Configure o acesso privado ao Google Drive no servidor.')
    from google.oauth2.service_account import Credentials
    from google.auth.transport.requests import AuthorizedSession

    credentials = Credentials.from_service_account_info(
        dict(service_account_info), scopes=['https://www.googleapis.com/auth/drive.readonly'])
    files = {}
    # Credentials are used only for these two explicitly configured files.
    with AuthorizedSession(credentials) as session:
        for name, file_id in file_ids.items():
            response = session.get(f'https://www.googleapis.com/drive/v3/files/{file_id}',
                                   params={'alt': 'media'}, timeout=30)
            if response.status_code != 200:
                # Never include response bodies, signed URLs, tokens or key fields in UI errors.
                raise PrivateDriveConfigurationError(f'Acesso à base {name} indisponível. Confira a configuração privada.')
            if not response.content.startswith(b'PK'):
                raise PrivateDriveConfigurationError(f'A base {name} não foi recebida como arquivo Excel.')
            files[name] = BytesIO(response.content)
    return files
