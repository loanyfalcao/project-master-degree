import pandas as pd
import numpy as np
import Tratamento_Base

def modelo_DBSCAN(df):
    from sklearn.cluster import DBSCAN

    df['CssRodSentido'] = df.apply(lambda x: '%s.%s.%s' % (x['Concessionaria'], x['Rodovia'], x['Sentido']), axis=1)
    sentido = df['Sentido_1'].unique()
    rodovia = df['Rodovia_1'].unique()
    resumo_total = pd.DataFrame()
    acidentes_total = pd.DataFrame()
    ultimo_DBSCAN = 0
    for i in sentido:
        df1 = df.query("Sentido_1 == @i")
        for j in rodovia:
            df2 = df1.query("Rodovia_1 == @j")
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

            resumo = resumo.query("extensao >= 0.1")
            resumo = resumo.query("CLUSTERS_DBSCAN >= 0")

            df2['CLUSTERS_DBSCAN'] = df2.apply(lambda row: resumo.loc[(resumo.CssRodSentido == row['CssRodSentido']) &
                                                                      (row['kmmt'] >= resumo.kmmin) &
                                                                      (row['kmmt'] < resumo.kmmax), 'CLUSTERS_DBSCAN'].values[0] if not resumo.loc[(resumo.CssRodSentido == row['CssRodSentido']) &
                                                                                                                                                   (row['kmmt'] >= resumo.kmmin) &
                                                                                                                                                   (row['kmmt'] < resumo.kmmax), 'CLUSTERS_DBSCAN'].empty else None, axis=1)

            df2.drop(["CssRodSentido", "Sentido_1", "Rodovia_1","Concessionaria_1", "UPS"], axis=1, inplace=True)
            df2.reset_index(inplace=True)

            acidentes_total = pd.concat([acidentes_total, df2], axis=0, ignore_index=True)
            resumo_total = pd.concat([resumo_total, resumo], axis=0, ignore_index=True)

            ultimo_DBSCAN = resumo_total['CLUSTERS_DBSCAN'].max()

    return resumo_total, acidentes_total


if __name__ == "__main__":
    df_acidentes = pd.read_csv('Arquivos/df_uniao.csv', encoding='utf-8', sep =',')

    #Apenas Acidentes com vitimas
    df_acidentes = df_acidentes.loc[(df_acidentes['DescrOcorrencia'] != 'Acidente com Danos Materiais')]

    #Apenas vitimas feridas
    df_acidentes = df_acidentes.loc[(df_acidentes['Gravidade'] != 'Ileso')]

    # df_acidentes = Tratamento_Base.definir_anos(df_acidentes, 2010, 2014)

    # Veiculo unico
    #df_veiculos = pd.read_csv('Arquivos/df_veiculo_unico.csv')
    #df_acidentes_veiculos = df_acidentes.merge(df_veiculos, how='inner', on='OcDataConcessionaria')

    resumo_total, acidente_total = modelo_DBSCAN(df_acidentes)

    resumo_total.to_csv('Arquivos/Cluster/ResumoVitimas_Acidentes_VeiculoUnico_ApenasFerido.csv', encoding='UTF-8', sep = ',')
    acidente_total.to_csv('Arquivos/Cluster/Vitimas_Acidentes_VeiculoUnico_ApenasFerido.csv', encoding='UTF-8', sep = ',', index=False)

