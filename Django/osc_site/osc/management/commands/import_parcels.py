from django.core.management.base import BaseCommand
import logging

from osc.services.importer import cadastre

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Imports the specified zipcodes indicated by the first characters'

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        logging.info('Importing parcels')

        cadastre.update_cadastral_information()
