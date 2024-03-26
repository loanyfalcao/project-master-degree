import os
import glob
import pandas as pd
from datetime import datetime
import numpy as np

def unir_arquivos (url):
    diretorio_atual = os.getcwd()

    extension = 'csv'
    os.chdir(url)
    all_filenames = [i for i in glob.glob('*.{}'.format(extension))]

    dfs = []
    for filename in all_filenames:
        df_temp = pd.read_csv(filename)
        dfs.append(df_temp)

    df = pd.concat(dfs, ignore_index=True)

    os.chdir(diretorio_atual)

    return df

def acidentes_delete_colunas(df):
    colunas_excluir = ['grupo', 'ncontrole', 'TipoOcorrencia', 'TipoAcidenteSub1', 'TipoAcidenteSub2', 'CausaProvavel', 'NumBO', 'Origem', 'CidadeV1', 'CidadeV2','CidadeV3','CidadeVx','NaoInfo','RecursosAcionados','ProvidenciasTomadas', 'DescricaoAcidente', 'Obs', 'CondicaoEspecial','CondicaoVisibilidade', 'CondicaoTempo', 'Latitude', 'Longitude', 'Unnamed: 45', 'TipoPista']
    df.drop(colunas_excluir, axis=1, errors='ignore', inplace=True)
    return df


def tratar_concessionaria(df):
    if "Concessionária" in df.columns:
        df.rename(columns={'Concessionária': 'Concessionaria'}, inplace=True)
    concessionaria = {'ARTERIS FLUMINENSE': 'Fluminense',
                      'INTERVIAS': 'Intervias',
                      'Arteris Planalto Sul': 'Planalto Sul',
                      'Arteris Fernão Dias': 'Fernão Dias',
                      'Arteris Litoral Sul': 'Litoral Sul',
                      'Auto Pista Regis': 'Régis Bittencourt',
                      'VIAPAULISTA': 'ViaPaulista'}
    df['Concessionaria'].replace(concessionaria, inplace=True)

    return df


def tratar_duplicadas(df):
    df['DataOcorrencia'] = pd.to_datetime(df['DataOcorrencia']).dt.date
    df['OcDataConcessionaria'] = df.apply(
        lambda row: '%s.%s.%s' %(row['NumOcorrencia'], row['DataOcorrencia'], row['Concessionaria']), axis=1)
    df.drop_duplicates(subset='OcDataConcessionaria', inplace=True)
    return df


def ajustando_formatos(df):
    coluna = ['km', 'mt']
    df[coluna] = df[coluna].astype(float)
    df = df.dropna(subset=['NumOcorrencia'])
    df['NumOcorrencia'] = df['NumOcorrencia'].astype(int)
    df['DataOcorrencia'] = pd.to_datetime(df['DataOcorrencia'], format='%m/%d/%Y')
    df['Hora'] = pd.to_datetime(df['Hora'], format='%H:%M:%S')

    return df


def incluir_colunas(df):
    df.loc[df['DescrOcorrencia'] == 'Acidente com Danos Materiais', 'UPS'] = 1
    df.loc[(df['DescrOcorrencia'] == 'Acidente com VITIMA') & (df['TipoAcidente'] != 'Atropelamento - Pedestre'), 'UPS'] = 4
    df.loc[(df['DescrOcorrencia'] == 'Acidente com VITIMA') & (df['TipoAcidente'] == 'Atropelamento - Pedestre'), 'UPS'] = 6
    df.loc[df['DescrOcorrencia'] == 'Acidente com Vitima Fatal', 'UPS'] = 13

    df['kmmt'] = round((df['km'] + (df['mt'] / 1000)), 1)
    df.drop(['km', 'mt'], axis=1, inplace=True)

    df['Estacao'] = df['DataOcorrencia'].apply(obter_estacao)

    df.dropna(subset=['DataOcorrencia'], inplace=True)
    df['Ano'] = pd.DatetimeIndex(df['DataOcorrencia']).year.astype(int)
    df['Mes'] = pd.DatetimeIndex(df['DataOcorrencia']).month.astype(int)

    # Periodo dia
    df.dropna(subset=['Hora'], inplace=True)
    inicio_noite = datetime.strptime('18:00:00', '%H:%M:%S')
    fim_noite = datetime.strptime('06:00:00', '%H:%M:%S')

    df['Período'] = df['Hora'].apply(lambda x: 'Noite' if (x.time() >= inicio_noite.time() or x.time() < fim_noite.time()) else 'Dia')
    df = df.drop(columns='Hora', axis=1)
    return df


