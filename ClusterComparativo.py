import tratamento
import pandas as pd
import numpy as np
from sklearn.cluster import DBSCAN

def cluster_comparativo(df_base,df_ano_1, df_ano_2):
    sentido = df_base['Sentido_1'].unique()
    rodovia = df_base['Rodovia_1'].unique()
    resumo_total = pd.DataFrame()
    df_total = pd.DataFrame()
    ultimo_DBSCAN = 0
    for i in sentido:
        df1 = df_base.query("Sentido_1 == @i")
        for j in rodovia:
            df2 = df1.query("Rodovia_1 == @j")
            X = df2[['Longitude', 'Latitude']].copy()
            X = X.dropna()
            X = np.array(X)
            X = X.astype(float)

            modelo = DBSCAN(eps=100 / 111320, min_samples=5).fit(X)

            class_predictions = modelo.labels_

            df2['CLUSTERS_DBSCAN'] = class_predictions
            # fit_predict é o que vamos fazer buscar os grupos.
            y_pred = modelo.fit_predict(X)

            labels = modelo.labels_
            n_clusters_ = len(set(labels)) - (1 if -1 in labels else 0)  # quantidade de grupos
            n_noise_ = list(labels).count(-1)  # ruidos


            kmmin = df2.groupby(['Concessionaria', 'Sentido', 'Rodovia', 'CssRodSentido', 'CLUSTERS_DBSCAN'])[
                'kmmt'].min().reset_index(name="kmmin")
            kmmin['CLUSTERS_DBSCAN'] = kmmin['CLUSTERS_DBSCAN'].apply(lambda x: x + ultimo_DBSCAN if x >= 0 else x)

            kmmax = df2.groupby(['CssRodSentido', 'CLUSTERS_DBSCAN'])['kmmt'].max().reset_index(name="kmmax")
            kmmax.drop(["CssRodSentido", "CLUSTERS_DBSCAN"], axis=1, inplace=True)

            contagem = df2.groupby(['CssRodSentido', 'CLUSTERS_DBSCAN'])['CLUSTERS_DBSCAN'].count().reset_index(
                name="contagem")
            contagem.drop(["CssRodSentido", "CLUSTERS_DBSCAN"], axis=1, inplace=True)


            somaUPS = df2.groupby(['CssRodSentido', 'CLUSTERS_DBSCAN'])['UPS'].sum().reset_index(name="somaUPS")
            somaUPS.drop(["CssRodSentido", "CLUSTERS_DBSCAN"], axis=1, inplace=True)

            resumo = pd.concat([kmmin, kmmax, contagem, somaUPS], axis=1)
            resumo['extensao'] = resumo['kmmax'] - resumo['kmmin']

            resumo = resumo.query("CLUSTERS_DBSCAN >= 0")

            resumo['UPS_Ano_1'] = resumo.apply(lambda row: df_ano_1[(df_ano_1.CssRodSentido == row['CssRodSentido']) &
                                                              (df_ano_1.kmmt >= row['kmmin']) &
                                                              (df_ano_1.kmmt < row['kmmax'])].UPS.sum(), axis=1)

            resumo['UPS_Ano_2'] = resumo.apply(lambda row: df_ano_2[(df_ano_2.CssRodSentido == row['CssRodSentido']) &
                                                              (df_ano_2.kmmt >= row['kmmin']) &
                                                              (df_ano_2.kmmt < row['kmmax'])].UPS.sum(), axis=1)

            df2['CLUSTERS_DBSCAN'] = df2.apply(lambda row: resumo.loc[(resumo.CssRodSentido == row['CssRodSentido']) &
                                                                      (row['kmmt'] >= resumo.kmmin) &
                                                                      (row['kmmt'] < resumo.kmmax), 'CLUSTERS_DBSCAN'].values[0] if not resumo.loc[(resumo.CssRodSentido == row['CssRodSentido']) &
                                                                                                                                                   (row['kmmt'] >= resumo.kmmin) &
                                                                                                                                                   (row['kmmt'] < resumo.kmmax), 'CLUSTERS_DBSCAN'].empty else None, axis=1)

            df_ano_1['CLUSTERS_DBSCAN'] = df_ano_1.apply(lambda row: resumo.loc[(resumo.CssRodSentido == row['CssRodSentido']) &
                                                               (row['kmmt'] >= resumo.kmmin) &
                                                               (row['kmmt'] < resumo.kmmax), 'CLUSTERS_DBSCAN'].values[0] if not resumo.loc[(resumo.CssRodSentido == row['CssRodSentido']) &
                                                                                                                                              (row['kmmt'] >= resumo.kmmin) & (row['kmmt'] < resumo.kmmax), 'CLUSTERS_DBSCAN'].empty else None, axis=1)

            df_ano_2['CLUSTERS_DBSCAN'] = df_ano_2.apply(lambda row: resumo.loc[(resumo.CssRodSentido == row['CssRodSentido']) &
                                                               (row['kmmt'] >= resumo.kmmin) &
                                                               (row['kmmt'] < resumo.kmmax), 'CLUSTERS_DBSCAN'].values[0] if not resumo.loc[(resumo.CssRodSentido == row['CssRodSentido']) &
                                                                                                                                            (row['kmmt'] >= resumo.kmmin) & (row['kmmt'] < resumo.kmmax), 'CLUSTERS_DBSCAN'].empty else None, axis=1)


            df_total = pd.concat([df_total, df2, df_ano_1,df_ano_2], axis=0, ignore_index=True)
            df_total.drop(["CssRodSentido", "Sentido_1", "Rodovia_1", "Concessionaria_1"], axis=1, inplace=True)

            resumo_total = pd.concat([resumo_total, resumo], axis=0, ignore_index=True)
            ultimo_DBSCAN = resumo_total['CLUSTERS_DBSCAN'].max()

    return resumo_total, df_total

df_acidentes = pd.read_csv('df_arquivos.csv', encoding='utf-8', sep =',')

df_cluster = df_acidentes.copy()
df_cluster['CssRodSentido'] = df_cluster.apply(lambda row: '%s.%s.%s' % (row['Concessionaria'],row['Rodovia'],row['Sentido']), axis=1)
df_cluster = tratamento.coluna_em_numeros (df_cluster)

df_base = tratamento.definir_anos(df_cluster, 2010, 2014)
df_base.loc[:,'Cluster_Ref'] = 'Ano_Base'

df_ano_1 = tratamento.definir_anos(df_cluster, 2015, 2018)
df_ano_1.loc[:,'Cluster_Ref'] = 'Ano_1'

df_ano_2= tratamento.definir_anos(df_cluster, 2019, 2022)
df_ano_2.loc[:,'Cluster_Ref'] = 'Ano_2'

resumo_total, cluster_total = cluster_comparativo(df_base,df_ano_1, df_ano_2)

resumo_total.to_csv('ResumoComparativo.csv', encoding='UTF-8', sep = ',')

cluster_total.to_csv('ClusterComparativo.csv', encoding='UTF-8', sep = ',')

