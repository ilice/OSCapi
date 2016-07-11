import os
from elasticsearch_dsl.connections import connections
import osc.importer.inforiego as inforiego

connections.create_connection('default', hosts=['81.61.197.16:9200'], timeout=20)

data_dir = os.path.join(os.getenv('OSC_HOME', '..'), 'data')
tmp_dir = os.path.join(os.getenv('OSC_HOME', '..'), 'tmp')

print 'Importing 2014-2016'

inforiego.save2elasticsearch(years=['2014', '2015', '2016'],
                             data_dir=data_dir,
                             tmp_dir=tmp_dir)


print 'Importing 2011-2013'
inforiego.save2elasticsearch(years=['2011', '2012', '2013'],
                             data_dir=data_dir,
                             tmp_dir=tmp_dir)

print 'Importing 2008-2010'

inforiego.save2elasticsearch(years=['2008', '2009', '2010'],
                             data_dir=data_dir,
                             tmp_dir=tmp_dir)

print 'Importing 2005-2007'

inforiego.save2elasticsearch(years=['2005', '2006', '2007'],
                             data_dir=data_dir,
                             tmp_dir=tmp_dir)

print 'Importing 2002-2004'

inforiego.save2elasticsearch(years=['2002', '2003', '2004'],
                             data_dir=data_dir,
                             tmp_dir=tmp_dir)

print 'Importing 2001'

inforiego.save2elasticsearch(years=['2001'],
                             data_dir=data_dir,
                             tmp_dir=tmp_dir)

