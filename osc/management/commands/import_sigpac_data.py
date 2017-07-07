from django.core.management.base import BaseCommand, CommandError

from osc.importer.sigpac import import_sigpac_data


class Command(BaseCommand):
    help = 'Imports data from SIGPAC and updates parcels'

    def handle(self, *args, **options):
        try:
            import_sigpac_data()
        except Exception:
            raise CommandError('Error importing SIGPAC data')

        self.stdout.write(self.style.SUCCESS('Successfully imported data'))
