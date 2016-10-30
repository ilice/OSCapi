from django.core.management.base import BaseCommand
import logging
from osc.models import Error, Feed
import datetime
from osc.util import localize_datetime

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Delete all the specified tables'

    def add_arguments(self, parser):
        parser.add_argument('tables', nargs='+', choices=['errors', 'feeds'])
        parser.add_argument('--from',
                            dest='from')

    def handle(self, *args, **options):
        tables = options['tables']
        date_from = options['from']
        for table in tables:
            if table == 'errors':
                if date_from:
                    day, month, year = date_from.split('/')
                    Error.objects.filter(date__gte=localize_datetime(datetime.datetime(int(year), int(month), int(day)))).delete()
                else:
                    Error.objects.all().delete()
            elif table == 'feeds':
                if date_from:
                    day, month, year = date_from.split('/')
                    Feed.objects.filter(date_launched__gte=localize_datetime(datetime.datetime(int(year), int(month), int(day)))).delete()
                else:
                    Feed.objects.all().delete()
