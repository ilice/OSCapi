# coding=utf-8

import logging

from django.conf import settings

from osc.util import es

logger = logging.Logger(__name__)

parcel_index = settings.CADASTRE['index']
parcel_mapping = settings.CADASTRE['mapping']


class Parcel(object):
    def __init__(self, *args, **kwargs):
        self._nationalCadastralReference = kwargs.get('nationalCadastralReference', '')

        query = {
            "query": {
                "match": {
                    "properties.nationalCadastralReference": self._nationalCadastralReference
                }
            }
        }

        self._parcelDocument = es.search(
            index=parcel_index,
            doc_type=parcel_mapping,
            body=query)['hits']['hits'][0]['_source']
        self._geometry = self._parcelDocument['geometry']
        self._properties = self._parcelDocument['properties']
        try:
            self._cadastralData = \
                self._parcelDocument['properties']['cadastralData']
        except KeyError:
            self._cadastralData = {}
        self._sigpacData = self._parcelDocument['properties']['sigpacData']
        self._bbox = self._parcelDocument['bbox']

    @property
    def nationalCadastralReference(self):
        return self._properties['nationalCadastralReference']

    @property
    def elevation(self):
        return self._properties['elevation']

    @property
    def areaValue(self):
        return self._properties['areaValue']

    @property
    def address(self):
        try:
            return self._cadastralData['bico']['bi']['ldt']
        except KeyError:
            return (u'Pol\xedgono {} Parcela {}. {} ({}) '
                    .format(self._sigpacData['POLIGONO'],
                            self._sigpacData['PARCELA'],
                            self._sigpacData['MUNICIPIO'],
                            self._sigpacData['PROVINCIA']))

    @property
    def constructionUnits(self):
        try:
            return self._cadastralData['control']['cucons']
        except KeyError:
            return 0

    @property
    def cadastralUse(self):
        try:
            return self._cadastralData['bico']['lspr']['spr'][0]['dspr']['dcc']
        except KeyError:
            return 'NO-USE'

    @property
    def sigpacUse(self):
        return self._sigpacData['USO_SIGPAC']

    @property
    def geometry(self):
        return self._geometry

    @property
    def properties(self):
        properties = {}
        properties['elevation'] = self.elevation
        properties['areaValue'] = self.areaValue
        return properties

    @property
    def cadastralData(self):
        cadastralData = {}
        cadastralData['address'] = self.address
        cadastralData['constructionUnits'] = self.constructionUnits
        cadastralData['use'] = self.cadastralUse
        return cadastralData

    @property
    def sigpacData(self):
        sigpacData = {}
        sigpacData['use'] = self.sigpacUse
        return sigpacData

    @property
    def bbox(self):
        return self._bbox

    @property
    def toGeoJSON(self):
        parcelGeoJSON = {}
        parcelGeoJSON['geometry'] = self.geometry
        parcelGeoJSON['bbox'] = self.bbox
        parcelGeoJSON['nationalCadastralReference'] = \
            self.nationalCadastralReference
        parcelGeoJSON['properties'] = self.properties
        parcelGeoJSON['cadastralData'] = self.cadastralData
        parcelGeoJSON['sigpacData'] = self.sigpacData
        parcelGeoJSON['type'] = 'Feature'
        return parcelGeoJSON
