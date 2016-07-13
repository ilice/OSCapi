from slack.error_bot import ErrorHandler
from elasticsearch_dsl.connections import connections
import logging
import ConfigParser
import os

config = ConfigParser.ConfigParser(defaults={'data_dir': '../data',
                                             'tmp_dir': '../tmp',
                                             'token': '',
                                             'port': None})

config.read([os.path.expanduser('~/opensmartcountry.ini')])

# Logging configuration
FORMAT = '%(asctime)-15s %(clientip)s %(user)-8s %(message)s'
logging.basicConfig(format=FORMAT)

# Error handler
error_handler = ErrorHandler(config.get('slack', 'token'))

# Elastic Search
connections.create_connection('default', hosts=[
    {'host': config.get('elasticsearch', 'host'),
     'port': config.get('elasticsearch', 'port')}],
                              timeout=20)
