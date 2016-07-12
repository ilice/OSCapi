import os
from elasticsearch_dsl.connections import connections
import osc.importer.inforiego as inforiego
import osc.util as util

connections.create_connection('default', hosts=['81.61.197.16:9200'], timeout=20)

data_dir = os.path.join(os.getenv('OSC_HOME', '..'), 'data')
err_dir = os.path.join(os.getenv('OSC_HOME', '..'), 'errors')
tmp_dir = os.path.join(os.getenv('OSC_HOME', '..'), 'tmp')
encoding = 'mbcs'
# encoding = 'iso-8859-1'

inforiego.set_error_handler(util.ErrorHandler(err_dir))

for y in ['2016', '2015', '2014', '2013', '2012', '2011', '2010', '2009', '2008', '2007', '2006',
          '2005', '2004', '2003', '2002', '2001']:
    year = str(y)

    print 'Importing ' + year

    inforiego.save2elasticsearch(years=[year],
                                 data_dir=data_dir,
                                 encoding=encoding,
                                 tmp_dir=tmp_dir)

