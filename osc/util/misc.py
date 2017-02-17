import logging
import matplotlib.pyplot as plt
import pytz

from django.conf import settings

logger = logging.Logger(__name__)


def localize_datetime(datetime):
    return pytz.timezone(settings.TIME_ZONE).localize(datetime)


def plot_polygon(polygon):
    plt.xkcd()
    plt.figure()

    for inner_pol in polygon:
        x = [point[0] for point in inner_pol]
        y = [point[1] for point in inner_pol]

        plt.plot(x, y, '-')
        plt.plot(x, y, '.')
        plt.plot([x[0]], [y[0]], 'o')
    plt.show()


def num(s):
    try:
        return int(s)
    except ValueError:
        return float(s)


def contains_any(text, text_list):
    return len([t for t in text_list if t.lower() in text.lower()]) >= 1
