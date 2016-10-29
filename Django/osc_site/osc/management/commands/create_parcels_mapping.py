from django.core.management.base import BaseCommand
import logging

from osc.services.cadastre import create_parcel_mapping

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'create the mapping for the parcels, in case it does not exist'

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        create_parcel_mapping()
