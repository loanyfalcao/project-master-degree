import pandas as pd
import numpy as np
import Tratamento_Veiculos_Detalhado

def veiculo_por_linha(df):

    df = df[['OcDataConcessionaria', 'Ano', 'Veiculos']]

    df = df.assign(Veiculos=df['Veiculos'].str.split(';')).explode('Veiculos')
    df['Veiculos'] = df['Veiculos'].str.strip()
    df = df.query('Veiculos != ""')

    df.rename(columns={'Ano': 'Ano_Acidente', 'Veiculos': 'Veiculo_Unico'}, inplace=True)

    return df

def tratar_erros_ano(df):

    df['Ano_Veiculo'] = df['Veiculo_Unico'].str.extract(r'/(\d+)[)]')
    df['Ano_Veiculo'] = pd.to_numeric(df['Ano_Veiculo'], errors='coerce').fillna(-1).astype(int)

    df['Ano_Veiculo'] = df['Ano_Veiculo'].replace([0, -1], np.nan)

    df['Ano_Veiculo'] = (df['Ano_Veiculo'].mask((df['Ano_Veiculo'] >= 10) & (df['Ano_Veiculo'] < 23), df['Ano_Veiculo'] + 2000))

    df['Ano_Veiculo'] = (df['Ano_Veiculo'].mask((df['Ano_Veiculo'] > 50) & (df['Ano_Veiculo'] <= 99), df['Ano_Veiculo'] + 1900))

    df['Ano_Veiculo'] = (df['Ano_Veiculo'].mask((df['Ano_Veiculo'] >= 200) & (df['Ano_Veiculo'] < 223), (df['Ano_Veiculo'] - 200) + 2000))

    df['Ano_Veiculo'] = (df['Ano_Veiculo'].mask((df['Ano_Veiculo'] > 2023) | (df['Ano_Veiculo'] < 1950), np.nan))

    return df

def tratar_placa(df):
    df['Placa'] = df['Veiculo_Unico'].str.extract(r':(.*?)-')
    df['Placa'].replace('', np.nan, inplace=True)
    df['Contagem_Caracteres'] = df['Placa'].str.len()
    df['Placa'] = df['Placa'].mask((df['Contagem_Caracteres'] < 7), np.nan)
    df['Placa'].replace(['', '0000000'], np.nan, inplace=True)
    df.drop('Contagem_Caracteres', axis=1, inplace=True)

    return df

def apenas_veiculo_com_informacoes(df):
    df = df.loc[(df['Ano_Veiculo'].notna()) | (df['Placa'].notna())]

    df['Contagem'] = df.groupby('OcDataConcessionaria')['OcDataConcessionaria'].transform('count')

    df = df.query('Contagem == 1')

    return df

def classificar_tipo_veiculo(df):


    df['Tipo_Veiculo'] = df['Veiculo_Unico'].str.extract(r'^(.*?)(?=\()')

    df['Marca_Veiculo'] = df['Veiculo_Unico'].str.extract(r'\((.*?)\/')

    df['Modelo_Veiculo'] = df['Veiculo_Unico'].str.extract(r'/(.*?):')

    df['Tipo_Veiculo'] = (df['Tipo_Veiculo'].replace(['AUTomovel', 'Perua/Caminhonete/Camioneta'],'Veiculo Leve').
                           replace(['MOTocicleta', 'MOTo Frete'],'Motocicleta').
                           replace(['CAMinhão', 'CARreta'], 'Veiculo Pesado').
                           replace(['Van', 'ONIbus', 'Microonibus'],'Veiculo Passageiro').
                           replace('BICicleta','Bicicleta').
                           replace('Trator','Outros'))

    return df

def incluir_placas_api(df, placas):

    df = pd.merge(df, placas, on='Placa', how='left')
    df['Ano_Veiculo'] = df.apply(lambda row: row['Ano'] if (pd.isna(row['Ano_Veiculo']) and pd.notna(row['Ano'])) else row['Ano_Veiculo'], axis=1)

    df['Ano_Veiculo'] = pd.to_numeric(df['Ano_Veiculo'], errors='coerce').fillna(-1).astype(int)
    df['Ano_Veiculo'] = df['Ano_Veiculo'].replace(-1, np.nan)

    df['Ano'] = pd.to_numeric(df['Ano'], errors='coerce').fillna(-1).astype(int)
    df['Ano'] = df['Ano'].replace(-1, np.nan)

    df.rename(columns={'Ano':'Ano_Placa'}, inplace=True)

    return df

def tratar_ano(row):

    idade_veiculo = (row['Ano_Acidente'] - row['Ano_Veiculo'])
    idade_placa = (row['Ano_Acidente'] - row['Ano_Placa'])

    if 0 <= idade_veiculo <= 20:
        return row['Ano_Veiculo']

    elif idade_veiculo > 20:
        if 0 <= idade_placa <= 20:
            return row['Ano_Placa']
        elif idade_placa > 20:
            if idade_veiculo <= idade_placa:
                return row['Ano_Veiculo']
            else:
                return row['Ano_Placa']
        elif idade_placa == -1:
            return row['Ano_Acidente']
        else:
            return row['Ano_Veiculo']

    elif idade_veiculo == -1:
        return row['Ano_Acidente']

    elif pd.notna(idade_veiculo) and pd.isna(idade_placa):
        return row['Ano_Veiculo']

    else:
        return None


if(__name__ == "__main__"):

    placas = pd.read_csv('Arquivos/placas_api.csv', sep=',', encoding='UTF-8')

    df_acidentes = pd.read_csv('Arquivos/df_acidentes.csv', sep=',', encoding='UTF-8')

    df_veiculos = veiculo_por_linha(df_acidentes)

    df_veiculos = tratar_erros_ano(df_veiculos)

    df_veiculos = tratar_placa(df_veiculos)

    df_veiculos = apenas_veiculo_com_informacoes(df_veiculos)

    df_veiculos = classificar_tipo_veiculo(df_veiculos)

    df_veiculos = incluir_placas_api(df_veiculos,placas)
    df_veiculos['Modelo_Veiculo'] = df_veiculos.apply(lambda row: row['Modelo'] if (pd.notna(row['Modelo']) and row['Modelo'] != '') else row['Modelo_Veiculo'],axis=1)

    df_veiculos['Ano_Veiculo'] = df_veiculos.apply(lambda row: tratar_ano(row), axis=1)
    df_veiculos['Idade_Veiculo'] = df_veiculos['Ano_Acidente'] - df_veiculos['Ano_Veiculo']

    df_veiculos.drop(columns=['Ano_Acidente', 'Ano_Veiculo', 'Placa', 'Contagem', 'Ano_Placa', 'Modelo'], axis=1, inplace=True)

    df_veiculos.to_csv('Arquivos/df_veiculo_unico.csv', sep=',', index=False, encoding='UTF-8')



