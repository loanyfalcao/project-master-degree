from sklearn.cluster import DBSCAN
import pandas as pd
import numpy as np

from Tratamento_Base import df_acidentes

def desvio_padrao(df,valor_minimo = 50, valor_maximo = 200):

    concessionaria = df['Concessionária_1'].unique()
    sentido = df['Sentido_1'].unique()
    rodovia = df['Rodovia_1'].unique()

    contagem_linhas=(valor_maximo-valor_minimo)*((df['Concessionária_1'].nunique())*(df['Sentido_1'].nunique())*(df['Rodovia_1']))
    arquivo_metricas = np.empty((contagem_linhas, 8), dtype=float)
    numero_linha=0
    for i in concessionaria:
        df1 = df.query ("Concessionaria_1 == @i" )
        for j in sentido:
            df2 = df1.query ("Sentido_1 == @j" )
            for k in rodovia:
                df3 = df2.query ("Rodovia_1 == @k" )
                X = df3[['Longitude', 'Latitude']].copy()
                X = X.dropna()
                X = np.array(X)
                X=X.astype(np.float)
                for m in range(valor_minimo, valor_maximo):

                    modelo = DBSCAN(eps=(m/111320), min_samples=5).fit(X)

                    class_predictions = modelo.labels_

                    df3['CLUSTERS_DBSCAN'] = class_predictions
                    #fit_predict é o que vamos fazer buscar os grupos.
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


                    resumo = pd.concat([kmmin, kmmax, contagem, somaUPS], axis = 1)
                    resumo ['extensao'] = resumo['kmmax'] - resumo['kmmin']
                    resumo = resumo.query ("CLUSTERS_DBSCAN >= 0")
                    resumo = resumo.query ("extensao > 0")

                    arquivo_metricas[numero_linha][0]=i
                    arquivo_metricas[numero_linha][1]=j
                    arquivo_metricas[numero_linha][2]=r
                    arquivo_metricas[numero_linha][3]=l
                    arquivo_metricas[numero_linha][4]=resumo['CLUSTERS_DBSCAN'].count()
                    arquivo_metricas[numero_linha][5]=resumo['extensao'].mean().astype (float)
                    arquivo_metricas[numero_linha][6]=resumo['extensao'].std().astype (float)
                    arquivo_metricas[numero_linha][7]=resumo['extensao'].sum().astype (float)
                    numero_linha += 1

    resumo_metricas = pd.DataFrame(arquivo_metricas, columns=['Concessionaria', 'Sentido', 'Rodovia', 'Meters', 'N Cluster','Media Extensao', 'Desvio Padrao Extensao', 'Soma Extensao'])

    return resumo_metricas


df_acidentes_desvio = df_acidentes.copy()
df_acidentes_desvio = df_acidentes_desvio.loc [(df_acidentes_desvio['DescrOcorrencia'] != 'Acidente com Danos Materiais')]

resumo = desvio_padrao(df_acidentes_desvio)

resumo.to_csv("Arquivos/ResumoMetricas.csv", index = False)








