# -*- coding: utf-8 -*-
"""
Created on Sat Jul 02 18:27:40 2016

@author: jlafuente
"""

import ftplib
import logging
import os
import ast
import utm
import re

import pandas as pd
import shapefile

import elasticsearch_dsl as dsl

from osc import util

import osc.config as conf

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

    try:
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
    except Exception as e:
        conf.error_handler.error(__name__, 'download_shapefile', zip_code + ': ' + str(e))


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

    try:
        sp = shapefile.Reader(shapefile_name)

        print "... finished getting zipfile: " + str(zip_code)

        return sp
    except Exception as e:
        conf.error_handler.error(__name__, "get_shapefile", zip_code + ': ' + str(e))
        return None


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
    return filter(lambda x: x is not None,
                  [get_shapefile(zip_code=zc,
                                 url=url,
                                 root_dir=root_dir,
                                 suffix=suffix,
                                 data_dir=data_dir,
                                 tmp_dir=tmp_dir,
                                 force_download=force_download) for zc in zip_codes])


def get_dataframe_from_shapefile(sf):
    fields_dict = {'bbox': [shape.bbox for shape in sf.shapes()],
                   'points': [shape.points for shape in sf.shapes()]}

    for i in range(1, len(sf.fields)):
        field_name = sf.fields[i][0]
        field_values = [record[i - 1] for record in sf.records()]

        fields_dict[field_name] = field_values

    try:
        return pd.DataFrame(fields_dict)
    except Exception as e:
        conf.error_handler.error(__name__, "get_dataframe_from_shapefile", str(e))
        return None


def write_csv(zip_codes,
              url='ftp.itacyl.es',
              root_dir='/cartografia/05_SIGPAC/2015_ETRS89/Parcelario_SIGPAC_CyL_Municipios',
              suffix='RECFE',
              data_dir='../data',
              tmp_dir='./tmp',
              force_download=False):

    for zip_code in filter(lambda x: not os.path.exists(csv_file(data_dir, x)), util.as_list(zip_codes)):
        sf = get_shapefile(zip_code=zip_code,
                           url=url,
                           root_dir=root_dir,
                           suffix=suffix,
                           data_dir=data_dir,
                           tmp_dir=tmp_dir,
                           force_download=force_download)

        if sf is not None:
            df = get_dataframe_from_shapefile(sf)

            if df is not None:
                try:
                    # create directory if it does not exist
                    if not os.path.exists(csv_path(data_dir=data_dir, zip_code=zip_code)):
                        os.makedirs(csv_path(data_dir=data_dir, zip_code=zip_code))

                    csv = csv_file(data_dir=data_dir, zip_code=zip_code)

                    df.to_csv(csv, sep=';')
                except Exception as e:
                    conf.error_handler.error(__name__, "write_csv", zip_code + ': ' + str(e))


def compute_bb_center(row, axis=None):
    bbox = ast.literal_eval(row['bbox'])

    if axis == 0:
        return bbox[0] + (bbox[2]-bbox[0]) / 2
    elif axis == 1:
        return bbox[1] + (bbox[3]-bbox[1]) / 2
    return bbox[0] + (bbox[2]-bbox[0]) / 2, bbox[1] + (bbox[3]-bbox[1]) / 2


def get_dataframe(zip_codes,
                  usecols=None,
                  url='ftp.itacyl.es',
                  root_dir='/cartografia/05_SIGPAC/2015_ETRS89/Parcelario_SIGPAC_CyL_Municipios',
                  suffix='RECFE',
                  data_dir='../data',
                  tmp_dir='./tmp',
                  force_download=False,
                  with_bbox_center=False):
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
            dataFrames.append(pd.read_csv(csv_file(data_dir, zip_code),
                                          sep=';',
                                          thousands='.',
                                          dayfirst=True,
                                          parse_dates=['FECHA_CAM0'],
                                          usecols=usecols))
        except Exception as e:
            conf.error_handler.error(__name__, 'get_dataframe', zip_code + ': ' + str(e))

    df = pd.concat(dataFrames)

    if with_bbox_center:
        df['x_bbox_center'] = df.apply(lambda x: compute_bb_center(x, axis=0), axis=1)
        df['y_bbox_center'] = df.apply(lambda x: compute_bb_center(x, axis=1), axis=1)

    return df

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


