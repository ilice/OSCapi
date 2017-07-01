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
from osc.util import error_managed

logger = logging.getLogger(__name__)

ITACYL_PROTOCOL = settings.ITACYL['ITACYL_PROTOCOL']
ITACYL_FTP = settings.ITACYL['ITACYL_FTP']
SIGPAC_PATH = settings.ITACYL['SIGPAC_PATH']
SIGPAC_FILE_DBF = settings.ITACYL['SIGPAC_FILE_DBF']


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
    print('{}_{}'.format(path.group(0), path.group(1)))
    if '37_901/' in zipfile.namelist():
        dbf = zipfile.open('37_901/' + SIGPAC_FILE_DBF, 'r')
    else:
        dbf = zipfile.open(SIGPAC_FILE_DBF, 'r')

    sf = shapefile.Reader(dbf=StringIO(dbf.read()))
    records = sf.records()
    for record in records:
        updateParcel(record)


@error_managed()
def updateParcel(record):
    cadastral_reference = getCadastralReference(record)
    logger.info('Updating cadastral parcel: %s - %s', cadastral_reference, record[11])
    # if cadastral_reference == '37284A00200076':
    #     print(record)


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


def import_sigpac_data():
    provinces = getProvinces()

    for province in provinces:
        municipalities = getMunicipalities(province)
        for municipality in municipalities:
            updateMunicipality(province, municipality)
