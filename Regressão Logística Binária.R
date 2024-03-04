
install.packages("pacman")
install.packages("ggplot2")
install.packages("lmtest")

library(lmtest)
library(pacman)
library(ggplot2)
pacman::p_load(dplyr, psych, car, MASS, DescTools, QuantPsyc, ggplot2)

dados1 <- read.csv('Arquivos/Cluster/ModeradosGraveFatal/df_vitimas_acidentes_2013-2022.csv', stringsAsFactors = TRUE,fileEncoding = "UTF-8")

dados <- read.csv('Arquivos/Logit/df_vitimas_acidentes_volume_2_2013-2022.csv', stringsAsFactors = TRUE,fileEncoding = "UTF-8")

glimpse(dados)

table(dados$Gravidade)

# Fatal = categoria de referencia
dados$Gravidade <- factor(dados$Gravidade, levels = c("1", "0"))
levels(dados$Gravidade)

#Outras categorias
dados$Sexo <- relevel(dados$Sexo, ref = "M")
dados$CondicaoPista <- relevel(dados$CondicaoPista, ref = "Seca")
dados$TracadoPista <- relevel(dados$TracadoPista, ref = "Reta")
dados$PerfilPista <- relevel(dados$PerfilPista, ref = "Em Nivel")
dados$Num_Veiculos <- relevel(dados$Num_Veiculos, ref = "Um")
levels(dados$Cat_Idade_Veiculo)

#dados$Faixa_Etaria <- factor(dados$Faixa_Etaria, levels = c("0-17 anos", "18-24 anos", "25-34 anos", "Maior que 50 anos","Não Informado"))
dados$Estacao <- factor(dados$Estacao, levels = c("Inverno", "Primavera", "Outono"))


mod <- glm(Gravidade ~ Sexo + Faixa_Etaria + TracadoPista + PerfilPista + Período + Volume,
           family = binomial(link = 'logit'), data = dados)

#mod <- glm(Gravidade ~ PosicaoVitima + Sexo + Faixa_Etaria + CondicaoPista + TracadoPista + PerfilPista + Estacao  + Período + TipoAcidente + Num_Veiculos + Volume + TracadoPista*CondicaoPista,
#           family = binomial(link = 'logit'), data = dados)


#Teste de White
bptest(mod, ~fitted(mod)^2)

# Aplicar filtro para manter apenas as colunas utilizadas
dados_filtrados <- dados[c("Gravidade", "PosicaoVitima", "Sexo", "Faixa_Etaria", "CondicaoPista", "TracadoPista", "PerfilPista", "Estacao", "Período", "TipoAcidente","Num_Veiculos", "Volume")]

boxplot(dados_filtrados)
#Ausencia de outliers/ pontos de alavancagem
plot(mod, which = 5)

#Precisa ficar entre -3 e 3
summary(stdres(mod))

#Ausencia de multicolinearidade

### Multicolinearidade: r > 0.9 (ou 0.8)
pairs.panels(dados_filtrados)
### Multicolinearidade: VIF > 10
VIF(mod)

## Overall effects. Quanto menor o Pvalue, mais influente
Anova(mod, type = 'II', test = "Wald")

## Efeitos especificos
summary(mod)


## Obtencao das razoes de chance com IC 95% (usando log-likelihood)
exp(cbind(OR = coef(mod), confint(mod)))


## Obtencao das razoes de chance com IC 95% (usando erro padrao = SPSS)
exp(cbind(OR = coef(mod), confint.default(mod)))



mod2 <- glm(Gravidade ~ Sexo + Faixa_Etaria + CondicaoPista + TracadoPista + PerfilPista + Estacao  + Período + TipoAcidente + Num_Veiculos,
           family = binomial(link = 'logit'), data = dados)

#Teste de White
bptest(mod2, ~fitted(mod)^2)

# Aplicar filtro para manter apenas as colunas utilizadas
dados_filtrados2 <- dados[c("Gravidade", "Sexo", "Faixa_Etaria", "CondicaoPista", "PerfilPista", "Estacao", "Período", "TipoAcidente","Num_Veiculos")]


#Ausencia de outliers/ pontos de alavancagem
plot(mod2, which = 5)

