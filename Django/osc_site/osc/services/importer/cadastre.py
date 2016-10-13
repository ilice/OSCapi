import requests
import xml.etree.ElementTree as ET
import utm

__all__ = ['get_catastral_parcels']

url_catastral_code = 'http://ovc.catastro.meh.es/ovcservweb/OVCSWLocalizacionRC/OVCCallejero.asmx/Consulta_DNPRC'
url_inspire = 'http://ovc.catastro.meh.es/INSPIRE/wfsCP.aspx'
ns = {'gml': 'http://www.opengis.net/gml/3.2',
      'gmd': 'http://www.isotc211.org/2005/gmd',
      'ogc': 'http://www.opengis.net/ogc',
      'xlink': 'http://www.w3.org/1999/xlink',
      'cp': 'urn:x-inspire:specification:gmlas:CadastralParcels:3.0'
      }


def get_gml_reference_point(cadastral_parcel):
    point_text = cadastral_parcel.find('./cp:referencePoint/gml:Point/gml:pos', ns).text

    reference_point = None

    if point_text is not None:
        lat_lon = point_text.split()

        reference_point = {'lat': lat_lon[0],
                           'lon': lat_lon[1]}

    return reference_point

def get_gml_bbox(cadastral_parcel):
    envelope = cadastral_parcel.find('./gml:boundedBy/gml:Envelope', ns)
    lower_corner_txt = envelope.find('gml:lowerCorner', ns).text
    upper_corner_txt = envelope.find('gml:upperCorner', ns).text

    bbox = {'type': 'envelope',
            'coordinates': [lower_corner_txt.split() if lower_corner_txt is not None else [],
                            upper_corner_txt.split() if upper_corner_txt is not None else []]}

    return bbox


def parse_inspire_response(xml_text):
    parcels = []

    root = ET.fromstring(xml_text)

    for feature_member in root.findall('gml:featureMember', ns):
        for cadastral_parcel in feature_member.findall('cp:CadastralParcel', ns):
            parcel = dict()

            parcel['areaValue'] = cadastral_parcel.find('cp:areaValue', ns).text
            parcel['beginLifespanVersion'] = cadastral_parcel.find('cp:beginLifespanVersion', ns).text
            parcel['endLifespanVersion'] = cadastral_parcel.find('cp:endLifespanVersion', ns).text
            parcel['label'] = cadastral_parcel.find('cp:label', ns).text
            parcel['nationalCadastralReference'] = cadastral_parcel.find('cp:nationalCadastralReference', ns).text

            #read BBOX
            parcel['bounded_by'] = get_gml_bbox(cadastral_parcel)

            #read Reference point
            parcel['reference_point'] = get_gml_reference_point(cadastral_parcel)

            parcels.append(parcel)


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



def get_catastral_parcels(min_x, min_y, max_x, max_y):
    pass