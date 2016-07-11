# -*- coding: utf-8 -*-
"""
Created on Sat Jul 02 18:27:40 2016

@author: jlafuente
"""

import ftplib
import logging
import os
import re

import pandas as pd
import shapefile

from osc import util

FORMAT = '%(asctime)-15s %(clientip)s %(user)-8s %(message)s'
logging.basicConfig(format=FORMAT)
logger = logging.Logger(__name__)


def path(data_dir, zip_code=None):
    res_path = os.path.join(data_dir, 'SIGPAC')

    if zip_code is not None:
        res_path = os.path.join(res_path, 'zip_' + str(zip_code)[0:2])
        res_path = os.path.join(res_path, 'zip_' + str(zip_code))

    return res_path


def csv_path(data_dir, zip_code):
    res_path = os.path.join(data_dir, 'SIGPAC')
    res_path = os.path.join(res_path, 'csv')
    res_path = os.path.join(res_path, 'mun_' + zip_code[0:2])

    return res_path


def csv_file(data_dir, zip_code):
    res_path = csv_path(data_dir=data_dir, zip_code=zip_code)
    res_path = os.path.join(res_path, 'zip_' + zip_code + '.csv')

    return res_path


def download_shapefile(zip_code,
                       url,
                       root_dir,
                       suffix,
                       working_dir,
                       force_download=True,
                       tmp_dir='./tmp'):
    if not force_download and os.path.exists(working_dir):
        return

    print "Downloading shapeFile for zipCode: " + str(zip_code)

    ftp = ftplib.FTP(url, user='anonymous', passwd='')
    ftp.cwd(root_dir)

    # Now we are at a province level. Check the first two digits so that they
    # are equal to the first two ones in the postal code
    files = filter(lambda x: x.startswith(zip_code[0:2]), ftp.nlst())
    if len(files) != 1:
        raise NameError(zip_code)

    # Change directory to the province one
    ftp.cwd(files[0])

    files = filter(lambda x: x.startswith(zip_code), ftp.nlst())
    if len(files) != 1:
        raise NameError(zip_code)

    # now we have a zip file, which we have to download and decompress
    zipped_shapefile = files[0]

    if not os.path.exists(tmp_dir):
        os.makedirs(tmp_dir)

    zipped_shapefile_path = os.path.join(tmp_dir, zipped_shapefile)

    with open(zipped_shapefile_path, 'wb') as f:
        logger.info("Downloading " + zipped_shapefile)
        ftp.retrbinary('RETR ' + zipped_shapefile, f.write)
        logger.info("... downloaded.")

    # uncompress the zipfile
    util.unzip_file(zipped_shapefile_path,
                    working_dir,
                    lambda x: suffix in x.filename)
    # remove the file
    # os.remove(compressedShapeFilePath)
    print "... finished downloading zipfile: " + str(zip_code)

    ftp.close()


def get_shapefile(zip_code,
                  url='ftp.itacyl.es',
                  root_dir='/cartografia/05_SIGPAC/2015_ETRS89/Parcelario_SIGPAC_CyL_Municipios',
                  suffix='RECFE',
                  data_dir='../data',
                  tmp_dir='./tmp',
                  force_download=False):
    print "Getting shapeFile for zipCode: " + str(zip_code)
    working_dir = path(data_dir, zip_code=zip_code)

    if force_download or not os.path.exists(working_dir):
        download_shapefile(zip_code=zip_code,
                           url=url,
                           root_dir=root_dir,
                           suffix=suffix,
                           working_dir=working_dir,
                           force_download=force_download,
                           tmp_dir=tmp_dir)

    shapefile_name = os.path.join(working_dir, zip_code + '_' + suffix)

    sp = shapefile.Reader(shapefile_name)

    print "... finished getting zipfile: " + str(zip_code)

    return sp


def download_shapefiles(zip_codes,
                        url='ftp.itacyl.es',
                        root_dir='/cartografia/05_SIGPAC/2015_ETRS89/Parcelario_SIGPAC_CyL_Municipios',
                        suffix='RECFE',
                        data_dir='../data',
                        tmp_dir='./tmp',
                        force_download=False):
    for zipCode in zip_codes:
        working_dir = path(data_dir, zip_code=zipCode)
        download_shapefile(zip_code=zipCode,
                           url=url,
                           root_dir=root_dir,
                           suffix=suffix,
                           working_dir=working_dir,
                           tmp_dir=tmp_dir,
                           force_download=force_download)


