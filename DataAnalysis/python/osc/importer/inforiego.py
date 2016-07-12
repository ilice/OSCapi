# -*- coding: utf-8 -*-
"""
Created on Sat Jul 02 18:27:40 2016

@author: jlafuente
"""

import ftplib
import logging
import os
import elasticsearch_dsl as dsl
import elasticsearch as es

import pandas as pd

from osc import util

FORMAT = '%(asctime)-15s %(clientip)s %(user)-8s %(message)s'
logging.basicConfig(format=FORMAT)
logger = logging.Logger(__name__)

error_handler = None


def handle_error(reg_id, desc=None):
    error_handler.handle(__name__, reg_id, desc)


def set_error_handler(handler):
    global error_handler
    error_handler = handler

def as_list(param):
    if type(param) is list:
        return param
    return [param]


def path(data_dir, year=None):
    path_str = os.path.join(data_dir, 'InfoRiego')
    
    if year is not None:
        path_str = os.path.join(path_str, str(year))
        
    return path_str


def get_daily_files_list(year,
                         url='ftp.itacyl.es',
                         root_dir='/Meteorologia/Datos_observacion_Red_InfoRiego/DatosHorarios'):
    ftp = ftplib.FTP(url, user='anonymous', passwd='')
    ftp.cwd(root_dir + '/' + year)
    
    files = ftp.nlst()
    ftp.close()
    
    return files


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
        print "Reading data frame " + csvPath
        dataframes.append(pd.read_csv(csvPath,
                                      dtype={u'Hora (HHMM)': str,
                                             u'Fecha (AAAA-MM-DD)': str},
                                      sep=';', 
                                      encoding=encoding))
    
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

    station_longitude = dsl.String()
    station_latitude = dsl.String()
    station_height = dsl.Integer()
    station_xutm = dsl.Integer()
    station_yutm = dsl.Integer()

    def save(self, ** kwargs):
        return super(InfoRiegoRecord, self).save(** kwargs)

    class Meta:
        index = 'inforiego'


def build_record(row):
    # just in case it was not initted
    InfoRiegoRecord.init()

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
                             station_latitude=row.latitude,
                             station_longitude=row.longitude,
                             station_height=int(row.height),
                             station_xutm=int(row.xutm),
                             station_yutm=int(row.yutm))

    return record


def read_locations(data_dir='../data'):
    csv_path = os.path.join(path(data_dir), 'UbicacionEstacionesITACyL 2009.csv')

    locations = pd.read_csv(csv_path,
                            sep=';',
                            encoding=None)
    locations.columns = ['province', 'station', 'code', 'name', 'longitude',
                         'latitude', 'height', 'xutm', 'yutm']
    return locations


def save2elasticsearch(years,
                       url='ftp.itacyl.es',
                       root_dir='/Meteorologia/Datos_observacion_Red_InfoRiego/DatosHorarios',
                       force_download=False,
                       encoding=None,
                       data_dir='../data',
                       tmp_dir='./tmp'):
    # download if necessary
    dataframe = get_dataframe(years=years,
                              url=url,
                              root_dir=root_dir,
                              force_download=force_download,
                              encoding=encoding,
                              data_dir=data_dir,
                              tmp_dir=tmp_dir)
    locations = read_locations(data_dir)

    dataframe = pd.merge(dataframe, locations, on='code', how='outer')

    for t in dataframe.itertuples():
        record = build_record(t)
        try:
            record.save()
        except es.exceptions.RequestError as e:
            handle_error(record.code + '_' + record.date.strftime(format='%Y%m%d%H%M'), str(e))



