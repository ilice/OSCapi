import certifi
from django.conf import settings
from elasticsearch import Elasticsearch
import elasticsearch.helpers as es_helpers
from elasticsearch import TransportError
import itertools
import logging

from osc.exceptions import ElasticException
from osc.util import error_managed
from osc.util import timer


logger = logging.getLogger(__name__)

__all__ = ['wait_for_yellow_cluster_status',
           'elastic_bulk_update',
           'elastic_bulk_save',
           'elastic_update',
           'es']

timeout = settings.ELASTICSEARCH['timeout']

# Elastic Search
es = Elasticsearch([settings.ELASTICSEARCH['host']],
                   port=settings.ELASTICSEARCH['port'],
                   use_ssl=settings.ELASTICSEARCH['use_ssl'])


@error_managed()
def wait_for_yellow_cluster_status(process_name):
    logger.debug('Check cluster status, waiting for yellow or green status...')
    for retry in itertools.count():
        with timer.elapsed_timer() as elapsed:
            if elapsed() < timeout:
                try:
                    cluster_status = es.cluster.health(
                        wait_for_status='yellow',
                        timeout=timeout)
                    logger.debug('Cluster status: %s',
                                 cluster_status['status'])
                    if cluster_status['status'] != 'red':
                        break
                    raise Exception('Red status')
                except TransportError as e:
                    if retry > settings.ELASTICSEARCH['retries']:
                        raise ElasticException(process_name,
                                               'Error connecting to elastic',
                                               cause=str(e))
                except Exception as e:
                    if retry > settings.ELASTICSEARCH['retries']:
                        raise ElasticException(
                            process_name,
                            'Error waiting for yellow status',
                            cause=str(e))


@error_managed()
def elastic_bulk_update(process_name,
                        index,
                        doc_type,
                        records,
                        ids=None,
                        retry=True):
    try:
        if ids is None:
            ids = [None] * len(records)

        wait_for_yellow_cluster_status(process_name)
        es_helpers.bulk(es,
                        ({'_op_type': 'update',
                          '_index': index,
                          '_id': idx,
                          '_type': doc_type,
                          '_source': r} for (r, idx) in zip(records, ids)))
    except Exception as e:
        for (r, idx) in zip(records, ids):
            if retry:
                elastic_bulk_update(process_name,
                                    index,
                                    doc_type,
                                    [r],
                                    [idx],
                                    retry=False)
            else:
                raise ElasticException(process_name,
                                       'Error saving to Elastic',
                                       cause=e.message,
                                       actionable_info=str(r))


@error_managed(inhibit_exception=True)
def elastic_bulk_save(process_name,
                      index,
                      doc_type,
                      records,
                      ids=None,
                      parents=None,
                      retry=True):
    try:
        if ids is None:
            ids = [None] * len(records)

        if parents is None:
            parents = [None] * len(records)

        wait_for_yellow_cluster_status(process_name)
        es_helpers.bulk(es,
                        ({'_index': index,
                          '_id': idx,
                          '_parent': parent,
                          '_type': doc_type,
                          '_source': r} for (r, idx, parent) in zip(records,
                                                                    ids,
                                                                    parents)))
    except Exception as e:
        for (r, idx) in zip(records, ids):
            if retry:
                elastic_bulk_save(process_name,
                                  index,
                                  doc_type,
                                  [r],
                                  [idx],
                                  retry=False)
            else:
                raise ElasticException(process_name,
                                       'Error saving to Elastic',
                                       actionable_info=str(r),
                                       cause=e)


@error_managed()
def elastic_update(process_name, index, doc_type, record, id):
    try:
        wait_for_yellow_cluster_status(process_name)
        es.index(index=index, doc_type=doc_type, id=id, body=record)
    except Exception as e:
        raise ElasticException(process_name,
                               'Error saving to Elastic',
                               actionable_info="",
                               cause=e)
