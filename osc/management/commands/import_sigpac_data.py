from django.core.management.base import BaseCommand
from django.core.management.base import CommandError

from osc.importer.sigpac import import_sigpac_data


class Command(BaseCommand):
    help = 'Imports data from SIGPAC and updates parcels'

    def add_arguments(self, parser):
        parser.add_argument(
            '--provinces',
            help='Province for updating (as many as you need)'
        )

    def handle(self, *args, **options):
        try:
            provinces = []
            if options['provinces']:
                provinces = options['provinces'].split(',')
            import_sigpac_data(provinces)
        except Exception as e:
            raise CommandError('Error importing SIGPAC data: {}'.format(e))

        self.stdout.write(self.style.SUCCESS('Successfully imported data'))
