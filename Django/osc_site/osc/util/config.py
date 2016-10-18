import ConfigParser
import os

from elasticsearch_dsl.connections import connections

from osc.util.handlers import SlackErrorHandler, DBErrorHandler

import atexit

__all__ = ['config', 'get_data_dir', 'get_tmp_dir', 'get_error_dir', 'get_dataframes_dir', 'error_handler']

config = ConfigParser.ConfigParser(defaults={'data_dir': '../data',
                                             'tmp_dir': '../tmp',
                                             'errors_dir': '../errors',
                                             'token': '',
                                             'port': None,
                                             'chunk_size': '100',
                                             'flush_bucket': '1000'})

config.read([os.path.expanduser('~/opensmartcountry.ini')])

# Directories
data_dir = config.get('importer', 'data_dir')
tmp_dir = config.get('importer', 'tmp_dir')
error_dir = config.get('importer', 'errors_dir')
dataframes_dir = config.get('importer', 'dataframes_dir')


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

#web
url = config.get('web', 'url')


# Error handler
class ErrorHandler:

    error_handlers = None

    def __init__(self, error_handlers):
        self.error_handlers = error_handlers

    def error(self, process_name, module_name, function_name, message, actionable_info=None):
        for handler in self.error_handlers:
            handler.error(process_name, module_name, function_name, message, actionable_info)

    def warning(self, process_name, module_name, function_name, message, actionable_info=None):
        for handler in self.error_handlers:
            handler.warning(process_name, module_name, function_name, message, actionable_info)

    def flush(self):
        for handler in self.error_handlers:
            handler.flush()

error_handler = ErrorHandler([DBErrorHandler(),
                              SlackErrorHandler(config.get('slack', 'token'),
                                                config.getint('slack', 'flush_bucket'),
                                                url)])


def flush_handlers():
    error_handler.flush()


atexit.register(flush_handlers)

# Elastic Search
connections.create_connection('default', hosts=[
    {'host': config.get('elasticsearch', 'host'),
     'port': config.get('elasticsearch', 'port')}])

