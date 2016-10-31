import os

from elasticsearch import Elasticsearch
from django.conf import settings

__all__ = ['data_dir', 'tmp_dir', 'error_dir', 'dataframes_dir', 'es']

# Directories
data_dir = settings.AUX_DIRS['data_dir']
tmp_dir = settings.AUX_DIRS['tmp_dir']
error_dir = settings.AUX_DIRS['errors_dir']
dataframes_dir = settings.AUX_DIRS['dataframes_dir']

# Elastic Search
es = Elasticsearch('http://{}:{}'.format(settings.ELASTICSEARCH['host'], settings.ELASTICSEARCH['port']))

