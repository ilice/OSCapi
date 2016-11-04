import requests
from django.conf import settings
import pytz
import time
from datetime import datetime
from geopy.distance import great_circle

from osc.exceptions import ConnectionError, ElasticException

from osc.util import elastic_bulk_save, error_managed, es
from elasticsearch.client import IndicesClient
from elasticsearch import ElasticsearchException

import logging

owm_url = 'http://api.openweathermap.org/data/2.5/weather'

logger = logging.getLogger(__name__)

"""
Parameters:

coord
    - coord.lon City geo location, longitude
    - coord.lat City geo location, latitude
weather (more info Weather condition codes)
    - weather.id Weather condition id
    - weather.main Group of weather parameters (Rain, Snow, Extreme etc.)
    - weather.description Weather condition within the group
    - weather.icon Weather icon id
base Internal parameter
main
    - main.temp Temperature. Unit Default: Kelvin, Metric: Celsius, Imperial: Fahrenheit.
    - main.pressure Atmospheric pressure (on the sea level, if there is no sea_level or grnd_level data), hPa
    - main.humidity Humidity, %
    - main.temp_min Minimum temperature at the moment. This is deviation from current temp that is possible for large cities and megalopolises geographically expanded (use these parameter optionally). Unit Default: Kelvin, Metric: Celsius, Imperial: Fahrenheit.
    - main.temp_max Maximum temperature at the moment. This is deviation from current temp that is possible for large cities and megalopolises geographically expanded (use these parameter optionally). Unit Default: Kelvin, Metric: Celsius, Imperial: Fahrenheit.
    - main.sea_level Atmospheric pressure on the sea level, hPa
    - main.grnd_level Atmospheric pressure on the ground level, hPa
wind
    - wind.speed Wind speed. Unit Default: meter/sec, Metric: meter/sec, Imperial: miles/hour.
    - wind.deg Wind direction, degrees (meteorological)
clouds
    - clouds.all Cloudiness, %
rain
    - rain.3h Rain volume for the last 3 hours
snow
    - snow.3h Snow volume for the last 3 hours
dt Time of data calculation, unix, UTC
sys
    - sys.type Internal parameter
    - sys.id Internal parameter
    - sys.message Internal parameter
    - sys.country Country code (GB, JP etc.)
    - sys.sunrise Sunrise time, unix, UTC
    - sys.sunset Sunset time, unix, UTC
id City ID
name City name
cod Internal parameter
"""

# https://openweathermap.org/weather-conditions

weather_index = settings.WEATHER['index']
weather_mapping = settings.WEATHER['weather.mapping']
locations_mapping = settings.WEATHER['locations.mapping']


def make_weather_mapping():
    idx_client = IndicesClient(es)

    mapping = {
        "_parent": {
            "type": locations_mapping
        },
        "properties": {
            "base": {
                "type": "keyword"
            },
            "clouds": {
                "properties": {
                    "all": {
                        "type": "long"
                    }
                }
            },
            "cod": {
                "type": "long"
            },
            "coord": {
                "properties": {
                    "lat": {
                        "type": "float"
                    },
                    "lon": {
                        "type": "float"
                    }
                }
            },
            "dt": {
                "type": "date"
            },
            "id": {
                "type": "long"
            },
            "main": {
                "properties": {
                    "grnd_level": {
                        "type": "float"
                    },
                    "humidity": {
                        "type": "long"
                    },
                    "pressure": {
                        "type": "long"
                    },
                    "sea_level": {
                        "type": "float"
                    },
                    "temp": {
                        "type": "float"
                    },
                    "temp_max": {
                        "type": "float"
                    },
                    "temp_min": {
                        "type": "float"
                    }
                }
            },
            "name": {
                "type": "keyword"
            },
            "rain": {
                "properties": {
                    "3h": {
                        "type": "float"
                    }
                }
            },
            "location_name": {
                "type": "keyword"
            },
            "sys": {
                "properties": {
                    "country": {
                        "type": "keyword"
                    },
                    "id": {
                        "type": "long"
                    },
                    "message": {
                        "type": "float"
                    },
                    "sunrise": {
                        "type": "date"
                    },
                    "sunset": {
                        "type": "date"
                    },
                    "type": {
                        "type": "long"
                    }
                }
            },
            "visibility": {
                "type": "long"
            },
            "weather": {
                "properties": {
                    "description": {
                        "type": "text"
                    },
                    "icon": {
                        "type": "keyword"
                    },
                    "id": {
                        "type": "long"
                    },
                    "main": {
                        "type": "keyword"
                    }
                }
            },
            "wind": {
                "properties": {
                    "deg": {
                        "type": "long"
                    },
                    "gust": {
                        "type": "float"
                    },
                    "speed": {
                        "type": "float"
                    }
                }
            }
        }
    }

    idx_client.put_mapping(doc_type=weather_mapping, index=[weather_index], body=mapping)


