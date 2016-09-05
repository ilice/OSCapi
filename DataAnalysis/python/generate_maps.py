import matplotlib
matplotlib.use('Agg')


from __future__ import division
import osc.importer.sigpac as sigpac
import matplotlib.pyplot as plt
import seaborn as sns
import os
import osc.config as config
import pandas as pd

# store = pd.HDFStore(os.path.join(config.data_dir, 'SIGPAC', 'dataframes.h5'))

# ['05', '09', '24', '34', '37', '40', '42', '47', '49']

for codigo_provincia in ['34', '40', '42', '47', '49', '24']:
    print 'Starting with zipcode ' + codigo_provincia

    df = sigpac.get_dataframe(sigpac.all_zipcodes(starting_with=codigo_provincia),
                              force_download=False,
                              with_bbox_center=True)

    xmin = df['x_bbox_center'].min() - 10000
    xmax = df['x_bbox_center'].max() + 20000
    ymin = df['y_bbox_center'].min() - 10000
    ymax = df['y_bbox_center'].max() + 10000
    aspect = (xmax - xmin) / (ymax - ymin)

    # Plot the whole map
    print 'Plotting all uses'
    g = sns.lmplot(x='x_bbox_center', y='y_bbox_center', hue='USO_SIGPAC', fit_reg=False, data=df, scatter_kws={'alpha': 0.2}, size=15, aspect=aspect)
    g.set(xlim=(xmin, xmax), ylim=(ymin, ymax))
    g.set_axis_labels(x_var='', y_var='')
    plt.savefig(os.path.join(config.tmp_dir, 'usos_sigpac', codigo_provincia + '_ALL.png'))
    plt.close('all')

    # Plot per SIGPAC_USE
    for uso_sigpac in df['USO_SIGPAC'].unique():
        print 'Plotting use ' + uso_sigpac
        g = sns.lmplot(x='x_bbox_center', y='y_bbox_center', fit_reg=False,
                       data=df[df['USO_SIGPAC'] == uso_sigpac], scatter_kws={'alpha': 0.2}, size=15, aspect=aspect)
        g.set(xlim=(xmin, xmax), ylim=(ymin, ymax))
        g.set_axis_labels(x_var='', y_var='')
        plt.savefig(os.path.join(config.tmp_dir, 'usos_sigpac', codigo_provincia + '_' + uso_sigpac + '.png'))
        plt.close('all')

    del df
    print 'Finishing ' + codigo_provincia


# in plotly
import plotly
import plotly.graph_objs as go
import plotly.plotly as py
plotly.tools.set_credentials_file(username='jlafuente', api_key='6gw4a0xabi')

codigo_provincia = '37'

df = sigpac.get_dataframe(sigpac.all_zipcodes(starting_with=codigo_provincia),
                          force_download=False,
                          with_bbox_center=True)

go_data = []
for uso_sigpac in df['USO_SIGPAC'].unique():
    data = df[df['USO_SIGPAC'] == uso_sigpac]
    go_data.append(go.Scattergl(x=data['x_bbox_center'], y=data['y_bbox_center'], name=uso_sigpac, mode='markers'))

fig = go.Figure(data=go_data)
py.iplot(fig, filename='Provincia ' + codigo_provincia)


# Save dataframes
store = pd.HDFStore(os.path.join(config.dataframes_dir, 'sigpac.h5'))
for codigo_provincia in ['05', '09', '24', '34', '37', '40', '42', '47', '49']:
    print 'Starting with zipcode ' + codigo_provincia

    df = sigpac.get_dataframe(sigpac.all_zipcodes(starting_with=codigo_provincia),
                              force_download=False,
                              with_bbox_center=True)

    print 'Finished reading zipcode ' + codigo_provincia

    store['province_' + codigo_provincia] = df

    print 'Finished writting zipcode ' + codigo_provincia
