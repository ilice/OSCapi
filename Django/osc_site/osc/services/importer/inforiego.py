# -*- coding: utf-8 -*-
"""
Created on Sat Jul 02 18:27:40 2016

@author: jlafuente
"""

import logging
import elasticsearch_dsl as dsl
from elasticsearch_dsl.connections import connections
import requests
import calendar

import osc.util as util

__all__ = ['insert_all_stations_inforiego_daily',
           'insert_all_stations_inforiego_hourly',
           'get_stations_from_elastic']

logger = logging.Logger(__name__)

daily_url = util.config.get('inforiego', 'url.daily')
user = util.config.get('inforiego', 'user')
password = util.config.get('inforiego', 'passwd')
es_index = util.config.get('inforiego', 'index')
es_daily_mapping = util.config.get('inforiego', 'daily.mapping')
es_station_mapping = util.config.get('inforiego', 'station.mapping')


def get_stations_from_elastic(index=es_index,
                              mapping=es_station_mapping):
    stations = []
    s = dsl.Search(index=index, doc_type=mapping)
    s.execute()
    for station in s.scan():
        stations.append(station.to_dict())

    return stations

#############################################################
#                                                           #
#                      DAILY DATA                           #
#                                                           #
#############################################################


def get_inforiego_daily_year(provincia,
                             estacion,
                             anno=None,
                             fecha_ultima_modificacion=None,
                             url=daily_url,
                             user=user,
                             passwd=password):
    assert fecha_ultima_modificacion is not None or anno is not None

    if fecha_ultima_modificacion is None:
        fecha_ultima_modificacion = '01/01/' + str(anno)

    params = {'username': user,
              'password': passwd,
              'provincia': provincia,
              'estacion': estacion,
              'fecha_ult_modif': fecha_ultima_modificacion}

    if anno is not None:
        params['fecha_ini'] = '01/01/' + str(anno)
        params['fecha_fin'] = '31/12/' + str(anno)

    response = requests.get(url, params=params)

    return response.json()


def store_daily_document(document,
                         lat_lon,
                         altitud,
                         index=es_index,
                         mapping=es_daily_mapping):
    connection = connections.get_connection()

    document['lat_lon'] = lat_lon
    document['altitud'] = altitud
    try:
        if document['HORMINHUMMAX'] is not None:
            document['HORMINHUMMAX'] = document['HORMINHUMMAX'].zfill(4).replace('2400', '0000')

        if document['HORMINHUMMIN'] is not None:
            document['HORMINHUMMIN'] = document['HORMINHUMMIN'].zfill(4).replace('2400', '0000')

        if document['HORMINTEMPMAX'] is not None:
            document['HORMINTEMPMAX'] = document['HORMINTEMPMAX'].zfill(4).replace('2400', '0000')

        if document['HORMINTEMPMIN'] is not None:
            document['HORMINTEMPMIN'] = document['HORMINTEMPMIN'].zfill(4).replace('2400', '0000')

        if document['HORMINVELMAX'] is not None:
            document['HORMINVELMAX'] = document['HORMINVELMAX'].zfill(4).replace('2400', '0000')

        id = document[u'FECHA'].replace('/', '_') + '_' + \
             document[u'IDPROVINCIA'] + '_' + \
             document[u'IDESTACION']

        util.wait_for_yellow_cluster_status()
        connection.index(index=index, doc_type=mapping, id=id, body=document)
    except Exception as e:
        util.error_handler.error(__name__, "insert_inforiego_daily_years", str(document))


def insert_inforiego_daily_years(provincia,
                                 estacion,
                                 years,
                                 lat_lon,
                                 altitud,
                                 fecha_ultima_modificacion=None,
                                 index=es_index,
                                 mapping=es_daily_mapping,
                                 url=daily_url,
                                 user=user,
                                 passwd=password):
    for year in years:
        logger.info('Inserting year ' + year + ' province ' + provincia + ' station ' + estacion)
        response = get_inforiego_daily_year(provincia,
                                            estacion,
                                            anno=year,
                                            fecha_ultima_modificacion=fecha_ultima_modificacion,
                                            url=url,
                                            user=user,
                                            passwd=passwd)

        for document in response:
            store_daily_document(document, lat_lon, altitud, index, mapping)

        logger.info('Inserted year ' + year + ' province ' + provincia + ' station ' + estacion)


def insert_inforiego_daily_recent(provincia,
                                  estacion,
                                  lat_lon,
                                  altitud,
                                  fecha_ultima_modificacion=None,
                                  index=es_index,
                                  mapping=es_daily_mapping,
                                  url=daily_url,
                                  user=user,
                                  passwd=password):
    response = get_inforiego_daily_year(provincia,
                                        estacion,
                                        anno=None,
                                        fecha_ultima_modificacion=fecha_ultima_modificacion,
                                        url=url,
                                        user=user,
                                        passwd=passwd)

    for document in response:
        store_daily_document(document, lat_lon, altitud, index, mapping)


