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

        parser.add_argument('provinces', nargs='*', type=int)

    def handle(self, *args, **options):
        logging.info('Importing parcels')

        force_update = options['force_update']
        provinces = None if not options['provinces'] else options['provinces']

        cadastre.update_cadastral_information(force_update=force_update, provinces=provinces)
