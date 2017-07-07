from django.core.management import call_command
from django.test import TestCase
# from django.core.management.base import CommandError
import mock


class ImportSigpacDataTest(TestCase):

    @mock.patch('osc.management.commands.import_sigpac_data.'
                'import_sigpac_data')
    def test_call_import_sigpac_data(
            self,
            mock_import_sigpac_data):
            call_command('import_sigpac_data')
            mock_import_sigpac_data.assert_called()