def ajustando_lat_lon(df):
    unico_km = pd.read_csv('Arquivos/Base/Latitude-Longitude.csv', encoding='latin-1', index_col=None)
    unico_km.drop(columns=['Concessionaria', 'kmmt', 'Rodovia'], axis=1, inplace=True)

    df.loc[(df['Concessionaria'] == 'Litoral Sul') & (df['kmmt'] == 682.5), 'kmmt'] = 681.1

    df['ConcessionariaRodoviakm'] = df.apply(
        lambda row: '%s.%s.%s' % (row['Concessionaria'], row['Rodovia'], row['kmmt']), axis=1)

    df = pd.merge(df, unico_km, on='ConcessionariaRodoviakm', how='left', right_index=False)
    df.drop(['ConcessionariaRodoviakm'], axis=1, inplace=True)
    df.dropna(subset=['Longitude', 'Latitude'], inplace=True)
    return df


def obter_estacao(data):
    mes = data.month
    if 3 <= mes <= 5:
        return 'Outono'
    elif 6 <= mes <= 8:
        return 'Inverno'
    elif 9 <= mes <= 11:
        return 'Primavera'
    else:
        return 'Verão'


def de_para_acidente(df):
    acidente = pd.read_csv('Arquivos/Base/TipoAcidente.csv', sep=",", encoding="ISO-8859-1", index_col=None)
    df = pd.merge(df, acidente, on='TipoAcidente', how='inner')
    df.drop(columns=['TipoAcidente'], inplace=True)
    df.rename(columns={'TipoAcidente2': 'TipoAcidente'}, inplace=True)

    #Padronizar local
    local = pd.read_csv('Arquivos/Base/Local.csv', sep=",", encoding="ISO-8859-1", index_col=None)
    df = pd.merge(df, local, on='strLocal', how='inner')
    df = df.loc[(df['Local2'] != 'Marginal') &
                (df['Local2'] != 'Base Operacional') &
                (df['Local2'] != 'Posto Policial') &
                (df['Local2'] != 'Fora')]
    df.drop(columns=['strLocal'], inplace=True)
    df.rename(columns={'Local2': 'Local'}, inplace=True)

    #Padronizar tipoLocal
    df['TipoLocal'] = df['TipoLocal'].replace(['Residencial','Comercial','Industrial','Escolar','Recreio'], 'Urbano')
    df['TipoLocal'] = df['TipoLocal'].replace(['Praça de Pedágio','0','Praça de Pedágio',np.nan], 'Rural')

    #Padronizar descrição da ocorrencia
    df['DescrOcorrencia'] = df['DescrOcorrencia'].str.replace('*', '').str.strip()

    #Padronizar não def
    df['TracadoPista'].replace('Não Def', 'Reta', inplace=True)
    df['CondicaoPista'].replace('Não Def', 'Seca', inplace=True)
    df['PerfilPista'].replace('Não Def', 'Em Nivel', inplace=True)

    return df


