from django.core.management.base import BaseCommand
import logging

from osc.services.importer import *

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Imports the specified years of hourly data at inforiego'

    def add_arguments(self, parser):
        parser.add_argument('--last_update_date', dest='last_update_date', type=str)
        parser.add_argument('--years', nargs='+', type=int)

    def handle(self, *args, **options):
        years = options['years']
        last_update_date = options['last_update_date']

        logger.info('Importing Inforiego Hourly for years %s with last update date %s', years, last_update_date)

        insert_all_stations_inforiego_hourly(years, last_update_date)

        logger.info('Finished Importing Inforiego Hourly')
