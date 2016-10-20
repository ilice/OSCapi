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

url_atom_inspire = 'http://www.catastro.minhap.es/INSPIRE/CadastralParcels/ES.SDGC.CP.atom.xml'


@error_managed(default_answer=[])
def get_parcels_from_url(zipfile_url):
    parcels = []

    r = requests.get(zipfile_url, stream=True)
    if r.ok:
        z = zipfile.ZipFile(StringIO.StringIO(r.content))

        files_to_parse = [x for x in z.namelist() if 'cadastralparcel' in x]

        for gml_file in files_to_parse:
            xml_text = z.read(gml_file)
            parcels = parse_inspire_response(xml_text)

    else:
        raise CadastreException('Error connecting to ' + zipfile_url + '. Status code: ' + r.status_code)
    return parcels


@error_managed()
def update_catastral_municipality(municipality, force_update=False):
    last_update_date = get_last_successful_update_date(municipality.link)

    if force_update or last_update_date is None or last_update_date < get_update_date(municipality):
        feed_id = start_feed_read(municipality.link, get_update_date(municipality))

        try:
            parcels = get_parcels_from_url(municipality.link)

            store_parcels(parcels)
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

    return datetime(year=updated_parsed.tm_year,
                    month=updated_parsed.tm_mon,
                    day=updated_parsed.tm_mday,
                    hour=updated_parsed.tm_hour,
                    minute=updated_parsed.tm_min,
                    second=updated_parsed.tm_sec)


@error_managed
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


