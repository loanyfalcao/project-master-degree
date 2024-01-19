import pandas as pd
import numpy as np
import tratamento
def classificar_tipo_veiculo(df):
    df = df[['Ano', 'OcDataConcessionaria', 'Numveic', 'Veiculos']]
    apoio_veiculos = df.copy()
    apoio_veiculos.drop(['Numveic','Ano'], inplace=True, axis=1)

    palavra_moto = 'moto'
    moto = apoio_veiculos[apoio_veiculos['Veiculos'].str.contains(palavra_moto, case=False)]
    moto = moto.drop(columns=['Veiculos'])
    moto['Veic. Moto'] = True
    df = pd.merge(df, moto, on='OcDataConcessionaria', how='left')


    palavra_veic_leve = 'autom'
    automovel = apoio_veiculos[apoio_veiculos['Veiculos'].str.contains(palavra_veic_leve, case=False)]

    palavra_veic_leve = 'caminhone'
    caminhonete = apoio_veiculos[apoio_veiculos['Veiculos'].str.contains(palavra_veic_leve, case=False)]

    palavra_veic_leve = 'perua'
    perua = apoio_veiculos[apoio_veiculos['Veiculos'].str.contains(palavra_veic_leve, case=False)]

    veic_leve = pd.concat([automovel, caminhonete, perua], axis=0, ignore_index=True)
    veic_leve = veic_leve.drop(columns=['Veiculos'])
    veic_leve = veic_leve.drop_duplicates(subset='OcDataConcessionaria')
    veic_leve['Veic. Leve'] = True
    df = pd.merge(df, veic_leve, on='OcDataConcessionaria', how='left')


    palavra_veic_pesado = 'caminhão'
    caminhao = apoio_veiculos[apoio_veiculos['Veiculos'].str.contains(palavra_veic_pesado, case=False)]

    palavra_veic_pesado = 'carreta'
    carreta = apoio_veiculos[apoio_veiculos['Veiculos'].str.contains(palavra_veic_pesado, case=False)]

    veic_pesado = pd.concat([caminhao, carreta], axis=0, ignore_index=True)
    veic_pesado = veic_pesado.drop(columns='Veiculos')
    veic_pesado = veic_pesado.drop_duplicates(subset='OcDataConcessionaria')
    veic_pesado['Veic. Pesado'] = True
    df = pd.merge(df, veic_pesado, on='OcDataConcessionaria', how='left')


    palavra_veic_onibus = 'Van'
    van = apoio_veiculos[apoio_veiculos['Veiculos'].str.contains(palavra_veic_onibus, case=False)]

    palavra_veic_onibus = 'onibus'
    onibus = apoio_veiculos[apoio_veiculos['Veiculos'].str.contains(palavra_veic_onibus, case=False)]

    veic_onibus = pd.concat([van, onibus], axis=0, ignore_index=True)
    veic_onibus = veic_onibus.drop(columns=['Veiculos'])
    veic_onibus = veic_onibus.drop_duplicates(subset='OcDataConcessionaria')
    veic_onibus['Veic. Onibus'] = True
    df = pd.merge(df, veic_onibus, on='OcDataConcessionaria', how='left')


    colunas = ['Veic. Leve','Veic. Moto','Veic. Pesado','Veic. Onibus']
    df[colunas] = df[colunas].fillna(False)

    return df

def veiculos_placas(df):

    df = df[['Ano', 'OcDataConcessionaria', 'Numveic', 'Veiculos']]

    veiculos = df['Veiculos'].str.split(';', expand=True)
    veiculos.columns = [f'Veiculo {i + 1}' for i in range(veiculos.shape[1])]
    df = pd.concat([df, veiculos], axis=1)

    # Separando placas
    for coluna in df.columns:
        if coluna.startswith('Veiculo '):
            nova_coluna = f'Placa {coluna.split(" ")[-1]}'
            df[nova_coluna] = df[coluna].str.extract(r':(.*?)-')
            for coluna in df.columns:
                if coluna.startswith('Veiculo '):
                    # Criando o nome da nova coluna
                    novo_ano = f'Ano {coluna.split(" ")[-1]}'
                    df[novo_ano] = df[coluna].str.extract(r'/(\d+)[)]')

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

