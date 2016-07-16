"""
Created on Mon Jul 04 17:16:53 2016

@author: jlafuente
"""

from sklearn.neighbors import KDTree

from osc import util


def get_(point, k, data, dimensions=None):
    data = data if dimensions is None else data[util.as_list(dimensions)]
    tree = KDTree(data)
    return tree.query(point, k)
