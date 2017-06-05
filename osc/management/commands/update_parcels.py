from django.core.management.base import BaseCommand
import logging

from osc.importer.cadastre import update_cadastre_information
from osc.services.parcels import update_parcel_by_cadastral_code

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Updates parcels data from sources on database'

    def add_arguments(self, parser):
        parser.add_argument(
            '--parcel',
            dest='cadastral_reference',
            default=False,
            help='Updates data from this cadastral parcel'
        )

    def handle(self, *args, **options):
        if options['cadastral_reference']:
            logger.info('Updating parcel %s', options['cadastral_reference'])
            update_parcel_by_cadastral_code(options['cadastral_reference'])
            self.stdout.write(
                self.style.SUCCESS('Successfully updated parcel'))
        else:
            logger.info('Updating parcels')
            update_cadastre_information()
            self.stdout.write(
                self.style.SUCCESS('Successfully updated parcels'))
