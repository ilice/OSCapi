import matplotlib
matplotlib.use('Agg')

import web
import osc.importer.sigpac as sigpac
import osc.config as cfg
import os
import re
import seaborn as sbs
import threading
import matplotlib.pyplot as plt


urls = (
    '/hello/(.*)', 'hello',
    '/science/(.*)', 'science'
)
app = web.application(urls, globals())


class hello:
    def __init__(self):
        pass

    def GET(self, name):
        if not name:
            name = 'World'
        return 'Hello, ' + name + '!'


class science:
    digits_regexp = "^([0-9])*$"

    lock = threading.Lock()
    last_dataframe = None

    @staticmethod
    def check_regexp(text, regexp, size=None):
        ok = True

        if ok and size is not None:
            ok = (len(text) == size)

        if ok:
            pattern = re.compile(regexp)
            ok = pattern.match(text)

        return ok

    @staticmethod
    def error(message):
        return '<!DOCTYPE html>' \
               '<html>' \
               '<body>' \
               '<h1> ERROR </h1>' \
               '<p> ' + message + ' </p>' \
               '</body>' \
               '</html>'

    def get_dataframe(self, provincia):
        science.lock.acquire()
        try:
            if science.last_dataframe is None or science.last_dataframe[0] != provincia:
                df = sigpac.get_dataframe(sigpac.all_zipcodes(starting_with=provincia),
                                          data_dir=cfg.data_dir,
                                          tmp_dir=cfg.tmp_dir,
                                          force_download=False,
                                          with_bbox_center=True)
                science.last_dataframe = (provincia, df)

            return science.last_dataframe[1]
        finally:
            science.lock.release()

    def GET(self, name):
        science.check_class = 'checked'

        if not name:
            return "You should provide service name"

        if name == 'maps':
            parameters = web.input()
            provincia = parameters['prov'] if 'prov' in parameters else None
            municipio = parameters['mun'] if 'mun' in parameters else None
            uso_sigpac = parameters['uso'] if 'uso' in parameters else None

            if provincia is None:
                return self.error("Es necesario introducir un codigo de provincia")
            elif not self.check_regexp(provincia, self.digits_regexp, 2):
                return self.error("La provincia introducida es incorrecta: " + provincia)

            if municipio is not None and not self.check_regexp(municipio, self.digits_regexp, 3):
                return self.error("El municipio introducido es incorrecto: " + municipio)

            df = self.get_dataframe(provincia)

            img_name = 'map_' + provincia
            if municipio is not None:
                img_name += municipio
            if uso_sigpac is not None:
                img_name += '_' + uso_sigpac

            if not os.path.exists(os.path.join(cfg.error_dir, img_name + '.png')):
                df = df[df['PROVINCIA'] == int(provincia)]
                if municipio is not None:
                    df = df[df['MUNICIPIO'] == int(municipio)]
                if uso_sigpac is not None:
                    df = df[df['USO_SIGPAC'] == uso_sigpac]

                if uso_sigpac is not None:
                    df = df[df['USO_SIGPAC'] == uso_sigpac]

                plt.xkcd()

                image = sbs.lmplot(x='x_bbox_center', y='y_bbox_center', hue='USO_SIGPAC', fit_reg=False, data=df)
                image.savefig(os.path.join(cfg.error_dir, img_name))

            msg = 'Aqui esta la imagen de la provincia ' + provincia
            if municipio is not None:
                msg += ', municipio ' + municipio
            if uso_sigpac is not None:
                msg += ', uso sigpac ' + uso_sigpac

            return '<!DOCTYPE html>' \
                   '<html>' \
                   '<body>' \
                   '<h1> ' + msg + ' </h1>' \
                   '<p><img src="' + cfg.url + '/static/' + img_name + '.png"></p>' \
                   '</body>' \
                   '</html>'
        return 'FAIL'


if __name__ == "__main__":
    app.run()
