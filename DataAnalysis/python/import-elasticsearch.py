import os
from elasticsearch_dsl.connections import connections
import osc.importer.inforiego as inforiego

connections.create_connection('casa-isa', hosts=['81.61.197.16:9200'], timeout=20)

data_dir = os.path.join(os.getenv('OSC_HOME', '../data'), 'data')
tmp_dir = os.path.join(os.getenv('OSC_HOME', '../tmp'), 'tmp')

inforiego.save2elasticsearch(years=['2016'],
                             data_dir=data_dir,
                             tmp_dir=tmp_dir)
