import pandas as pd
import numpy as np
import tratamento


def um_veic(df):

    df = df[['OcDataConcessionaria', 'Veiculos']]

    df = df.assign(Veiculos=df['Veiculos'].str.split(';')).explode('Veiculos')
    df['Veiculos'] = df['Veiculos'].str.strip()
    df = df.query('Veiculos != ""')

    df['Ano Veiculo'] = df['Veiculos'].str.extract(r'/(\d+)[)]')
    df['Ano Veiculo'] = pd.to_numeric(df['Ano Veiculo'], errors='coerce').fillna(-1).astype(int)

    df['Ano Veiculo'] = df['Ano Veiculo'].replace([0, -1], np.nan)

    df['Ano Veiculo'] = (df['Ano Veiculo'].mask((df['Ano Veiculo'] >= 10) & (df['Ano Veiculo'] < 23), df['Ano Veiculo'] + 2000))

    df['Ano Veiculo'] = (df['Ano Veiculo'].mask((df['Ano Veiculo'] > 50) & (df['Ano Veiculo'] <= 99), df['Ano Veiculo'] + 1900))

    df['Ano Veiculo'] = (df['Ano Veiculo'].mask((df['Ano Veiculo'] >= 200) & (df['Ano Veiculo'] < 223), (df['Ano Veiculo'] - 200) + 2000))

    df['Ano Veiculo'] = (df['Ano Veiculo'].mask((df['Ano Veiculo'] > 2023) | (df['Ano Veiculo'] < 1950), np.nan))

    df['Placa'] = df['Veiculos'].str.extract(r':(.*?)-')
    df['Placa'].replace('', np.nan, inplace=True)
    df['Contagem_Caracteres'] = df['Placa'].str.len()
    df['Placa'] = df['Placa'].mask((df['Contagem_Caracteres'] < 7), np.nan)
    df['Placa'].replace(['', '0000000'], np.nan, inplace=True)
    df.drop('Contagem_Caracteres', axis=1, inplace=True)

    df = df.loc[(df['Ano Veiculo'].notna()) | (df['Placa'].notna())]

    df['Contagem'] = df.groupby('OcDataConcessionaria')['OcDataConcessionaria'].transform('count')

    df = df.query('Contagem == 1')

    return df

def classificar_tipo_veiculo(df):


    df['Tipo_Veiculo'] = df['Veiculos'].str.extract(r'^(.*?)(?=\()')
    df['Marca'] = df['Veiculos'].str.extract(r'\((.*?)\/')
    df['Modelo'] = df['Veiculos'].str.extract(r'/(.*?):')

    df['Tipo_Veiculo'] = (df['Tipo_Veiculo'].replace(['AUTomovel', 'Perua/Caminhonete/Camioneta'],'Veiculo Leve').
                           replace(['MOTocicleta', 'MOTo Frete'],'Motocicleta').
                           replace(['CAMinhão', 'CARreta'], 'Veiculo Pesado').
                           replace(['Van', 'ONIbus', 'Microonibus'],'Veiculo Passageiro').
                           replace('BICicleta','Bicicleta').
                           replace('Trator','Outros'))


    return df


def aquivo_placas(df, placas):
    df_placas = df[['Ano', 'OcDataConcessionaria', 'NumVeic', 'Veiculos']]

    df_placas = df_placas.assign(Veiculos=df_placas['Veiculos'].str.split(';')).explode('Veiculos')
    df_placas['Veiculos'] = df_placas['Veiculos'].str.strip()
    df_acidentes_placas['Contagem_Caracteres'] = df_placas['Veiculos'].str.len()
    df_placas = df_placas.loc[(df_placas['Contagem_Caracteres'] != 0)]
    df_placas = df_placas.drop('Contagem_Caracteres', axis=1)

    df_placas['Ano Placa'] = df_placas['Veiculos'].str.extract(r'/(\d+)[)]')
    df_placas['Ano Placa'] = pd.to_numeric(df_placas['Ano Placa'], errors='coerce').fillna(-1).astype(int)
    df_placas['Ano Placa'] = np.where((df_placas['Ano Placa'] > 1950) & (df_placas['Ano Placa'] <= 2022),
                                      df_placas['Ano Placa'], '')
    df_placas['Ano Placa'] = pd.to_numeric(df_placas['Ano Placa'], errors='coerce').fillna(-1).astype(int)
    df_placas['Placa'] = df_placas['Veiculos'].str.extract(r':(.*?)-')

    # Contagem de quantos veiculos no acidente
    df_placas['Contagem'] = df_placas.groupby('OcDataConcessionaria')['OcDataConcessionaria'].transform('count')

    # Unindo a planilha de placas da API com a planilha original
    df_placas = pd.merge(df_placas, placas, on='Placa', how='left')
    df_placas['Ano Placa'] = df_placas.apply(
        lambda row: row['Ano_y'] if pd.notna(row['Ano_y']) and row['Ano_y'] != '' else row['Ano Placa'], axis=1)
    df_placas = df_placas.drop('Ano_y', axis=1)
    return df_placas



if(__name__ == "__main__"):
    df = classificar_tipo_veiculo(df)


    df = veiculos_placas (df)
    df_placas = apenas_placas (df)
    df_placas = contar_evasao(df_placas)
    df = pd.read_csv('C:/Users/Public/Documents/Mestrado/Dados/Cluster/PowerBi/Logit/df.csv', sep=",", encoding = "UTF-8")

    placas_api = pd.read_csv('C:/Users/Public/Documents/Mestrado/Dados/Cluster/PowerBi/Logit/placas_api2.csv', sep=",", encoding = "UTF-8")

    #Unindo a tabela fipe com a planilha placas criada
    placas = pd.merge(df_placas, placas_api, on='Placa', how='left')
    placas.loc[placas['Ano_y'] > 1900, 'Ano Placa'] = placas['Ano_y']
    placas['Ano Placa'].value_counts()
    placas.dtypes


    placas = pd.merge(df_placas_veic1, placas_api, left_on='Placa 1' ,right_on='Placa', how='left')
    placas['Ano veic'] = (placas['Ano'].fillna(placas['Ano 1'])).astype(int)
    #placas['Ano veic']= placas['Ano veic'].astype (int)

    placas = placas.drop(['Ano_y',], axis=1)
    placas.dtypes





    #Tratar idade
    placas ['Idade'] = placas.apply(lambda row: row['Ano_x'] - row['Ano veic'] if row['Ano veic'] != '' and (row['Ano_x'] - row['Ano veic']) >= 0 else None, axis=1)




    vitimas_feridos['Ano Placa'] = vitimas_feridos['Ano Placa'].replace(-1,0)
    vitimas_feridos['Idade Veiculo'] = vitimas_feridos.apply(lambda row: row['Ano'] - row['Ano Placa'] if (row['Ano Placa']>0 and (row['Ano'] - row['Ano Placa']) >= 0) else (np.nan if row['Ano Placa']==0 else 0), axis = 1)
    vitimas_feridos = vitimas_feridos[~vitimas_feridos['Veiculos'].str.contains('BICi',na=False)]
    vitimas_feridos.loc[vitimas_feridos['Veiculos'].str.contains('Van', na=False), 'Tipo Veic'] = 'Veic. Onibus'
    vitimas_feridos['Tipo Veic'] = vitimas_feridos['Tipo Veic'].fillna('Outros')
    vitimas_feridos = vitimas_feridos.drop(['Ano Placa', 'Veiculos'], axis=1)