def insert_all_stations_inforiego_daily(years=None, fecha_ultima_modificacion=None):
    assert years is not None or fecha_ultima_modificacion is not None

    stations = get_stations_from_elastic()

    for station in stations:
        provincia = station['IDPROVINCIA']
        estacion = station['IDESTACION']
        lat_lon = station['lat_lon']
        altitud = station['ALTITUD']

        if years is None:
            insert_inforiego_daily_recent(provincia, estacion, lat_lon, altitud, fecha_ultima_modificacion)
        else:
            insert_inforiego_daily_years(provincia, estacion, years, lat_lon, altitud, fecha_ultima_modificacion)


###############################################################
##                                                           ##
##                      HOURLY DATA                          ##
##                                                           ##
###############################################################


def get_inforiego_hourly_month(provincia,
                               estacion,
                               anno=None,
                               mes=None,
                               fecha_ultima_modificacion=None,
                               url=daily_url,
                               user=user,
                               passwd=password):
    assert fecha_ultima_modificacion is not None or (anno is not None and mes is not None)

    if fecha_ultima_modificacion is None:
        mstart, mend = calendar.monthrange(anno, mes)
        fecha_ultima_modificacion = mstart + '/' + str(mes) + '/' + str(anno)

    params = {'username': user,
              'password': passwd,
              'provincia': provincia,
              'estacion': estacion,
              'fecha_ult_modif': fecha_ultima_modificacion}

    if anno is not None and mes is not None:
        mstart, mend = calendar.monthrange(anno, mes)

        params['fecha_ini'] = str(mstart) + '/' + str(mes) + '/' + str(anno)
        params['fecha_fin'] = str(mend) + '/' + str(mes) + '/' + str(anno)

    response = requests.get(url, params=params)

    return response.json()


def store_hourly_document(document,
                          lat_lon,
                          altitud,
                          index=es_index,
                          mapping=es_daily_mapping):
    connection = connections.get_connection()

    document['lat_lon'] = lat_lon
    document['altitud'] = altitud
    try:
        if document['HORAMIN'] is not None:
            document['HORAMIN'] = document['HORAMIN'].zfill(4).replace('2400', '0000')

        id = document[u'FECHA'].replace('/', '_') + '_' + \
             document[u'HORAMIN'] + '_' + \
             document[u'IDPROVINCIA'] + '_' + \
             document[u'IDESTACION']

        util.wait_for_yellow_cluster_status()
        connection.index(index=index, doc_type=mapping, id=id, body=document)
    except Exception as e:
        util.error_handler.error(__name__, "insert_inforiego_daily_years", str(document))


def insert_inforiego_hourly_years(provincia,
                                  estacion,
                                  years,
                                  lat_lon,
                                  altitud,
                                  fecha_ultima_modificacion=None,
                                  index=es_index,
                                  mapping=es_daily_mapping,
                                  url=daily_url,
                                  user=user,
                                  passwd=password):
    for year in years:
        for month in range(1, 13):
            logger.info('Inserting year ' + year + ' month ' + str(month) + ' province ' + provincia + ' station ' + estacion)
            response = get_inforiego_daily_year(provincia,
                                                estacion,
                                                anno=year,
                                                fecha_ultima_modificacion=fecha_ultima_modificacion,
                                                url=url,
                                                user=user,
                                                passwd=passwd)

            for document in response:
                store_daily_document(document, lat_lon, altitud, index, mapping)

            logger.info('Inserted year ' + year + ' month ' + str(month) + ' province ' + provincia + ' station ' + estacion)


def insert_inforiego_hourly_recent(provincia,
                                   estacion,
                                   lat_lon,
                                   altitud,
                                   fecha_ultima_modificacion,
                                   index=es_index,
                                   mapping=es_daily_mapping,
                                   url=daily_url,
                                   user=user,
                                   passwd=password):
    response = get_inforiego_daily_year(provincia,
                                        estacion,
                                        anno=None,
                                        fecha_ultima_modificacion=fecha_ultima_modificacion,
                                        url=url,
                                        user=user,
                                        passwd=passwd)

    for document in response:
        store_daily_document(document, lat_lon, altitud, index, mapping)


def insert_all_stations_inforiego_hourly(years=None, fecha_ultima_modificacion=None):
    assert years is not None or fecha_ultima_modificacion is not None

    stations = get_stations_from_elastic()

    for station in stations:
        provincia = station['IDPROVINCIA']
        estacion = station['IDESTACION']
        lat_lon = station['lat_lon']
        altitud = station['ALTITUD']

        if years is None:
            insert_inforiego_hourly_recent(provincia, estacion, lat_lon, altitud, fecha_ultima_modificacion)
        else:
            insert_inforiego_hourly_years(provincia, estacion, years, lat_lon, altitud, fecha_ultima_modificacion)
