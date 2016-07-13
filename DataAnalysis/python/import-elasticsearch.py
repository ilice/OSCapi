import os
from elasticsearch_dsl.connections import connections
import osc.importer.inforiego as inforiego
import sys

connections.create_connection('default', hosts=[
    {'host': 'search-opensmartcountry-trmalel6c5huhmpfhdh7j7m7ey.eu-west-1.es.amazonaws.com',
     'port': 9200}],
                              timeout=20)

"""
connections.create_connection('default', hosts=[{'host': 'search-opensmartcountry-trmalel6c5huhmpfhdh7j7m7ey.eu-west-1.es.amazonaws.com',
                                                 'port': None}],
                              timeout=20)
"""

data_dir = os.path.join(os.getenv('OSC_HOME', '..'), 'data')
err_dir = os.path.join(os.getenv('OSC_HOME', '..'), 'errors')
tmp_dir = os.path.join(os.getenv('OSC_HOME', '..'), 'tmp')
# encoding = 'mbcs'
encoding = 'iso-8859-1'

if __name__ == "__main__":
    for y in sys.argv[1:]:
        year = str(y)

        print 'Importing ' + year

        inforiego.save2elasticsearch(years=[year],
                                     data_dir=data_dir,
                                     encoding=encoding,
                                     tmp_dir=tmp_dir)
