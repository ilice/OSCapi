# coding=utf-8

from elasticsearch import ElasticsearchException
from osc.exceptions import ElasticException
from osc.util import error_managed, es

from django.conf import settings

es_index = settings.SOIL['index']
es_soil_mapping = settings.SOIL['mapping']

@error_managed(default_answer={})
def get_closest_soil_measure(lat, lon):
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

        result = es.search(index=es_index, doc_type=es_soil_mapping, body=query)

        soil_measures = [hits['_source'] for hits in result['hits']['hits']]
        soil_measures_distances = [hits['sort'] for hits in result['hits']['hits']]
        

        closest_soil_measure = {}

        if len(soil_measures) == 1:
            closest_soil_measure = soil_measures[0]
            closest_soil_measure['distance_to_parcel'] = soil_measures_distances[0][0]
        return closest_soil_measure

    except ElasticsearchException as e:
        raise ElasticException('SOIL', 'ElasticSearch Error getting closest soil measure', e)
