from elasticsearch import ElasticsearchException
from osc.exceptions import ElasticException
from osc.util import error_managed, es

crop_index = 'osc'
crop_mapping = 'requirements'

__all__ = ['retrieve_crops_from_elastic', 'update_crops_in_elastic', 'index_crops_in_elastic']


def retrieve_crops_from_elastic(query):
    try:
        result = es.search(index=crop_index, doc_type=crop_mapping, body=query)

        crops = [hits for hits in result['hits']['hits']]

        return {'total': result['hits']['total'],
                'crops': crops}
    except ElasticsearchException as e:
        raise ElasticException('CROPS', 'ElasticSearch Error from query: ' + str(query), e)


def update_crops_in_elastic(crop_id, query):
    try:
        es.update(index=crop_index, doc_type=crop_mapping, id=crop_id, body=query)
    except ElasticsearchException as e:
        raise ElasticException('CROPS', 'ElasticSearch Error from query: ' + str(query), e)


def index_crops_in_elastic(crop_id, query):
    try:
        es.index(index=crop_index, doc_type=crop_mapping, id=crop_id, body=query)
    except ElasticsearchException as e:
        raise ElasticException('CROPS', 'ElasticSearch Error from query: ' + str(query), e)
