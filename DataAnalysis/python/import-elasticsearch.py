import os
from elasticsearch_dsl.connections import connections
import osc.importer.inforiego as inforiego
import osc.util as util
import sys

connections.create_connection('default', hosts=['search-opensmartcountry-trmalel6c5huhmpfhdh7j7m7ey.eu-west-1.es.amazonaws.com'], timeout=20)

data_dir = os.path.join(os.getenv('OSC_HOME', '..'), 'data')
err_dir = os.path.join(os.getenv('OSC_HOME', '..'), 'errors')
tmp_dir = os.path.join(os.getenv('OSC_HOME', '..'), 'tmp')
# encoding = 'mbcs'
encoding = 'iso-8859-1'

inforiego.set_error_handler(util.ErrorHandler(err_dir))

if __name__ == "__main__":
    for y in sys.argv[1:]:
        year = str(y)

        print 'Importing ' + year

        inforiego.save2elasticsearch(years=[year],
                                     data_dir=data_dir,
                                     encoding=encoding,
                                     tmp_dir=tmp_dir)
