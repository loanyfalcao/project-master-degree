import datetime as dt
import pandas as pd
import os
import glob


def unir_arquivos(url):
    diretorio_atual = os.getcwd()

    extension = 'csv'
    os.chdir(url)
    all_filenames = [i for i in glob.glob('*.{}'.format(extension))]

    dfs = []
    for filename in all_filenames:
        df_temp = pd.read_csv(filename, sep=';', encoding='latin1')
        dfs.append(df_temp)

    df = pd.concat(dfs, ignore_index=True)

    os.chdir(diretorio_atual)

    return df


def tratamento_pracas_pedagio(df):
    concessionaria = {'AUTOPISTA FLUMINENSE': 'Fluminense', 'Autopista Fluminense': 'Fluminense',
                      'AUTOPISTA PLANALTO SUL': 'Planalto Sul', 'Autopista Planalto Sul': 'Planalto Sul',
                      'AUTOPISTA FERNÃO DIAS': 'Fernão Dias',
                      'AUTOPISTA LITORAL SUL': 'Litoral Sul', 'Autopista Litoral Sul': 'Litoral Sul',
                      'AUTOPISTA REGIS BITTENCOURT': 'Régis Bittencourt',
                      'Autopista Regis Bittencourt': 'Régis Bittencourt'}
    df['concessionaria'].replace(concessionaria, inplace=True)

    df = df.query('concessionaria == "Fernão Dias" or concessionaria == "Fluminense" or concessionaria == "Litoral Sul" or concessionaria == "Planalto Sul" or concessionaria == "Régis Bittencourt"')
    df['mes_ano'] = df['mes_ano'].str.replace('/', '-')

    df['mes_ano'] = pd.to_datetime(df['mes_ano'])
    df['ano'] = df['mes_ano'].dt.year
    df['mes'] = df['mes_ano'].dt.day

    df['sentido'].replace({'Decrescente': 'N', 'Decrescente ': 'N', 'Crescente': 'S', 'Crescente ': 'S'}, inplace=True)

    df.rename(columns={'praca': 'info_praca'}, inplace=True)
    df['praca'] = df['info_praca'].str[:8]
    df['rodovia'] = df['info_praca'].str.rsplit(' ').str[2]
    df['km_praca'] = df['info_praca'].str.rsplit(' ').str[-1]
    df.loc[(df['km_praca'] == ""), 'km_praca'] = df['info_praca'].str.rsplit(' ').str[4]

    df = df[['ano', 'mes', 'concessionaria', 'info_praca', 'rodovia', 'sentido', 'praca', 'km_praca', 'volume_total',
             'multiplicador_de_tarifa', 'volume_veiculo_equivalente']]

    df[['volume_veiculo_equivalente', 'volume_total']] = df[['volume_veiculo_equivalente', 'volume_total']].applymap(lambda x: x.replace(',', '.') if isinstance(x, str) and ',' in x else x)
    df[['volume_veiculo_equivalente', 'volume_total']] = df[['volume_veiculo_equivalente', 'volume_total']].astype(float)

    return df


def calculo_volume(df):
    df['Uniao'] = df['concessionaria'].astype(str) + '.' + df['praca'].astype(str) + '.' + df['ano'].astype(str) + '.' + df['mes'].astype(str) + '.' + df['sentido'].astype(str)

    df['Volume_Equivalente'] = df.groupby('Uniao')['volume_veiculo_equivalente'].transform('sum')
    df['Volume_Total'] = df.groupby('Uniao')['volume_total'].transform('sum')

    df.drop_duplicates(subset=['Uniao'], inplace=True)
    df.drop(columns=['info_praca', 'multiplicador_de_tarifa'], axis=1, inplace=True)

    return df


