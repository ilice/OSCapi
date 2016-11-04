import requests
from django.conf import settings
import pytz
import time
from datetime import datetime

from osc.exceptions import ConnectionError
from osc.services import get_all_stations

from osc.util import elastic_bulk_save, error_managed, es
from elasticsearch.client import IndicesClient

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
weather_mapping = settings.WEATHER['mapping']


def make_weather_mapping():
    idx_client = IndicesClient(es)

    mapping = {
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
            "station_name": {
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
    else:
        raise ConnectionError('OPENWEATHERMAP', 'Error connecting to ' + owm_url + '. Status code: ' + response.status_code)

    return weather_record


def get_weather_from_stations():
    chunk_size = settings.WEATHER['owm_chunk_size']
    chunk_time = settings.WEATHER['owm_chunk_time']

    stations = get_all_stations()
    weather_list = []

    begin = None
    for i in range(0, len(stations), chunk_size):
        chunk = stations[i:i+chunk_size]
        # wait for the waiting time
        if begin:
            time_spent = (datetime.now() - begin).seconds
            if time_spent < chunk_time:
                time.sleep(chunk_time - time_spent)

        begin = datetime.now()

        for station in chunk:
            weather = get_weather(station['coordinates']['lat'], station['coordinates']['lon'])
            if weather is not None:
                weather['station_name'] = station['name']
                weather_list.append(weather)
            else:
                logger.warning('No weather obtained for station %s', str(station))

    return weather_list


def store_weather(weather_list):
    chunk_size = settings.ELASTICSEARCH['chunk_size']

    for i in range(0, len(weather_list), chunk_size):
        records = weather_list[i:i + chunk_size]

        ids = [str(time.mktime(r['dt'].timetuple())) + '_' +
               str(r['coord']['lat']) + '_' +
               str(r['coord']['lon']) for r in records]

        elastic_bulk_save('STORE_WEATHER', weather_index, weather_mapping, records, ids=ids)
