from django.core.management.base import BaseCommand
import logging

from osc.services.importer import *

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Imports the specified zipcodes indicated by the first characters'

    def add_arguments(self, parser):
        parser.add_argument('zipcode_start', nargs='+', type=int)

    def handle(self, *args, **options):
        for zipcode_start in options['zipcode_start']:
            zipcode = str(zipcode_start)

            logging.info('Importing ' + zipcode)

            save_plots_to_elasticsearch(zip_codes=all_sigpac_zipcodes(starting_with=zipcode))
