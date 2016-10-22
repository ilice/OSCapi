import ConfigParser
from osc_site.settings import *

SECRETS_PATH = 'C:/Users/jlafu/opensmartcountry.ini'

secrets = ConfigParser.ConfigParser()
secrets.read(SECRETS_PATH)

ELASTICSEARCH = {
    'chunk_size': 100,
    'host': '94.76.229.213',
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
    'token': secrets.get('slack', 'token'),
    'flush_bucket': 200
}

WEB = {
    'url': 'http://89.141.96.206:8080'
}

AUX_DIRS = {
    'data_dir': 'C:/Users/jlafu/Downloads/OpenSmartCountry/data',
    'tmp_dir': 'C:/Users/jlafu/Downloads/OpenSmartCountry/tmp',
    'errors_dir': 'C:/Users/jlafu/Downloads/OpenSmartCountry/errors',
    'dataframes_dir': 'C:/Users/jlafu/Downloads/OpenSmartCountry/dataframes'
}

