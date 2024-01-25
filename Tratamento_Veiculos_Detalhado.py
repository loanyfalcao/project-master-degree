import pandas as pd
import numpy as np
import Tratamento_Um_Veiculo

def incluir_placas_api(df, placas):

    df = pd.merge(df, placas, on='Placa', how='left')
    df.rename(columns={'Ano':'Ano_Placa'}, inplace=True)

    df['Ano_Placa'] = pd.to_numeric(df['Ano_Placa'], errors='coerce').fillna(-1).astype(int)
    df['Ano_Placa'] = df['Ano_Placa'].replace([0, -1], np.nan)

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

def colunas_tipo_veiculo(df):

    df = df[['OcDataConcessionaria', 'Ano', 'Numveic', 'Veiculos']]
    apoio_veiculos = df.copy()
    apoio_veiculos.drop(['Ano', 'Numveic'], inplace=True, axis=1)

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

def colunas_placas_ano(df):

    df = df[['Ano', 'OcDataConcessionaria', 'Numveic', 'Veiculos']]

    veiculos = df['Veiculos'].str.split(';', expand=True)
    veiculos.columns = [f'Veiculo {i + 1}' for i in range(veiculos.shape[1])]
    df = pd.concat([df, veiculos], axis=1)

    for coluna in df.columns:
        if coluna.startswith('Veiculo '):
            nova_coluna = f'Placa {coluna.split(" ")[-1]}'
            df[nova_coluna] = df[coluna].str.extract(r':(.*?)-')
            for coluna in df.columns:
                if coluna.startswith('Veiculo '):
                    novo_ano = f'Ano {coluna.split(" ")[-1]}'
                    df[novo_ano] = df[coluna].str.extract(r'/(\d+)[)]')
                    df[novo_ano] = df[novo_ano].replace(0.0,'')
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
        df[f'Veiculo {i + 1}'] = df[f'Veiculo {i + 1}'].replace('',np.nan)
        df[f'Placa {i + 1}'] = df[f'Placa {i + 1}'].replace('',np.nan)
        df[f'Ano {i + 1}'] = df[f'Ano {i + 1}'].replace('',np.nan)

    return df



if(__name__ == "__main__"):

    placas = pd.read_csv('Arquivos/placas_api.csv', sep=',', encoding='UTF-8')

    df_acidentes = pd.read_csv('Arquivos/df_acidentes.csv', sep=',', encoding='UTF-8')

    df_placa = Tratamento_Um_Veiculo.veiculo_por_linha(df_acidentes)

    df_placa = Tratamento_Um_Veiculo.tratar_ano(df_placa)

    df_placa = Tratamento_Um_Veiculo.tratar_placa(df_placa)

    df_placa = incluir_placas_api(df_placa, placas)
    df.dropna(subset='Ano_Veiculo', inplace=True)

    df_placa['Ano_Veiculo'] = df_placa.apply(lambda row: tratar_ano(row), axis=1)
    df_placa = df_placa.drop(columns=['Ano_Placa', 'Ano_Acidente'], axis=1)

    df_placa.to_csv('Arquivos/df_placa.csv', sep=',', index=False, encoding='UTF-8')

    df_veiculos = colunas_tipo_veiculo(df_acidentes)

    df_veiculos = colunas_placas_ano(df_veiculos)

    df_veiculos = contar_evasao(df_veiculos)

    #df_veiculos = retirar_vazios(df_veiculos)

    df_veiculos.to_csv('Arquivos/df_veiculo_detalhado.csv', sep=',', index=False, encoding='UTF-8')

