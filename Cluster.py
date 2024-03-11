import pandas as pd
import numpy as np
from sklearn.cluster import DBSCAN
import Tratamento_Base

def desvio_padrao(df, valor_minimo=50, valor_maximo=200):

    concessionaria = df['Concessionária_1'].unique()
    contagem_linhas = (valor_maximo-valor_minimo)*((df['Concessionária_1'].nunique())*(df['Sentido_1'].nunique())*(df['Rodovia_1']))
    arquivo_metricas = np.empty((contagem_linhas, 8), dtype=float)
    numero_linha = 0
    for i in concessionaria:
        df1 = df.query("Concessionaria_1 == @i").copy()
        sentido = df1['Sentido_1'].unique()
        for j in sentido:
            df2 = df1.query("Sentido_1 == @j").copy()
            rodovia = df2['Rodovia_1'].unique()
            for k in rodovia:
                df3 = df2.query("Rodovia_1 == @k").copy()
                X = df3[['Longitude', 'Latitude']]
                X = X.dropna()
                X = np.array(X)
                X = X.astype(np.float)
                for m in range(valor_minimo, valor_maximo):

                    modelo = DBSCAN(eps=(m/111320), min_samples=5).fit(X)

                    class_predictions = modelo.labels_

                    df3['CLUSTERS_DBSCAN'] = class_predictions
                    y_pred = modelo.fit_predict(X)

                    labels = modelo.labels_
                    n_clusters_ = len(set(labels)) - (1 if -1 in labels else 0) #quantidade de grupos
                    n_noise_ = list(labels).count(-1) #ruidos

                    kmmin = df3.groupby(['Rodovia','CLUSTERS_DBSCAN']) ['kmmt'].min().reset_index(name="kmmin")
                    kmmax = df3.groupby(['Rodovia','CLUSTERS_DBSCAN'])['kmmt'].max().reset_index(name="kmmax")
                    kmmax.drop(["Rodovia","CLUSTERS_DBSCAN"], axis=1, inplace=True)

                    contagem = df3.groupby(['Rodovia','CLUSTERS_DBSCAN']) ['CLUSTERS_DBSCAN'].count().reset_index(name="contagem")
                    contagem.drop(["Rodovia","CLUSTERS_DBSCAN"], axis=1, inplace=True)

                    somaUPS = df3.groupby(['Rodovia','CLUSTERS_DBSCAN']) ['UPS'].sum().reset_index(name="somaUPS")
                    somaUPS.drop(["Rodovia","CLUSTERS_DBSCAN"], axis=1, inplace=True)


                    resumo = pd.concat([kmmin, kmmax, contagem, somaUPS], axis=1)
                    resumo['extensao'] = resumo['kmmax'] - resumo['kmmin']
                    resumo = resumo.query("CLUSTERS_DBSCAN >= 0")
                    resumo = resumo.query("extensao > 0")

                    arquivo_metricas[numero_linha][0] = i
                    arquivo_metricas[numero_linha][1] = j
                    arquivo_metricas[numero_linha][2] = k
                    arquivo_metricas[numero_linha][3] = m
                    arquivo_metricas[numero_linha][4] = resumo['CLUSTERS_DBSCAN'].count()
                    arquivo_metricas[numero_linha][5] = resumo['extensao'].mean().astype(float)
                    arquivo_metricas[numero_linha][6] = resumo['extensao'].std().astype(float)
                    arquivo_metricas[numero_linha][7] = resumo['extensao'].sum().astype(float)
                    numero_linha += 1

    resumo_metricas = pd.DataFrame(arquivo_metricas, columns=['Concessionaria', 'Sentido', 'Rodovia', 'Meters', 'N Cluster','Media Extensao', 'Desvio Padrao Extensao', 'Soma Extensao'])

    return resumo_metricas


