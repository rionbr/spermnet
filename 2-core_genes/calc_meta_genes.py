# coding=utf-8
# Author: Rion B Correia
# Date: Jul 05, 2019
#
# Description: Processes original String-DB .zip.gz files.
#    Keeps only those ids that are present in at least one of the species.
#    In practice it lowers the search space for next scripts.
#
#
import math
import numpy as np
import pandas as pd
pd.set_option('display.max_rows', 100)
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)
from utils import open_undefined_last_column_files, ensurePathExists

if __name__ == '__main__':

    # Load Species Files
    df_HS = pd.read_csv('results/HS-DE_genes.csv', index_col='id_gene')
    df_MM = pd.read_csv('results/MM-DE_genes.csv', index_col='id_gene')
    df_DM = pd.read_csv('results/DM-DE_genes.csv', index_col='id_gene')

    string_HS = np.hstack(df_HS['id_string'].values).tolist()
    string_MM = np.hstack(df_MM['id_string'].values).tolist()
    string_DM = np.hstack(df_DM['id_string'].values).tolist()

    string_ALL = frozenset(string_HS + string_MM + string_DM)

    string_HS = frozenset(string_HS)
    string_MM = frozenset(string_MM)
    string_DM = frozenset(string_DM)

    # Load EggNOG Annotation File
    df_A = pd.read_csv(
        '../eggnog/33208_annotations.tsv',
        sep='\t',
        names=['species', 'id_eggnog', 'letter', 'annotation']).\
        set_index('id_eggnog')

    #
    # Metazoa (33208) EggNOG - [M]embers
    #
    df_Egg = open_undefined_last_column_files(
        "../eggnog/33208_members.tsv.gz",
        n_fixed_cols=5,
        names=['family', 'id_eggnog', '_1', '_2', 'aliases', 'species'],
        nrows=None
    )

    # Only keep columns we need
    df_Egg = df_Egg.set_index('id_eggnog')['aliases']

    print("> Separating by Species")
    wanted_species = frozenset(['7227', '9606', '10090'])

    def select_by_species(text, keeplist):
        # Only keep genes from species we are interested in (lower the search space)
        return [i for i in text.split(',') if i.split('.', 1)[0] in keeplist]

    df = df_Egg.apply(select_by_species, args=(wanted_species,))

    def select_by_at_least_one_match(ilist, keeplist):
        # Only keep genes that are found in any of our gene list (lower the search space)
        spermgenes = [i for i in ilist if i in keeplist]
        return spermgenes if len(spermgenes) >= 1 else None

    print("> Separating by At Least One Match")
    df = df.apply(select_by_at_least_one_match, args=(string_ALL, ))
    df = df.dropna()

    def select_by_gene_and_separate_by_species(ilist, keeplist_HS, keeplist_MM, keeplist_DM):
        # Separate by species, keeping only the sperm genes we are interested in
        spermgenes_HS = [i for i in ilist if i in keeplist_HS]
        spermgenes_MM = [i for i in ilist if i in keeplist_MM]
        spermgenes_DM = [i for i in ilist if i in keeplist_DM]

        return pd.Series({'id_string_HS': spermgenes_HS, 'id_string_MM': spermgenes_MM, 'id_string_DM': spermgenes_DM})

    print("> Selecting Sperm Genes")
    df = df.apply(select_by_gene_and_separate_by_species, args=(string_HS, string_MM, string_DM))

    # Map Annotation
    df['annotation'] = df_A['annotation']

    # From List to String
    for column in ['id_string_HS', 'id_string_MM', 'id_string_DM']:
        df[column] = df[column].apply(lambda x: ",".join([str(y) for y in x]))

    print("> Exporting")
    wCSVFile = 'results/meta_meiotic_genes.csv'
    ensurePathExists(wCSVFile)
    df.to_csv(wCSVFile)

    print('done.')
