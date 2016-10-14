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
                          "by_year": {
                             "terms": {
                                "field": u'AÑO',
                                "order": {
                                   "_term": "desc"
                                },
                                "size": 1
                             },
                             "aggs": {
                                "sum_precipitation": {
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
                                      "precipitation": {
                                         "sum": {
                                            "field": "PRECIPITACION"
                                         }
                                      },
                                      "temperature": {
                                         "avg": {
                                            "field": "TEMPERATURA"
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
    hit = result.aggregations

    return hit.to_dict()