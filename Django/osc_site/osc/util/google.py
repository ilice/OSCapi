import requests
import polyline
import time

api_key = 'AIzaSyB-K-4XmS9a5ItnkrqJSS9070qAeRuXt6M'


def compose_locations_param(points):
    param = polyline.encode(points)

    return 'enc:'+param


def obtain_elevation_from_google(centers):
    url = 'https://maps.googleapis.com/maps/api/elevation/json'
    sleep_time_when_over_quota = 3600

    while True:
        response = requests.get(url, params={'key': api_key,
                                             'locations': compose_locations_param(centers)})

        if response.json()['status'] != 'OVER_QUERY_LIMIT':
            break

        # Wait for the next trial
        time.sleep(sleep_time_when_over_quota)

    return response.json()