# Não necessaria
def contar_veiculos(df):
    colunas_veiculos = df.filter(regex='^Veiculo').columns.tolist()
    df[colunas_veiculos] = df[colunas_veiculos].replace(['', ' ', 0], [None, None, None])
    df['NumVeiculos'] = df[colunas_veiculos].count(axis=1)
    return df

def contar_evasao(df):

    palavra = 'evadi'
    numero_colunas = len(df.filter(regex='^Veiculo ').columns.tolist())
    df_concat = pd.DataFrame()
    for i in range(0, numero_colunas):
        df_evasao = df[['OcDataConcessionaria', f'Veiculo {i + 1}']]
        df_evasao = df_evasao.dropna()

        df_evasao_v1 = df_evasao[df_evasao[f'Veiculo {i + 1}'].str.contains(palavra, case=False)]
        df_evasao_v1['Evasao'] = True

        df_evasao_v1 = df_evasao_v1.drop(columns=[f'Veiculo {i + 1}'])
        df_concat = pd.concat([df_concat, df_evasao_v1], ignore_index=True)

    df = pd.merge(df, df_concat, on='OcDataConcessionaria', how='left')
    df['Evasao'] = df['Evasao'].fillna(False)

    df['NumVeiculosEvadidos'] = df.groupby('OcDataConcessionaria')['OcDataConcessionaria'].transform('count')
    df['NumVeiculos_NaoEvadidos'] = np.where(df['Evasao'] == True, df['Numveic'] - df['NumVeiculosEvadidos'], df['Numveic'])
    df = df.drop_duplicates(subset='OcDataConcessionaria')


    return df

def retirar_vazios (df):
    for i in range(len(df.filter(regex='^Veiculo ').columns.tolist())):
        df[f'Veiculo {i + 1}'] = df[f'Veiculo {i + 1}'].replace(np.nan,'')
        df[f'Placa {i + 1}'] = df[f'Placa {i + 1}'].replace(np.nan,'')
        df[f'Ano {i + 1}'] = df[f'Ano {i + 1}'].replace(np.nan,'')

    return df

def contar_com_info(df):

    #palavra = 'evadi'
    numero_colunas = len(df.filter(regex='^Veiculo ').columns.tolist())
    df_concat = pd.DataFrame()
    for i in range(0, numero_colunas):
        df_auxiliar = df[['OcDataConcessionaria', f'Ano {i + 1}', f'Placa {i+1}']]
        df_auxiliar = df_auxiliar.loc[(df_auxiliar[f'Ano {i + 1}'] != np.nan) | (df_auxiliar[f'Placa {i+1}'] != np.nan)]

        df_evasao_v1 = df_evasao[df_evasao[f'Veiculo {i + 1}'].str.contains(palavra, case=False)]
        df_evasao_v1['Evasao'] = True

        df_evasao_v1 = df_evasao_v1.drop(columns=[f'Veiculo {i + 1}'])
        df_concat = pd.concat([df_concat, df_evasao_v1], ignore_index=True)

    df = pd.merge(df, df_concat, on='OcDataConcessionaria', how='left')
    df['Evasao'] = df['Evasao'].fillna(False)

    df['NumVeiculosEvadidos'] = df.groupby('OcDataConcessionaria')['OcDataConcessionaria'].transform('count')
    df['NumVeiculos_NaoEvadidos'] = np.where(df['Evasao'] == True, df['Numveic'] - df['NumVeiculosEvadidos'], df['Numveic'])
    df = df.drop_duplicates(subset='OcDataConcessionaria')


    return df

def um_veic(df):

    df = df.loc[(df['NumVeiculos_NaoEvadidos'] == 1)]
    df = df[['OcDataConcessionaria', 'Veiculo 1', 'Placa 1', 'Ano 1', 'NumVeiculos', 'NumVeiculos_v1', 'Evadiu']]

    df = pd.merge(df, placas_api, left_on='Placa 1', right_on='Placa', how='left')
    df['Ano'] = df['Ano'].astype(float)
    df['Ano 1'] = df['Ano 1'].astype(float)
    df['Ano 1'] = np.where(df['Ano'].notna(), df['Ano'], df['Ano 1'])
    # apenas verificar quanto % esta sem placa
    1 - (df['Ano 1'].isna().sum() / df['OcDataConcessionaria'].count())
    return df


