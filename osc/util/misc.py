import logging
import pytz

from django.conf import settings

logger = logging.Logger(__name__)


def localize_datetime(datetime):
    return pytz.timezone(settings.TIME_ZONE).localize(datetime)


def num(s):
    try:
        return int(s)
    except ValueError:
        return float(s)


def contains_any(text, text_list):
    return len([t for t in text_list if t.lower() in text.lower()]) >= 1
