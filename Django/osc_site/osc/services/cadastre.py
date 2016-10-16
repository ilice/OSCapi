import requests
import xml.etree.ElementTree as ET

from osc.util import xml_to_json, elastic_bulk_save
from osc.util import config

import elasticsearch_dsl as dsl

import utm

__all__ = ['get_cadastral_parcels_by_bbox', 'get_cadastral_parcels_by_code', 'get_public_cadastre_info', 'store_parcels']

url_public_cadastral_info = 'http://ovc.catastro.meh.es/ovcservweb/OVCSWLocalizacionRC/OVCCallejero.asmx/Consulta_DNPRC'
url_inspire = 'http://ovc.catastro.meh.es/INSPIRE/wfsCP.aspx'
zone_number = 30

ns = {'gml': 'http://www.opengis.net/gml/3.2',
      'gmd': 'http://www.isotc211.org/2005/gmd',
      'ogc': 'http://www.opengis.net/ogc',
      'xlink': 'http://www.w3.org/1999/xlink',
      'cp': 'urn:x-inspire:specification:gmlas:CadastralParcels:3.0'
      }


def create_parcel_mapping(index, mapping_name='parcel'):
    m = dsl.Mapping(mapping_name)

    properties = dsl.Nested()
    properties.field('areaValue', dsl.Float())
    properties.field('beginLifespanVersion', dsl.Date())
    properties.field('endLifespanVersion', dsl.Date())
    properties.field('label', dsl.String())
    properties.field('nationalCadastralReference', dsl.String())
    properties.field('reference_point', dsl.GeoPoint(lat_lon=True))
    properties.field('elevation', dsl.Float())

    m.field('properties', properties)
    m.field('bbox', dsl.GeoShape())
    m.field('geometry', dsl.GeoShape())

    m.save(index)


def latlon_2_utm(lat, lon):
    return utm.from_latlon(lat, lon, force_zone_number=zone_number)


def utm_2_latlon(x, y):
    return utm.to_latlon(x, y, zone_number, zone_letter='N')


def get_gml_linear_ring(linear_ring_elem):
    linear_ring = []

    pos_list = linear_ring_elem.find('./gml:posList', ns)

    if pos_list is not None:
        linear_ring_text = pos_list.text

        if linear_ring_text is not None:
            linear_ring_coords = linear_ring_text.split()
            for c in range(0, len(linear_ring_coords), 2):
                lat, lon = utm_2_latlon(*map(lambda x: float(x), linear_ring_coords[c:(c+2)]))

                linear_ring.append([lon, lat])

    return linear_ring


def get_gml_geometry(cadastral_parcel):
    geometry = []

    linear_ring_elem = cadastral_parcel.find('./cp:geometry/gml:MultiSurface/gml:surfaceMember/gml:Surface/'
                                             'gml:patches/gml:PolygonPatch/gml:exterior/gml:LinearRing', ns)

    exterior_linear_ring = get_gml_linear_ring(linear_ring_elem) if linear_ring_elem is not None else []
    geometry.append(exterior_linear_ring)

    for interior_elem in cadastral_parcel.findall('./cp:geometry/gml:MultiSurface/gml:surfaceMember/gml:Surface/'
                                                  'gml:patches/gml:PolygonPatch/gml:interior/gml:LinearRing', ns):
        geometry.append(get_gml_linear_ring(interior_elem))

    return {'type': 'polygon',
            'coordinates': geometry}


def get_reference_point(cadastral_parcel):
    point_text = cadastral_parcel.find('./cp:referencePoint/gml:Point/gml:pos', ns).text

    reference_point = None

    if point_text is not None:
        lat, lon = utm_2_latlon(*map(lambda x: float(x), point_text.split()))

        reference_point = {'lat': lat,
                           'lon': lon}

    return reference_point


def get_gml_bbox(cadastral_parcel):
    envelope = cadastral_parcel.find('./gml:boundedBy/gml:Envelope', ns)
    lower_corner_txt = envelope.find('gml:lowerCorner', ns).text
    upper_corner_txt = envelope.find('gml:upperCorner', ns).text

    lower_corner = []
    if lower_corner_txt is not None:
        lat, lon = utm_2_latlon(*map(lambda x: float(x), lower_corner_txt.split()))
        lower_corner = [lon, lat]

    upper_corner = []
    if upper_corner_txt is not None:
        lat, lon = utm_2_latlon(*map(lambda x: float(x), upper_corner_txt.split()))
        upper_corner = [lon, lat]

    return {'type': 'envelope',
            'coordinates': [lower_corner, upper_corner]}


