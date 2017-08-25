# coding=utf-8

import logging

from django.conf import settings
import geojson

from rest_framework.reverse import reverse

from osc.util import es

logger = logging.getLogger(__name__)

PARCEL_INDEX = settings.CADASTRE['index']
PARCEL_MAPPING = settings.CADASTRE['mapping']
MAX_ELASTIC_QUERY_SIZE = settings.CADASTRE['max.query.size']
PARCEL_SEARCH_BY_BBOX = settings.ELASTICSEARCH['parcel_search_by_bbox']
PARCEL_SEARCH = settings.ELASTICSEARCH['parcel_search']


class Parcel(geojson.Feature):

    def __init__(self, *args, **kwargs):
        __parcel_document = kwargs.get('parcelDocument', '')
        __request = kwargs.get('request', None)
        self.__class__.__name__ = 'Feature'
        if __parcel_document == '':
            _query = {
                "query": {
                    "match": {
                        "properties.nationalCadastralReference": kwargs.get('nationalCadastralReference', '')
                    }
                }
            }
            __parcel_document = es.search(
                index=PARCEL_INDEX,
                doc_type=PARCEL_MAPPING,
                body=_query)['hits']['hits'][0]['_source']

        __properties = self.__properties(__parcel_document['properties'], request=__request)

        geojson.Feature.__init__(self, geometry=geojson.Polygon(__parcel_document['geometry']['coordinates']), properties=__properties)

    def __address(self, properties):
        try:
            return properties['cadastralData']['bico']['bi']['ldt']
        except KeyError:
            return (u'Pol\xedgono {} Parcela {}. {} ({}) '
                    .format(properties['sigpacData']['POLIGONO'],
                            properties['sigpacData']['PARCELA'],
                            properties['sigpacData']['MUNICIPIO'],
                            properties['sigpacData']['PROVINCIA']))

    def __constructionUnits(self, properties):
        try:
            return properties['cadastralData']['control']['cucons']
        except KeyError:
            return 0

    def __cadastralUse(self, properties):
        try:
            return properties['cadastralData']['bico']['lspr']['spr'][0]['dspr']['dcc']
        except KeyError:
            return 'NO-USE'

    def __sigpacUse(self, properties):
        return properties['sigpacData']['USO_SIGPAC']

    def __properties(self, properties, request=None):
        __properties = {}
        __properties['elevation'] = properties['elevation']
        __properties['areaValue'] = properties['areaValue']
        __properties['nationalCadastralReference'] = \
            properties['nationalCadastralReference']
        if request is not None:
            __properties['parcel-url'] = reverse('parcels-detail', args=[properties['nationalCadastralReference']], request=request)
        __properties['cadastralData'] = self.__cadastralData(properties)
        __properties['sigpacData'] = self.__sigpacData(properties)
        return __properties

    def __cadastralData(self, properties):
        __cadastralData = {}
        __cadastralData['address'] = self.__address(properties)
        __cadastralData['constructionUnits'] = self.__constructionUnits(properties)
        __cadastralData['use'] = self.__cadastralUse(properties)
        return __cadastralData

    def __sigpacData(self, properties):
        __sigpacData = {}
        __sigpacData['use'] = self.__sigpacUse(properties)
        return __sigpacData


def getParcelByNationalCadastralReference(nationalCadastralReference):
    query = {
        "query": {
            "match": {
                "properties.nationalCadastralReference": nationalCadastralReference
            }
        }
    }

    parcelDocument = es.search(
        index=PARCEL_INDEX,
        doc_type=PARCEL_MAPPING,
        body=query)['hits']['hits'][0]['_source']

    return Parcel(parcelDocument=parcelDocument)


def getParcels(request=None, bbox=None):
    __max_elastic_query_size = 20 if bbox is None else MAX_ELASTIC_QUERY_SIZE

    bottom, left, top, right = bbox.split(',') if bbox is not None else ["", "", "", ""]
    PARCEL_SEARCH_BY_BBOX['query']['bool']['filter']['geo_bounding_box']['properties.reference_point']['top'] = top
    PARCEL_SEARCH_BY_BBOX['query']['bool']['filter']['geo_bounding_box']['properties.reference_point']['left'] = left
    PARCEL_SEARCH_BY_BBOX['query']['bool']['filter']['geo_bounding_box']['properties.reference_point']['bottom'] = bottom
    PARCEL_SEARCH_BY_BBOX['query']['bool']['filter']['geo_bounding_box']['properties.reference_point']['right'] = right

    __query = PARCEL_SEARCH if bbox is None else PARCEL_SEARCH_BY_BBOX

    __parcelsDocuments = es.search(
        index=PARCEL_INDEX,
        doc_type=PARCEL_MAPPING,
        body=__query,
        size=__max_elastic_query_size)['hits']['hits']

    __parcels = []

    for __parcelDocument in __parcelsDocuments:
        __parcels.append(Parcel(parcelDocument=__parcelDocument['_source'], request=request))

    return geojson.FeatureCollection(__parcels)
