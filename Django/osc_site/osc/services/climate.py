# coding=utf-8

from elasticsearch import ElasticsearchException
from osc.exceptions import ElasticException
from geopy.distance import great_circle
from osc.util import error_managed, es

from django.conf import settings

es_index = settings.INFORIEGO['index']
es_daily_mapping = settings.INFORIEGO['daily.mapping']
es_station_mapping = settings.INFORIEGO['station.mapping']


@error_managed(default_answer={})
def get_closest_station(lat, lon):
    try:
        query = {"size": 1,
                 "sort": [
                     {
                         "_geo_distance": {
                             "lat_lon": {
                                 "lat": lat,
                                 "lon": lon
                             },
                             "order": "asc",
                             "unit": "km",
                             "mode": "min",
                             "distance_type": "sloppy_arc"
                         }
                     }
                 ]
                 }

        result = es.search(index=es_index, doc_type=es_station_mapping, body=query)

        stations = [hits['_source'] for hits in result['hits']['hits']]

        closest_station = {}

        if len(stations) == 1:
            closest_station = stations[0]

            this_loc = (lat, lon)
            station_loc = (closest_station['lat_lon']['lat'], closest_station['lat_lon']['lon'])

            closest_station['distance_to_parcel'] = great_circle(this_loc, station_loc).kilometers

        return closest_station

    except ElasticsearchException as e:
        raise ElasticException('CLIMATE', 'ElasticSearch Error getting closest station', e)


def parse_by_month(bymonth):
    result = []

    for year_info in bymonth:
        year = dict()
        year['year'] = year_info['key']
        year['monthly_measures'] = []

        for month_info in year_info['measure']['buckets']:
            month = dict()
            month['month'] = int(month_info['key_as_string'])
            month['rainfall'] = month_info['rainfall']['value']
            month['avg_temperature'] = month_info['avg_temperature']['value']
            month['radiation'] = month_info['radiation']['value']
            month['sun_hours'] = month_info['sun_hours']['value']

            year['monthly_measures'].append(month)

        result.append(year)

    return result


def parse_by_day(byday):
    result = []

    for year_info in byday:
        year = dict()
        year['year'] = year_info['key']
        year['daily_measures'] = []

        for day_info in year_info['measure']['buckets']:
            day = dict()
            day['day'] = day_info['key_as_string']
            day['avg_temperature'] = day_info['avg_temperature']['value']
            day['radiation'] = day_info['radiation']['value']
            day['sun_hours'] = day_info['sun_hours']['value']

            year['daily_measures'].append(day)

        result.append(year)

    return result


def parse_last_year(last_year):
    result = {}

    if len(last_year) == 1:
        result['max_sun_hours'] = last_year[0]['max_sun_hours']['value']
        result['sum_sun_hours'] = last_year[0]['sum_sun_hours']['value']
        result['avg_radiation'] = last_year[0]['avg_radiation']['value']
        result['avg_sun_hours'] = last_year[0]['avg_sun_hours']['value']
        result['avg_temperature'] = last_year[0]['avg_temperature']['value']
        result['sum_radiation'] = last_year[0]['sum_radiation']['value']
        result['max_temperature'] = last_year[0]['max_temperature']['value']
        result['sum_rainfall'] = last_year[0]['sum_rainfall']['value']
        result['sum_rainfall'] = last_year[0]['sum_rainfall']['value']
        result['min_temperature'] = last_year[0]['min_temperature']['value']
        result['max_radiation'] = last_year[0]['max_radiation']['value']
        result['rainy_days'] = last_year[0]['rainy_days']['doc_count']

    return result


@error_managed(default_answer={})
def get_aggregated_climate_measures(station_id, province_id, num_years_back):
    try:
        query = {
            "size": 0,
            "query": {
                "constant_score": {
                    "filter": {
                        "bool": {
                            "must": [
                                {
                                    "term": {
                                        "IDESTACION": station_id
                                    }
                                },
                                {
                                    "term": {
                                        "IDPROVINCIA": province_id
                                    }
                                }
                            ]
                        }
                    }
                }
            },
            "aggs": {
                "last_year": {
                    "terms": {
                        "field": u'AÑO',
                        "order": {
                            "_term": "desc"
                        },
                        "size": 1
                    },
                    "aggs": {
                        "sum_rainfall": {
                            "sum": {
                                "field": "PRECIPITACION"
                            }
                        },
                        "max_temperature": {
                            "max": {
                                "field": "TEMPMAX"
                            }
                        },
                        "min_temperature": {
                            "min": {
                                "field": "TEMPMIN"
                            }
                        },
                        "avg_temperature": {
                            "avg": {
                                "field": "TEMPMEDIA"
                            }
                        },
                        "avg_sun_hours": {
                            "avg": {
                                "field": "N"
                            }
                        },
                        "max_sun_hours": {
                            "max": {
                                "field": "N"
                            }
                        },
                        "sum_sun_hours": {
                            "sum": {
                                "field": "N"
                            }
                        },
                        "avg_radiation": {
                            "avg": {
                                "field": "RADIACION"
                            }
                        },
                        "max_radiation": {
                            "max": {
                                "field": "RADIACION"
                            }
                        },
                        "sum_radiation": {
                            "sum": {
                                "field": "RADIACION"
                            }
                        },
                        "rainy_days": {
                            "filter": {
                                "range": {
                                    "PRECIPITACION": {
                                        "gt": 0
                                    }
                                }
                            }
                        }
                    }
                },
                "by_month": {
                    "terms": {
                        "field": u'AÑO',
                        "order": {
                            "_term": "desc"
                        },
                        "size": num_years_back
                    },
                    "aggs": {
                        "measure": {
                            "date_histogram": {
                                "field": "FECHA",
                                "interval": "month",
                                "format": "M"
                            },
                            "aggs": {
                                "rainfall": {
                                    "sum": {
                                        "field": "PRECIPITACION"
                                    }
                                },
                                "avg_temperature": {
                                    "avg": {
                                        "field": "TEMPMEDIA"
                                    }
                                },
                                "sun_hours": {
                                    "sum": {
                                        "field": "N"
                                    }
                                },
                                "radiation": {
                                    "sum": {
                                        "field": "RADIACION"
                                    }
                                }
                            }
                        }
                    }
                },
                "by_day": {
                    "terms": {
                        "field": u'AÑO',
                        "order": {
                            "_term": "desc"
                        },
                        "size": num_years_back
                    },
                    "aggs": {
                        "measure": {
                            "date_histogram": {
                                "field": "FECHA",
                                "interval": "day",
                                "format": "dd-MM-yyyy"
                            },
                            "aggs": {
                                "avg_temperature": {
                                    "avg": {
                                        "field": "TEMPMEDIA"
                                    }
                                },
                                "sun_hours": {
                                    "sum": {
                                        "field": "N"
                                    }
                                },
                                "radiation": {
                                    "sum": {
                                        "field": "RADIACION"
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }

        result = es.search(index=es_index, doc_type=es_daily_mapping, body=query)

        hit = result['aggregations']

        by_month = parse_by_month(hit['by_month']['buckets'])
        by_day = parse_by_day(hit['by_day']['buckets'])
        last_year = parse_last_year(hit['last_year']['buckets'])

        return {'by_month': by_month,
                'by_day': by_day,
                'last_year': last_year}
    except ElasticsearchException as e:
        raise ElasticException('CLIMATE', 'ElasticSearch error getting climate aggregates', e)
