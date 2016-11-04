import logging

from django.core.management.base import BaseCommand

from osc.importer.stations import import_stations

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Imports the specified stations'

    def add_arguments(self, parser):
        parser.add_argument('file_name')

    def handle(self, *args, **options):
        file_name = options['file_name']

        logger.info('Started importing stations from file: %s', file_name)

        import_stations(file_name)

        logger.debug('   ...Finished!!')
