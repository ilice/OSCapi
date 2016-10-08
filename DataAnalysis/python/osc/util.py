import os
import logging
import zipfile
import matplotlib.pyplot as plt
from elasticsearch_dsl.connections import connections
import elasticsearch as es
import config as conf
import datetime
import time


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


def try_rest(last_rest_time, working_interval_minutes, rest_time_minutes):
    working_time = (datetime.datetime.now() - last_rest_time).total_seconds() / 60

    if working_time > working_interval_minutes:
        time.sleep(rest_time_minutes * 60)
        last_rest_time = datetime.datetime.now()

    return last_rest_time


def try_times(f, max_trials, time_wait):
    trial = 0
    while trial < max_trials:
        try:
            f()
            return
        except Exception as e:
            conf.error_handler.error(__name__, "try_times -- " + f.__name__, str(e))
            conf.error_handler.flush()
            if trial > max_trials:
                raise

            trial += 1
            time.sleep(time_wait)


def wait_for_yellow_cluster_status():
    connection = connections.get_connection()
    while True:
        try:
            cluster_status = connection.cluster.health(wait_for_status='yellow')
            if cluster_status['status'] != 'red':
                break
        except Exception as e:
            print 'Cluster status is red. Waiting for yellow status'


def elastic_bulk_update(records, retry=True):
    try:
        connection = connections.get_connection()
        wait_for_yellow_cluster_status()
        es.helpers.bulk(connection,
                        ({'_op_type': 'update',
                          '_index': getattr(r.meta, 'index', r._doc_type.index),
                          '_id': getattr(r.meta, 'id', None),
                          '_type': r._doc_type.name,
                          'doc': r.to_dict()} for r in records))
    except Exception as e:
        for record in records:
            if retry:
                elastic_bulk_update([record], retry=False)
            else:
                conf.error_handler.error(__name__,
                                         'elastic_bulk_update',
                                         str(type(e)) + ': ' + str(record.to_dict()))


def elastic_bulk_save(records, retry=True):
    try:
        connection = connections.get_connection()
        wait_for_yellow_cluster_status()
        es.helpers.bulk(connection,
                        ({'_index': getattr(r.meta, 'index', r._doc_type.index),
                          '_id': getattr(r.meta, 'id', None),
                          '_type': r._doc_type.name,
                          '_source': r.to_dict()} for r in records))
    except Exception as e:
        for record in records:
            if retry:
                elastic_bulk_save([record], retry=False)
            else:
                conf.error_handler.error(__name__,
                                         'save2elasticsearch',
                                         str(type(e)) + ': ' + str(record.to_dict()))
