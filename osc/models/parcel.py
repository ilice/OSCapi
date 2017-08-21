# coding=utf-8

import logging

from django.conf import settings
import geojson

from rest_framework.reverse import reverse

from osc.util import es

logger = logging.Logger(__name__)

parcel_index = settings.CADASTRE['index']
parcel_mapping = settings.CADASTRE['mapping']


class ParcelMeta(type):
    """docstring for ParcelMeta."""
    def __name__(self):
        return 'Feature'


class Parcel(geojson.Feature):

    def __init__(self, *args, **kwargs):
        _parcelDocument = kwargs.get('parcelDocument', '')
        request = kwargs.get('request', None)
        self.__class__.__name__ = 'Feature'
        if _parcelDocument == '':
            query = {
                "query": {
                    "match": {
                        "properties.nationalCadastralReference": kwargs.get('nationalCadastralReference', '')
                    }
                }
            }
            _parcelDocument = es.search(
                index=parcel_index,
                doc_type=parcel_mapping,
                body=query)['hits']['hits'][0]['_source']

        _properties = self.properties(_parcelDocument['properties'], request=request)

        geojson.Feature.__init__(self, geometry=geojson.Polygon(_parcelDocument['geometry']['coordinates']), properties=_properties)

    def address(self, _properties):
        try:
            return _properties['cadastralData']['bico']['bi']['ldt']
        except KeyError:
            return (u'Pol\xedgono {} Parcela {}. {} ({}) '
                    .format(_properties['sigpacData']['POLIGONO'],
                            _properties['sigpacData']['PARCELA'],
                            _properties['sigpacData']['MUNICIPIO'],
                            _properties['sigpacData']['PROVINCIA']))

    def constructionUnits(self, _properties):
        try:
            return _properties['cadastralData']['control']['cucons']
        except KeyError:
            return 0

    def cadastralUse(self, _properties):
        try:
            return _properties['cadastralData']['bico']['lspr']['spr'][0]['dspr']['dcc']
        except KeyError:
            return 'NO-USE'

    def sigpacUse(self, _properties):
        return _properties['sigpacData']['USO_SIGPAC']

    def properties(self, _properties, request=None):
        properties = {}
        properties['elevation'] = _properties['elevation']
        properties['areaValue'] = _properties['areaValue']
        properties['nationalCadastralReference'] = \
            _properties['nationalCadastralReference']
        if request is not None:
            properties['parcel-url'] = reverse('parcels-detail', args=[_properties['nationalCadastralReference']], request=request)
        properties['cadastralData'] = self.cadastralData(_properties)
        properties['sigpacData'] = self.sigpacData(_properties)
        return properties

    def cadastralData(self, _properties):
        cadastralData = {}
        cadastralData['address'] = self.address(_properties)
        cadastralData['constructionUnits'] = self.constructionUnits(_properties)
        cadastralData['use'] = self.cadastralUse(_properties)
        return cadastralData

    def sigpacData(self, _properties):
        sigpacData = {}
        sigpacData['use'] = self.sigpacUse(_properties)
        return sigpacData


def getParcelByNationalCadastralReference(nationalCadastralReference):
    query = {
        "query": {
            "match": {
                "properties.nationalCadastralReference": nationalCadastralReference
            }
        }
    }

    parcelDocument = es.search(
        index=parcel_index,
        doc_type=parcel_mapping,
        body=query)['hits']['hits'][0]['_source']

    return Parcel(parcelDocument=parcelDocument)


def getParcels(request=None):
    query = {
        "query": {
            "bool": {
                "must": [
                    {
                        "exists": {
                            "field": "properties.sigpacData"
                        }
                    },
                    {
                        "exists": {
                            "field": "properties.elevation"
                        }
                    }
                ]
            }
        }
    }

    parcelsDocuments = es.search(
        index=parcel_index,
        doc_type=parcel_mapping,
        body=query)['hits']['hits']

    parcels = []

    for parcelDocument in parcelsDocuments:
        parcels.append(Parcel(parcelDocument=parcelDocument['_source'], request=request))

    return geojson.FeatureCollection(parcels)