def previsao_dados_nulos(df):
    import numpy as np
    from sklearn.preprocessing import OneHotEncoder
    from sklearn.compose import ColumnTransformer
    from sklearn.pipeline import Pipeline
    from sklearn.linear_model import LinearRegression

    dados = df[['ano', 'mes', 'concessionaria', 'sentido', 'praca', 'Volume_Equivalente']]
    dados.loc[(dados['concessionaria'] == 'Litoral Sul') & (dados['praca'] == 'Praça 05') & (dados['ano'] == 2013) & (dados['Volume_Equivalente'] < 800), 'Volume_Equivalente'] = 0.0
    dados.loc[(dados['concessionaria'] == 'Litoral Sul') & (dados['praca'] == 'Praça 05') & (dados['ano'] == 2014) & (dados['Volume_Equivalente'] < 800), 'Volume_Equivalente'] = 0.0
    dados.loc[(dados['concessionaria'] == 'Fernão Dias') & (dados['praca'] == 'Praça 06') & (dados['ano'] == 2022) & (dados['Volume_Equivalente'] < 800), 'Volume_Equivalente'] = 0.0
    dados['Volume_Equivalente'] = dados['Volume_Equivalente'].replace(0.0, np.nan)

    dados_treino = dados.dropna()
    dados_teste = dados[dados['Volume_Equivalente'].isnull()]

    X_treino = dados_treino[['ano', 'mes', 'concessionaria', 'sentido', 'praca']]
    y_treino = dados_treino['Volume_Equivalente']
    X_teste = dados_teste[['ano', 'mes', 'concessionaria', 'sentido', 'praca']]

    transformador = ColumnTransformer([('encoder', OneHotEncoder(), ['concessionaria', 'sentido', 'praca'])], remainder='passthrough')

    modelo = Pipeline([('transformador', transformador), ('regressao', LinearRegression())])
    modelo.fit(X_treino, y_treino)

    previsoes = modelo.predict(X_teste)

    dados.loc[dados['Volume_Equivalente'].isnull(), 'Volume_Equivalente'] = previsoes

    return dados


def incluir_praca_acidentes(df):
    df_praca = pd.read_csv('Arquivos/df_km_pracas.csv')

    df_auxiliar = df[['OcDataConcessionaria', 'Concessionaria', 'Ano', 'Mes', 'Rodovia', 'Sentido', 'kmmt']]
    df_auxiliar = df_auxiliar.query('Concessionaria == "Fernão Dias" or '
                                    'Concessionaria == "Litoral Sul" or '
                                    'Concessionaria == "Régis Bittencourt"')

    df_auxiliar['Praca_pedagio'] = df_auxiliar.apply(
        lambda row: df_praca.loc[(row['Concessionaria'] == df_praca['Concessionaria']) &
                                 (row['Rodovia'] == df_praca['Rodovia']) &
                                 (row['kmmt'] >= df_praca['Inicio']) &
                                 (row['kmmt'] < df_praca['Fim']), 'Praça'].
        values[0] if not df_praca.loc[(row['Concessionaria'] == df_praca['Concessionaria']) &
                                      (row['Rodovia'] == df_praca['Rodovia']) &
                                      (row['kmmt'] >= df_praca['Inicio']) &
                                      (row['kmmt'] < df_praca['Fim']), 'Praça'].empty else None, axis=1)

    return df_auxiliar


def uniao_volume_acidentes(df_pedagio, df):
    df_pedagio['Uniao'] = df_pedagio['concessionaria'].astype(str) + '.' + df_pedagio['praca'].astype(str) + '.' + df_pedagio['ano'].astype(str) + '.' + df_pedagio['mes'].astype(str) + '.' + df_pedagio['sentido'].astype(str)

    df_auxiliar = df_pedagio[['Uniao', 'Volume_Equivalente', 'Volume_Total']]

    df['Uniao'] = df['Concessionaria'].astype(str) + '.' + df['Praca_pedagio'].astype(str) + '.' + df['Ano'].astype(str) + '.' + df['Mes'].astype(str) + '.' + df['Sentido'].astype(str)
    df['Mes_Ano'] = pd.to_datetime(df['Ano'].astype(str) + '-' + df['Mes'].astype(str), format='%Y-%m')
    df = df[['OcDataConcessionaria', 'Mes_Ano', 'Uniao', 'Praca_pedagio']]

    df_pedagio['Uniao'] = df_pedagio['concessionaria'].astype(str) + '.' + df_pedagio['praca'].astype(str) + '.' + df_pedagio['ano'].astype(str) + '.' + df_pedagio['mes'].astype(str) + '.' + df_pedagio['sentido'].astype(str)
    df = pd.merge(df, df_auxiliar, on='Uniao', how='left')


    df.drop(columns=['Uniao'], axis=1, inplace=True)

    df_acidentes = pd.read_csv('Arquivos/df_acidentes.csv', encoding='utf-8')
    df_acidentes = pd.merge(df_acidentes, df, on='OcDataConcessionaria', how='left')

    return df_acidentes



df_pedagio = unir_arquivos('C:/Users/Public/Documents/Mestrado/Dados/Volume_Trafego')
df_pedagio = tratamento_pracas_pedagio(df_pedagio)
df_pedagio = calculo_volume(df_pedagio)
#df_pedagio = previsao_dados_nulos(df_pedagio)

df_acidentes = pd.read_csv('Arquivos/df_acidentes.csv')
df_acidentes = incluir_praca_acidentes(df_acidentes)
df_acidentes = uniao_volume_acidentes(df_pedagio, df_acidentes)

df_acidentes.to_csv('Arquivos/df_acidentes_volume.csv', index=False, encoding='utf-8')




