import osc.config as config
import pandas as pd
import os
import seaborn as sns
import matplotlib.pyplot as plt

df = pd.read_csv(os.path.join(config.data_dir, 'MAGRAMA', 'csv', 'historico_superficie_cultivos.csv'), encoding='utf-8')

code_name = df['des'].str.split(' ', 1)
df['codigo_cultivo'] = code_name.apply(lambda x: x[0])
df['nombre_cultivo'] = code_name.apply(lambda x: x[1])
df.drop('des', axis=1, inplace=True)
df['cana'] = df['cana'].str.split(' ', 1).apply(lambda x: x[1])
df.columns = [u'año', u'codigo_comunidad', u'nombre_comunidad', u'SRI', u'SRI_desc', u'grupo',
              u'superficie', u'codigo_cultivo', u'nombre_cultivo']


no_cultivos=['ERIAL', 'BALDIO', 'IMPRODUCTIVO', 'NO AGRICOLA',
             'AGUAS INTERIORES', 'ESPARTIZAL', 'SUPERFICIE VACIA INVERNA',
             'SIN CULTIVO (NO INVESTIG']

cultivos = filter(lambda x: x not in no_cultivos, df['nombre_cultivo'].unique())

"""
First plot the time series for  Girasol, Melon, Cebolla
"""
df_girasol = df[df['nombre_cultivo'] == 'GIRASOL']
df_melon = df[df['nombre_cultivo'] == 'MELON']
df_cebolla = df[df['nombre_cultivo'] == 'CEBOLLA']
df_maiz = df[df['nombre_cultivo'] == 'MAIZ']
df_sandia = df[df['nombre_cultivo'] == 'SANDIA']


"""
Superficie Girasol
"""

def plt_barplot(df, cultivo = None, nombre = None, comunidad = None):
    if nombre is None:
        nombre = str(cultivo)

    if isinstance(cultivo, list):
        data = df[df['nombre_cultivo'].isin(cultivo)]
    else:
        data = df[df['nombre_cultivo'] == cultivo] if cultivo is not None else df

    if comunidad is not None:
        data = data[data[u'nombre_comunidad'] == comunidad]

    plt.figure()
    sns.barplot(x=u'año', y=u'superficie', data=data, estimator=sum, ci=None)
    plt.suptitle(nombre, fontsize=20)
    plt.savefig(os.path.join(config.tmp_dir, 'barplot_' + nombre + '.png'))

plt_barplot(df, 'GIRASOL')
plt_barplot(df, 'MELON')
plt_barplot(df, 'CEBOLLA')
plt_barplot(df, 'MAIZ')
plt_barplot(df, 'SANDIA')
plt_barplot(df, 'VIÑEDO')
plt_barplot(df, 'HUERTOS FAMILIARES')

plt_barplot(df, no_cultivos, nombre='NO CULTIVOS', comunidad='CASTILLA-LEON')

plt_barplot(df, cultivos, nombre='TODOS_LOS_CULTIVOS', comunidad='CASTILLA-LEON')

plt.figure()
sns.barplot(x=u'año', y=u'superficie', data=df[df[u'grupo'] == '0c Vi\xf1edo'], estimator=sum, ci=None)
plt.suptitle('VIÑEDO', fontsize=20)

data = df_girasol[[u'año', u'superficie', u'nombre_comunidad']].groupby(by=[u'año', u'nombre_comunidad']).sum()
data = data.reset_index()
sns.barplot(x=u'nombre_comunidad', y=u'superficie', hue=u'año', data=data, estimator=sum)


(df[df['nombre_cultivo'].isin(cultivos)][[u'año', u'superficie']].groupby(u'año').sum() / 1e7).plot()

(df[df['nombre_cultivo'].isin(no_cultivos)][[u'año', u'superficie']].groupby(u'año').sum() / 1e7).plot()

(df[[u'año', u'superficie']].groupby(u'año').sum() / 1e7).plot()



# in plotly
import plotly
import plotly.graph_objs as go
import plotly.plotly as py
plotly.tools.set_credentials_file(username='jlafuente', api_key='6gw4a0xabi')

go_data = []
for cultivo in no_cultivos:
    data = df[df[u'nombre_cultivo'] == cultivo][[u'año', u'superficie']].groupby(u'año').sum()
    data.reset_index(inplace=True)

    go_data.append(go.Scatter(x=data[u'año'], y=data[u'superficie'], name=cultivo, mode='markers'))

fig = go.Figure(data=go_data)
py.iplot(fig, filename='MAGRAMA NO CULTIVOS')
