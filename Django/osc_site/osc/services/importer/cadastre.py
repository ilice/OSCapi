import feedparser
import requests
import zipfile
import StringIO
from osc.util import contains_any
from datetime import datetime
from osc.services import start_feed_read, finish_feed_read, get_last_successful_update_date, store_parcels
from osc.util import error_managed

from osc.services.cadastre import parse_inspire_response
from osc.exceptions import CadastreException

import pytz
from django.conf import settings

url_atom_inspire = 'http://www.catastro.minhap.es/INSPIRE/CadastralParcels/ES.SDGC.CP.atom.xml'


def partition_inspire_xml_file(xml_file, chunk_size):
    parcel_start = '<gml:featureMember>'
    parcel_end = '</gml:featureMember>'

    header = ''
    footer = '</gml:FeatureCollection>'
    chunk = []

    header_read = False

    parcels = 0

    for line in xml_file:
        # capture parcel start
        if parcel_start in line:
            header_read = True

        # Consider finding the footer
        if footer in line:
            xml_chunk = join(chunk, footer, header)
            chunk = []
            yield xml_chunk

        # distinguish between header and chunk
        if header_read:
            chunk.append(line)
        else:
            header += line

        # check wether parcel has ended
        if parcel_end in line:
            parcels += 1
            if parcels >= chunk_size:
                xml_chunk = join(chunk, footer, header)
                chunk = []
                parcels = 0
                yield xml_chunk


def join(chunk, footer, header):
    xml_list = [header] + chunk + [footer]
    xml_chunk = ''.join(xml_list)
    return xml_chunk


@error_managed(default_answer=[])
def store_parcels_from_url(zipfile_url, chunk_size=1000):
    r = requests.get(zipfile_url, stream=True)
    if r.ok:
        z = zipfile.ZipFile(StringIO.StringIO(r.content))

        files_to_parse = [x for x in z.namelist() if 'cadastralparcel' in x]

        for gml_file in files_to_parse:
            xml_file = z.open(gml_file)
            for xml_chunk in partition_inspire_xml_file(xml_file, chunk_size):
                parcels = parse_inspire_response(xml_chunk)
                store_parcels(parcels)
    else:
        raise CadastreException('Error connecting to ' + zipfile_url + '. Status code: ' + r.status_code)


@error_managed()
def update_catastral_municipality(municipality, force_update=False):
    last_update_date = get_last_successful_update_date(municipality.link)

    if force_update or last_update_date is None or last_update_date < get_update_date(municipality):
        feed_id = start_feed_read(municipality.link, get_update_date(municipality))

        try:
            store_parcels_from_url(municipality.link)

            finish_feed_read(feed_id, True)
        except Exception as e:
            finish_feed_read(feed_id, False, e.message)
            raise


@error_managed()
def update_catastral_province(province, force_update=False):
    last_update_date = get_last_successful_update_date(province.link)

    if force_update or last_update_date is None or last_update_date < get_update_date(province):
        feed_id = start_feed_read(province.link, get_update_date(province))
        feed = feedparser.parse(province.link)

        try:
            for municipality in feed.entries:
                update_catastral_municipality(municipality, force_update)

            finish_feed_read(feed_id, True)
        except Exception as e:
            finish_feed_read(feed_id, False, e.message)
            raise


def get_update_date(feed):
    updated_parsed = feed.updated_parsed

    date = datetime(year=updated_parsed.tm_year,
                    month=updated_parsed.tm_mon,
                    day=updated_parsed.tm_mday,
                    hour=updated_parsed.tm_hour,
                    minute=updated_parsed.tm_min,
                    second=updated_parsed.tm_sec)

    return pytz.timezone(settings.TIME_ZONE).localize(date)


@error_managed()
def update_cadastral_information(force_update=False, provinces=None):
    feed = feedparser.parse(url_atom_inspire)

    last_update_date = get_last_successful_update_date(url_atom_inspire)

    if force_update or last_update_date is None or last_update_date < get_update_date(feed):
        feed_id = start_feed_read(url_atom_inspire, get_update_date(feed))

        try:
            for province in feed.entries:
                if provinces is None or contains_any(feed.title, provinces):
                    update_catastral_province(province, force_update)
            finish_feed_read(feed_id, True)
        except Exception as e:
            finish_feed_read(feed_id, False, e.message)
            raise


