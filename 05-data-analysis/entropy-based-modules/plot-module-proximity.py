# coding=utf-8
# Author: Rion B Correia
# Date: Sept 02, 2019
#
# Description: Reads the similarity-celltype and plots the results.
#
#
import numpy as np
import pandas as pd
pd.set_option('display.max_rows', 100)
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)
import matplotlib as mpl
mpl.rcParams['font.family'] = 'Helvetica'
mpl.rcParams['mathtext.fontset'] = 'cm'
from matplotlib import cm
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from utils import ensurePathExists


def plot_module_proximity(celltype='spermatocyte', network='thr', threshold=0.5):

    threshold_str = str(threshold).replace('.', 'p')

    #
    print('Loading .csv')
    rCSVFile = 'results/module-proximity/module-proximity-{celltype:s}-{network:s}-{threshold:s}.csv.gz'.format(celltype=celltype, network=network, threshold=threshold_str)

    df = pd.read_csv(rCSVFile, index_col=0)

    dict_replace = {
        'Ubiquitination': 'Ubiq.',
        'Splicing': 'Splc.',
        'Translation': 'Trsl.',
        'rRNA regulation': 'rRNA',
        'Vesicle transport': 'Ves. trsp.',
        'Respiration': 'Resp.',
        'Cell cycle': 'Cell cyc.',
        'DNA repair': 'DNA rep.',
        'Mitochondrial translation': 'M. trsl.',
        'Cell cycle (II)': 'Cell cyc. II',
        'Metabolism': 'Metb.',
        'Peptidyl-histidine dephosphorylation': 'Pep. dephospho.'
    }

    # Only plot M1 - M6
    df = df.loc[((df['id-i'] <= 6) & (df['id-j'] <= 6)), :]

    df['short-i'] = df['name-i'].replace(dict_replace)
    df['short-j'] = df['name-j'].replace(dict_replace)

    fig, axes = plt.subplots(figsize=(8.5, 2.8), nrows=1, ncols=3)
    axcb = fig.add_axes([0.27, 0.08, 0.12, 0.03])
    #
    layer_pairs = [('HS', 'MM'), ('HS', 'DM'), ('MM', 'DM')]
    species_name = {'HS': 'Human', 'MM': 'Mouse', 'DM': 'Insect'}
    cmap = cm.get_cmap('jet')
    cmap.set_bad(color='#bdbdbd')

    for (layer_i, layer_j), ax in zip(layer_pairs, axes):
        #
        dft = df.loc[(df['layer-i'] == layer_i) & (df['layer-j'] == layer_j), :]

        dft = dft.pivot_table(index=['id-i', 'short-i'], columns=['id-j', 'short-j'], values='proximity', aggfunc='first')

        index = dft.index if len(dft.index) > len(dft.columns) else dft.columns
        dft = dft.reindex(index=index, columns=index, fill_value=np.nan).T

        print(dft)

        ticks = list(range(max(dft.shape)))
        ticklabels = ['M{id:d}-{short:s}'.format(id=id, short=short) for id, short in dft.index.values]

        im = ax.imshow(dft.values, cmap=cmap, vmin=0.0, vmax=1.0)

        celltype_str = 'germ cell' if celltype == 'spermatocyte' else 'soma'

        species_i = species_name[layer_i]
        xlabel = '{species:s} {celltype:s}'.format(species=species_i, celltype=celltype_str)
        ax.set_xlabel(xlabel)
        ax.xaxis.set_label_position("top")

        species_j = species_name[layer_j]
        ylabel = '{species:s} {celltype:s}'.format(species=species_j, celltype=celltype_str)
        ax.set_ylabel(ylabel)
        ax.yaxis.set_label_position("right")

        # Ticks
        ax.set_xticks(ticks)
        ax.set_yticks(ticks)

        ax.set_yticklabels(ticklabels, rotation=0)
        ax.set_xticklabels(ticklabels, rotation=45, ha='right', va='top')

    # Create colorbar
    cbar = plt.colorbar(im, cax=axcb, orientation='horizontal', ticks=[0, 0.5, 1], boundaries=np.linspace(0, 1, 30))
    cbar.ax.tick_params(labelsize='small')
    cbar.ax.set_title('Similarity', rotation=0, fontsize='medium')

    #plt.subplots_adjust(left=0.12, right=0.96, bottom=0.2, top=0.98, wspace=0.6, hspace=0.0)
    plt.tight_layout()
    wIMGfile = 'images/module-proximity/img-module-proximity-{celltype:s}-{network:s}-{threshold:s}.pdf'.format(celltype=celltype, network=network, threshold=threshold_str)
    ensurePathExists(wIMGfile)
    plt.savefig(wIMGfile, dpi=150, bbox_inches=None, pad_inches=0.0)
    plt.close()


if __name__ == '__main__':

    celltype = 'spermatocyte'  # spermatocyte or enterocyte
    network = 'thr'  # 'thr'
    threshold = 0.5

    # plot_module_proximity(celltype=celltype, network=network, threshold=threshold)

    for celltype in ['spermatocyte', 'enterocyte']:
        plot_module_proximity(celltype=celltype, network=network, threshold=threshold)
