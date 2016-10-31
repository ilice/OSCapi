from django.core.management.base import BaseCommand
import logging

from osc.services.importer import cadastre

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Imports the specified zipcodes indicated by the first characters'

    def add_arguments(self, parser):
        parser.add_argument('--force_update',
                            action='store_true',
                            dest='force_update',
                            help='Force Update the parcels, even if the date does not fit')

        parser.add_argument('--import_zip_url',
                            dest='import_zip_url',
                            help='imports just a particular zip file pointed by the zip url')

    def handle(self, *args, **options):
        force_update = options['force_update']
        import_zip_url = options['import_zip_url']

        logger.info('Importing parcels: force_update = %s, import_zip_url = %s',
                    force_update,
                    import_zip_url)

        if import_zip_url:
            cadastre.store_parcels_from_url(import_zip_url)
        else:
            cadastre.update_cadastral_information(force_update=force_update)
