from osc.models import Feed
from django.db.models import Max
from django.utils import timezone


def get_last_successful_update_date(feed_url):
    return Feed.objects.filter(url=feed_url, success=True).aggregate(max=Max('update_date'))['max']


def start_feed_read(feed_url, update_date):
    feed = Feed(url=feed_url, date_launched=timezone.now(), update_date=update_date, success=False)
    feed.save()

    return feed.id


def finish_feed_read(feed_id, success, info=None):
    feed = Feed.objects.get(pk=feed_id)

    if feed is not None:
        feed.success = success
        feed.date_finished = timezone.now()
        feed.info = info

        feed.save()
