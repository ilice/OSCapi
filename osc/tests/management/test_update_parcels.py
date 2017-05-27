from django.core.management import call_command
from django.test import TestCase
from django.core.management.base import CommandError
from unittest import skip


class UpdateParcelsTest(TestCase):
    def test_fails_when_there_is_no_parcel_args(self):
        with self.assertRaises(CommandError):
            call_command('update_parcels')

    @skip
    def test_update_parcel(self):
        raise NotImplementedError("Update parcel")
