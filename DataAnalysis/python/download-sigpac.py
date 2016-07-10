# -*- coding: utf-8 -*-
"""
Created on Mon Jul 04 17:16:53 2016

@author: jlafuente
"""
import sigpac
import os

data_dir = os.path.join(os.getenv('OSC_HOME', '../data'), 'data')
tmp_dir = os.path.join(os.getenv('OSC_HOME', '../tmp'), 'tmp')

print "Downloading SIGPAC shapefiles. data_dir = " + data_dir + ' tmp_dir = ' + tmp_dir


sigpac.download_shapefiles(sigpac.all_zipcodes(),
                           data_dir=data_dir,
                           tmp_dir=tmp_dir,
                           force_download=False)

print "I'm done!!!"