def alterar_acidente_bicicleta (df):

    df.dropna(subset=['Veiculos'], inplace=True)
    auxiliar = df[['Veiculos', 'TipoAcidente']]

    palavra = 'bicicleta'
    tipoac = auxiliar[auxiliar['Veiculos'].str.contains(palavra, case=False)]

    tipoac['TipoAcidente'] = tipoac['TipoAcidente'].replace(['Colisão Traseira','Colisão Transversal','Colisão Lateral','Engavetamento''Colisão Frontal'],
                                                            'Atropelamento - Ciclista', regex=True)

    tipoac = tipoac.loc[(tipoac['TipoAcidente'] == 'Atropelamento - Ciclista')]
    tipoac['Analise'] = 1
    tipoac.drop(columns=['TipoAcidente', 'Veiculos'],axis=1, inplace=True)

    df = pd.merge(df, tipoac, left_index=True, right_index=True, how='left')
    df.loc[df['Analise'] == 1, 'TipoAcidente'] = 'Atropelamento - Ciclista'
    df.drop('Analise', axis=1, inplace=True)

    return df


def incluir_qgis(df):
    qgis = pd.read_csv('Arquivos/Base/QGIS.csv', index_col=None)

    df.rename(columns={'TracadoPista': 'TracadoPista_1', 'TipoLocal': 'TipoLocal_1'}, inplace=True)
    df = pd.merge(df, qgis, how='left', on='OcDataConcessionaria')

    df['TracadoPista'] = df['TracadoPista'].fillna(df['TracadoPista_1'])
    df['TipoLocal'] = df['TipoLocal'].fillna(df['TipoLocal_1'])

    df.drop(columns=['TracadoPista_1', 'TipoLocal_1'], inplace=True)
    return df


def definir_anos(df, year1, year2):
    df = df.loc[(df['Ano'] >= year1) & (df['Ano'] <= year2)]
    return df

def tipo_veiculo(df):
    apoio_veiculos = df.copy()
    apoio_veiculos = apoio_veiculos[['OcDataConcessionaria', 'Ano', 'Numveic', 'Veiculos']]
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
    veic_leve['Veiculo_Leve'] = True
    df = pd.merge(df, veic_leve, on='OcDataConcessionaria', how='left')


    palavra_veic_pesado = 'caminhão'
    caminhao = apoio_veiculos[apoio_veiculos['Veiculos'].str.contains(palavra_veic_pesado, case=False)]

    palavra_veic_pesado = 'carreta'
    carreta = apoio_veiculos[apoio_veiculos['Veiculos'].str.contains(palavra_veic_pesado, case=False)]

    veic_pesado = pd.concat([caminhao, carreta], axis=0, ignore_index=True)
    veic_pesado = veic_pesado.drop(columns='Veiculos')
    veic_pesado = veic_pesado.drop_duplicates(subset='OcDataConcessionaria')
    veic_pesado['Veiculo_Pesado'] = True
    df = pd.merge(df, veic_pesado, on='OcDataConcessionaria', how='left')


    palavra_veic_onibus = 'Van'
    van = apoio_veiculos[apoio_veiculos['Veiculos'].str.contains(palavra_veic_onibus, case=False)]

    palavra_veic_onibus = 'onibus'
    onibus = apoio_veiculos[apoio_veiculos['Veiculos'].str.contains(palavra_veic_onibus, case=False)]

    veic_onibus = pd.concat([van, onibus], axis=0, ignore_index=True)
    veic_onibus = veic_onibus.drop(columns=['Veiculos'])
    veic_onibus = veic_onibus.drop_duplicates(subset='OcDataConcessionaria')
    veic_onibus['Veiculo_Passageiro'] = True
    df = pd.merge(df, veic_onibus, on='OcDataConcessionaria', how='left')


    colunas = ['Veiculo_Leve', 'Motocicleta', 'Veiculo_Pesado', 'Veiculo_Passageiro']
    df[colunas] = df[colunas].fillna(False)

    return df


def vitimas_tipo_acidente(df):
    df['DescrOcorrencia'] = df['DescrOcorrencia'].str.replace('\*', '', regex=True)
    condicao = df['DescrOcorrencia'].isin(['Acidente com VITIMA', 'Acidente com Vitima Fatal', 'Acidente com Danos Materiais'])
    df = df[condicao]

    return df


