import sys
from types import ModuleType
import unittest
from unittest.mock import MagicMock, patch

from drive_workbooks import read_private_workbooks, read_private_json, PrivateDriveConfigurationError


class PrivateDriveTests(unittest.TestCase):
    def test_missing_credentials_fail_closed(self):
        with self.assertRaises(PrivateDriveConfigurationError):
            read_private_workbooks(None, {'periodicos':'file-one'})
        with self.assertRaises(PrivateDriveConfigurationError):
            read_private_json(None,'metrics')

    def test_private_json_reader_is_restricted_and_validates_shape(self):
        modules={name:ModuleType(name) for name in ['google','google.oauth2','google.oauth2.service_account','google.auth','google.auth.transport','google.auth.transport.requests']}
        cred=MagicMock();modules['google.oauth2.service_account'].Credentials=cred
        auth=MagicMock();modules['google.auth.transport.requests'].AuthorizedSession=auth
        response=auth.return_value.__enter__.return_value.get.return_value
        response.status_code=200;response.json.return_value={'records':[]}
        with patch.dict(sys.modules,modules):
            self.assertEqual(read_private_json({'type':'service_account'},'metrics'),{'records':[]})
            response.json.return_value=[]
            with self.assertRaises(PrivateDriveConfigurationError):
                read_private_json({'type':'service_account'},'metrics')
        self.assertEqual(cred.from_service_account_info.call_args.kwargs['scopes'],['https://www.googleapis.com/auth/drive.readonly'])

    def test_downloads_only_configured_files_with_readonly_scope(self):
        credentials=MagicMock()
        session=MagicMock()
        session.get.return_value.status_code=200
        session.get.return_value.content=b'PK-excel-fixture'
        modules={name:ModuleType(name) for name in ['google','google.oauth2','google.oauth2.service_account','google.auth','google.auth.transport','google.auth.transport.requests']}
        modules['google.oauth2.service_account'].Credentials=credentials
        auth=MagicMock()
        auth.return_value.__enter__.return_value=session
        modules['google.auth.transport.requests'].AuthorizedSession=auth
        with patch.dict(sys.modules,modules):
            files=read_private_workbooks({'type':'service_account'}, {'periodicos':'one','instituicoes':'two'})
        self.assertEqual(set(files),{'periodicos','instituicoes'})
        self.assertEqual(session.get.call_count,2)
        self.assertEqual(credentials.from_service_account_info.call_args.kwargs['scopes'],['https://www.googleapis.com/auth/drive.readonly'])
        self.assertTrue(all(call.kwargs['timeout']==30 for call in session.get.call_args_list))
        self.assertEqual(session.get.call_args_list[0].args[0],'https://www.googleapis.com/drive/v3/files/one')

    def test_access_error_does_not_expose_response_body(self):
        modules={name:ModuleType(name) for name in ['google','google.oauth2','google.oauth2.service_account','google.auth','google.auth.transport','google.auth.transport.requests']}
        modules['google.oauth2.service_account'].Credentials=MagicMock()
        auth=MagicMock()
        response=auth.return_value.__enter__.return_value.get.return_value
        response.status_code=403
        response.content=b'private-response-marker'
        modules['google.auth.transport.requests'].AuthorizedSession=auth
        with patch.dict(sys.modules,modules),self.assertRaises(PrivateDriveConfigurationError) as error:
            read_private_workbooks({'type':'service_account'},{'periodicos':'one'})
        self.assertNotIn('private-response-marker',str(error.exception))


if __name__=='__main__':
    unittest.main()
