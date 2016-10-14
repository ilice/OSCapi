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
                          "por_anio": {
                             "terms": {
                                "field": u'AÑO',
                                "order": {
                                   "_term": "desc"
                                },
                                "size": 1
                             },
                             "aggs": {
                                "sum_precipitacion": {
                                   "sum": {
                                      "field": "PRECIPITACION"
                                   }
                                },
                                "max_temperatura": {
                                   "max": {
                                      "field": "TEMPMAX"
                                   }
                                },
                                "min_temperatura": {
                                   "min": {
                                      "field": "TEMPMIN"
                                   }
                                },
                                "media_temperatura": {
                                   "avg": {
                                      "field": "TEMPMEDIA"
                                   }
                                },
                                "media_horas_sol": {
                                   "avg": {
                                      "field": "N"
                                   }
                                },
                                "max_horas_sol": {
                                   "max": {
                                      "field": "N"
                                   }
                                },
                                "sum_horas_sol": {
                                   "sum": {
                                      "field": "N"
                                   }
                                },
                                "media_radiacion": {
                                   "avg": {
                                      "field": "RADIACION"
                                   }
                                },
                                "max_radiacion": {
                                   "max": {
                                      "field": "RADIACION"
                                   }
                                },
                                "sum_radiacion": {
                                   "sum": {
                                      "field": "RADIACION"
                                   }
                                }

                             }
                          },
                          "por_mes": {
                             "terms": {
                                "field": u'AÑO',
                                "order": {
                                   "_term": "desc"
                                },
                                "size": num_years_back
                             },
                             "aggs": {
                                "medida": {
                                   "date_histogram": {
                                      "field": "FECHA",
                                      "interval": "month",
                                      "format": "M"
                                   },
                                   "aggs": {
                                      "precipitacion": {
                                         "sum": {
                                            "field": "PRECIPITACION"
                                         }
                                      },
                                      "temperatura": {
                                         "avg": {
                                            "field": "TEMPERATURA"
                                         }
                                      },
                                      "horas_sol": {
                                         "sum": {
                                            "field": "N"
                                         }
                                      },
                                      "radiacion": {
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
    hit = result.aggregations

    return hit.to_dict()