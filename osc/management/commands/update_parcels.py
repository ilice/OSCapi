from django.core.management.base import BaseCommand, CommandError


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
            pass
        else:
            raise CommandError('parcel arg is mandatory: --parcel=')

        self.stdout.write(
            self.style.SUCCESS('Successfully updated parcel'))
