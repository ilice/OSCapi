from django.core.management.base import BaseCommand
import logging

from osc.services.importer import *

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Imports the specified years of daily data at inforiego'

    def add_arguments(self, parser):
        parser.add_argument('years', nargs='+', type=int)

    def handle(self, *args, **options):
        years = options['years']

        insert_all_stations_inforiego_daily(years)