# Elastic Search
class SIGPACRecord(dsl.DocType):
    dn_pk = dsl.String()

    provincia = dsl.Integer()
    municipio = dsl.Integer()
    poligono = dsl.Integer()
    parcela = dsl.Integer()
    recinto = dsl.Integer()
    zona = dsl.Integer()

    perimetro = dsl.Long()
    superficie = dsl.Long()
    pend_med = dsl.Integer()
    points = dsl.GeoShape(tree='quadtree', precision='1m')
    bbox = dsl.GeoShape(tree='quadtree', precision='1m')

    uso_sigpac = dsl.String()

    agregado = dsl.Integer()
    cap_auto = dsl.Integer()
    cap_manual = dsl.Integer()
    coef_regadio = dsl.Float()
    c_refpar = dsl.String()
    c_refpol = dsl.String()
    c_refrec = dsl.String()
    dn_oid = dsl.Long()

    def save(self, ** kwargs):
        return super(SIGPACRecord, self).save(** kwargs)

    class Meta:
        index = 'sigpac'


def convert_to_latlong(coords):
    lat, lon = utm.to_latlon(coords[0], coords[1], 30, northern=True)

    return [lat, lon]


def create_geojson_feature(bbox_str, points_str):
    bbox = []

    bbox_list = ast.literal_eval(bbox_str)

    bbox.append(convert_to_latlong(bbox_list[:2]))
    bbox.append(convert_to_latlong(bbox_list[2:]))

    points_list = ast.literal_eval(points_str)

    outer_points = [convert_to_latlong(x) for x in points_list]

    orig = outer_points[0]
    dest = outer_points[-1]

    # close the circle
    if orig[0] != dest[0] or orig[1] != dest[1]:
        outer_points.append(orig)

    points = [outer_points]

    return ({'type': 'envelope',
            'coordinates': bbox},
            {'type': 'polygon',
             'coordinates': points})


def build_record(row):
    record = SIGPACRecord(meta={'id': str(row.DN_PK) +
                                      ' - ' + str(row.PROVINCIA) +
                                      ' - ' + str(row.MUNICIPIO) +
                                      ' - ' + str(row.POLIGONO) +
                                      ' - ' + str(row.PARCELA) +
                                      ' - ' + str(row.RECINTO) +
                                      ' - ' + str(row.ZONA)})

    record.dn_pk = str(row.DN_PK)

    record.provincia = int(row.PROVINCIA)
    record.municipio = int(row.MUNICIPIO)
    record.poligono = int(row.POLIGONO)
    record.parcela = int(row.PARCELA)
    record.recinto = int(row.RECINTO)
    record.zona = int(row.ZONA)

    record.perimetro = long(row.PERIMETRO)
    record.superficie = long(row.SUPERFICIE)
    record.pend_med = int(row.PEND_MED)

    record.bbox, record.points = create_geojson_feature(bbox_str=row.bbox, points_str=row.points)

    record.uso_sigpac = row.USO_SIGPAC

    record.agregado = int(row.AGREGADO)
    record.cap_auto = int(row.CAP_AUTO)
    record.cap_manual = int(row.CAP_MANU)
    record.coef_regadio = float(row.COEF_REGA0)
    record.c_refpar = str(row.C_REFPAR)
    record.c_refpol = str(row.C_REFPOL)
    record.c_refrec = str(row.C_REFREC)
    record.dn_oid = long(row.DN_OID)

    return record


def read_codigos(data_dir='../data'):
    codigos_path = os.path.join(path(data_dir), 'codigos.csv')

    codigos = pd.read_csv(codigos_path,
                            sep=';',
                            encoding=None)
    codigos.columns = ['codigo', 'uso']
    return codigos


def save2elasticsearch(zip_codes,
                       url='ftp.itacyl.es',
                       root_dir='/Meteorologia/Datos_observacion_Red_InfoRiego/DatosHorarios',
                       force_download=False,
                       data_dir='../data',
                       tmp_dir='./tmp'):
    try:
        SIGPACRecord.init()
    except Exception as e:
        conf.error_handler.error(__name__, "build_record", str(e))
        conf.error_handler.flush()
        raise

    # download if necessary
    dataframe = get_dataframe(zip_codes=zip_codes,
                              url=url,
                              root_dir=root_dir,
                              force_download=force_download,
                              with_bbox_center=False,
                              data_dir=data_dir,
                              tmp_dir=tmp_dir)
    codigos = read_codigos(data_dir)

    dataframe = pd.merge(dataframe, codigos, left_on='USO_SIGPAC', right_on='codigo', how='outer')

    for t in dataframe.itertuples():
        record = build_record(t)
        try:
            record.save()
        except Exception as e:
            conf.error_handler.error(__name__,
                                     'save2elasticsearch',
                                     str(type(e)) + str(record.dn_pk) + ' ' + str(record.to_dict()))
