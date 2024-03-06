import pandas as pd
import numpy as np
import Tratamento_Base

def modelo_DBSCAN(df):
    from sklearn.cluster import DBSCAN

    df['CssRodSentido'] = df.apply(lambda x: '%s.%s.%s' % (x['Concessionaria'], x['Rodovia'], x['Sentido']), axis=1)
    concessionaria = df['Concessionaria_1'].unique()
    sentido = df['Sentido_1'].unique()
    rodovia = df['Rodovia_1'].unique()
    resumo_total = pd.DataFrame()
    acidentes_total = pd.DataFrame()
    ultimo_DBSCAN = 0
    for i in concessionaria:
        df0 = df.query("Concessionaria_1 == @i")
        for j in sentido:
            df1 = df0.query("Sentido_1 == @j")
            for k in rodovia:
                df2 = df1.query("Rodovia_1 == @k")
                if df2.shape[0] == 0:
                    continue
                else:
                    X = df2[['Longitude', 'Latitude']].copy()
                    X = X.dropna()
                    X = np.array(X)
                    X = X.astype(float)

                    modelo = DBSCAN(eps=(100/111320), min_samples=5).fit(X)

                    class_predictions = modelo.labels_

                    df2['CLUSTERS_DBSCAN'] = class_predictions
                    # fit_predict é o que vamos fazer buscar os grupos.
                    y_pred = modelo.fit_predict(X)

                    labels = modelo.labels_
                    n_clusters_ = len(set(labels)) - (1 if -1 in labels else 0)  # quantidade de grupos
                    n_noise_ = list(labels).count(-1)  # ruidos

                    kmmin = df2.groupby(['Concessionaria', 'Sentido', 'Rodovia', 'CssRodSentido', 'CLUSTERS_DBSCAN'])['kmmt'].min().reset_index(name="kmmin")
                    kmmin['CLUSTERS_DBSCAN'] = kmmin['CLUSTERS_DBSCAN'].apply(lambda x: x + ultimo_DBSCAN if x >= 0 else x)

                    kmmax = df2.groupby(['CssRodSentido', 'CLUSTERS_DBSCAN'])['kmmt'].max().reset_index(name="kmmax")
                    kmmax.drop(["CssRodSentido", "CLUSTERS_DBSCAN"], axis=1, inplace=True)

                    contagem = df2.groupby(['CssRodSentido', 'CLUSTERS_DBSCAN'])['CLUSTERS_DBSCAN'].count().reset_index(name="contagem")
                    contagem.drop(["CssRodSentido", "CLUSTERS_DBSCAN"], axis=1, inplace=True)


                    somaUPS = df2.groupby(['CssRodSentido', 'CLUSTERS_DBSCAN'])['UPS'].sum().reset_index(name="somaUPS")
                    somaUPS.drop(["CssRodSentido", "CLUSTERS_DBSCAN"], axis=1, inplace=True)

                    resumo = pd.concat([kmmin, kmmax, contagem, somaUPS], axis=1)
                    resumo['extensao'] = resumo['kmmax'] - resumo['kmmin']

                    resumo = resumo.query("extensao > 0.4")
                    resumo = resumo.query("CLUSTERS_DBSCAN >= 0")

                    df2['CLUSTERS_DBSCAN'] = df2.apply(lambda row: resumo.loc[(resumo.CssRodSentido == row['CssRodSentido']) & (row['kmmt'] >= resumo.kmmin) &(row['kmmt'] < resumo.kmmax), 'CLUSTERS_DBSCAN'].values[0] if not resumo.loc[(resumo.CssRodSentido == row['CssRodSentido']) & (row['kmmt'] >= resumo.kmmin) & (row['kmmt'] < resumo.kmmax), 'CLUSTERS_DBSCAN'].empty else None, axis=1)

                    df2.drop(["CssRodSentido", "Sentido_1", "Rodovia_1","Concessionaria_1", "UPS"], axis=1, inplace=True)
                    df2.reset_index(inplace=True)

                    acidentes_total = pd.concat([acidentes_total, df2], axis=0, ignore_index=True)
                    resumo_total = pd.concat([resumo_total, resumo], axis=0, ignore_index=True)

                    ultimo_DBSCAN = resumo_total['CLUSTERS_DBSCAN'].max()

    return resumo_total, acidentes_total


if __name__ == "__main__":
    df_acidentes = pd.read_csv('Arquivos/Logit/df_vitimas_acidentes_volume_2_2009-2022.csv', encoding='utf-8', sep =',')
    #df_acidentes.query('Concessionaria == "Litoral Sul"', inplace=True)

    resumo_total, acidente_total = modelo_DBSCAN(df_acidentes)

    acidente_total['Cluster'] = np.where(acidente_total['CLUSTERS_DBSCAN'].notna(), True, False)
    resumo_total.to_csv('Arquivos/Cluster/df_vitimas_acidentes_volume_2_2009-2022.csv', encoding='UTF-8', sep=',', index=False)
    acidente_total.to_csv('Arquivos/Cluster/resumo_vitimas_acidentes_volume_2_2009-2022.csv', encoding='UTF-8', sep=',', index=False)

