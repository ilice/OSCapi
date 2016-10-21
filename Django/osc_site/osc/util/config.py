import os

from elasticsearch_dsl.connections import connections
from django.conf import settings


__all__ = ['get_data_dir', 'get_tmp_dir', 'get_error_dir', 'get_dataframes_dir']

# Directories
data_dir = settings.AUX_DIRS['data_dir']
tmp_dir = settings.AUX_DIRS['tmp_dir']
error_dir = settings.AUX_DIRS['errors_dir']
dataframes_dir = settings.AUX_DIRS['dataframes_dir']


def get_data_dir():
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
    return data_dir


def get_tmp_dir():
    if not os.path.exists(tmp_dir):
        os.makedirs(tmp_dir)
    return tmp_dir


def get_error_dir():
    if not os.path.exists(error_dir):
        os.makedirs(error_dir)
    return error_dir


def get_dataframes_dir():
    if not os.path.exists(dataframes_dir):
        os.makedirs(dataframes_dir)
    return dataframes_dir

# Elastic Search
connections.create_connection('default', hosts=[
    {'host': settings.ELASTICSEARCH['host'],
     'port': settings.ELASTICSEARCH['port']}])

