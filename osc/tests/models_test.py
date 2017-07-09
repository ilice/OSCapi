from django.test import TestCase
from django.utils import timezone

from osc.models import Error


class ErrorTest(TestCase):

    def test_save_Error(self):
        date = timezone.now()
        error = Error(date=date,
                      process_name='TEST',
                      module_name='Error model test',
                      function_name='test_create_Error',
                      severity=Error.S_ERROR,
                      message='message',
                      cause='cause',
                      actionable_info='actionable_info')
        error.save()
        errorFromDB = Error.objects.get(pk=error.pk)
        self.assertEqual(errorFromDB.date, date)
        self.assertEqual(errorFromDB.process_name, 'TEST')
        self.assertEqual(errorFromDB.module_name, 'Error model test')
        self.assertEqual(errorFromDB.function_name, 'test_create_Error')
        self.assertEqual(errorFromDB.severity, Error.S_ERROR)
        self.assertEqual(errorFromDB.message, 'message')
        self.assertEqual(errorFromDB.cause, 'cause')
        self.assertEqual(errorFromDB.actionable_info, 'actionable_info')