def modelo_DBSCAN(df):
    from sklearn.cluster import DBSCAN

    df['CssRodSentido'] = df.apply(lambda x: '%s.%s.%s' % (x['Concessionaria'], x['Rodovia'], x['Sentido']), axis=1)
    concessionaria = df['Concessionaria_1'].unique()
    resumo_total = pd.DataFrame()
    acidentes_total = pd.DataFrame()
    ultimo_DBSCAN = 0
    for i in concessionaria:
        df0 = df.query("Concessionaria_1 == @i").copy()
        sentido = df0['Sentido_1'].unique()
        for j in sentido:
            df1 = df0.query("Sentido_1 == @j").copy()
            rodovia = df1['Rodovia_1'].unique()
            for k in rodovia:
                df2 = df1.query("Rodovia_1 == @k").copy()
                X = df2[['Longitude', 'Latitude']]
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

                resumo = resumo.query("extensao > 0.1")
                resumo = resumo.query("CLUSTERS_DBSCAN >= 0")

                df2['CLUSTERS_DBSCAN'] = df2.apply(lambda row: resumo.loc[(resumo.CssRodSentido == row['CssRodSentido']) & (row['kmmt'] >= resumo.kmmin) &(row['kmmt'] < resumo.kmmax), 'CLUSTERS_DBSCAN'].values[0] if not resumo.loc[(resumo.CssRodSentido == row['CssRodSentido']) & (row['kmmt'] >= resumo.kmmin) & (row['kmmt'] < resumo.kmmax), 'CLUSTERS_DBSCAN'].empty else None, axis=1)

                df2.drop(["CssRodSentido", "Sentido_1", "Rodovia_1","Concessionaria_1", "UPS"], axis=1, inplace=True)
                df2.reset_index(inplace=True)

                acidentes_total = pd.concat([acidentes_total, df2], axis=0, ignore_index=True)
                resumo_total = pd.concat([resumo_total, resumo], axis=0, ignore_index=True)

                ultimo_DBSCAN = resumo_total['CLUSTERS_DBSCAN'].max()

    return resumo_total, acidentes_total


def cluster_comparativo(df_base, df_ano_1, df_ano_2):
    resumo_total = pd.DataFrame()
    df_total = pd.DataFrame()
    ultimo_DBSCAN = 0
    for i in concessionaria:
        df0 = df_base.query("Concessionaria_1 == @i").copy()
        sentido = df0['Sentido_1'].unique()
        for j in sentido:
            df1 = df0.query("Sentido_1 == @j").copy()
            rodovia = df1['Rodovia_1'].unique()
            for k in rodovia:
                df2 = df1.query("Rodovia_1 == @k").copy()
                X = df2[['Longitude', 'Latitude']]
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

                resumo['UPS_Ano_1'] = resumo.apply(
                    lambda row: df_ano_1[(df_ano_1.CssRodSentido == row['CssRodSentido']) &
                                         (df_ano_1.kmmt >= row['kmmin']) &
                                         (df_ano_1.kmmt < row['kmmax'])].UPS.sum(), axis=1)

                resumo['UPS_Ano_2'] = resumo.apply(
                    lambda row: df_ano_2[(df_ano_2.CssRodSentido == row['CssRodSentido']) &
                                         (df_ano_2.kmmt >= row['kmmin']) &
                                         (df_ano_2.kmmt < row['kmmax'])].UPS.sum(), axis=1)

                df2['CLUSTERS_DBSCAN'] = df2.apply(
                    lambda row: resumo.loc[(resumo.CssRodSentido == row['CssRodSentido']) &
                                           (row['kmmt'] >= resumo.kmmin) &
                                           (row['kmmt'] < resumo.kmmax), 'CLUSTERS_DBSCAN'].values[0] if not resumo.loc[
                        (resumo.CssRodSentido == row['CssRodSentido']) &
                        (row['kmmt'] >= resumo.kmmin) &
                        (row['kmmt'] < resumo.kmmax), 'CLUSTERS_DBSCAN'].empty else None, axis=1)

                df_ano_1['CLUSTERS_DBSCAN'] = df_ano_1.apply(
                    lambda row: resumo.loc[(resumo.CssRodSentido == row['CssRodSentido']) &
                                           (row['kmmt'] >= resumo.kmmin) &
                                           (row['kmmt'] < resumo.kmmax), 'CLUSTERS_DBSCAN'].values[0] if not resumo.loc[
                        (resumo.CssRodSentido == row['CssRodSentido']) &
                        (row['kmmt'] >= resumo.kmmin) & (
                                    row['kmmt'] < resumo.kmmax), 'CLUSTERS_DBSCAN'].empty else None, axis=1)

                df_ano_2['CLUSTERS_DBSCAN'] = df_ano_2.apply(
                    lambda row: resumo.loc[(resumo.CssRodSentido == row['CssRodSentido']) &
                                           (row['kmmt'] >= resumo.kmmin) &
                                           (row['kmmt'] < resumo.kmmax), 'CLUSTERS_DBSCAN'].values[0] if not resumo.loc[
                        (resumo.CssRodSentido == row['CssRodSentido']) &
                        (row['kmmt'] >= resumo.kmmin) & (
                                    row['kmmt'] < resumo.kmmax), 'CLUSTERS_DBSCAN'].empty else None, axis=1)

                df_total = pd.concat([df_total, df2, df_ano_1, df_ano_2], axis=0, ignore_index=True)
                df_total.drop(["CssRodSentido", "Sentido_1", "Rodovia_1", "Concessionaria_1"], axis=1, inplace=True)

                resumo_total = pd.concat([resumo_total, resumo], axis=0, ignore_index=True)
                ultimo_DBSCAN = resumo_total['CLUSTERS_DBSCAN'].max()

    return resumo_total, df_total


