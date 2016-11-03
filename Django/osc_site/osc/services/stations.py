from osc.util import error_managed, es
from osc.exceptions import ElasticException
from django.conf import settings
from geopy.distance import great_circle

from elasticsearch import ElasticsearchException

stations_index = settings.STATIONS['index']
stations_mapping = settings.STATIONS['mapping']


@error_managed(default_answer={})
def get_closest_station(lat, lon):
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

        result = es.search(index=stations_index, doc_type=stations_mapping, body=query)

        stations = [hits['_source'] for hits in result['hits']['hits']]

        closest_station = {}

        if len(stations) == 1:
            closest_station = stations[0]

            this_loc = (lat, lon)
            station_loc = (closest_station['lat_lon']['lat'], closest_station['lat_lon']['lon'])

            closest_station['distance_to_parcel'] = great_circle(this_loc, station_loc).kilometers

        return closest_station

    except ElasticsearchException as e:
        raise ElasticException('STATIONS', 'ElasticSearch Error getting closest station', e)


def get_all_stations():
    result = es.search(index=stations_index, doc_type=stations_mapping, size=10000)

    stations = [hits['_source'] for hits in result['hits']['hits']]

    return stations

