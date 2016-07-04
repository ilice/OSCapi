# -*- coding: utf-8 -*-
"""
Created on Sat Jul 02 18:27:40 2016

@author: jlafuente
"""

import shapefile
import ftplib
import zipfile
import os
import logging
import re
import pandas as pd

FORMAT = '%(asctime)-15s %(clientip)s %(user)-8s %(message)s'
logging.basicConfig(format=FORMAT)
logger = logging.Logger("OpenSmartCountry -- data-import")

def forceToBeList(param):
    if type(param) is list:
        return param
    return [param]
    
def getInfoRiegoPath(datadir, year = None):
    path = os.path.join(datadir, 'InfoRiego')
    
    if year != None:
        path = os.path.join(path, str(year))
        
    return path

def getSIGPACPath(datadir):
    return os.path.join(datadir, 'SIGPAC')

def unzipFile(zipFilePath,
              toPath,
              filterFunc = None):
    #uncompress the zipfile
    if not os.path.exists(toPath):
        os.makedirs(toPath)

    with (zipfile.ZipFile(zipFilePath)) as file:
        infos = file.infolist()
        if filter != None:
            infos = filter(filterFunc, infos)
    
        for info in infos:
            logger.debug("Extracting " + info.filename + " to " + toPath) 
            file.extract(info, path=toPath)
            logger.debug("... extracted")
                     

def downloadShapeFileFromSIGPAC(zipCode,
                                url, 
                                root_dir, 
                                suffix,
                                workingDir,
                                forceDownload=True,
                                tmpDir = './tmp'):
    if not forceDownload and os.path.exists(workingDir):
        return
        
    ftp =  ftplib.FTP(url, user = 'anonymous', passwd='')
    ftp.cwd(root_dir)

    # Now we are at a province level. Check the first two digits so that they 
    # are equal to the first two ones in the postal code
    files = filter(lambda x: x.startswith(zipCode[0:2]), ftp.nlst())    
    if len(files) != 1:
        raise NameError(zipCode)

    #Change directory to the province one
    ftp.cwd(files[0])
    
    files = filter(lambda x : x.startswith(zipCode), ftp.nlst())
    if len(files) != 1:
        raise NameError(zipCode)


    #now we have a zip file, which we have to download and decompress
    compressedShapeFile = files[0]
    
    if not os.path.exists(tmpDir):
        os.makedirs(tmpDir)
        
    compressedShapeFilePath = os.path.join(tmpDir, compressedShapeFile)
    
    with open(compressedShapeFilePath, 'wb') as file:
        logger.info("Downloading " + compressedShapeFile)
        ftp.retrbinary('RETR ' + compressedShapeFile, file.write)
        logger.info("... downloaded.")
            
    #uncompress the zipfile
    unzipFile(compressedShapeFilePath, 
                 workingDir, 
                 lambda x: suffix in x.filename)
    #remove the file             
    #os.remove(compressedShapeFilePath)
                 
    ftp.close()

def getShapeFileFromSIGPAC(zipCode,
                           url = 'ftp.itacyl.es', 
                           root_dir = '/cartografia/05_SIGPAC/2015_ETRS89/Parcelario_SIGPAC_CyL_Municipios', 
                           suffix = 'RECFE', 
                           datadir = '../data', 
                           tmpDir = './tmp',
                           forceDownload = False):
    workingDir = datadir + '/SIGPAC/zip_' + zipCode

    if forceDownload or not os.path.exists(workingDir):
        downloadShapeFileFromSIGPAC(zipCode=zipCode, 
                                    url=url,
                                    root_dir=root_dir,
                                    suffix=suffix,
                                    workingDir=workingDir,
                                    forceDownload=forceDownload,
                                    tmpDir=tmpDir)
                                    
    shapeFileName = os.path.join(workingDir, zipCode + '_' + suffix)

    return shapefile.Reader(shapeFileName)
    

def downloadShapeFilesFromSIGPAC(zipCodes,
                                 url = 'ftp.itacyl.es', 
                                 root_dir = '/cartografia/05_SIGPAC/2015_ETRS89/Parcelario_SIGPAC_CyL_Municipios', 
                                 suffix = 'RECFE', 
                                 datadir = '../data',
                                 tmpDir = './tmp',
                                 forceDownload = False):
    for zipCode in zipCodes:
        workingDir = os.path.join(getSIGPACPath(datadir), 'zip_' + zipCode)
        downloadShapeFileFromSIGPAC(zipCode=zipCode,
                                    url=url,
                                    root_dir=root_dir,
                                    suffix=suffix,
                                    workingDir=workingDir,
                                    tmpDir=tmpDir,
                                    forceDownload=forceDownload)                                     

