"""
Created on Mon Jul 04 17:16:53 2016

@author: jlafuente
"""

import util
from sklearn.neighbors import KDTree

def get_nearest(point, k, data, dimensions = None):
    data = data if dimensions is None else data[util.as_list(dimensions)]
    tree = KDTree(data)
    return tree.query(point, k)
