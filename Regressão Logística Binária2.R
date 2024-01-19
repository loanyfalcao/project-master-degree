


if(!require(pacman)) install.packages("pacman")
install.packages("pacman")
library(pacman)
install.packages("ggplot2")
library(ggplot2)

pacman::p_load(dplyr, psych, car, MASS, DescTools, QuantPsyc, ggplot2)


dados_v2 <- read.csv('rvt900_litoral_feridos.csv', stringsAsFactors = TRUE,fileEncoding = "UTF-8")

dados <- dados_v2

dados <- subset(dados_v2, Ano_x >= 2016)

View(dados)  
glimpse(dados) 


# Passo 3: Análise das frequencias das categorias da VD

table(dados$Gravidade)

summary(dados)


levels(dados$Gravidade)  # Fatal = categoria de referencia

mod <- glm(Gravidade ~ Período + Ano_x + PosicaoVitima,
           family = binomial(link = 'logit'), data = dados)

summary(stdres(mod))
#Gravidade + CondicaoPista + TipoAcidente2 + Período + Estação + Idade_y + Tipo.Veic,
#PosicaoVitima, Sexo, TracadoPista, Ano_x, 


#Ausencia de outliers/ pontos de alavancagem
plot(mod, which = 5)

#Precisa ficar entre -3 e 3
summary(stdres(mod))


#Ausencia de multicolinearidade

### Multicolinearidade: r > 0.9 (ou 0.8)
pairs.panels(dados)


### Multicolinearidade: VIF > 10
vif(mod)


#Box-Tidwell - Analisar relaçao entre a VI e o log da VD

intlog1 <- dados$Período * log(dados$Período)
intlog2 <- dados$Ano_x * log(dados$Ano_x)
intlog3 <- dados$Idade_y * log(dados$Idade_y)
intlog3 <- dados$PosicaoVitima * log(dados$PosicaoVitima)

dados$intlog1 <- intlog1
dados$intlog2 <- intlog2
dados$intlog3 <- intlog3
dados$intlog4 <- intlog4

modint <- glm(Gravidade ~ Ano_x + Idade_y + PosicaoVitima + intlog2 + intlog3,
              family = binomial(link = 'logit'), data = dados)

summary(modint)


### Outra opcao

logito <- mod$linear.predictors
# prob <- predict(mod, type = "response")
# logito <- log(prob/(1-prob))

dados$logito <- logito

#### Analise da relacao linear

ggplot(dados, aes(logito, Gravidade)) +
  geom_point(size = 0.5, alpha = 0.5) +
  geom_smooth(method = "loess") +
  theme_classic()


##Passo 6

## Overall effects. Quanto menor o Pr, mais influente
Anova(mod, type = 'II', test = "Wald")


## Efeitos especificos
summary(mod)


## Obtencao das raz?es de chance com IC 95% (usando log-likelihood)

#exp(cbind(OR = coef(mod), confint(mod)))


## Obtencao das razoes de chance com IC 95% (usando erro padrao = SPSS)


exp(cbind(OR = coef(mod), confint.default(mod)))



# Passo 7: Cria??o e an?lise de um segundo modelo

mod2 <- glm(Gravidade ~ Período,
            family = binomial(link = 'logit'), data = dados)


## Overall effects

Anova(mod2, type="II", test="Wald")


## Efeitos espec?ficos

summary(mod2)

## Obten??o das raz?es de chance com IC 95% (usando log-likelihood)

exp(cbind(OR = coef(mod2), confint(mod2)))


## Obten??o das raz?es de chance com IC 95% (usando erro padr?o = SPSS)

exp(cbind(OR = coef(mod2), confint.default(mod2)))



# Passo 8: Avalia??o da qualidade e compara??o entre modelos

## Pseudo R-quadrado

PseudoR2(mod, which = "Nagelkerke")

PseudoR2(mod2, which = "Nagelkerke")


# Compara??o de modelos
## AIC e BIC
AIC(mod, mod2)
BIC(mod, mod2)


## Qui-quadrado
anova(mod2, mod, test="Chisq")


# Tabela de classifica??o
ClassLog(mod, dados$Gravidade)
ClassLog(mod2, dados$Gravidade)



####### Como modificar as categorias de refer?ncia? ########

levels(dados$Gravidade)

dados$Gravidade <- relevel(dados$Gravidade, ref = "Fatal")


### ATEN??O: ? necess?rio rodar o modelo novamente!


levels(dados$Cancer)

dados$Cancer <- relevel(dados$Cancer, ref = "Sim")

