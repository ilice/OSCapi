# coding=utf-8

from elasticsearch_dsl.query import *
from elasticsearch_dsl import Search


def get_closest_station(lat, lon):
    s = Search(index='inforiego', doc_type='info_riego_station')
    s.update_from_dict({
                       "size": 1,
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
                       })

    result = s.execute()
    hit = result.hits[0] if len(result.hits) == 1 else {}

    return hit.to_dict()


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


def parse_last_year(last_year):
    result = {}

    if len(last_year) == 1:
        result['max_sun_hours'] = last_year[0]['max_sun_hours']['value']
        result['avg_radiation'] = last_year[0]['avg_radiation']['value']
        result['avg_sun_hours'] = last_year[0]['avg_sun_hours']['value']
        result['avg_temperature'] = last_year[0]['avg_temperature']['value']
        result['sum_radiation'] = last_year[0]['sum_radiation']['value']
        result['max_temperature'] = last_year[0]['max_temperature']['value']
        result['sum_rainfall'] = last_year[0]['sum_rainfall']['value']
        result['sum_rainfall'] = last_year[0]['sum_rainfall']['value']
        result['min_temperature'] = last_year[0]['min_temperature']['value']
        result['max_radiation'] = last_year[0]['max_radiation']['value']

    return result


def get_aggregated_climate_measures(station_id, province_id, num_years_back):
    s = Search(index='inforiego', doc_type='info_riego_daily')
    s.update_from_dict({
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
                          }
                       }
                       })

    result = s.execute()
    hit = result.aggregations.to_dict()

    by_month = parse_by_month(hit['by_month']['buckets'])
    last_year = parse_last_year(hit['last_year']['buckets'])

    return { 'by_month': by_month,
             'last_year': last_year }