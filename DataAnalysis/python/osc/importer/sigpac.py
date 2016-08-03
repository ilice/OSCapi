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
import polyline
import shapefile

import elasticsearch_dsl as dsl
from elasticsearch_dsl.connections import connections

import elasticsearch as es

import requests

from osc import util

import osc.config as conf

import time

from osc.exceptions import ConnectionError

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
                       force_download=True):
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

        if not os.path.exists(conf.tmp_dir):
            os.makedirs(conf.tmp_dir)

        zipped_shapefile_path = os.path.join(conf.tmp_dir, zipped_shapefile)

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
                  force_download=False):
    print "Getting shapeFile for zipCode: " + str(zip_code)
    working_dir = path(conf.data_dir, zip_code=zip_code)

    if force_download or not os.path.exists(working_dir):
        download_shapefile(zip_code=zip_code,
                           url=url,
                           root_dir=root_dir,
                           suffix=suffix,
                           working_dir=working_dir,
                           force_download=force_download)

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
                        force_download=False):
    for zipCode in zip_codes:
        working_dir = path(conf.data_dir, zip_code=zipCode)
        download_shapefile(zip_code=zipCode,
                           url=url,
                           root_dir=root_dir,
                           suffix=suffix,
                           working_dir=working_dir,
                           force_download=force_download)


def get_shapefiles(zip_codes,
                   url='ftp.itacyl.es',
                   root_dir='/cartografia/05_SIGPAC/2015_ETRS89/Parcelario_SIGPAC_CyL_Municipios',
                   suffix='RECFE',
                   force_download=False):
    return filter(lambda x: x is not None,
                  [get_shapefile(zip_code=zc,
                                 url=url,
                                 root_dir=root_dir,
                                 suffix=suffix,
                                 force_download=force_download) for zc in zip_codes])


def get_dataframe_from_shapefile(zip_code, sf):
    try:
        fields_dict = {'bbox': [shape.bbox for shape in sf.shapes()],
                       'points': [shape.points for shape in sf.shapes()]}

        for i in range(1, len(sf.fields)):
            field_name = sf.fields[i][0]
            field_values = [record[i - 1] for record in sf.records()]

            fields_dict[field_name] = field_values

        return pd.DataFrame(fields_dict)
    except Exception as e:
        conf.error_handler.error(__name__, "get_dataframe_from_shapefile", zip_code + ': ' + str(e))
        return None


