import pandas as pd
import numpy as np
import Tratamento_Um_Veiculo

def incluir_placas_api(df, placas):

    df = pd.merge(df, placas, on='Placa', how='left')
    df['Ano_Veiculo'] = df.apply(lambda row: row['Ano'] if (pd.isna(row['Ano_Veiculo']) and pd.notna(row['Ano'])) else row['Ano_Veiculo'],axis=1)

    df['Ano_Veiculo'] = pd.to_numeric(df['Ano_Veiculo'], errors='coerce').fillna(-1).astype(int)
    df['Ano_Veiculo'] = df['Ano_Veiculo'].replace(-1, np.nan)

    df['Ano'] = pd.to_numeric(df['Ano'], errors='coerce').fillna(-1).astype(int)
    df['Ano'] = df['Ano'].replace(-1, np.nan)

    df.rename(columns={'Ano': 'Ano_Placa'}, inplace=True)

    return df


def colunas_tipo_veiculo(df):

    df = df[['OcDataConcessionaria', 'Ano', 'Numveic', 'Veiculos']]
    apoio_veiculos = df.copy()
    apoio_veiculos.drop(['Ano', 'Numveic'], inplace=True, axis=1)

    palavra_moto = 'moto'
    moto = apoio_veiculos[apoio_veiculos['Veiculos'].str.contains(palavra_moto, case=False)]
    moto = moto.drop(columns=['Veiculos'])
    moto['Motocicleta'] = True
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
    veic_leve['Veiculo Leve'] = True
    df = pd.merge(df, veic_leve, on='OcDataConcessionaria', how='left')


    palavra_veic_pesado = 'caminhão'
    caminhao = apoio_veiculos[apoio_veiculos['Veiculos'].str.contains(palavra_veic_pesado, case=False)]

    palavra_veic_pesado = 'carreta'
    carreta = apoio_veiculos[apoio_veiculos['Veiculos'].str.contains(palavra_veic_pesado, case=False)]

    veic_pesado = pd.concat([caminhao, carreta], axis=0, ignore_index=True)
    veic_pesado = veic_pesado.drop(columns='Veiculos')
    veic_pesado = veic_pesado.drop_duplicates(subset='OcDataConcessionaria')
    veic_pesado['Veiculo Pesado'] = True
    df = pd.merge(df, veic_pesado, on='OcDataConcessionaria', how='left')


    palavra_veic_onibus = 'Van'
    van = apoio_veiculos[apoio_veiculos['Veiculos'].str.contains(palavra_veic_onibus, case=False)]

    palavra_veic_onibus = 'onibus'
    onibus = apoio_veiculos[apoio_veiculos['Veiculos'].str.contains(palavra_veic_onibus, case=False)]

    veic_onibus = pd.concat([van, onibus], axis=0, ignore_index=True)
    veic_onibus = veic_onibus.drop(columns=['Veiculos'])
    veic_onibus = veic_onibus.drop_duplicates(subset='OcDataConcessionaria')
    veic_onibus['Veiculo Passageiro'] = True
    df = pd.merge(df, veic_onibus, on='OcDataConcessionaria', how='left')


    colunas = ['Veiculo Leve', 'Motocicleta', 'Veiculo Pesado', 'Veiculo Passageiro']
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

def alterar_ano(df, placas):
    n_veiculos = df.filter(regex='^Veiculo ').columns.tolist()
    for i in range(1, len(n_veiculos) + 1):
        auxiliar = df.loc[df[f'Placa {i}'].notna()]
        auxiliar = auxiliar[['OcDataConcessionaria', f'Placa {i}']]
        auxiliar_placas = placas[['Placa', 'Ano_Veiculo']]
        auxiliar = pd.merge(auxiliar, auxiliar_placas, left_on=f'Placa {i}', right_on='Placa', how='left')
        auxiliar.drop(['Placa', f'Placa {i}'], axis=1, inplace=True)
        df = pd.merge(df, auxiliar, on='OcDataConcessionaria', how='left')

        df[f'Ano {i}'] = df.apply(lambda row: row['Ano_Veiculo'] if pd.notna(row['Ano_Veiculo']) else row[f'Ano {i}'],
                                  axis=1)
        df.drop('Ano_Veiculo', axis=1, inplace=True)

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
    df_placa = Tratamento_Um_Veiculo.tratar_erros_ano(df_placa)
    df_placa = Tratamento_Um_Veiculo.tratar_placa(df_placa)
    df_placa = Tratamento_Um_Veiculo.incluir_placas_api(df_placa, placas)

    df_placa['Ano_Veiculo'] = df_placa.apply(lambda row: tratar_ano(row), axis=1)
    df_placa = df_placa.drop(columns=['Ano_Placa', 'Ano_Acidente'], axis=1)

    df_placa.to_csv('Arquivos/df_placa.csv', sep=',', index=False, encoding='UTF-8')

    df_veiculos = colunas_tipo_veiculo(df_acidentes)
    df_veiculos = colunas_placas_ano(df_veiculos)
    #df_veiculos = alterar_ano(df_veiculos, df_placa)
    df_veiculos = contar_evasao(df_veiculos)
    #df_veiculos = retirar_vazios(df_veiculos)

    df_veiculos.to_csv('Arquivos/df_veiculo_detalhado.csv', sep=',', index=False, encoding='UTF-8')

