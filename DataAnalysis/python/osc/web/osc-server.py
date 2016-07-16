import web
import osc.importer.sigpac as sigpac
import osc.config as cfg
import seaborn as sbs
import os

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

            if last_dataframe is None or last_dataframe[0] != zipcode:
                df = sigpac.get_dataframe(sigpac.all_zipcodes(starting_with=zipcode),
                                          data_dir=cfg.data_dir,
                                          tmp_dir=cfg.tmp_dir,
                                          force_download=False,
                                          with_bbox_center=True)
                last_dataframe = (zipcode, df)

                image = sbs.lmplot(x='x_bbox_center', y='y_bbox_center', hue='USO_SIGPAC', fit_reg=False, data=last_dataframe[1])

                image.savefig(os.path.join(cfg.error_dir, 'map_' + zipcode))

        return '<!DOCTYPE html>' \
               '<html>' \
               '<body>' \
               '<h1> Aqui tienes la imagen de los codigos postales que empiezan por ' + zipcode + ' </h1>' \
               '<p><img src="' + cfg.url + '/static/map_' + zipcode + '.png"></p>' \
               '</body>' \
               '</html>'


if __name__ == "__main__":
    app.run()