# http://api.openweathermap.org/data/2.5/weather?lat=35&lon=139&appid=b1b15e88fa797225412429c1c50c122a1

@error_managed(default_answer=None, inhibit_exception=True)
def get_weather(lat, lon):
    appid = settings.WEATHER['owm_token']

    response = requests.get(owm_url, params={'lat': lat,
                                             'lon': lon,
                                             'appid': appid})

    if response.ok:
        weather_record = response.json()
        weather_record['dt'] = pytz.timezone(settings.TIME_ZONE).localize(datetime.fromtimestamp(weather_record['dt']))
        weather_record['sys']['sunrise'] = pytz.timezone(settings.TIME_ZONE).localize(datetime.fromtimestamp(weather_record['sys']['sunrise']))
        weather_record['sys']['sunset'] = pytz.timezone(settings.TIME_ZONE).localize(datetime.fromtimestamp(weather_record['sys']['sunset']))
        weather_record['coordinates'] = weather_record['coord']
        del(weather_record['coord'])
    else:
        raise ConnectionError('OPENWEATHERMAP', 'Error connecting to ' + owm_url + '. Status code: ' + response.status_code)

    return weather_record


def get_weather_from_locations():
    chunk_size = settings.WEATHER['owm_chunk_size']
    chunk_time = settings.WEATHER['owm_chunk_time']

    locations = get_all_locations()
    weather_list = []

    begin = None
    for i in range(0, len(locations), chunk_size):
        chunk = locations[i:i+chunk_size]
        # wait for the waiting time
        if begin:
            time_spent = (datetime.now() - begin).seconds
            if time_spent < chunk_time:
                time.sleep(chunk_time - time_spent)

        begin = datetime.now()

        for (id_location, location) in chunk:
            weather_rec = get_weather(location['coordinates']['lat'], location['coordinates']['lon'])

            if weather_rec is not None:
                weather = {'location': id_location,
                           'record': weather_rec}

                weather_list.append(weather)
            else:
                logger.warning('No weather obtained for location %s', str(location))

    return weather_list


def store_weather(weather_list):
    chunk_size = settings.ELASTICSEARCH['chunk_size']

    for i in range(0, len(weather_list), chunk_size):
        records = weather_list[i:i + chunk_size]

        docs = [r['record'] for r in records]
        ids = [str(time.mktime(r['record']['dt'].timetuple())) + '_' + r['location'] for r in records]
        parents = [r['location'] for r in records]

        elastic_bulk_save('STORE_WEATHER', weather_index, weather_mapping, docs, ids=ids, parents=parents)


@error_managed(default_answer={})
def get_closest_location(lat, lon):
    try:
        query = {"size": 1,
                 "sort": [
                     {
                         "_geo_distance": {
                             "coordinates": {
                                 "lat": lat,
                                 "lon": lon
                             },
                             "order": "asc",
                             "unit": "km",
                             "mode": "min",
                             "distance_type": "sloppy_arc"
                         }
                     }
                 ]
                 }

        result = es.search(index=weather_index, doc_type=locations_mapping, body=query)

        locations = [(hits['_id'], hits['_source']) for hits in result['hits']['hits']]

        closest_location = {}
        id_location = None

        if len(locations) == 1:
            id_location, closest_location = locations[0]

            this_loc = (lat, lon)
            location_loc = (closest_location['coordinates']['lat'], closest_location['coordinates']['lon'])

            closest_location['distance_to_parcel'] = great_circle(this_loc, location_loc).kilometers

        return id_location, closest_location

    except ElasticsearchException as e:
        raise ElasticException('locationS', 'ElasticSearch Error getting closest location', e)


def get_all_locations():
    result = es.search(index=weather_index, doc_type=locations_mapping, size=10000)

    locations = [(hits['_id'], hits['_source']) for hits in result['hits']['hits']]

    return locations

