# -*- coding: utf-8 -*-

import xml.etree.ElementTree as ET
from django.conf import settings
from osc.util import elastic_bulk_save, es

from osc.services import obtain_elevation_from_google

from elasticsearch.client import IndicesClient

ns = {'default': 'http://www.opengis.net/kml/2.2'}

stations_index = settings.WEATHER['index']
stations_mapping = settings.WEATHER['locations.mapping']


def read_stations(from_file):
    root = ET.parse(from_file)

    stations = []

    for placemark_elem in root.findall('./default:Document/default:Folder/default:Placemark', ns):
        placemark = dict()
        placemark['name'] = placemark_elem.find('default:name', ns).text
        if placemark_elem.find('./default:ExtendedData/default:Data/default:value', ns) is not None:
            placemark['link'] = placemark_elem.find('./default:ExtendedData/default:Data/default:value', ns).text
        lon, lat, other = placemark_elem.find('./default:Point/default:coordinates', ns).text.split(',')
        placemark['coordinates'] = {
            'lat': float(lat),
            'lon': float(lon)
        }

        stations.append(placemark)

    return stations


def add_elevation_from_google(stations):
    centers = [(station['coordinates']['lat'],
                station['coordinates']['lon']) for station in stations]

    elevations = obtain_elevation_from_google(centers)

    if elevations:
        for elevation, station in zip(elevations, stations):
            station['elevation'] = elevation


def create_stations_mapping():
    idx_client = IndicesClient(es)

    mapping = {
        "properties": {
            "name": {
                "type": "text"
            },
            "link": {
                "type": "text"
            },
            "elevation": {
                "type": "float"
            },
            "coordinates": {
                "type": "geo_point"
            }
        }
    }

    idx_client.put_mapping(doc_type=stations_mapping, index=[stations_index], body=mapping)


def store_stations(stations):
    chunk_size = settings.ELASTICSEARCH['chunk_size']

    for i in range(0, len(stations), chunk_size):
        records = stations[i:i+chunk_size]

        ids = [r['name'] + '_' + str(r['coordinates']['lat']) + '_' + str(r['coordinates']['lon']) for r in records]

        elastic_bulk_save('STORE_STATIONS', stations_index, stations_mapping, records, ids=ids)


def import_stations(file_name):
    # create_stations_mapping()

    stations = read_stations(file_name)
    add_elevation_from_google(stations)
    store_stations(stations)
