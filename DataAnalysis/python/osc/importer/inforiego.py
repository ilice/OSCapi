# -*- coding: utf-8 -*-
"""
Created on Sat Jul 02 18:27:40 2016

@author: jlafuente
"""

import ftplib
import logging
import os
import elasticsearch_dsl as dsl
from elasticsearch_dsl.connections import connections
import pandas as pd
import osc.config as conf
import requests

from osc import util

import utm

logger = logging.Logger(__name__)

def as_list(param):
    if type(param) is list:
        return param
    return [param]


def path(data_dir, year=None):
    path_str = os.path.join(data_dir, 'InfoRiego')
    
    if year is not None:
        path_str = os.path.join(path_str, str(year))
        
    return path_str


def read_stations(data_dir='../data'):
    csv_path = os.path.join(path(data_dir), 'UbicacionEstacionesITACyL 2009.csv')

    locations = pd.read_csv(csv_path,
                            sep=';',
                            encoding=None)
    locations.columns = ['province', 'station', 'code', 'name', 'longitude',
                         'latitude', 'height', 'xutm', 'yutm']
    return locations


###############################################################
##                                                           ##
##                      HOURLY DATA                          ##
##                                                           ##
###############################################################

def get_daily_files_list(year,
                         url='ftp.itacyl.es',
                         root_dir='/Meteorologia/Datos_observacion_Red_InfoRiego/DatosHorarios'):
    try:
        ftp = ftplib.FTP(url, user='anonymous', passwd='')
        ftp.cwd(root_dir + '/' + year)

        files = ftp.nlst()
        ftp.close()

        return files
    except Exception as e:
        conf.error_handler.error(__name__, "get_daily_files_list", year + ': ' + str(e))
        return []


def download_daily_files(years,
                         url='ftp.itacyl.es',
                         root_dir='/Meteorologia/Datos_observacion_Red_InfoRiego/DatosHorarios',
                         data_dir='../data',
                         force_download=True,
                         tmp_dir='./tmp'):
    years = as_list(years)
                          
    for year in years:
        working_dir = path(data_dir, year)

        print os.path.exists(working_dir)
        
        if os.path.exists(working_dir) and not force_download:
            continue

        print "Downloading " + working_dir

        try:
            ftp = ftplib.FTP(url, user='anonymous', passwd='')
            ftp.cwd(root_dir + '/' + year)

            # Check the files in the directory
            files = ftp.nlst()

            if len(files) == 0:
                raise NameError(year)

            if not os.path.exists(tmp_dir):
                os.makedirs(tmp_dir)

            for zipFile in files:
                zipfile_path = tmp_dir + '/' + zipFile

                with open(zipfile_path, 'wb') as f:
                    logger.info("Downloading " + zipfile_path)
                    ftp.retrbinary('RETR ' + zipFile, f.write)
                    logger.info("... downloaded.")

                # uncompress the zipfile
                util.unzip_file(zipfile_path,
                                working_dir)

                # remove the file
                # os.remove(compressedShapeFilePath)
            ftp.close()
        except Exception as e:
            conf.error_handler.error(__name__, "download_daily_files", year + ': ' + str(e))


def get_dataframe(years,
                  url='ftp.itacyl.es',
                  root_dir='/Meteorologia/Datos_observacion_Red_InfoRiego/DatosHorarios',
                  data_dir='../data',
                  force_download=False,
                  encoding=None,
                  tmp_dir='./tmp'):
    # download if necessary
    download_daily_files(years=years,
                         url=url,
                         root_dir=root_dir,
                         data_dir=data_dir,
                         force_download=force_download,
                         tmp_dir=tmp_dir)

    csv_paths = [os.path.join(path(data_dir, year), fileName)
                 for year in as_list(years)
                 for fileName in os.listdir(path(data_dir, year))]
                
    print "Composing data frame"

    dataframes = []
    for csvPath in csv_paths:
        try:
            print "Reading data frame " + csvPath
            dataframes.append(pd.read_csv(csvPath,
                                          dtype={u'Hora (HHMM)': str,
                                                 u'Fecha (AAAA-MM-DD)': str},
                                          sep=';',
                                          encoding=encoding,
                                          error_bad_lines=False))
        except Exception as e:
            conf.error_handler.error(__name__, "get_dataframe", csvPath + ': ' + str(e))

    
    dataframe = pd.concat(dataframes)
    
    # Filter registers with incorrect date
    dataframe = dataframe[(dataframe[u'Fecha (AAAA-MM-DD)'].str.len() == 10) &
                          (dataframe[u'Hora (HHMM)'].str.len() == 4)]

    # rename the columns so they are more clear
    dataframe.columns = ['code', 'location', 'day', 'hour', 'rain', 'temperature',
                         'rel_humidity', 'radiation', 'wind_speed', 'wind_direction']

    dataframe['date'] = pd.to_datetime(dataframe['day'] + ' ' +
                                       dataframe['hour'].replace('2400', '0000'),
                                       format='%Y-%m-%d %H%M')

    dataframe = dataframe.drop(['day', 'hour'], axis=1)

    dataframe.index = dataframe['date']

    return dataframe