def obter_idade(idade):
    if 1 <= idade <= 17:
        return '1-17 anos'
    elif 18 <= idade <= 24:
        return '18-24 anos'
    elif 25 <= idade <= 34:
        return '25-34 anos'
    elif 35 <= idade <= 49:
        return '35-49 anos'
    elif idade >= 50:
        return 'Maior que 50 anos'
    else:
        return 'Não Informado'


def de_para_vitimas(df):
    df['Sexo'] = df['Sexo'].replace('NI', 'M')

    df['PosicaoVitima'] = df['PosicaoVitima'].replace(['Piloto', 'Condutor'], 'Condutor')
    df['PosicaoVitima'] = df['PosicaoVitima'].replace(['Outros', 'Ignorado', 'Caçamba', 'Cadeirinha', 'Atrás do motorista', 'Atrás do acompanhante', 'Acompanhante', 'Garupa', np.nan], 'Passageiro')
    df['PosicaoVitima'] = df['PosicaoVitima'].replace(['Bicicleta', 'Pedestre'], 'Bicicleta/Pedestre')

    df['Gravidade'].replace('Não Informado', 'Ileso', inplace=True)

    df['Idade'] = df['Idade'].replace('Não Informado', 0).fillna(0).astype(int)
    df['Idade'] = df.apply(lambda row: row['Idade'] if (row['Idade'] > 15) else (
        0 if (row['Idade'] <= 15 and row['PosicaoVitima'] == 'Condutor') else row['Idade']), axis=1)

    df['Faixa_Etaria'] = df['Idade'].apply(obter_idade)
    return df


def coluna_unica(df):
    df['DataOcorrencia'] = pd.to_datetime(df['DataOcorrencia']).dt.date
    df['OcDataConcessionaria'] = df.apply(lambda x: '%s.%s.%s' %(x['NumOcorrencia'], x['DataOcorrencia'], x['Concessionaria']), axis=1)
    return df


def vitimas_delete_colunas(df):
    colunas_a_manter = ['OcDataConcessionaria', 'Concessionaria', 'NumVitima', 'NumOcorrencia', 'DataOcorrencia', 'DescrOcorrencia', 'PosicaoVitima', 'Sexo', 'Idade', 'Gravidade', 'Faixa_Etaria']
    return df.loc[:, colunas_a_manter]


if __name__ == "__main__":

    df_acidentes = unir_arquivos('C:/Users/Public/Documents/Mestrado/Dados/Acidentes/CSV')
    df_acidentes = acidentes_delete_colunas(df_acidentes)
    df_acidentes = tratar_concessionaria(df_acidentes)
    concessionaria = ['Litoral Sul', 'Fernão Dias', 'Régis Bittencourt']
    df_acidentes = df_acidentes[df_acidentes['Concessionaria'].isin(concessionaria)]

    df_acidentes = ajustando_formatos(df_acidentes)
    df_acidentes = tratar_duplicadas(df_acidentes)
    df_acidentes = incluir_colunas(df_acidentes)
    df_acidentes = ajustando_lat_lon(df_acidentes)
    df_acidentes = de_para_acidente(df_acidentes)
    df_acidentes = alterar_acidente_bicicleta(df_acidentes)
    df_acidentes = incluir_qgis(df_acidentes)
    df_acidentes = tipo_veiculo(df_acidentes)
    df_acidentes = definir_anos(df_acidentes, 2009, 2022)
    #df_acidentes = coluna_em_numeros(df_acidentes)

    df_acidentes.to_csv('Arquivos/df_acidentes.csv', index=False, encoding='utf-8')

    df_vitimas = unir_arquivos('C:/Users/Public/Documents/Mestrado/Dados/RVT900')
    df_vitimas = vitimas_tipo_acidente(df_vitimas)
    df_vitimas = de_para_vitimas(df_vitimas)
    df_vitimas = tratar_concessionaria(df_vitimas)
    df_vitimas = ajustando_formatos(df_vitimas)
    df_vitimas = coluna_unica(df_vitimas)
    df_vitimas = vitimas_delete_colunas(df_vitimas)

    df_vitimas.to_csv('Arquivos/df_vitimas.csv', index=False, encoding='utf-8')