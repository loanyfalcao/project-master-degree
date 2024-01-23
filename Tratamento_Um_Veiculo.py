import pandas as pd
import numpy as np
import tratamento


def um_veic(df):

    df = df[['OcDataConcessionaria', 'Veiculos']]

    df = df.assign(Veiculos=df['Veiculos'].str.split(';')).explode('Veiculos')
    df['Veiculos'] = df['Veiculos'].str.strip()
    df = df.query('Veiculos != ""')

    df['Ano_Veiculo'] = df['Veiculos'].str.extract(r'/(\d+)[)]')
    df['Ano_Veiculo'] = pd.to_numeric(df['Ano_Veiculo'], errors='coerce').fillna(-1).astype(int)

    df['Ano_Veiculo'] = df['Ano_Veiculo'].replace([0, -1], np.nan)

    df['Ano_Veiculo'] = (df['Ano_Veiculo'].mask((df['Ano_Veiculo'] >= 10) & (df['Ano_Veiculo'] < 23), df['Ano_Veiculo'] + 2000))

    df['Ano_Veiculo'] = (df['Ano_Veiculo'].mask((df['Ano_Veiculo'] > 50) & (df['Ano_Veiculo'] <= 99), df['Ano_Veiculo'] + 1900))

    df['Ano_Veiculo'] = (df['Ano_Veiculo'].mask((df['Ano_Veiculo'] >= 200) & (df['Ano_Veiculo'] < 223), (df['Ano_Veiculo'] - 200) + 2000))

    df['Ano_Veiculo'] = (df['Ano_Veiculo'].mask((df['Ano_Veiculo'] > 2023) | (df['Ano_Veiculo'] < 1950), np.nan))

    df['Placa'] = df['Veiculos'].str.extract(r':(.*?)-')
    df['Placa'].replace('', np.nan, inplace=True)
    df['Contagem_Caracteres'] = df['Placa'].str.len()
    df['Placa'] = df['Placa'].mask((df['Contagem_Caracteres'] < 7), np.nan)
    df['Placa'].replace(['', '0000000'], np.nan, inplace=True)
    df.drop('Contagem_Caracteres', axis=1, inplace=True)

    df = df.loc[(df['Ano_Veiculo'].notna()) | (df['Placa'].notna())]

    df['Contagem'] = df.groupby('OcDataConcessionaria')['OcDataConcessionaria'].transform('count')

    df = df.query('Contagem == 1')

    return df

def classificar_tipo_veiculo(df):


    df['Tipo_Veiculo'] = df['Veiculos'].str.extract(r'^(.*?)(?=\()')
    df['Marca_Veiculo'] = df['Veiculos'].str.extract(r'\((.*?)\/')
    df['Modelo_Veiculo'] = df['Veiculos'].str.extract(r'/(.*?):')

    df['Tipo_Veiculo'] = (df['Tipo_Veiculo'].replace(['AUTomovel', 'Perua/Caminhonete/Camioneta'],'Veiculo Leve').
                           replace(['MOTocicleta', 'MOTo Frete'],'Motocicleta').
                           replace(['CAMinhão', 'CARreta'], 'Veiculo Pesado').
                           replace(['Van', 'ONIbus', 'Microonibus'],'Veiculo Passageiro').
                           replace('BICicleta','Bicicleta').
                           replace('Trator','Outros'))


    return df


def aquivo_placas(df, placas):

    df = pd.merge(df, placas, on='Placa', how='left')
    df['Ano_Veiculo'] = df.apply(lambda row: row['Ano'] if (pd.notna(row['Ano']) and row['Ano'] != '') else row['Ano_Veiculo'], axis=1)
    df['Ano_Veiculo'] = pd.to_numeric(df['Ano_Veiculo'], errors='coerce').fillna(-1).astype(int)
    df['Ano_Veiculo'] = df['Ano_Veiculo'].replace(-1, np.nan)

    df['Modelo_Veiculo'] = df.apply(lambda row: row['Modelo'] if (pd.notna(row['Modelo']) and row['Modelo'] != '') else row['Modelo_Veiculo'], axis=1)

    df = df.drop(columns=['Ano', 'Modelo'], axis=1)

    return df



if(__name__ == "__main__"):

    placas = pd.read_csv('')

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


