import ConfigParser
from osc_site.settings import *

SECRETS_PATH = '/home/osc/opensmartcountry.ini'

secrets = ConfigParser.ConfigParser()
secrets.read(SECRETS_PATH)

ELASTICSEARCH = {
    'chunk_size': 100,
    'host': '82.158.80.73',
    'port': 9200
}

GOOGLE_ELEVATION = {
    'chunk_size': 512,
    'api_key': secrets.get('Google Elevation', 'api_key')
}

INFORIEGO = {
    'url.daily': 'http://www.inforiego.org/opencms/rest/diario',
    'index': 'inforiego',
    'daily.mapping': 'info_riego_daily',
    'station.mapping': 'info_riego_station',
    'user': secrets.get('inforiego', 'user'),
    'passwd': secrets.get('inforiego', 'passwd')
}

SLACK = {
    'token': 'xoxb-59407964018-w5PcoTnCMt9A023kgE7BxCul',
    'flush_bucket': 200
}

WEB = {
    'url': 'http://89.141.96.206:8080'
}

AUX_DIRS = {
    'data_dir': '/opt/OpenSmartCountry/data',
    'tmp_dir': '/opt/OpenSmartCountry/tmp',
    'errors_dir': '/opt/OpenSmartCountry/errors',
    'dataframes_dir': '/opt/OpenSmartCountry/dataframes'
}

