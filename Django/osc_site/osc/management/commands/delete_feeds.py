from django.core.management.base import BaseCommand
import logging
from osc.models import Feed

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Delete all the feeds in order to reimport'

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        logging.info('deleting feeds')

        Feed.objects.all().delete()