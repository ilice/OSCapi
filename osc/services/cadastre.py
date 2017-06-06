import Geohash
import logging
import requests
import xml.etree.ElementTree as ET

from django.conf import settings

from osc.exceptions import CadastreException
from osc.exceptions import ElasticException

from osc.services.google import obtain_elevation_from_google
from osc.util import elastic_bulk_save
from osc.util import elastic_bulk_update
from osc.util import elastic_update
from osc.util import error_managed
from osc.util import es
from osc.util import xml_to_json

from elasticsearch.client import IndicesClient
from elasticsearch import ElasticsearchException
from elasticsearch.helpers import scan
from pyproj import Proj

__all__ = ['get_parcels_by_bbox',
           'get_public_cadastre_info',
           'store_parcels',
           'get_parcels_by_cadastral_code']

logger = logging.getLogger(__name__)

# Example: http://ovc.catastro.meh.es/ovcservweb/OVCSWLocalizacionRC/
# OVCCallejero.asmx/Consulta_DNPRC?Provincia=&Municipio=&RC=11015A01400009
url_public_cadastral_info = settings.CADASTRE['cadastral_info_url']

# Example: http://ovc.catastro.meh.es/INSPIRE/wfsCP.aspx?
# service=wfs&request=getfeature&STOREDQUERIE_ID=GetParcel&SRSname=
# EPSG::25830&REFCAT=37284A01600146
url_inspire = settings.CADASTRE['url_inspire']

parcel_index = settings.CADASTRE['index']
parcel_mapping = settings.CADASTRE['mapping']

zone_for_queries = settings.CADASTRE['zone.for.queries']
max_elastic_query_size = settings.CADASTRE['max.query.size']

query_cadastre_when_bbox = settings.CADASTRE['query.cadastre.when.bbox']

ns = {'gml': 'http://www.opengis.net/gml/3.2',
      'gmd': 'http://www.isotc211.org/2005/gmd',
      'ogc': 'http://www.opengis.net/ogc',
      'xlink': 'http://www.w3.org/1999/xlink',
      'cp': 'urn:x-inspire:specification:gmlas:CadastralParcels:3.0',
      'ows': 'http://www.opengis.net/ows/1.1',
      'ct': 'http://www.catastro.meh.es/'
      }


class Parcel(object):
    def __init__(self):
        pass

    @staticmethod
    def get_cadastral_reference(parcel):
        return parcel['properties']['nationalCadastralReference']


@error_managed()
def get_zone_number(node):
    zone_number = None
    if 'srsName' in node.attrib:
        srs_name = node.attrib['srsName']

        pos = srs_name.find('EPSG')
        if pos > 0:
            zone_number = srs_name[pos:].replace('::', ':')
    if zone_number is None:
        raise CadastreException("No zone in srsName",
                                actionable_info=str(srs_name))

    return zone_number


def parse_inspire_exception(elem):
    exception = elem.find('ows:Exception', ns)
    exception_text_elem = elem.find('./ows:Exception/ows:ExceptionText', ns)

    message = ''
    if exception is not None \
       and exception.attrib is not None \
       and 'exceptionCode' in exception.attrib:
        message += exception.attrib['exceptionCode']
    message += ' - '

    if exception_text_elem is not None:
        message += exception_text_elem.text

    return message


def parse_cadastre_exception(elem):
    message = ''

    err_cod = elem.find('./ct:lerr/ct:err/ct:cod', ns).text
    err_msg = elem.find('./ct:lerr/ct:err/ct:des', ns).text

    if err_cod is not None and err_msg is not None:
        message = 'code: ' + err_cod + ' message: ' + err_msg

    return message