def write_csv(zip_codes,
              url='ftp.itacyl.es',
              root_dir='/cartografia/05_SIGPAC/2015_ETRS89/Parcelario_SIGPAC_CyL_Municipios',
              suffix='RECFE',
              force_download=False):

    for zip_code in filter(lambda x: not os.path.exists(csv_file(conf.data_dir, x)), util.as_list(zip_codes)):
        sf = get_shapefile(zip_code=zip_code,
                           url=url,
                           root_dir=root_dir,
                           suffix=suffix,
                           force_download=force_download)

        if sf is not None:
            df = get_dataframe_from_shapefile(zip_code, sf)

            if df is not None:
                try:
                    # create directory if it does not exist
                    if not os.path.exists(csv_path(data_dir=conf.data_dir, zip_code=zip_code)):
                        os.makedirs(csv_path(data_dir=conf.data_dir, zip_code=zip_code))

                    csv = csv_file(data_dir=conf.data_dir, zip_code=zip_code)

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
                  force_download=False,
                  with_bbox_center=False):
    write_csv(zip_codes,
              url=url,
              root_dir=root_dir,
              suffix=suffix,
              force_download=force_download)

    dataFrames = []
    for zip_code in util.as_list(zip_codes):
        try:
            dataFrames.append(pd.read_csv(csv_file(conf.data_dir, zip_code),
                                          sep=';',
                                          thousands='.',
                                          dayfirst=True,
                                          parse_dates=['FECHA_CAM0'],
                                          dtype={'DN_PK': long,
                                                 'CAP_AUTO': long,
                                                 'CAP_MANU': long,
                                                 'DN_OID': long,
                                                 'DN_PK': long,
                                                 'MUNICIPIO': int,
                                                 'PARCELA': int,
                                                 'PEND_MED': int,
                                                 'PERIMETRO': int,
                                                 'POLIGONO': int,
                                                 'PROVINCIA': int,
                                                 'RECINTO': int,
                                                 'SUPERFICIE': long,
                                                 'ZONA': long},
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
class sigpac_record(dsl.DocType):
    dn_pk = dsl.Long()

    provincia = dsl.Integer()
    municipio = dsl.Integer()
    poligono = dsl.Integer()
    parcela = dsl.Integer()
    recinto = dsl.Integer()
    zona = dsl.Integer()

    perimetro = dsl.Long()
    superficie = dsl.Long()
    pend_med = dsl.Integer()
    points = dsl.GeoShape()
    bbox = dsl.GeoShape()
    bbox_center = dsl.GeoPoint(lat_lon=True)

    uso_sigpac = dsl.String()

    agregado = dsl.Integer()
    cap_auto = dsl.Integer()
    cap_manual = dsl.Integer()
    coef_regadio = dsl.Float()
    c_refpar = dsl.String()
    c_refpol = dsl.String()
    c_refrec = dsl.String()
    dn_oid = dsl.Long()

    elevation = dsl.Float()

    def save(self, ** kwargs):
        return super(sigpac_record, self).save(** kwargs)

    class Meta:
        index = 'plots'


def convert_to_latlong(coords):
    lat, lon = utm.to_latlon(coords[0], coords[1], 30, northern=True)

    return [lat, lon]


def make_polygon(points):
    main = []
    others = []
    pos_in_points = 0
    for point in points:
        try:
            point_idx = main.index(point)
        except ValueError:
            point_idx = -1

        main.append(point)

        if point_idx != -1:
            # We are just closing the main polygon
            if point_idx == 0:
                return [main] + others + make_polygon(points[pos_in_points+1:])
            else:
                others.append(main[point_idx:])
                main = main[:(point_idx+1)]

        pos_in_points += 1

    return [main] + others if len(main) > 0 else []


def create_geojson_envelope(bbox_str):
    bbox = []

    bbox_list = ast.literal_eval(bbox_str)

    bbox.append(convert_to_latlong(bbox_list[:2]))
    bbox.append(convert_to_latlong(bbox_list[2:]))

    return {'type': 'envelope',
            'coordinates': bbox}


def create_geojson_polygon(points_str):
    points_list = ast.literal_eval(points_str)

    points = [convert_to_latlong(x) for x in points_list]

    polygon = make_polygon(points)

    return {'type': 'polygon',
            'coordinates': polygon}


def create_geojson_point(x, y):

    lat, lon = convert_to_latlong([x, y])

    return {'lat': lat, 'lon': lon}


def build_record_id(row):
    return str(row.PROVINCIA) + '-' + str(row.MUNICIPIO) + '-' + str(row.AGREGADO) + '-' + str(
        row.POLIGONO) + '-' + str(row.PARCELA) + '-' + str(row.RECINTO)


def build_record(row):
    try:
        record = sigpac_record(meta={'id': build_record_id(row)})

        record.dn_pk = long(row.DN_PK)

        record.provincia = int(row.PROVINCIA)
        record.municipio = int(row.MUNICIPIO)
        record.poligono = int(row.POLIGONO)
        record.parcela = int(row.PARCELA)
        record.recinto = int(row.RECINTO)
        record.zona = int(row.ZONA)

        record.perimetro = long(row.PERIMETRO)
        record.superficie = long(row.SUPERFICIE)
        record.pend_med = int(row.PEND_MED)

        record.bbox = create_geojson_envelope(row.bbox)
        record.points = create_geojson_polygon(row.points)
        record.bbox_center = create_geojson_point(row.x_bbox_center, row.y_bbox_center)

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
    except Exception as e:
        conf.error_handler.error(__name__,
                                 'save2elasticsearch',
                                 str(e) + ': ' + str(row))
        return None


def read_codigos():
    codigos_path = os.path.join(path(conf.data_dir), 'codigos.csv')

    codigos = pd.read_csv(codigos_path,
                            sep=';',
                            encoding=None)
    codigos.columns = ['codigo', 'uso']
    return codigos


def wait_for_yellow_cluster_status():
    connection = connections.get_connection()
    while True:
        cluster_status = connection.cluster.health(wait_for_status='yellow')
        if cluster_status['status'] != 'red':
            break

        print 'Cluster status is red. Waiting for yellow status'


def elastic_bulk_update(records):
    try:
        connection = connections.get_connection()
        wait_for_yellow_cluster_status()
        es.helpers.bulk(connection,
                        ({'_op_type': 'update',
                          '_index': getattr(r.meta, 'index', r._doc_type.index),
                          '_id': getattr(r.meta, 'id', None),
                          '_type': r._doc_type.name,
                          'doc': r.to_dict()} for r in records))
    except Exception as e:
        for record in records:
            conf.error_handler.error(__name__,
                                     'save2elasticsearch',
                                     str(type(e)) + ': ' + str(record.to_dict()))


def elastic_bulk_save(records):
    try:
        connection = connections.get_connection()
        wait_for_yellow_cluster_status()
        es.helpers.bulk(connection,
                        ({'_index': getattr(r.meta, 'index', r._doc_type.index),
                          '_id': getattr(r.meta, 'id', None),
                          '_type': r._doc_type.name,
                          '_source': r.to_dict()} for r in records))
    except Exception as e:
        for record in records:
            conf.error_handler.error(__name__,
                                     'save2elasticsearch',
                                     str(type(e)) + ': ' + str(record.to_dict()))



def save2elasticsearch(zip_codes,
                       url='ftp.itacyl.es',
                       root_dir='/Meteorologia/Datos_observacion_Red_InfoRiego/DatosHorarios',
                       force_download=False):
    chunk_size = conf.config.getint('elasticsearch', 'chunk_size')

    try:
        sigpac_record.init()
        time.sleep(5)
    except Exception as e:
        conf.error_handler.error(__name__, "build_record", str(e))
        conf.error_handler.flush()
        raise

    # download if necessary
    dataframe = get_dataframe(zip_codes=zip_codes,
                              url=url,
                              root_dir=root_dir,
                              force_download=force_download,
                              with_bbox_center=True)
    codigos = read_codigos()

    dataframe = dataframe.merge(codigos, left_on='USO_SIGPAC', right_on='codigo', how='left')

    records_to_save = []
    for t in dataframe.itertuples():
        rec = build_record(t)
        if rec is not None:
            records_to_save.append(rec)

        if len(records_to_save) >= chunk_size:
            elastic_bulk_save(records_to_save)
            records_to_save = []

    if len(records_to_save) > 0:
        elastic_bulk_save(records_to_save)


def compose_locations_param(points):
    param = polyline.encode(points)

    return 'enc:'+param


def obtain_elevation_from_google(records, centers):
    api_key = conf.config.get('Google Elevation', 'api_key')
    url = 'https://maps.googleapis.com/maps/api/elevation/json'
    sleep_time_when_over_quota = 3600

    while True:
        response = requests.get(url, params={'key': api_key,
                                             'locations': compose_locations_param(centers)})

        if response.json()['status'] != 'OVER_QUERY_LIMIT':
            break

        # Wait for the next trial
        time.sleep(sleep_time_when_over_quota)

    # Process response
    json_response = response.json()

    if json_response['status'] == 'OK':
        for elev in zip(records, json_response['results']):
            elev[0].elevation = elev[1]['elevation']
    else:
        raise ConnectionError('GOOGLE MAPS',
                              response['error_message'] if 'error_message' in response else str(response))

    return records


def add_altitude_info(provincia, municipio=None):
    chunk_size = conf.config.getint('Google Elevation', 'chunk_size')
    print "Chunk Size = " + str(chunk_size)

    try:
        sigpac_record.init()
        time.sleep(5)
    except Exception as e:
        conf.error_handler.error(__name__, "build_record", str(e))
        conf.error_handler.flush()
        raise

    filter = [dsl.Q("term", provincia=provincia)]
    if municipio is not None:
        filter.append(dsl.Q("term", municipio=municipio))

    # query elasticsearch for the neccesary registers
    search = dsl.Search(index='plots').query('bool', filter=filter).fields(['bbox_center.lat', 'bbox_center.lon'])
    search.execute()

    records = []
    centers = []
    for r in search.scan():
        record = sigpac_record(meta={'id': r.meta.id})

        records.append(record)
        centers.append((r['bbox_center.lat'][0], r['bbox_center.lon'][0]))

        if len(records) >= chunk_size:
            print "Inserting next " + str(chunk_size) + " elevations"
            try:
                records = obtain_elevation_from_google(records, centers)
                print " ... Obtained info from google"
                elastic_bulk_update(records)
                print " ...success"
            except ConnectionError as e:
                print " ...success"
                conf.error_handler.error(__name__,
                                         'obtain_elevation_from_google',
                                         e.message)

            records = []
            centers = []

    if len(records) > 0:
        try:
            records = obtain_elevation_from_google(records, centers)
            elastic_bulk_update(records)
        except ConnectionError as e:
            conf.error_handler.error(__name__,
                                     'obtain_elevation_from_google',
                                     e.message)
