def transformar_categorica(dados):
    variaveis_categoricas = ['PosicaoVitima', 'Sexo', 'Faixa_Etaria', 'CondicaoPista', 'PerfilPista', 'Estacao', 'Período',
                         'TipoAcidente', 'Volume_Total', 'TracadoPista', 'TipoLocal', 'Motocicleta', 'Veiculo Leve',
                         'Veiculo Pesado', 'Veiculo Passageiro', 'Ano_2014', 'Num_Veiculos', 'Cluster']

    for variavel in variaveis_categoricas:
        dados[variavel] = pd.Categorical(dados[variavel])

    return dados


def residuos_padronizados(modelo):
    std_residuos = modelo.get_influence().resid_studentized
    return print(f'Residuo mínimo: {round(np.min(std_residuos), 2)} \nResiduo maximo: {round(np.max(std_residuos), 2)}')


def calculando_vif(modelo):
    X = modelo.model.exog
    vif_data = pd.DataFrame()
    vif_data["variavel"] = range(X.shape[1])
    vif_data["VIF"] = [variance_inflation_factor(X, i) for i in range(X.shape[1])]
    return vif_data


def calcular_anova(modelo):
    anova_stats = pd.DataFrame(
        {"Efeito": modelo.params.index, "Estatística": modelo.tvalues, "Valor p": modelo.pvalues})
    return print(anova_stats)


def intervalo_confianca(modelo):
    coeficientes = modelo.params
    intervalos_confianca = modelo.conf_int()

    OR = np.exp(coeficientes)

    lower_CI = np.exp(intervalos_confianca[0])
    upper_CI = np.exp(intervalos_confianca[1])

    resultado_OR_CI = pd.DataFrame({
        'OR': OR,
        'CI 95% inferior': lower_CI,
        'CI 95% superior': upper_CI
    })

    return resultado_OR_CI


if __name__ == '__main__':
    import pandas as pd
    import numpy as np
    import statsmodels.api as sm
    import statsmodels.stats.diagnostic as smd
    from statsmodels.stats.outliers_influence import variance_inflation_factor

    dados = pd.read_csv('Arquivos/Cluster/resumo_vitimas_acidentes_volume_2_2018-2022.csv', encoding="UTF-8")

    dados = dados[
        ['Gravidade', 'PosicaoVitima', 'Sexo', 'Faixa_Etaria', 'CondicaoPista', 'PerfilPista', 'Estacao', 'Período',
         'TipoAcidente', 'Volume_Total', 'TracadoPista', 'TipoLocal', 'Motocicleta', 'Veiculo Leve', 'Veiculo Pesado',
         'Veiculo Passageiro', 'Ano_2014', 'Num_Veiculos', 'Cluster']]

    dados = transformar_categorica(dados)
    '''
    dados['Sexo'] = dados['Sexo'].cat.reorder_categories(['M', 'F'], ordered=True)
    dados['Faixa_Etaria'] = dados['Faixa_Etaria'].cat.reorder_categories(['25-34 anos', '1-17 anos', '35-49 anos', 'Maior que 50 anos', 'Não Informado'], ordered=True)
    '''

    # Ajustando o modelo de regressão logística
    modelo = sm.formula.glm(
        "Gravidade ~ PosicaoVitima + Sexo + Faixa_Etaria + CondicaoPista + PerfilPista + Estacao + Período + TipoAcidente + Volume_Total + TracadoPista + TipoLocal + Motocicleta +  Q('Veiculo Leve') + Q('Veiculo Pesado') + Q('Veiculo Passageiro') + Ano_2014 + Num_Veiculos + Cluster",
        family=sm.families.Binomial(link=sm.families.links.Logit()), data=dados).fit()


    print(modelo.summary())

    calculando_vif(modelo)
    residuos_padronizados(modelo)
    calcular_anova(modelo)
    intervalo_confianca(modelo)