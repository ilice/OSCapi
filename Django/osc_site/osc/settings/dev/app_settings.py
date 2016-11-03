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

CADASTRE = {
    'index': 'parcels',
    'mapping': 'parcel',
    'zone.for.queries': 'EPSG::25830',
    'query.cadastre.when.bbox': True,
    'max.query.size': 5000
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
    'log_dir': 'C:/Users/jlafu/Downloads/OpenSmartCountry/logs',
    'errors_dir': 'C:/Users/jlafu/Downloads/OpenSmartCountry/errors',
    'dataframes_dir': 'C:/Users/jlafu/Downloads/OpenSmartCountry/dataframes'
}

for dir_name in AUX_DIRS:
    if not os.path.exists(AUX_DIRS[dir_name]):
        os.makedirs(AUX_DIRS[dir_name])

LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'standard': {
            'format': "[%(asctime)s] %(levelname)s [%(name)s:%(lineno)s] %(message)s",
            'datefmt': "%d/%b/%Y %H:%M:%S"
        },
    },
    'handlers': {
        'logfile': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': AUX_DIRS['log_dir'] + "/osc.log",
            'maxBytes': 50000,
            'backupCount': 2,
            'formatter': 'standard',
        },
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'standard'
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'propagate': True,
            'level': 'WARN',
        },
        'django.db.backends': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'osc': {
            'handlers': ['console', 'logfile'],
            'level': 'DEBUG',
        },
    }
}