#Precisa ficar entre -3 e 3
summary(stdres(mod2))


#Ausencia de multicolinearidade

### Multicolinearidade: r > 0.9 (ou 0.8)
pairs.panels(dados_filtrados2)
### Multicolinearidade: VIF > 10
VIF(mod2)


## Overall effects
Anova(mod2, type="II", test="Wald")


## Efeitos especificos
summary(mod2)

## Obtencao das razoes de chance com IC 95% (usando erro padrao = SPSS)
exp(cbind(OR = coef(mod2), confint.default(mod2)))


## Qui-quadrado, caso o p-value seja menor que 0.05 os modelos são estatisticamente diferentes
anova(mod2, mod, test="Chisq")


# Tabela de classificacao
ClassLog(mod, dados_filtrados$Gravidade)
ClassLog(mod2, dados_filtrados2$Gravidade)


#Criacao e analise de um segundo modelo

mod3 <- glm(Gravidade ~Sexo + Faixa_Etaria + TracadoPista + PerfilPista  + Período + TipoAcidente + Num_Veiculos,
           family = binomial(link = 'logit'), data = dados)

#Teste de White
bptest(mod3, ~fitted(mod)^2)

# Aplicar filtro para manter apenas as colunas utilizadas
dados_filtrados3 <- dados[c("Gravidade", "Sexo", "Faixa_Etaria", "TracadoPista", "PerfilPista", "Período", "TipoAcidente", "Num_Veiculos")]


#Ausencia de outliers/ pontos de alavancagem
plot(mod3, which = 5)

#Precisa ficar entre -3 e 3
summary(stdres(mod3))


#Ausencia de multicolinearidade

### Multicolinearidade: r > 0.9 (ou 0.8)
pairs.panels(dados_filtrados3)
### Multicolinearidade: VIF > 10
VIF(mod3)


## Overall effects
Anova(mod3, type="II", test="Wald")


## Efeitos especificos
summary(mod3)

## Obtencao das razoes de chance com IC 95% (usando erro padrao = SPSS)
exp(cbind(OR = coef(mod3), confint.default(mod3)))



#Avaliacao da qualidade e comparacao entre modelos

## Pseudo R-quadrado
PseudoR2(mod, which = "Nagelkerke")
PseudoR2(mod2, which = "Nagelkerke")
PseudoR2(mod3, which = "Nagelkerke")


# Compara??o de modelos
## AIC e BIC
AIC(mod, mod2, mod3)
BIC(mod, mod2, mod3)


## Qui-quadrado, caso o p-value seja menor que 0.05 os modelos são estatisticamente diferentes
anova(mod2, mod3, test="Chisq")



#Box-Tidwell - Analisar relaçao entre a VI e o log da VD
intlog1 <- dados_filtrados$PosicaoVitima * log(dados_filtrados$PosicaoVitima)
intlog2 <- dados_filtrados$Sexo * log(dados_filtrados$Sexo)
intlog3 <- dados_filtrados$TracadoPista * log(dados_filtrados$TracadoPista)
intlog4 <- dados_filtrados$Estacao * log(dados_filtrados$Estacao)
intlog5 <- dados_filtrados$PerfilPista * log(dados_filtrados$PerfilPista)
intlog6 <- dados_filtrados$Período * log(dados_filtrados$Período)

dados_filtrados$intlog1 <- intlog1
dados_filtrados$intlog2 <- intlog2
dados_filtrados$intlog3 <- intlog3
dados_filtrados$intlog4 <- intlog4
dados_filtrados$intlog4 <- intlog5
dados_filtrados$intlog4 <- intlog5

modint <- glm(Gravidade ~ PosicaoVitima + Sexo + TracadoPista + Estacao + PerfilPista +  Período + intlog1 + intlog2 + intlog3 + intlog4 + intlog5 + intlog46,
              family = binomial(link = 'logit'), data = dados_filtrados)

summary(modint)


### Outra opcao

logito <- mod$linear.predictors

dados_filtrados$logito <- logito

#### Analise da relacao linear
ggplot(dados_filtrados, aes(logito, Gravidade)) +
  geom_point(size = 0.5, alpha = 0.5) +
  geom_smooth(method = "loess") +
  theme_classic()

