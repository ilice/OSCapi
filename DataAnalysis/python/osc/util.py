import os
import logging
import zipfile
import matplotlib.pyplot as plt
from elasticsearch_dsl.connections import connections


FORMAT = '%(asctime)-15s %(clientip)s %(user)-8s %(message)s'
logging.basicConfig(format=FORMAT)
logger = logging.Logger(__name__)


def as_list(param):
    if type(param) is list:
        return param
    return [param]


def unzip_file(zipfile_path,
               to_path,
               filter_func=None):
    # uncompress the zipfile
    if not os.path.exists(to_path):
        os.makedirs(to_path)

    with (zipfile.ZipFile(zipfile_path)) as file:
        infos = file.infolist()
        if filter_func is not None:
            infos = filter(filter_func, infos)

        for info in infos:
            logger.debug("Extracting " + info.filename + " to " + to_path)

            try:
                file.extract(info, path=to_path)
                logger.debug("... extracted")
            except:
                logger.error("Error unzipping file: " + info.filename)


def plot_polygon(polygon):
    plt.xkcd()
    plt.figure()

    for inner_pol in polygon:
        x = [point[0] for point in inner_pol]
        y = [point[1] for point in inner_pol]

        plt.plot(x, y, '-')
        plt.plot(x, y, '.')
        plt.plot([x[0]], [y[0]], 'o')
    plt.show()


def wait_for_yellow_cluster_status():
    connection = connections.get_connection()
    while True:
        try:
            cluster_status = connection.cluster.health(wait_for_status='yellow')
            if cluster_status['status'] != 'red':
                break
        except Exception as e:
            print 'Cluster status is red. Waiting for yellow status'