# Elastic Search
class InfoRiegoRecord(dsl.DocType):
    code = dsl.String()
    location = dsl.String()
    date = dsl.Date()
    rain = dsl.Float()
    temperature = dsl.Float()
    rel_humidity = dsl.Float()
    radiation = dsl.Float()
    wind_speed = dsl.Float()
    wind_direction = dsl.Float()

    lat_lon = dsl.GeoPoint(lat_lon=True)
    station_height = dsl.Integer()

    def save(self, ** kwargs):
        return super(InfoRiegoRecord, self).save(** kwargs)

    class Meta:
        index = 'inforiego'

def build_record(row):
    record = InfoRiegoRecord(meta={'id': row.code + ' - ' + str(row.date)},
                             code=row.code,
                             location=row.location,
                             date=row.date,
                             rain=float(row.rain),
                             temperature=float(row.temperature),
                             rel_humidity = float(row.rel_humidity),
                             radiation=float(row.radiation),
                             wind_speed=float(row.wind_speed),
                             wind_direction=float(row.wind_direction),
                             station_height=int(row.height))

    lat, lon = utm.to_latlon(row.xutm, row.yutm, 30, northern=True)
    record.lat_lon = {'lat': lat, 'lon': lon}

    return record


def save2elasticsearch(years,
                       url='ftp.itacyl.es',
                       root_dir='/Meteorologia/Datos_observacion_Red_InfoRiego/DatosHorarios',
                       force_download=False,
                       encoding=None,
                       data_dir='../data',
                       tmp_dir='./tmp'):
    try:
        InfoRiegoRecord.init()
    except Exception as e:
        conf.error_handler.error(__name__, "build_record", str(e))
        conf.error_handler.flush()
        raise

    # download if necessary
    dataframe = get_dataframe(years=years,
                              url=url,
                              root_dir=root_dir,
                              force_download=force_download,
                              encoding=encoding,
                              data_dir=data_dir,
                              tmp_dir=tmp_dir)
    locations = read_stations(data_dir)

    dataframe = pd.merge(dataframe, locations, on='code', how='outer')

    for t in dataframe.itertuples():
        record = build_record(t)
        try:
            record.save()
        except Exception as e:
            conf.error_handler.error(__name__,
                                     'save2elasticsearch',
                                     record.code + '_' + record.date.strftime(format='%Y%m%d%H%M') + ':' + str(record))


###############################################################
##                                                           ##
##                      DAILY DATA                           ##
##                                                           ##
###############################################################


def get_stations_from_elastic(index=conf.inforiego_index,
                              mapping=conf.inforiego_station_mapping):
    stations = []
    s = dsl.Search(index=index, doc_type=mapping)
    s.execute()
    for station in s.scan():
        stations.append(station.to_dict())

    return stations


def get_inforiego_daily_year(provincia,
                             estacion,
                             anno,
                             url=conf.inforiego_daily_url,
                             user=conf.inforiego_user,
                             passwd=conf.inforiego_password):
    response = requests.get(url,
                            params={'username': user,
                                    'password': passwd,
                                    'provincia': provincia,
                                    'estacion': estacion,
                                    'fecha_ini': '01/01/' + str(anno),
                                    'fecha_fin': '31/12/' + str(anno),
                                    'fecha_ult_modif': '01/01/' + str(anno)})


    return response.json()


def insert_inforiego_daily_years(provincia,
                                 estacion,
                                 years,
                                 lat_lon,
                                 altitud,
                                 index=conf.inforiego_index,
                                 mapping=conf.inforiego_daily_mapping,
                                 url=conf.inforiego_daily_url,
                                 user=conf.inforiego_user,
                                 passwd=conf.inforiego_password):

    connection = connections.get_connection()

    for year in years:
        print 'Inserting year ' + year + ' province ' + provincia + ' station ' + estacion
        response = get_inforiego_daily_year(provincia, estacion, year, url, user, passwd)

        for document in response:
            document['lat_lon'] = lat_lon
            document['altitud'] = altitud
            if 'HORMINHUMMAX' in document:
                document['HORMINHUMMAX'] = document['HORMINHUMMAX'].zfill(4).replace('2400', '0000')
            if 'HORMINHUMMIN' in document:
                document['HORMINHUMMIN'] = document['HORMINHUMMIN'].zfill(4).replace('2400', '0000')
            if 'HORMINTEMPMAX' in document:
                document['HORMINTEMPMAX'] = document['HORMINTEMPMAX'].zfill(4).replace('2400', '0000')
            if 'HORMINTEMPMIN' in document:
                document['HORMINTEMPMIN'] = document['HORMINTEMPMIN'].zfill(4).replace('2400', '0000')
            if 'HORMINVELMAX' in document:
                document['HORMINVELMAX'] = document['HORMINVELMAX'].zfill(4).replace('2400', '0000')

            id = document[u'FECHA'].replace('/', '_') + '_' + \
                 document[u'IDPROVINCIA'] + '_' + \
                 document[u'IDESTACION']

            try:
                util.wait_for_yellow_cluster_status()
                connection.index(index=index, doc_type=mapping, id=id, body=document)
            except Exception as e:
                conf.error_handler.error(__name__, "insert_inforiego_daily_years", str(document))

        print 'Inserted year ' + year + ' province ' + provincia + ' station ' + estacion


def insert_all_stations_inforiego_daily(years):
    stations = get_stations_from_elastic()

    for station in stations:
        provincia = station['IDPROVINCIA']
        estacion = station['IDESTACION']
        lat_lon = station['lat_lon']
        altitud = station['ALTITUD']

        insert_inforiego_daily_years(provincia, estacion, years, lat_lon, altitud)