if __name__ == "__main__":
    df_acidentes = pd.read_csv('Arquivos/Logit/df_vitimas_acidentes_volume_2_2018-2022.csv', encoding='utf-8', sep=',')

    '''
    #Avaliar o desvio padrão
    resumo = desvio_padrao(df_acidentes, valor_minimo=50, valor_maximo=200)
    resumo.to_csv("Arquivos/Cluster/DesvioPadrao.csv", index=False)
    '''

    #Modelo Cluster
    resumo_total, acidente_total = modelo_DBSCAN(df_acidentes)
    acidente_total.drop(columns=['Unnamed: 0', 'DescrOcorrencia', 'Sentido', 'Rodovia', 'CondicaoTempo', 'Latitude', 'Longitude', 'kmmt', 'Mes_Ano', 'Praca_pedagio', 'FaixaEtaria_Não Informado'], inplace=True)

    acidente_total['Cluster'] = np.where(acidente_total['CLUSTERS_DBSCAN'].notna(), True, False)
    resumo_total.to_csv('Arquivos/Cluster/df_vitimas_acidentes_volume_2_2018-2022.csv', encoding='UTF-8', sep=',', index=False)
    acidente_total.to_csv('Arquivos/Cluster/resumo_vitimas_acidentes_volume_2_2018-2022.csv', encoding='UTF-8', sep=',', index=False)

    '''
    #Modelo Cluster Comparativo
    df_cluster = df_acidentes.copy()
    df_cluster['CssRodSentido'] = df_cluster.apply(lambda row: '%s.%s.%s' % (row['Concessionaria'],row['Rodovia'],row['Sentido']), axis=1)
    
    df_base = Tratamento_Base.definir_anos(df_cluster, 2010, 2014)
    df_base.loc[:, 'Cluster_Ref'] = 'Ano_Base'
    
    df_ano_1 = Tratamento_Base.definir_anos(df_cluster, 2015, 2018)
    df_ano_1.loc[:, 'Cluster_Ref'] = 'Ano_1'
    
    df_ano_2 = Tratamento_Base.definir_anos(df_cluster, 2019, 2022)
    df_ano_2.loc[:, 'Cluster_Ref'] = 'Ano_2'
    
    resumo_total, cluster_total = cluster_comparativo(df_base, df_ano_1, df_ano_2)
    
    resumo_total.to_csv('Arquivos/Cluster/ComparativoResumo.csv', encoding='UTF-8', sep = ',')
    cluster_total.to_csv('Arquivos/Cluster/ComparativoAcidentes.csv', encoding='UTF-8', sep = ',')
    '''