def create_parcel_mapping():

    idx_client = IndicesClient(es)

    mapping = {
        "properties": {
            "bbox": {
                "type": "geo_shape"
            },
            "geometry": {
                "properties": {
                    "coordinates": {
                        "type": "float",
                        "index": "no"
                    },
                    "type": {
                        "type": "keyword",
                        "index": "no"
                    }
                }
            },
            "properties": {
                "properties": {
                    "areaValue": {
                        "type": "float"
                    },
                    "beginLifespanVersion": {
                        "type": "date"
                    },
                    "elevation": {
                        "type": "float"
                    },
                    "endLifespanVersion": {
                        "type": "date"
                    },
                    "label": {
                        "type": "keyword",
                    },
                    "nationalCadastralReference": {
                        "type": "keyword"
                    },
                    "reference_point": {
                        "type": "geo_point"
                    },
                    "cadastralData": {
                        "properties": {
                            "bico": {
                                "properties": {
                                    "bi": {
                                        "properties": {
                                            "debi": {
                                                "properties": {
                                                    "ant": {
                                                        "type": "short"
                                                    },
                                                    "cpt": {
                                                        "type": "keyword"
                                                    },
                                                    "luso": {
                                                        "type": "keyword"
                                                    },
                                                    "sfc": {
                                                        "type": "keyword"
                                                    }
                                                }
                                            },
                                            "dt": {
                                                "properties": {
                                                    "cmc": {
                                                        "type": "keyword"
                                                    },
                                                    "locs": {
                                                        "properties": {
                                                            "lors": {
                                                                "properties": {
                                                                    "lorus": {
                                                                        "properties": {
                                                                            "cpaj": {
                                                                                "type": "keyword"
                                                                            },
                                                                            "cpp": {
                                                                                "properties": {
                                                                                    "cpa": {
                                                                                        "type": "keyword"
                                                                                    },
                                                                                    "cpo": {
                                                                                        "type": "keyword"
                                                                                    }
                                                                                }
                                                                            },
                                                                            "czc": {
                                                                                "type": "keyword"
                                                                            },
                                                                            "npa": {
                                                                                "type": "keyword"
                                                                            }
                                                                        }
                                                                    }
                                                                }
                                                            },
                                                            "lous": {
                                                                "properties": {
                                                                    "lourb": {
                                                                        "properties": {
                                                                            "dir": {
                                                                                "properties": {
                                                                                    "cv": {
                                                                                        "type": "keyword"
                                                                                    },
                                                                                    "nv": {
                                                                                        "type": "keyword"
                                                                                    },
                                                                                    "pnp": {
                                                                                        "type": "keyword"
                                                                                    },
                                                                                    "snp": {
                                                                                        "type": "keyword"
                                                                                    },
                                                                                    "tv": {
                                                                                        "type": "keyword"
                                                                                    }
                                                                                }
                                                                            },
                                                                            "dm": {
                                                                                "type": "keyword"
                                                                            },
                                                                            "dp": {
                                                                                "type": "keyword"
                                                                            },
                                                                            "loint": {
                                                                                "properties": {
                                                                                    "es": {
                                                                                        "type": "keyword"
                                                                                    },
                                                                                    "pt": {
                                                                                        "type": "keyword"
                                                                                    },
                                                                                    "pu": {
                                                                                        "type": "keyword"
                                                                                    }
                                                                                }
                                                                            }
                                                                        }
                                                                    }
                                                                }
                                                            }
                                                        }
                                                    },
                                                    "loine": {
                                                        "properties": {
                                                            "cm": {
                                                                "type": "keyword"
                                                            },
                                                            "cp": {
                                                                "type": "keyword"
                                                            }
                                                        }
                                                    },
                                                    "nm": {
                                                        "type": "keyword"
                                                    },
                                                    "np": {
                                                        "type": "keyword"
                                                    }
                                                }
                                            },
                                            "idbi": {
                                                "properties": {
                                                    "cn": {
                                                        "type": "keyword"
                                                    },
                                                    "rc": {
                                                        "properties": {
                                                            "car": {
                                                                "type": "keyword"
                                                            },
                                                            "cc1": {
                                                                "type": "keyword"
                                                            },
                                                            "cc2": {
                                                                "type": "keyword"
                                                            },
                                                            "pc1": {
                                                                "type": "keyword"
                                                            },
                                                            "pc2": {
                                                                "type": "keyword"
                                                            }
                                                        }
                                                    }
                                                }
                                            },
                                            "ldt": {
                                                "type": "text"
                                            }
                                        }
                                    },
                                    "lcons": {
                                        "properties": {
                                            "cons": {
                                                "type": "nested",
                                                "properties": {
                                                    "dfcons": {
                                                        "properties": {
                                                            "stl": {
                                                                "type": "keyword"
                                                            }
                                                        }
                                                    },
                                                    "dt": {
                                                        "properties": {
                                                            "lourb": {
                                                                "properties": {
                                                                    "loint": {
                                                                        "properties": {
                                                                            "es": {
                                                                                "type": "keyword"
                                                                            },
                                                                            "pt": {
                                                                                "type": "keyword"
                                                                            },
                                                                            "pu": {
                                                                                "type": "keyword"
                                                                            }
                                                                        }
                                                                    }
                                                                }
                                                            }
                                                        }
                                                    },
                                                    "lcd": {
                                                        "type": "keyword"
                                                    }
                                                }
                                            }
                                        }
                                    },
                                    "lspr": {
                                        "properties": {
                                            "spr": {
                                                "type": "nested",
                                                "properties": {
                                                    "cspr": {
                                                        "type": "keyword"
                                                    },
                                                    "dspr": {
                                                        "properties": {
                                                            "ccc": {
                                                                "type": "keyword"
                                                            },
                                                            "dcc": {
                                                                "type": "keyword"
                                                            },
                                                            "ip": {
                                                                "type": "keyword"
                                                            },
                                                            "ssp": {
                                                                "type": "keyword"
                                                            }
                                                        }
                                                    }
                                                }
                                            }
                                        }
                                    }
                                }
                            },
                            "control": {
                                "properties": {
                                    "cucons": {
                                        "type": "long"
                                    },
                                    "cucul": {
                                        "type": "long"
                                    },
                                    "cudnp": {
                                        "type": "long"
                                    }
                                }
                            },
                            "lrcdnp": {
                                "properties": {
                                    "rcdnp": {
                                        "type": "nested",
                                        "properties": {
                                            "dt": {
                                                "properties": {
                                                    "cmc": {
                                                        "type": "keyword"
                                                    },
                                                    "locs": {
                                                        "properties": {
                                                            "lous": {
                                                                "properties": {
                                                                    "lourb": {
                                                                        "properties": {
                                                                            "dir": {
                                                                                "properties": {
                                                                                    "cv": {
                                                                                        "type": "keyword"
                                                                                    },
                                                                                    "nv": {
                                                                                        "type": "keyword"
                                                                                    },
                                                                                    "pnp": {
                                                                                        "type": "keyword"
                                                                                    },
                                                                                    "snp": {
                                                                                        "type": "keyword"
                                                                                    },
                                                                                    "tv": {
                                                                                        "type": "keyword"
                                                                                    }
                                                                                }
                                                                            },
                                                                            "dm": {
                                                                                "type": "keyword"
                                                                            },
                                                                            "dp": {
                                                                                "type": "keyword"
                                                                            },
                                                                            "loint": {
                                                                                "properties": {
                                                                                    "pt": {
                                                                                        "type": "keyword"
                                                                                    },
                                                                                    "pu": {
                                                                                        "type": "keyword"
                                                                                    }
                                                                                }
                                                                            }
                                                                        }
                                                                    }
                                                                }
                                                            }
                                                        }
                                                    },
                                                    "loine": {
                                                        "properties": {
                                                            "cm": {
                                                                "type": "keyword"
                                                            },
                                                            "cp": {
                                                                "type": "keyword"
                                                            }
                                                        }
                                                    },
                                                    "nm": {
                                                        "type": "keyword"
                                                    },
                                                    "np": {
                                                        "type": "keyword"
                                                    }
                                                }
                                            },
                                            "rc": {
                                                "properties": {
                                                    "car": {
                                                        "type": "keyword"
                                                    },
                                                    "cc1": {
                                                        "type": "keyword"
                                                    },
                                                    "cc2": {
                                                        "type": "keyword"
                                                    },
                                                    "pc1": {
                                                        "type": "keyword"
                                                    },
                                                    "pc2": {
                                                        "type": "keyword"
                                                    }
                                                }
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }

                }
            }
        }
    }

    if not idx_client.exists(index=parcel_index):
        idx_client.create(index=parcel_index)

    idx_client.put_mapping(doc_type=parcel_mapping,
                           index=[parcel_index],
                           body=mapping)


def latlon_2_utm(lat, lon, zone_number):
    p = Proj(init=zone_number)
    return p(lon, lat)


def utm_2_latlon(x, y, zone_number):
    p = Proj(init=zone_number)
    lon, lat = p(x, y, inverse=True)
    return lat, lon


def get_gml_linear_ring(linear_ring_elem, zone_number):
    linear_ring = []

    pos_list = linear_ring_elem.find('./gml:posList', ns)

    if pos_list is not None:
        linear_ring_text = pos_list.text

        if linear_ring_text is not None:
            linear_ring_coords = linear_ring_text.split()
            for c in range(0, len(linear_ring_coords), 2):
                lat, lon = utm_2_latlon(*map(lambda x: float(x),
                                        linear_ring_coords[c:(c+2)]),
                                        zone_number=zone_number)

                linear_ring.append([lon, lat])

    return linear_ring


@error_managed()
def get_gml_geometry(cadastral_parcel):
    geometry = []

    surface_elem = cadastral_parcel.find(
        './cp:geometry/gml:MultiSurface/gml:surfaceMember/gml:Surface',
        ns)
    zone_number = get_zone_number(surface_elem)

    linear_ring_elem = surface_elem.find(
        './gml:patches/gml:PolygonPatch/gml:exterior/gml:LinearRing',
        ns)

    exterior_linear_ring = \
        get_gml_linear_ring(linear_ring_elem, zone_number=zone_number) \
        if linear_ring_elem is not None else []
    geometry.append(exterior_linear_ring)

    for interior_elem in cadastral_parcel.findall(
            './cp:geometry/gml:MultiSurface/gml:surfaceMember/gml:Surface/'
            'gml:patches/gml:PolygonPatch/gml:interior/gml:LinearRing',
            ns):
        geometry.append(get_gml_linear_ring(interior_elem,
                                            zone_number=zone_number))

    return {'type': 'polygon',
            'coordinates': geometry}


def get_reference_point(cadastral_parcel):
    point_node = cadastral_parcel.find('./cp:referencePoint/gml:Point', ns)

    zone_number = get_zone_number(point_node)

    point_text = point_node.find('./gml:pos', ns).text

    reference_point = None

    if point_text is not None:
        lat, lon = utm_2_latlon(*map(lambda x: float(x), point_text.split()),
                                zone_number=zone_number)

        reference_point = {'lat': lat,
                           'lon': lon}

    return reference_point


def get_gml_bbox(cadastral_parcel):
    envelope = cadastral_parcel.find('./gml:boundedBy/gml:Envelope', ns)

    zone_number = get_zone_number(envelope)

    lower_corner_txt = envelope.find('gml:lowerCorner', ns).text
    upper_corner_txt = envelope.find('gml:upperCorner', ns).text

    lower_corner = []
    if lower_corner_txt is not None:
        lat, lon = utm_2_latlon(*map(lambda x: float(x),
                                lower_corner_txt.split()),
                                zone_number=zone_number)
        lower_corner = [lon, lat]

    upper_corner = []
    if upper_corner_txt is not None:
        lat, lon = utm_2_latlon(
            *map(lambda x: float(x), upper_corner_txt.split()),
            zone_number=zone_number)
        upper_corner = [lon, lat]

    return {'type': 'envelope',
            'coordinates': [lower_corner, upper_corner]}


@error_managed(default_answer=None, inhibit_exception=True)
def parse_cadastral_parcel(cadastral_parcel_elem):
    parcel = dict()

    try:
        parcel['properties'] = dict()

        area_text = cadastral_parcel_elem.find('cp:areaValue', ns).text
        parcel['properties']['areaValue'] = \
            float(area_text) if area_text is not None else None
        parcel['properties']['beginLifespanVersion'] = \
            cadastral_parcel_elem.find('cp:beginLifespanVersion', ns).text
        parcel['properties']['endLifespanVersion'] = \
            cadastral_parcel_elem.find('cp:endLifespanVersion', ns).text
        parcel['properties']['label'] = \
            cadastral_parcel_elem.find('cp:label', ns).text
        parcel['properties']['nationalCadastralReference'] = \
            cadastral_parcel_elem.find('cp:nationalCadastralReference',
                                       ns).text

        # read Reference point
        parcel['properties']['reference_point'] = \
            get_reference_point(cadastral_parcel_elem)

        # read BBOX
        parcel['bbox'] = get_gml_bbox(cadastral_parcel_elem)

        # read geometry
        parcel['geometry'] = get_gml_geometry(cadastral_parcel_elem)
    except Exception as e:
        raise CadastreException(e.message,
                                cause=e,
                                actionable_info=str(parcel))

    return parcel


@error_managed(default_answer=[])
def parse_inspire_response(xml_text):
    logger.debug('parse_inspire_response(%s)', xml_text)
    parcels = []

    root = ET.fromstring(xml_text)

    if 'ExceptionReport' in root.tag:
        raise CadastreException(parse_inspire_exception(root))

    for cadastral_parcel_elem in root.findall(
            './gml:featureMember/cp:CadastralParcel', ns):
        parcel = parse_cadastral_parcel(cadastral_parcel_elem)

        if parcel is not None:
            parcels.append(parcel)

    return parcels


@error_managed(default_answer=[])
def get_inspire_data_by_bbox(min_x, min_y, max_x, max_y):
    """Documented in

    http://www.catastro.minhap.es/webinspire/documentos/inspire-cp-WFS.pdf
    :param min_x:
    :param min_y:
    :param max_x:
    :param max_y:
    :return:
    """

    bbox_text = '{},{},{},{}'.format(min_x, min_y, max_x, max_y)

    response = requests.get(url_inspire,
                            params={'service': 'wfs',
                                    'request': 'getfeature',
                                    'Typenames': 'cp.cadastralparcel',
                                    'SRSname': zone_for_queries,
                                    'bbox': bbox_text})

    if response.ok:
        parcels = parse_inspire_response(response.text)
    else:
        raise CadastreException('Error connecting to ' + url_inspire +
                                '. Status code: ' + response.status_code)

    return parcels


@error_managed(default_answer=[])
def get_inspire_data_by_code(codes):
    """Documented in:

    http://www.catastro.minhap.es/webinspire/documentos/inspire-cp-WFS.pdf
    """
    logger.debug('get_inspire_data_by_code(%s)', codes)
    parcels = []

    response = requests.get(url_inspire,
                            params={'service': 'wfs',
                                    'request': 'getfeature',
                                    'STOREDQUERIE_ID': 'GetParcel',
                                    'srsname': zone_for_queries,
                                    'REFCAT': codes})
    if response.ok:
        parcels += parse_inspire_response(response.text)
    else:
        raise CadastreException('Error connecting to '
                                + url_inspire
                                + '. Status code: '
                                + str(response.status_code))
    return parcels


def get_cadastral_parcels_by_bbox(
        min_lat, min_lon,
        max_lat, max_lon,
        zone_number=zone_for_queries.replace('::', ':')):
    min_x, min_y = latlon_2_utm(min_lat, min_lon, zone_number=zone_number)
    max_x, max_y = latlon_2_utm(max_lat, max_lon, zone_number=zone_number)

    parcels = get_inspire_data_by_bbox(min_x, min_y, max_x, max_y)

    add_public_cadastral_info(parcels)
    add_elevation_from_google(parcels)

    return parcels


@error_managed(default_answer={})
def parse_public_cadastre_response(elem):
    logger.debug('parse_public_cadastre_response(%s)', elem)
    if elem.find('./ct:control/ct:cuerr', ns) is not None:
        raise CadastreException(parse_cadastre_exception(elem))

    # The 'lists' come from the xsd:
    # http://www.catastro.meh.es/ws/esquemas/consulta_dnp.xsd
    return xml_to_json(elem,
                       lists=['cons', 'spr', 'rcdnp', 'calle'],
                       forced_int=['cumun', 'cuca', 'cunum', 'cudnp',
                                   'cucons', 'cucul', 'cuerr'])


@error_managed(default_answer={}, inhibit_exception=True)
def get_public_cadastre_info(code):
    logger.debug('get_public_cadastre_info(%s)', code)
    response = requests.get(url_public_cadastral_info, params={'Provincia': '',
                                                               'Municipio': '',
                                                               'RC': code})

    if response.ok:
        root = ET.fromstring(response.text.encode('utf-8'))
        return parse_public_cadastre_response(root)
    else:
        raise CadastreException('Error connecting to '
                                + url_public_cadastral_info
                                + '. Status code: '
                                + str(response.status_code))


def store_parcels(parcels):
    chunk_size = settings.ELASTICSEARCH['chunk_size']

    for i in range(0, len(parcels), chunk_size):
        records = parcels[i:i+chunk_size]
        ids = [Parcel.get_cadastral_reference(r) for r in records]

        elastic_bulk_save('STORE_PARCELS',
                          parcel_index,
                          parcel_mapping,
                          records,
                          ids)


def update_parcels(parcels):
    chunk_size = settings.ELASTICSEARCH['chunk_size']

    for i in range(0, len(parcels), chunk_size):
        records = parcels[i:i+chunk_size]
        ids = [Parcel.get_cadastral_reference(r) for r in records]

        elastic_bulk_update('STORE_PARCELS',
                            parcel_index,
                            parcel_mapping,
                            records,
                            ids)


def update_parcel(parcel):
    logger.debug('update_parcel(%s)', parcel)
    elastic_update('UPDATE_PARCEL',
                   parcel_index,
                   parcel_mapping,
                   parcel,
                   Parcel.get_cadastral_reference(parcel))


@error_managed(default_answer=[])
def get_parcels_by_cadastral_code(cadastral_code,
                                  include_public_info=False,
                                  include_google_info=False):
    logger.debug('get_parcels_by_cadastral_code(%s,%s)',
                 cadastral_code,
                 include_public_info)
    try:
        query = {
            "query": {
                "match": {
                    "properties.nationalCadastralReference": cadastral_code
                }
            }
        }

        result = es.search(index=parcel_index,
                           doc_type=parcel_mapping,
                           body=query)

        parcels = [hits['_source'] for hits in result['hits']['hits']]

        if not parcels:
            parcels = get_inspire_data_by_code(cadastral_code)

        if include_public_info:
            add_public_cadastral_info(parcels)

        # Convert into geojson
        for parcel in parcels:
            parcel['type'] = 'Feature'
        if include_google_info:
            add_elevation_from_google(parcels)

        return parcels
    except ElasticsearchException as e:
        raise ElasticException('PARCEL', e.message, e)


@error_managed(inhibit_exception=True)
def index_parcel(parcel):
    try:
        es.index(index=parcel_index,
                 doc_type=parcel_mapping,
                 body=parcel,
                 id=Parcel.get_cadastral_reference(parcel))
    except ElasticsearchException as e:
        raise ElasticException('CADASTRE',
                               'Error indexing parcel',
                               cause=e,
                               actionable_info=parcel)


@error_managed()
def add_public_cadastral_info(parcels):
    logger.debug('add_public_cadastral_info(%s)', parcels)
    to_update = []

    for parcel in parcels:
        if 'cadastralData' not in parcel['properties'] \
                or not parcel['properties']['cadastralData']:

            public_info = get_public_cadastre_info(
                Parcel.get_cadastral_reference(parcel))

            if public_info:
                parcel['properties']['cadastralData'] = public_info

                # add to elastic
                to_update.append(Parcel.get_cadastral_reference(parcel))

    return to_update


@error_managed(inhibit_exception=True, default_answer=())
def add_elevation_from_google(parcels):
    logger.debug('add_elevation_from_google(%s)', parcels)
    to_update = []
    pending_elevations = \
        filter(lambda x: 'elevation' not in x['properties']
               and 'reference_point' in x['properties'], parcels)

    if pending_elevations:
        centers = [(parcel['properties']['reference_point']['lat'],
                    parcel['properties']['reference_point']['lon'])
                   for parcel in pending_elevations]

        elevations = obtain_elevation_from_google(centers)

        if elevations:
            for item in zip(elevations, pending_elevations):
                elevation = item[0]
                parcel = item[1]

                parcel['properties']['elevation'] = elevation

                to_update.append(Parcel.get_cadastral_reference(parcel))

    return to_update


@error_managed(default_answer={})
def get_parcels_by_bbox(min_lat, min_lon, max_lat, max_lon):
    try:
        query = {
            "query": {
                "bool": {
                    "must": {
                        "match_all": {}
                    },
                    "filter": {
                        "geo_shape": {
                            "bbox": {
                                "shape": {
                                    "type": "envelope",
                                    "coordinates": [
                                        [min_lon, min_lat],
                                        [max_lon, max_lat]]
                                }
                            }
                        }
                    }
                }
            }
        }

        result = es.search(index=parcel_index,
                           doc_type=parcel_mapping,
                           body=query,
                           size=max_elastic_query_size)

        parcels = [hits['_source'] for hits in result['hits']['hits']]

        if query_cadastre_when_bbox:
            to_update = list()
            to_update += add_public_cadastral_info(parcels)
            to_update += add_elevation_from_google(parcels)

            to_update = set(to_update)

            updatable_parcels = [parcel for parcel in parcels
                                 if Parcel.get_cadastral_reference(parcel)
                                 in to_update]
            store_parcels(updatable_parcels)

        # Convert into geojson
        for parcel in parcels:
            parcel['type'] = 'Feature'

        parcels_geojson = {'type': 'FeatureCollection',
                           'features': parcels}

        return parcels_geojson
    except ElasticsearchException as e:
        raise ElasticException('PARCEL', e.message, e)


@error_managed(default_answer={})
def get_bucket_of_parcels_by_bbox_and_precision(
        min_lat, min_lon, max_lat, max_lon, precision):
    try:
        query = {
            "size": 0,
            "query": {
                "bool": {
                    "must": {
                        "match_all": {}
                    },
                    "filter": {
                        "geo_shape": {
                            "bbox": {
                                "shape": {
                                    "type": "envelope",
                                    "coordinates": [
                                        [min_lon, min_lat],
                                        [max_lon, max_lat]]
                                }
                            }
                        }
                    }
                }
            },
            "aggs": {
                "2": {
                    "geohash_grid": {
                        "field": "properties.reference_point",
                        "precision": precision
                    },
                    "aggs": {
                        "area": {
                            "sum": {
                                "field": "properties.areaValue"
                            }
                        }
                    }
                }
            }
        }

        result = es.search(
            index=parcel_index,
            doc_type=parcel_mapping,
            body=query,
            request_timeout=30)

        parcels_buckets = []
        max = min = 0
        for bucket in result['aggregations']['2']['buckets']:
            (lat, lng, lat_err, lng_err) = Geohash.decode_exactly(
                bucket['key'])
            parcels_buckets.append(
                {"geometry": {
                    "type": "Point",
                    "coordinates": [float(lng), float(lat)]},
                    "properties": {
                        "value": bucket['doc_count'],
                        "area": bucket['area']['value']},
                    "type": "Feature"})
            if bucket['doc_count'] > max:
                max = bucket['doc_count']
            if bucket['doc_count'] < min:
                min = bucket['doc_count']

        for parcel in parcels_buckets:
            parcel['properties']['num_buckets'] = len(parcels_buckets)
            parcel['properties']['min_value'] = min
            parcel['properties']['max_value'] = max

        parcels_geojson = {'type': 'FeatureCollection',
                           'features': parcels_buckets,
                           'properties': {
                               'total': result['hits']['total'],
                               'num_buckets': len(parcels_buckets),
                               'max': max,
                               'min': min
                               }
                           }

        return parcels_geojson
    except ElasticsearchException as e:
        raise ElasticException('PARCEL', e.message, e)


def scan_parcels(update):
    # TODO(teanocrata) must update all parcels but we need to have cadastre
    # info as soon as possible, remove query then.
    query = {
        "_source": [
            "properties.nationalCadastralReference"
        ],
        "query": {
            "bool": {
                "must_not": {
                    "exists": {
                        "field": "properties.cadastralData"
                    }
                }
            }
        }
    }
    index = 'parcels'
    doc_type = 'parcel'
    result_parcels = scan(es,
                          query=query,
                          scroll=u'5m',
                          size=100,
                          index=index,
                          doc_type=doc_type)
    for parcel in result_parcels:
        update(parcel['_source']['properties']['nationalCadastralReference'])
