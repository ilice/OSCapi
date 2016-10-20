import ConfigParser
from osc_site.settings import *

SECRETS_PATH = '/code/tmp/secrets.ini'

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
    'token': secrets.get('slack', 'token'),
    'flush_bucket': 200
}

WEB = {
    'url': 'http://89.141.96.206:8080'
}

AUX_DIRS = {
    'data_dir': '/code/tmp/data',
    'tmp_dir': '/code/tmp/tmp',
    'errors_dir': '/code/tmp/errors',
    'dataframes_dir': '/code/tmp/dataframes'
}

DATABASES = {
     'default': {
         'ENGINE': 'django.db.backends.postgresql_psycopg2',
         'NAME': 'postgres',
         'USER': 'postgres',
         'HOST': 'db',
         'PORT': 5432,
     }
}