def porcentagem(df):
    '''
    df['Concessionária'] = df['Concessionária'].replace('Fernão Dias',1)
    df['Concessionária'] = df['Concessionária'].replace('Régis Bittencourt',2)
    df['Concessionária'] = df['Concessionária'].replace('Litoral Sul',3)
    '''
    css_unico = df['Concessionária'].unique()
    ano_unico = df['Ano_x'].unique()
    # a = (df['Ano_x'].max() - df['Ano_x'].min())+1
    n = np.empty((14, 2), dtype=int)
    k = 0

    for css in css_unico:
        for ano in ano_unico:
            df_v_ano = df[df['Ano_x'] == ano]
            linhas_vazias = (1 - (df_v_ano['Ano 1'].isna().sum() / df_v_ano['OcDataConcessionaria'].count())) * 100
            n[k][0] = ano
            n[k][1] = linhas_vazias
            # n[k][2]=css
            k = k + 1

    # mapeamento = {1: "Fernão Dias", 2: "Regis Bittencourt", 3: "Litoral Sul",}
    # n[:, 2] = np.vectorize(mapeamento.get)(n[:, 2])
    return n



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


    df_veic2.dtypes
    df2 = df
    df2 = retirar_evadiu (df2)
    df2 = um_veic(df2)

    #Levando para o df apenas 1 veiculo
    df_v1 = pd.merge(df, df2, on = 'OcDataConcessionaria', how='inner')
    porcentagem(df_v1)

    df_litoral = df_v1.loc [(df_v1['Concessionária']=='Litoral Sul')]
    df_fernao = df_v1.loc [(df_v1['Concessionária']=='Fernão Dias')]
    df_v1['Concessionária'].unique()


    #Apenas acidentes com 1 veículo + Evadiu
    df_veic2 = df.loc [(df['NumVeiculos_v1'] == 1)]

    #Tratar idade
    placas ['Idade'] = placas.apply(lambda row: row['Ano_x'] - row['Ano veic'] if row['Ano veic'] != '' and (row['Ano_x'] - row['Ano veic']) >= 0 else None, axis=1)


    placas.dtypes
    df_placas_veic1 = idade_carro (df_placas_veic1)

    placas.to_csv("C:/Users/Public/Documents/Mestrado/Dados/Cluster/PowerBi/Logit/df_placas_veic1.csv", index = False, encoding = "UTF-8")




    placas.to_csv("C:/Users/Public/Documents/Mestrado/Dados/Cluster/PowerBi/Logit/df_placas2.csv", index = False, encoding = "UTF-8")


    df_placas = df_placas[~df_placas['Veiculos'].str.contains('Evadi', case=False).fillna(True)]
    df_placas['Contagem'] = df_placas.groupby('OcDataConcessionaria')['OcDataConcessionaria'].transform('count')
    df_placas = df_placas.query("Contagem == 1")

    #excluir algumas colunas
    df_placas.drop(["Contagem","Ano_x","DescrOcorrencia"], axis=1, inplace=True)
    df.drop(["Veiculos","Numveic","NaoInfo"], axis=1, inplace=True)

    #Unindo placas/veiculos com acidentes
    df2 = pd.merge(df, df_placas, on='OcDataConcessionaria', how = 'right')

    df2= function_numeros(df2)
    resumo, acidentes = function_resumo_v2(df2)


    vitimas_feridos['Ano Placa'] = vitimas_feridos['Ano Placa'].replace(-1,0)
    vitimas_feridos['Idade Veiculo'] = vitimas_feridos.apply(lambda row: row['Ano'] - row['Ano Placa'] if (row['Ano Placa']>0 and (row['Ano'] - row['Ano Placa']) >= 0) else (np.nan if row['Ano Placa']==0 else 0), axis = 1)
    vitimas_feridos = vitimas_feridos[~vitimas_feridos['Veiculos'].str.contains('BICi',na=False)]
    vitimas_feridos.loc[vitimas_feridos['Veiculos'].str.contains('Van', na=False), 'Tipo Veic'] = 'Veic. Onibus'
    vitimas_feridos['Tipo Veic'] = vitimas_feridos['Tipo Veic'].fillna('Outros')
    vitimas_feridos = vitimas_feridos.drop(['Ano Placa', 'Veiculos'], axis=1)