def parse_cadastral_parcel(cadastral_parcel_elem):
    parcel = dict()

    parcel['properties'] = dict()

    area_text = cadastral_parcel_elem.find('cp:areaValue', ns).text
    parcel['properties']['areaValue'] = float(area_text) if area_text is not None else None
    parcel['properties']['beginLifespanVersion'] = cadastral_parcel_elem.find('cp:beginLifespanVersion', ns).text
    parcel['properties']['endLifespanVersion'] = cadastral_parcel_elem.find('cp:endLifespanVersion', ns).text
    parcel['properties']['label'] = cadastral_parcel_elem.find('cp:label', ns).text
    parcel['properties']['nationalCadastralReference'] = cadastral_parcel_elem.find('cp:nationalCadastralReference', ns).text

    # read Reference point
    parcel['properties']['reference_point'] = get_reference_point(cadastral_parcel_elem)

    # read BBOX
    parcel['bbox'] = get_gml_bbox(cadastral_parcel_elem)

    # read geometry
    parcel['geometry'] = get_gml_geometry(cadastral_parcel_elem)

    return parcel


def parse_inspire_response(xml_text):
    parcels = []

    root = ET.fromstring(xml_text)

    for cadastral_parcel_elem in root.findall('./gml:featureMember/cp:CadastralParcel', ns):
        parcel = parse_cadastral_parcel(cadastral_parcel_elem)

        parcels.append(parcel)

    return parcels


def get_inspire_data_by_bbox(min_x, min_y, max_x, max_y):
    """
    Documented in http://www.catastro.minhap.es/webinspire/documentos/inspire-cp-WFS.pdf

    :param min_x:
    :param min_y:
    :param max_x:
    :param max_y:
    :return:
    """

    bbox_text = '{},{},{},{}'.format(min_x, min_y, max_x, max_y)

    response = requests.get(url_inspire, params={'service': 'wfs',
                                                 'request': 'getfeature',
                                                 'Typenames': 'cp.cadastralparcel',
                                                 'SRSname': 'EPSG::25830',
                                                 'bbox': bbox_text})

    if response.ok:
        parcels = parse_inspire_response(response.text)

        return parcels

    return []


def get_inspire_data_by_code(code):
    """
    Documented in http://www.catastro.minhap.es/webinspire/documentos/inspire-cp-WFS.pdf
    """

    response = requests.get(url_inspire, params={'service': 'wfs',
                                                 'request': 'getfeature',
                                                 'STOREDQUERIE_ID': 'GetParcel',
                                                 'srsname': 'EPSG::25830',
                                                 'REFCAT': code})

    if response.ok:
        parcels = parse_inspire_response(response.text)

        return parcels

    return []


def get_cadastral_parcels_by_bbox(min_lat, min_lon, max_lat, max_lon):
    min_x, min_y, zn, zl = latlon_2_utm(min_lat, min_lon)
    max_x, max_y, zn, zl = latlon_2_utm(max_lat, max_lon)

    parcels = get_inspire_data_by_bbox(min_x, min_y, max_x, max_y)

    return parcels


def get_cadastral_parcels_by_code(code):
    parcels = get_inspire_data_by_code(code)

    return parcels


def get_public_cadastre_info(code):
    response = requests.get(url_public_cadastral_info, params={'Provincia': '',
                                                               'Municipio': '',
                                                               'RC': code})

    if response.ok:
        root = ET.fromstring(response.text.encode('utf-8'))
        return xml_to_json(root)


def store_parcels(parcels):
    create_parcel_mapping('parcels')

    chunk_size = config.getint('elasticsearch', 'chunk_size')

    for i in range(0, len(parcels), chunk_size):
        records = parcels[i:i+chunk_size]
        ids = [r['properties']['nationalCadastralReference'] for r in records]

        elastic_bulk_save('STORE_PARCELS', 'parcels', 'parcel', records, ids)


