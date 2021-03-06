# coding=utf-8
# Author: Rion B Correia
# Date: Aug 06, 2019
#
# Description: Plots the linear relationship between FPKM and mean(Fert-Rate)
#
# Instructions:
#
import numpy as np
import pandas as pd
pd.set_option('display.max_rows', 100)
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from matplotlib import colors
mpl.rcParams['font.family'] = 'Helvetica'
mpl.rcParams['mathtext.fontset'] = 'cm'
import matplotlib.ticker as mtick
import statsmodels.api as sm
from statsmodels.graphics.regressionplots import abline_plot


def calc_control_mean_std_fert_rate(x):
    fertrate = x['hatched'] / x['eggs']
    return pd.Series({'mean fert-rate': fertrate.mean(), 'std fert-rate': fertrate.std()})


if __name__ == '__main__':

    # Load genes
    df = pd.read_csv('../02-core_genes/results/pipeline-core/DM_meiotic_genes.csv', index_col=0, usecols=['id_gene', 'gene'])

    # Load Screened data
    dfs = pd.read_csv('data/core_DM_screened_2020-10-21.csv', index_col=0)

    # Load Control data
    dfc = pd.read_csv('data/screened_DM_controls.csv', index_col=0)
    dfc = dfc.groupby(dfc.index).apply(calc_control_mean_std_fert_rate)

    # Load FPKM data
    dfFPKM = pd.read_csv('../02-core_genes/results/FPKM/DM/DM-FPKM-spermatocyte.csv.gz', index_col=0, usecols=['id_gene', 'FPKM'])

    dfs_only = dfs.loc[~dfs['FT1 eggs'].isnull(), :]

    status_cats = ['Screened', 'To be crossed', 'Pending', 'Reorder']
    dfs['Status'] = pd.Categorical(dfs['Status'], categories=status_cats, ordered=True)
    df['Status'] = dfs['Status']

    cols = ['FT1 eggs', 'FT1 hatched', 'FT2 eggs', 'FT2 hatched', 'FT3 eggs', 'FT3 hatched', 'FT4 eggs', 'FT4 hatched']
    df[cols] = dfs_only[cols]

    # Only plot screened genes
    df = df.loc[df['Status'] == 'Screened', :]

    # Calculations
    df['total-eggs'] = 0
    df['total-hatched'] = 0
    for ft in range(1, 5):

        col_eggs = 'FT{:d} eggs'.format(ft)
        col_hatched = 'FT{:d} hatched'.format(ft)
        col_fertate = 'FT{:d} fert-rate'.format(ft)
        df[col_fertate] = df[col_hatched] / df[col_eggs]
        df['total-eggs'] += df[col_eggs]
        df['total-hatched'] += df[col_hatched]

    # Mean/SD
    df['mean fert-rate'] = df[['FT1 fert-rate', 'FT2 fert-rate', 'FT3 fert-rate', 'FT4 fert-rate']].mean(axis=1)
    df['std fert-rate'] = df[['FT1 fert-rate', 'FT2 fert-rate', 'FT3 fert-rate', 'FT4 fert-rate']].std(axis=1)

    # FPKM
    df['FPKM'] = dfFPKM['FPKM']
    df['logFPKM'] = df['FPKM'].apply(lambda x: np.log2(x + 1))

    maxfpkm, minfpkm = df['logFPKM'].max(), df['logFPKM'].min()

    #
    # Plot all data
    #

    fig = plt.figure(figsize=(6, 3))

    gs = gridspec.GridSpec(nrows=15, ncols=21)
    ax = plt.subplot(gs[3:17, 0:18])
    axt = plt.subplot(gs[0:2, 0:18])
    axb = plt.subplot(gs[3:18, 19:21])

    axt.set_title("Core genes expression level", fontsize='medium')

    # Data
    x = df['logFPKM']
    y = df['mean fert-rate']

    # OLS
    X = sm.add_constant(x)
    model = sm.OLS(y, X)
    results = model.fit()

    # Main
    sc = ax.scatter(x=x, y=y, fc='#3182bdcc', ec='#3182bd', s=8, zorder=5)
    ax.set_ylabel('Fertility rate')
    ax.set_xlabel(r'Log$_2$(FPKM+1)')
    ax.grid()

    ax.text(x=9, y=0.5, s=r"$R^2={rsquared:.2f}$".format(rsquared=results.rsquared))
    abline_plot(model_results=results, color='#d62728', ax=ax, zorder=6) # regression line

    # Top
    xw = np.ones(shape=len(x)) / len(x)
    axt.hist(x, bins=22, color='#ff9896', weights=xw, zorder=5)
    #axt.axes.get_xaxis().set_visible(False)
    axt.set_xticklabels([])
    axt.yaxis.set_major_formatter(mtick.PercentFormatter(1, decimals=0))
    axt.set_ylabel('%')
    axt.grid()

    # Bottom
    yw = np.ones(shape=len(y))/len(y)
    axb.hist(y, bins=22, color='#aec7e8', weights=yw, orientation='horizontal', zorder=5)
    #axb.axes.get_yaxis().set_visible(False)
    axb.yaxis.set_label_position("right")
    axb.set_ylabel('Silenced core genes phen.')
    axb.set_yticklabels([])
    axb.xaxis.set_major_formatter(mtick.PercentFormatter(1, decimals=0))
    axb.set_xlabel('%')
    #axb.set_xlim(-0.02,0.2)
    axb.grid()

    plt.subplots_adjust(left=0.13, right=0.774, bottom=0.16, top=0.90, wspace=0.50, hspace=0.50)
    fig.savefig('images/img-linreg-FPKM-fertrate.pdf')