import logging

from django.core.management.base import BaseCommand

import osc.services.weather as weather

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Imports the weather from open weather map'

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        logger.info('Started importing stations from open weather map')

        weather.make_weather_mapping()

        weather_list = weather.get_weather_from_stations()
        weather.store_weather(weather_list)

        logger.info('   ...Finished!!')
