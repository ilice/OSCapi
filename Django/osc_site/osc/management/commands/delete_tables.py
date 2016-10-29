from django.core.management.base import BaseCommand
import logging
from osc.models import Error, Feed

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Delete all the specified tables'

    def add_arguments(self, parser):
        parser.add_argument('tables', nargs='+', choices=['errors', 'feeds'])

    def handle(self, *args, **options):
        tables = options['tables']
        for table in tables:
            if table == 'errors':
                Error.objects.all().delete()
            elif table == 'feeds':
                Feed.objects.all().delete()
