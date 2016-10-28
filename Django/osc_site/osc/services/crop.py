from elasticsearch import ElasticsearchException
from osc.exceptions import ElasticException
from osc.util import error_managed, es

crop_index = 'osc'
crop_mapping = 'requirements'

__all__ = ['retrieve_crops_from_elastic']


def retrieve_crops_from_elastic(query):
    try:
        result = es.search(index=crop_index, doc_type=crop_mapping, body=query)

        crops = [{'_id': hits['_id'],
                  '_source': hits['_source']} for hits in result['hits']['hits']]

        return {'total': result['hits']['total'],
                'crops': crops}
    except ElasticsearchException as e:
        raise ElasticException('CROPS', 'ElasticSearch Error from query: ' + str(query), e)

