import requests
import xml.etree.ElementTree as ET

import utm

__all__ = ['get_catastral_parcels']

url_catastral_code = 'http://ovc.catastro.meh.es/ovcservweb/OVCSWLocalizacionRC/OVCCallejero.asmx/Consulta_DNPRC'
url_inspire = 'http://ovc.catastro.meh.es/INSPIRE/wfsCP.aspx'
zone_number = 30

ns = {'gml': 'http://www.opengis.net/gml/3.2',
      'gmd': 'http://www.isotc211.org/2005/gmd',
      'ogc': 'http://www.opengis.net/ogc',
      'xlink': 'http://www.w3.org/1999/xlink',
      'cp': 'urn:x-inspire:specification:gmlas:CadastralParcels:3.0'
      }


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

                linear_ring.append([lat, lon])

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


def get_gml_reference_point(cadastral_parcel):
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
        lower_corner = [lat, lon]

    upper_corner = []
    if upper_corner_txt is not None:
        lat, lon = utm_2_latlon(*map(lambda x: float(x), upper_corner_txt.split()))
        upper_corner = [lat, lon]

    bbox = {'type': 'envelope',
            'coordinates': [lower_corner, upper_corner]}

    return bbox


def parse_inspire_response(xml_text):
    parcels = []

    root = ET.fromstring(xml_text)

    for cadastral_parcel_elem in root.findall('./gml:featureMember/cp:CadastralParcel', ns):
        parcel = dict()

        parcel['areaValue'] = cadastral_parcel_elem.find('cp:areaValue', ns).text
        parcel['beginLifespanVersion'] = cadastral_parcel_elem.find('cp:beginLifespanVersion', ns).text
        parcel['endLifespanVersion'] = cadastral_parcel_elem.find('cp:endLifespanVersion', ns).text
        parcel['label'] = cadastral_parcel_elem.find('cp:label', ns).text
        parcel['nationalCadastralReference'] = cadastral_parcel_elem.find('cp:nationalCadastralReference', ns).text

        #read BBOX
        parcel['bounded_by'] = get_gml_bbox(cadastral_parcel_elem)

        #read Reference point
        parcel['reference_point'] = get_gml_reference_point(cadastral_parcel_elem)

        #read geometry
        parcel['geometry'] = get_gml_geometry(cadastral_parcel_elem)

        parcels.append(parcel)

    return parcels


def get_inspire_data(min_x, min_y, max_x, max_y):
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

    if not response.ok:
        return None

    parcels = parse_inspire_response(response.text)

    return parcels


def get_catastral_parcels(min_lat, min_lon, max_lat, max_lon):
    min_x, min_y, zn, zl = latlon_2_utm(min_lat, min_lon)
    max_x, max_y, zn, zl = latlon_2_utm(max_lat, max_lon)

    parcels = get_inspire_data(min_x, min_y, max_x, max_y)

    return parcels
