import requests
import polyline
import time
from osc.exceptions import ConnectionError

__all__ = ['obtain_elevation_from_google', 'try_obtain_elevation_from_google']

api_key = 'AIzaSyB-K-4XmS9a5ItnkrqJSS9070qAeRuXt6M'


def compose_locations_param(points):
    param = polyline.encode(points)

    return 'enc:'+param


def obtain_elevation_from_google(centers):
    url = 'https://maps.googleapis.com/maps/api/elevation/json'

    if centers is tuple:
        centers = [centers]

    response = requests.get(url, params={'key': api_key,
                                         'locations': compose_locations_param(centers)})
    json_response = response.json()

    if json_response['status'] != 'OK':
        raise ConnectionError('GOOGLE MAPS',
                              response['error_message'] if 'error_message' in response else json_response['status'])

    return json_response['results']


def try_obtain_elevation_from_google(centers, sleep_time=3600, max_num_trials=10):
    num_trials = 0
    while num_trials < max_num_trials:
        try:
            return obtain_elevation_from_google(centers)
        except ConnectionError:
            num_trials += 1

    return None
