


if(!require(pacman)) install.packages("pacman")
install.packages("pacman")
library(pacman)
install.packages("ggplot2")
library(ggplot2)

pacman::p_load(dplyr, psych, car, MASS, DescTools, QuantPsyc, ggplot2)


dados <- read.csv('Arquivos/Logit/teste.csv', stringsAsFactors = TRUE,fileEncoding = "UTF-8")

View(dados)  
glimpse(dados) 


# Passo 3: Análise das frequencias das categorias da VD

table(dados$Gravidade)

summary(dados)


levels(dados$Gravidade)  # Fatal = categoria de referencia

mod <- glm(Gravidade ~ PosicaoVitima + Sexo + TracadoPista + Estacao + PerfilPista +  Período,
           family = binomial(link = 'logit'), data = dados)

# Aplicar filtro para manter apenas as colunas utilizadas
dados_filtrados <- dados[c("Gravidade","PosicaoVitima", "Sexo", "TracadoPista","Estacao", "PerfilPista", "Período")]

#Ausencia de outliers/ pontos de alavancagem
plot(mod, which = 5)

#Precisa ficar entre -3 e 3
summary(stdres(mod))


#Ausencia de multicolinearidade

### Multicolinearidade: r > 0.9 (ou 0.8)
pairs.panels(dados_filtrados)


### Multicolinearidade: VIF > 10
VIF(mod)


#Box-Tidwell - Analisar relaçao entre a VI e o log da VD

intlog1 <- dados_filtrados$PosicaoVitima * log(dados_filtrados$PosicaoVitima)
intlog2 <- dados_filtrados$Sexo * log(dados_filtrados$Sexo)
intlog3 <- dados_filtrados$CondicaoPista * log(dados_filtrados$CondicaoPista)
intlog4 <- dados_filtrados$Período * log(dados_filtrados$Período)

dados_filtrados$intlog1 <- intlog1
dados_filtrados$intlog2 <- intlog2
dados_filtrados$intlog3 <- intlog3
dados_filtrados$intlog4 <- intlog4

modint <- glm(Gravidade ~ PosicaoVitima + Sexo + CondicaoPista + Período + intlog1 + intlog2 + intlog3 + intlog4,
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


##Passo 6

## Overall effects. Quanto menor o Pr, mais influente
Anova(mod, type = 'II', test = "Wald")


## Efeitos especificos
summary(mod)


## Obtencao das raz?es de chance com IC 95% (usando log-likelihood)

#exp(cbind(OR = coef(mod), confint(mod)))


## Obtencao das razoes de chance com IC 95% (usando erro padrao = SPSS)
exp(coef(mod))

exp(cbind(OR = coef(mod), confint.default(mod)))



# Passo 7: Cria??o e an?lise de um segundo modelo

mod2 <- glm(Gravidade ~ Período,
            family = binomial(link = 'logit'), data = dados_filtrados)


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
ClassLog(mod, dados_filtrados$Gravidade)
ClassLog(mod2, dados_filtrados$Gravidade)



####### Como modificar as categorias de refer?ncia? ########

levels(dados_filtrados$Gravidade)

dados_filtrados$Gravidade <- relevel(dados_filtrados$Gravidade, ref = "Fatal")


### ATEN??O: ? necess?rio rodar o modelo novamente!


levels(dados_filtrados$Cancer)

dados_filtrados$Cancer <- relevel(dados_filtrados$Cancer, ref = "Sim")