def get_shapefiles(zip_codes,
                   url='ftp.itacyl.es',
                   root_dir='/cartografia/05_SIGPAC/2015_ETRS89/Parcelario_SIGPAC_CyL_Municipios',
                   suffix='RECFE',
                   data_dir='../data',
                   tmp_dir='./tmp',
                   force_download=False):
    return [get_shapefile(zip_code=zc,
                          url=url,
                          root_dir=root_dir,
                          suffix=suffix,
                          data_dir=data_dir,
                          tmp_dir=tmp_dir,
                          force_download=force_download) for zc in zip_codes]


def get_dataframe_from_shapefile(sf):
    fields_dict = {'bbox': [shape.bbox for shape in sf.shapes()],
                   'points': [shape.points for shape in sf.shapes()]}

    for i in range(1, len(sf.fields)):
        field_name = sf.fields[i][0]
        field_values = [record[i - 1] for record in sf.records()]

        fields_dict[field_name] = field_values

    return pd.DataFrame(fields_dict)


def write_csv(zip_codes,
              url='ftp.itacyl.es',
              root_dir='/cartografia/05_SIGPAC/2015_ETRS89/Parcelario_SIGPAC_CyL_Municipios',
              suffix='RECFE',
              data_dir='../data',
              tmp_dir='./tmp',
              force_download=False):

    for zip_code in filter(lambda x: not os.path.exists(csv_file(data_dir, x)), util.as_list(zip_codes)):
        try:
            sf = get_shapefile(zip_code=zip_code,
                               url=url,
                               root_dir=root_dir,
                               suffix=suffix,
                               data_dir=data_dir,
                               tmp_dir=tmp_dir,
                               force_download=force_download)

            df = get_dataframe_from_shapefile(sf)

            # create directory if it does not exist
            if not os.path.exists(csv_path(data_dir=data_dir, zip_code=zip_code)):
                os.makedirs(csv_path(data_dir=data_dir, zip_code=zip_code))

            csv = csv_file(data_dir=data_dir, zip_code=zip_code)

            df.to_csv(csv, sep=';')
        except:
            logger.error("Unable to write csv file: " + zip_code)


def get_dataframe(zip_codes,
                  usecols=None,
                  url='ftp.itacyl.es',
                  root_dir='/cartografia/05_SIGPAC/2015_ETRS89/Parcelario_SIGPAC_CyL_Municipios',
                  suffix='RECFE',
                  data_dir='../data',
                  tmp_dir='./tmp',
                  force_download=False):
    write_csv(zip_codes,
              url=url,
              root_dir=root_dir,
              suffix=suffix,
              data_dir=data_dir,
              tmp_dir=tmp_dir,
              force_download=force_download)


    dataFrames = []
    for zip_code in util.as_list(zip_codes):
        try:
            dataFrames.append(pd.read_csv(csv_file(data_dir, zip_code), sep=';', usecols=usecols))
        except:
            logger.error('Unable to get dataFrame: ' + zip_code)

    return pd.concat(dataFrames)


def all_zipcodes(url='ftp.itacyl.es',
                 root_dir='/cartografia/05_SIGPAC/2015_ETRS89/Parcelario_SIGPAC_CyL_Municipios',
                 starting_with=None):
    zip_codes = []
    ftp = ftplib.FTP(url, user='anonymous', passwd='')
    ftp.cwd(root_dir)

    # Get all the directories, in order to enter each of them and check for
    # the zipcodes
    for municipality in ftp.nlst():
        ftp.cwd(root_dir + '/' + municipality)
        zip_codes = zip_codes + [re.split('_|\.', x)[0] for x in ftp.nlst()]

    ftp.close()

    if starting_with is not None:
        zip_codes = filter(lambda x: x.startswith(starting_with), zip_codes)

    return filter(lambda x: len(x) == 5, zip_codes)
