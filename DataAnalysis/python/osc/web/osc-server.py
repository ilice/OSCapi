import matplotlib
matplotlib.use('Agg')

import web
import osc.importer.sigpac as sigpac
import osc.config as cfg
import os
import seaborn as sbs


urls = (
    '/hello/(.*)', 'hello',
    '/science/(.*)', 'science'
)
app = web.application(urls, globals())

last_dataframe = None

class hello:
    def GET(self, name):
        if not name:
            name = 'World'
        return 'Hello, ' + name + '!'


class science:
    def GET(self, name):
        global last_dataframe

        if not name:
            return "You should provide service name"

        if name == 'maps':
            parameters = web.input()
            zipcode = parameters['zipcode']
            uso_sigpac = parameters['uso'] if 'uso' in parameters else None

            if last_dataframe is None or last_dataframe[0] != zipcode:
                df = sigpac.get_dataframe(sigpac.all_zipcodes(starting_with=zipcode),
                                          data_dir=cfg.data_dir,
                                          tmp_dir=cfg.tmp_dir,
                                          force_download=False,
                                          with_bbox_center=True)
                last_dataframe = (zipcode, df)

            image = None
            img_name = None

            if uso_sigpac is not None:
                df = last_dataframe[1]
                df = df[df['USO_SIGPAC'] == uso_sigpac]

                img_name = 'map_' + uso_sigpac + '_' + zipcode

                image = sbs.lmplot(x='x_bbox_center', y='y_bbox_center', fit_reg=False, data=df)
            else:
                img_name = 'map_' + zipcode

                image = sbs.lmplot(x='x_bbox_center', y='y_bbox_center', hue='USO_SIGPAC', fit_reg=False, data=last_dataframe[1])

            image.savefig(os.path.join(cfg.error_dir, img_name))

            return '<!DOCTYPE html>' \
                   '<html>' \
                   '<body>' \
                   '<h1> Aqui tienes la imagen de los codigos postales que empiezan por ' + zipcode + ' </h1>' \
                   '<p><img src="' + cfg.url + '/static/' + img_name + '.png"></p>' \
                   '</body>' \
                   '</html>'
        return 'FAIL'


if __name__ == "__main__":
    app.run()