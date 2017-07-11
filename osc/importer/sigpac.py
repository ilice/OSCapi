# coding=utf-8

from ftplib import FTP
import logging
import re
import shapefile
from StringIO import StringIO
from urllib import urlopen
from zipfile import ZipFile

from django.conf import settings

from osc.exceptions import ItacylException
from osc.services.cadastre import update_parcel
from osc.util import error_managed

logger = logging.getLogger(__name__)

ITACYL_PROTOCOL = settings.ITACYL['ITACYL_PROTOCOL']
ITACYL_FTP = settings.ITACYL['ITACYL_FTP']
SIGPAC_PATH = settings.ITACYL['SIGPAC_PATH']
SIGPAC_FILE_DBF = settings.ITACYL['SIGPAC_FILE_DBF']

parcels = []


def getDemarcations(demarcation=''):
    logger.info('Obtaining %s demarcations', demarcation)
    ftp = FTP(ITACYL_FTP)
    ftp.login()
    ftp.cwd('{}/{}'.format(SIGPAC_PATH, demarcation))
    demarcations = []
    ftp.retrlines('NLST', demarcations.append)
    ftp.quit()
    return demarcations


def getProvinces():
    logger.info('Obtaining provinces')
    return getDemarcations()


def getMunicipalities(province):
    logger.info('Obtaining municipalities from: %s', province)
    return getDemarcations(province)


def updateMunicipality(province, municipality):
    logger.info('Updating municipality: %s (%s)', municipality, province)
    url = '{}{}/{}/{}/{}'.format(ITACYL_PROTOCOL,
                                 ITACYL_FTP,
                                 SIGPAC_PATH,
                                 province,
                                 municipality)
    conn = urlopen(url)
    zipfile = ZipFile(StringIO(conn.read()))
    conn.close()

    path = re.match(r'(\d{2})_?(\d{3})(?:_|\.)', municipality)
    dirPath = '{}_{}/'.format(path.group(1), path.group(2))

    if dirPath in zipfile.namelist():
        dbf = zipfile.open(dirPath + SIGPAC_FILE_DBF, 'r')
    else:
        dbf = zipfile.open(SIGPAC_FILE_DBF, 'r')

    sf = shapefile.Reader(dbf=StringIO(dbf.read()))
    records = sf.records()
    for record in records:
        updateParcel(createParcelDocument(record))


@error_managed(inhibit_exception=True)
def updateParcel(parcel):
    update_parcel(parcel)


def createParcelDocument(record):
    nationalCadastralReference = getCadastralReference(record)
    logger.debug('Updating cadastral parcel: %s - %s',
                 nationalCadastralReference, record[11])
    properties = {}
    properties['nationalCadastralReference'] = nationalCadastralReference
    sigpacData = {}
    sigpacData['DN_OID'] = record[0]
    sigpacData['SUPERFICIE'] = record[1]
    sigpacData['PERIMETRO'] = record[2]
    sigpacData['PROVINCIA'] = record[3]
    sigpacData['MUNICIPIO'] = record[4]
    sigpacData['AGREGADO'] = record[5]
    sigpacData['ZONA'] = record[6]
    sigpacData['POLIGONO'] = record[7]
    sigpacData['PARCELA'] = record[8]
    sigpacData['RECINTO'] = record[9]
    sigpacData['COEF_REGAD'] = record[10]
    sigpacData['USO_SIGPAC'] = record[11]
    properties['sigpacData'] = sigpacData
    doc = {}
    doc['properties'] = properties
    parcel = {}
    parcel['doc'] = doc
    return parcel


def getCadastralReference(record):
    logger.debug('Composing cadastral reference from %s', record)
    try:
        cadastral_reference = str(record[3]).zfill(2) + \
            str(record[4]).zfill(3) + \
            'A' + \
            str(record[7]).zfill(3) + \
            str(record[8]).zfill(5)

        if re.match(r'\d{5}[A-Z]\d{8}', cadastral_reference) is None:
            raise ValueError('No match cadastral reference pattern: {}'
                             .format(cadastral_reference))

        return cadastral_reference
    except Exception as e:
        raise ItacylException(
            'Error updating parcel from record {}'.format(record),
            e.message,
            record)


def import_sigpac_data(provinces=[]):
    available_provinces = getProvinces()
    for province in available_provinces:
        if province in provinces or len(provinces) == 0:
            municipalities = getMunicipalities(province)
            for municipality in municipalities:
                updateMunicipality(province, municipality)
