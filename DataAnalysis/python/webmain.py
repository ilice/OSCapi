# -*- coding: utf-8 -*-
"""
Created on Mon Jul 04 17:16:53 2016

@author: jlafuente
"""
import sigpac
import science

sigpac.download_shapefiles(sigpac.all_zipcodes(),
                           data_dir='d:/OpenSmartCountry/data',
                           tmp_dir='d:/OpenSmartCountry/tmp',
                           force_download=False)
"""
dataFrame = sigpac.get_dataframe(sigpac.all_zipcodes(starting_with='0500'),
                                 usecols=['FACTOR_PE0', 'FACTOR_SU0', 'FACTOR_VE0', 'FECHA_CAM0', 'MUNICIPIO',
                                          'PARCELA', 'PEND_MED', 'PERIMETRO', 'POLIGONO', 'PROVINCIA', 'RECINTO',
                                          'SUPERFICIE', 'USO_SIGPAC', 'ZONA', 'bbox'],
                                 data_dir='d:/OpenSmartCountry/data',
                                 tmp_dir='d:/OpenSmartCountry/tmp',
                                 force_download=False)


def compute_bb_center(list_str, axis=None):
    import ast

    bbox = ast.literal_eval(list_str)

    if axis == 0:
        return bbox[0] + (bbox[2]-bbox[0]) / 2
    elif axis == 1:
        return bbox[1] + (bbox[3]-bbox[1]) / 2
    return bbox[0] + (bbox[2]-bbox[0]) / 2, bbox[1] + (bbox[3]-bbox[1]) / 2

dataFrame['bbcenter_x'] = dataFrame['bbox'].apply(lambda x: compute_bb_center(x, axis=0))
dataFrame['bbcenter_y'] = dataFrame['bbox'].apply(lambda x: compute_bb_center(x, axis=1))

nearest_1000 = science.get_nearest(point=[341947, 4546986],
                                   k=1000,
                                   data=dataFrame,
                                   dimensions=['bbcenter_x', 'bbcenter_y'])


sigpac.download_shapefiles(sigpac.all_zipcodes(),
                           data_dir='d:/OpenSmartCountry/data',
                           tmp_dir='d:/OpenSmartCountry/tmp',
                           force_download=False)
                                       

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
