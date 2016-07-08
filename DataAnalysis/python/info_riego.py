# -*- coding: utf-8 -*-
"""
Created on Sat Jul 02 18:27:40 2016

@author: jlafuente
"""

import ftplib
import os
import logging
import pandas as pd
import util

FORMAT = '%(asctime)-15s %(clientip)s %(user)-8s %(message)s'
logging.basicConfig(format=FORMAT)
logger = logging.Logger("OSC - info_riego")


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
    years_list = as_list(years)
                          
    for year in years_list:
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
