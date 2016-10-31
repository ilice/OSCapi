import os
import logging
import zipfile
import matplotlib.pyplot as plt
import elasticsearch.helpers as es_helpers
import datetime
import time
from osc.util import error_managed, es
from osc.exceptions import ElasticException
import pytz
from django.conf import settings

logger = logging.Logger(__name__)


def localize_datetime(datetime):
    return pytz.timezone(settings.TIME_ZONE).localize(datetime)


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
            if trial > max_trials:
                raise

            trial += 1
            time.sleep(time_wait)


def wait_for_yellow_cluster_status():
    while True:
        try:
            cluster_status = es.cluster.health(wait_for_status='yellow')
            if cluster_status['status'] != 'red':
                break
        except Exception as e:
            print ('Cluster status is red. Waiting for yellow status')


@error_managed()
def elastic_bulk_update_dsl(process_name, records, retry=True):
    try:
        wait_for_yellow_cluster_status()
        es_helpers.bulk(es,
                        ({'_op_type': 'update',
                          '_index': getattr(r.meta, 'index', r._doc_type.index),
                          '_id': getattr(r.meta, 'id', None),
                          '_type': r._doc_type.name,
                          '_source': r.to_dict()} for r in records))
    except Exception as e:
        for record in records:
            if retry:
                elastic_bulk_update_dsl([record], retry=False)
            else:
                raise ElasticException(process_name, 'Error saving to Elastic', actionable_info=str(record))


@error_managed()
def elastic_bulk_save_dsl(process_name, records, retry=True):
    try:
        wait_for_yellow_cluster_status()
        es_helpers.bulk(es,
                        ({'_index': getattr(r.meta, 'index', r._doc_type.index),
                          '_id': getattr(r.meta, 'id', None),
                          '_type': r._doc_type.name,
                          '_source': r.to_dict()} for r in records))
    except Exception as e:
        for record in records:
            if retry:
                elastic_bulk_save_dsl([record], retry=False)
            else:
                raise ElasticException(process_name, 'Error saving to Elastic', actionable_info=str(record))


@error_managed()
def elastic_bulk_update(process_name, index, doc_type, records, ids=None, retry=True):
    try:
        if ids is None:
            ids = [None] * len(records)

        wait_for_yellow_cluster_status()
        es_helpers.bulk(es,
                        ({'_op_type': 'update',
                          '_index': index,
                          '_id': idx,
                          '_type': doc_type,
                          '_source': r} for (r, idx) in zip(records, ids)))
    except Exception as e:
        for (r, idx) in zip(records, ids):
            if retry:
                elastic_bulk_update(process_name, index, doc_type, [r], [idx], retry=False)
            else:
                raise ElasticException(process_name, 'Error saving to Elastic', actionable_info=str(r))


@error_managed(inhibit_exception=True)
def elastic_bulk_save(process_name, index, doc_type, records, ids=None, retry=True):
    try:
        if ids is None:
            ids = [None] * len(records)

        wait_for_yellow_cluster_status()
        es_helpers.bulk(es,
                        ({'_index': index,
                          '_id': idx,
                          '_type': doc_type,
                          '_source': r} for (r, idx) in zip(records, ids)))
    except Exception as e:
        for (r, idx) in zip(records, ids):
            if retry:
                elastic_bulk_save(process_name, index, doc_type, [r], [idx], retry=False)
            else:
                raise ElasticException(process_name, 'Error saving to Elastic', actionable_info=str(r), cause=e)


def num(s):
    try:
        return int(s)
    except ValueError:
        return float(s)


def xml_to_json(element, lists=(), forced_int=()):
    json_element = dict()
    for child in element:
        tag = child.tag.split('}')[-1]
        json_child = xml_to_json(child, lists, forced_int=forced_int)

        if tag in lists:
            json_element[tag] = (json_element[tag] if tag in json_element else []) + [json_child]
        else:
            json_element[tag] = json_child

    if len(json_element) == 0:
        json_element = None
        if element.text is not None:
            if element.tag.split('}')[-1] in forced_int:
                try:
                    json_element = num(element.text) if len(str(num(element.text))) == len(element.text) else element.text
                except ValueError:
                    json_element = element.text
            else:
                json_element = element.text

    return json_element


def contains_any(text, text_list):
    return len([t for t in text_list if t.lower() in text.lower()]) >= 1
