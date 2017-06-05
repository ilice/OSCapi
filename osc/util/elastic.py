import elasticsearch.helpers as es_helpers
import certifi
from osc.util import error_managed
from osc.exceptions import ElasticException
from elasticsearch import Elasticsearch
from django.conf import settings

__all__ = ['wait_for_yellow_cluster_status', 'elastic_bulk_update', 'elastic_bulk_save', 'elastic_update', 'es']


# Elastic Search
es = Elasticsearch([settings.ELASTICSEARCH['host']],
                   port=settings.ELASTICSEARCH['port'],
                   use_ssl=settings.ELASTICSEARCH['use_ssl'])


def wait_for_yellow_cluster_status():
    while True:
        try:
            cluster_status = es.cluster.health(wait_for_status='yellow')
            if cluster_status['status'] != 'red':
                break
        except Exception as e:
            print ('Cluster status is red. Waiting for yellow status')


@error_managed()
def elastic_bulk_update(process_name, index, doc_type, records, ids=None, retry=True):
    try:
        if ids is None:
            ids = [None] * len(records)

        wait_for_yellow_cluster_status()
        es_helpers.bulk(es,
                        ({'_op_type': 'update',
                          '_index': index,
                          '_id': idx,
                          '_type': doc_type,
                          '_source': r} for (r, idx) in zip(records, ids)))
    except Exception as e:
        for (r, idx) in zip(records, ids):
            if retry:
                elastic_bulk_update(process_name, index, doc_type, [r], [idx], retry=False)
            else:
                raise ElasticException(process_name, 'Error saving to Elastic', actionable_info=str(r))


@error_managed(inhibit_exception=True)
def elastic_bulk_save(process_name, index, doc_type, records, ids=None, parents=None, retry=True):
    try:
        if ids is None:
            ids = [None] * len(records)

        if parents is None:
            parents = [None] * len(records)

        wait_for_yellow_cluster_status()
        es_helpers.bulk(es,
                        ({'_index': index,
                          '_id': idx,
                          '_parent': parent,
                          '_type': doc_type,
                          '_source': r} for (r, idx, parent) in zip(records, ids, parents)))
    except Exception as e:
        for (r, idx) in zip(records, ids):
            if retry:
                elastic_bulk_save(process_name, index, doc_type, [r], [idx], retry=False)
            else:
                raise ElasticException(process_name, 'Error saving to Elastic', actionable_info=str(r), cause=e)


@error_managed()
def elastic_update(process_name, index, doc_type, record, id):
    try:
        wait_for_yellow_cluster_status()
        es.index(index=index, doc_type=doc_type, id=id, body=record)
    except Exception as e:
        raise ElasticException(process_name,
                               'Error saving to Elastic',
                               actionable_info="",
                               cause=e)
