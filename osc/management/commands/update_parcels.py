from django.core.management.base import BaseCommand, CommandError
from osc.services.parcels import update_parcel_by_cadastral_code


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
        else:
            raise CommandError('parcel arg is mandatory: --parcel=')

        self.stdout.write(
            self.style.SUCCESS('Successfully updated parcel'))
