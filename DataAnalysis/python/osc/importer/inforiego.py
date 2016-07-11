# -*- coding: utf-8 -*-
"""
Created on Sat Jul 02 18:27:40 2016

@author: jlafuente
"""

import ftplib
import logging
import os
import elasticsearch_dsl as dsl
import csv
import datetime

import pandas as pd

from osc import util

FORMAT = '%(asctime)-15s %(clientip)s %(user)-8s %(message)s'
logging.basicConfig(format=FORMAT)
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
                  encoding='mbcs',
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
    
    dataframe['FECHA'] = pd.to_datetime(dataframe[u'Fecha (AAAA-MM-DD)'] +
                                        ' ' +
                                        dataframe[u'Hora (HHMM)'].replace('2400', '0000'),
                                        format='%Y-%m-%d %H%M')
    
    dataframe = dataframe.drop([u'Fecha (AAAA-MM-DD)', u'Hora (HHMM)'], axis=1)
    
    dataframe.index = dataframe['FECHA']
    
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
        return super.save(** kwargs)

    class Meta:
        index = 'inforiego'


def build_record(row, locations):
    # just in case it was not initted
    InfoRiegoRecord.init()

    record = None

    if len(row['day']) == 10 and len(row['hour']) == 4:
        record = InfoRiegoRecord(code=row['code'], location=row['location'], rain=row['rain'],
                                 temperature=row['temperature'], rel_humidity = row['rel_humidity'],
                                 radiation=row['radiation'], wind_speed=row['wind_speed'],
                                 wind_direction=row['wind_direction'])

        record.date = datetime.datetime.strptime(row['day'] + ' ' +
                                                 row['hour'].replace('2400', '0000'), format='%Y/%m/%d %H%M')

        if row['code'] in locations:
            location = locations[row['code']]
            record.station_latitude = location['latitude']
            record.station_longitude = location['longitude']
            record.station_height = location['height']
            record.station_xutm = location['xutm']
            record.station_yutm = location['yutm']

    return record


def read_locations(data_dir='../data'):
    csv_path = os.path.join(path(data_dir), 'UbicacionEstacionesITACyL 2009.csv')

    locations = {}
    with open(csv_path) as csvfile:
        reader = csv.DictReader(csv_path, fieldnames=['province', 'station', 'code', 'name', 'longitude',
                                                      'latitude', 'height', 'xutm', 'yutm'])
        for row in reader:
            locations[row['code']] = row

    return locations


def save2elasticsearch(years,
                       url='ftp.itacyl.es',
                       root_dir='/Meteorologia/Datos_observacion_Red_InfoRiego/DatosHorarios',
                       force_download=False,
                       data_dir='../data',
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
    # first read the SIGPAC locations in a dictionary

    for csvPath in csv_paths:
        with open(csvPath) as csvfile:
            reader = csv.DictReader(csvfile, fieldnames=['code', 'location', 'day', 'hour', 'rain', 'temperature',
                                                         'rel_humidity', 'radiation', 'wind_speed', 'wind_direction'])
            for row in reader:
                record = build_record(row)
                if record is not None:
                    record.save()
