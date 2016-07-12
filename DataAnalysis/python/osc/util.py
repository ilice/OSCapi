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
            except:
                logger.error("Error unzipping file: " + info.filename)


class ErrorHandler:
    error_path = None

    def __init__(self, error_path):
        self.error_path = error_path

    def path(self, module_name, reg_id):
        return os.path.join(self.error_path, module_name + '_' + reg_id)

    def handle(self, module_name, reg_id, desc = None):
        if not os.path.exists(self.error_path):
            os.makedirs(self.error_path)

        file_path = self.path(module_name, reg_id)

        with open(file_path, mode='w') as f:
            if desc is not None:
                f.write(desc)
