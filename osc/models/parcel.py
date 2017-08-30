# coding=utf-8

import logging


from django.conf import settings
from django.utils.http import urlencode
import geohash
import geojson

from rest_framework.reverse import reverse

from osc.util import es

logger = logging.getLogger(__name__)

PARCEL_INDEX = settings.CADASTRE['index']
PARCEL_MAPPING = settings.CADASTRE['mapping']
MAX_ELASTIC_QUERY_SIZE = settings.CADASTRE['max.query.size']
CLUSTER_AGG = settings.ELASTICSEARCH['cluster_agg']
PARCEL_SEARCH = settings.ELASTICSEARCH['parcel_search']
PARCEL_SEARCH_BY_BBOX = settings.ELASTICSEARCH['parcel_search_by_bbox']


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


class ParcelBucket(geojson.Feature):
    """Bucket of parcels with the number of parcels that 'fell into' the bucket."""
    def __init__(self, *args, **kwargs):
        __parcel_bucket_document = kwargs.get('parcelBucketDocument', '')
        __request = kwargs.get('request', None)
        (__lat, __lng, __lat_err, __lng_err) = geohash.decode_exactly(__parcel_bucket_document['key'])
        __bbox = self.__bbox(__parcel_bucket_document)
        __properties = self.__properties(__parcel_bucket_document, __bbox, request=__request)
        self.__class__.__name__ = 'Feature'
        geojson.Feature.__init__(self, geometry=geojson.Point((float(__lng), float(__lat))), properties=__properties, bbox=__bbox)
    def __properties(self, parcel_bucket_document, bbox, request=None):
        __properties = {}
        __properties['value'] = parcel_bucket_document['doc_count']
        __properties['area'] = parcel_bucket_document['area']['value']
        if request is not None:
            __url = reverse('parcels-list', request=request)
            __properties['parcel-url'] = u'%s?%s=%s' % (__url, 'bbox', ','.join(str(coord) for coord in bbox))
        return __properties
    def __bbox(self, parcel_bucket_document):
        __bbox = geohash.bbox(parcel_bucket_document['key'])
        return [__bbox['w'],__bbox['s'],__bbox['e'],__bbox['n']]


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


def getParcels(request=None, bbox=None, precision=None):
    logger.debug('getParcels(%s, %s, %s)', request, bbox, precision)

    __max_elastic_query_size = 20 if bbox is None else MAX_ELASTIC_QUERY_SIZE
    __query = PARCEL_SEARCH

    if bbox is not None:
        __query = dict(PARCEL_SEARCH_BY_BBOX)
        west, south, east, north = bbox.split(',')
        __query['query']['bool']['filter']['geo_bounding_box']['properties.reference_point']['top'] = north
        __query['query']['bool']['filter']['geo_bounding_box']['properties.reference_point']['left'] = west
        __query['query']['bool']['filter']['geo_bounding_box']['properties.reference_point']['bottom'] = south
        __query['query']['bool']['filter']['geo_bounding_box']['properties.reference_point']['right'] = east
        if precision is not None:
            __agg = dict(CLUSTER_AGG)
            __agg['2']['geohash_grid']['precision']=precision
            __query['aggs']=__agg
            __query['size']=0
            __max_elastic_query_size=0

    __result = es.search(
        index=PARCEL_INDEX,
        doc_type=PARCEL_MAPPING,
        body=__query,
        size=__max_elastic_query_size)

    __parcelsDocuments = __result['hits']['hits']
    __parcelsBucketsDocuments = __result['aggregations']['2']['buckets'] if 'aggregations' in __result else []

    __parcels = []

    for __parcelDocument in __parcelsDocuments:
        __parcels.append(Parcel(parcelDocument=__parcelDocument['_source'], request=request))

    __parcels_buckets = []
    max = min = 0
    for __parcelBucketDocument in __parcelsBucketsDocuments:
        __parcels_buckets.append(ParcelBucket(parcelBucketDocument=__parcelBucketDocument, request=request))
        if __parcelBucketDocument['doc_count'] > max:
            max = __parcelBucketDocument['doc_count']
        if __parcelBucketDocument['doc_count'] < min:
            min = __parcelBucketDocument['doc_count']

    # for __parcels_bucket in __parcels_buckets:
    #     __parcels_bucket['properties']['num_buckets'] = len(__parcels_buckets)
    #     __parcels_bucket['properties']['min_value'] = min
    #     __parcels_bucket['properties']['max_value'] = max

    return geojson.FeatureCollection(__parcels_buckets) if len(__parcels_buckets) > 0 else geojson.FeatureCollection(__parcels)
