# -*- coding: utf-8 -*-
"""
Created on Mon Jul 04 17:16:53 2016

@author: jlafuente
"""
import sigpac

                                       
sigpac.download_shapefiles(sigpac.all_zipcodes(),
                           data_dir='d:/OpenSmartCountry/data',
                           tmp_dir='d:/OpenSmartCountry/tmp',
                           force_download=False)
                                       
"""
dataFrame = data.get_dataframe(['2015'],
                                       datadir='d:/OpenSmartCountry/data', 
                                       tmpDir='d:/OpenSmartCountry/tmp')

dataFrame = pd.read_csv(os.path.join('d:/OpenSmartCountry/data/InfoRiego/2001', 
                         '20011231_RedClimaITACYL_Horario.csv'),
            encoding='mbcs',
            sep=';')


data.download_daily_files(['2001', '2002', '2003', '2004', '2005',
                                  '2006', '2007', '2008', '2009', '2010', 
                                  '2011', '2012', '2013', '2014'], 
                                 datadir='d:/OpenSmartCountry/data', 
                                 tmpDir='d:/OpenSmartCountry/tmp')

zipCodes = data.getAllZipCodesFromSIGPAC()
print (zipCodes)                                
       
data.downloadShapeFilesFromSIGPAC(zipCodes, 
                             datadir='d:/OpenSmartCountry/data', 
                             tmpDir='d:/OpenSmartCountry/tmp')
                             
                             
                         
shapes = getShapeFilesFromSIGPAC(['49287', '42319'], forceDownload=True)
"""       
