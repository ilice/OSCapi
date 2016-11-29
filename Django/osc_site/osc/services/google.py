import requests
import polyline
from osc.exceptions import ConnectionError
from osc.util import error_managed

from django.conf import settings

__all__ = ['obtain_elevation_from_google', 'try_obtain_elevation_from_google']

api_key = 'AIzaSyDEYNecKjBWYMEAEKzOMLmLYf1vM8Mn2Aw'


def compose_locations_param(points):
    param = polyline.encode(points)

    return 'enc:'+param


@error_managed(default_answer=[])
def obtain_elevation_from_google(centers):

    if centers is tuple:
        centers = [centers]

    chunk_size = settings.GOOGLE['chunk_size']

    elevations = []
    for i in range(0, len(centers), chunk_size):
        chunk = centers[i:i+chunk_size]
        elevations += obtain_elevations_from_chunk(chunk)

    return elevations


def obtain_elevations_from_chunk(centers):
    url = 'https://maps.googleapis.com/maps/api/elevation/json'

    composed_locations = compose_locations_param(centers)
    response = requests.get(url, params={'key': api_key,
                                         'locations': composed_locations})
    json_response = response.json()

    if json_response['status'] != 'OK':
        raise ConnectionError('GOOGLE MAPS',
                              response['error_message'] if 'error_message' in response else json_response['status'],
                              response.url)

    elevations = [result['elevation'] for result in json_response['results']]

    return elevations


def try_obtain_elevation_from_google(centers, sleep_time=3600, max_num_trials=10):
    num_trials = 0
    while num_trials < max_num_trials:
        try:
            return obtain_elevation_from_google(centers)
        except ConnectionError:
            num_trials += 1

    return None
