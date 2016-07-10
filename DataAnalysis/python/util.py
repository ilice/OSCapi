import os
import logging
import zipfile


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
	    except zipfile.BadZipFile:
		logger.error("Error unzipping file: " + info.filename)

