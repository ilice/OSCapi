from django.core.management.base import BaseCommand
from osc.services.parcels import update_parcel_by_cadastral_code
from osc.importer.cadastre import update_cadastre_information


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
            update_parcel_by_cadastral_code(options['cadastral_reference'])
            self.stdout.write(
                self.style.SUCCESS('Successfully updated parcel'))
        else:
            update_cadastre_information()
            self.stdout.write(
                self.style.SUCCESS('Successfully updated parcels'))