def getShapeFilesFromSIGPAC(zipCodes,
                            url = 'ftp.itacyl.es', 
                            root_dir = '/cartografia/05_SIGPAC/2015_ETRS89/Parcelario_SIGPAC_CyL_Municipios', 
                            suffix = 'RECFE', 
                            datadir = '../data', 
                            tmpDir = './tmp',
                            forceDownload = False):
    return [getShapeFileFromSIGPAC(zipCode=zc,
                                   url=url,
                                   root_dir=root_dir,
                                   suffix=suffix,
                                   datadir=datadir,
                                   forceDownload=forceDownload) for zc in zipCodes]
                                        
def getAllZipCodesFromSIGPAC(url = 'ftp.itacyl.es', 
                            root_dir = '/cartografia/05_SIGPAC/2015_ETRS89/Parcelario_SIGPAC_CyL_Municipios'):
    allZipCodes = []
    ftp = ftplib.FTP(url, user = 'anonymous', passwd='')
    ftp.cwd(root_dir)
    
    # Get all the directories, in order to enter each of them and check for
    # the zipcodes
    for municipio in ftp.nlst():
        ftp.cwd(root_dir + '/' + municipio)
        allZipCodes = allZipCodes + [re.split('_|\.', x)[0] for x in ftp.nlst()]
        
    ftp.close();
        
    return allZipCodes

def getInfoRiegoDailyFilesList(year,
                               url = 'ftp.itacyl.es', 
                               root_dir = '/Meteorologia/Datos_observacion_Red_InfoRiego/DatosHorarios'):
    ftp = ftplib.FTP(url, user = 'anonymous', passwd='')
    ftp.cwd(root_dir + '/' + year)
    
    files = ftp.nlst()
    ftp.close()
    
    return files

def downloadInfoRiegoDailyFiles(years,
                                url = 'ftp.itacyl.es', 
                                root_dir = '/Meteorologia/Datos_observacion_Red_InfoRiego/DatosHorarios',
                                datadir = '../data',
                                forceDownload = True,
                                tmpDir = './tmp'):
    yearsList = forceToBeList(years)
                          
    for year in yearsList:                    
        workingDir = getInfoRiegoPath(datadir, year)

        print os.path.exists(workingDir)        
        
        if os.path.exists(workingDir) and not forceDownload:
            continue

        print "Downloading " + workingDir                    
        
        ftp = ftplib.FTP(url, user = 'anonymous', passwd='')
        ftp.cwd(root_dir + '/' + year)
    
        #Check the files in the directory
        files =  ftp.nlst()    
        
        if len(files) == 0:
            raise NameError(year)
    
        if not os.path.exists(tmpDir):
            os.makedirs(tmpDir)
    
        for zipFile in files:
            zipFilePath = tmpDir + '/' + zipFile
            
            with open(zipFilePath, 'wb') as file:
                logger.info("Downloading " + zipFilePath)
                ftp.retrbinary('RETR ' + zipFile, file.write)
                logger.info("... downloaded.")
                    
            #uncompress the zipfile
            unzipFile(zipFilePath, 
                      workingDir)
                      
            #remove the file             
            #os.remove(compressedShapeFilePath)
        ftp.close()                 

def getInfoRiegoDataFrame(years,
                          url = 'ftp.itacyl.es', 
                          root_dir = '/Meteorologia/Datos_observacion_Red_InfoRiego/DatosHorarios',
                          datadir = '../data',
                          forceDownload = False,
                          encoding='mbcs',
                          tmpDir = './tmp'):
    #download if neccesary
    downloadInfoRiegoDailyFiles(years=years,
                                url=url,
                                root_dir=root_dir,
                                datadir=datadir,
                                forceDownload=forceDownload,
                                tmpDir=tmpDir)

    csvPaths = [os.path.join(getInfoRiegoPath(datadir, year), fileName) for year in forceToBeList(years) for fileName in os.listdir(getInfoRiegoPath(datadir, year))]
                
    print "Composing data frame"

    dataFrames = []
    for csvPath in csvPaths:
        print "Reading data frame " + csvPath
        dataFrames.append(pd.read_csv(csvPath, sep=';', encoding=encoding))
    
    dataFrame = pd.concat(dataFrames)
    
    return dataFrame
    
        
