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

FORMAT = '%(asctime)-15s %(clientip)s %(user)-8s %(message)s'
logging.basicConfig(format=FORMAT)
logger = logging.Logger("OpenSmartCountry -- data-import")

def unzipTmpFile(zipFilePath,
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
                                tmpDir = './tmp'):
    ftp = ftplib.FTP(url, user = 'anonymous', passwd='')
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
        
    compressedShapeFilePath = tmpDir + '/' + compressedShapeFile
    
    with open(compressedShapeFilePath, 'wb') as file:
        logger.info("Downloading " + compressedShapeFile)
        ftp.retrbinary('RETR ' + compressedShapeFile, file.write)
        logger.info("... downloaded.")
            
    #uncompress the zipfile
    unzipTmpFile(compressedShapeFilePath, 
                 workingDir, 
                 lambda x: suffix in x.filename)
    #remove the file             
    #os.remove(compressedShapeFilePath)

def getShapeFileFromSIGPAC(zipCode,
                           url = 'ftp.itacyl.es', 
                           root_dir = '/cartografia/05_SIGPAC/2015_ETRS89/Parcelario_SIGPAC_CyL_Municipios', 
                           suffix = 'RECFE', 
                           datadir = '../data', 
                           forceDownload = False):
    workingDir = datadir+ '/zip_' + zipCode

    if forceDownload or not os.path.exists(workingDir):
        downloadShapeFileFromSIGPAC(zipCode=zipCode, 
                                    url=url,
                                    root_dir=root_dir,
                                    suffix=suffix,
                                    workingDir=workingDir)
                                    
    shapeFileName = workingDir + '/' + zipCode + '_' + suffix

    return shapefile.Reader(shapeFileName)
    

def getShapeFilesFromSIGPAC(zipCodes,
                            url = 'ftp.itacyl.es', 
                            root_dir = '/cartografia/05_SIGPAC/2015_ETRS89/Parcelario_SIGPAC_CyL_Municipios', 
                            suffix = 'RECFE', 
                            datadir = '../data', 
                            forceDownload = False):
    return [getShapeFileFromSIGPAC(zipCode=zc,
                                   url=url,
                                   root_dir=root_dir,
                                   suffix=suffix,
                                   datadir=datadir,
                                   forceDownload=forceDownload) for zc in zipCodes]
                                        
    
shape = getShapeFilesFromSIGPAC(['49287', '42319'], forceDownload=True)
        
