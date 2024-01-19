
######################### Regress?o Log?stica Bin?ria #########################

# Passo 1: Carregar os pacotes que ser?o usados

if(!require(pacman)) install.packages("pacman")
install.packages("pacman")
library(pacman)

pacman::p_load(dplyr, psych, car, MASS, DescTools, QuantPsyc, ggplot2)


# Passo 2: Carregar o banco de dados

# Importante: selecionar o diret?rio de trabalho (working directory)
# Isso pode ser feito manualmente: Session > Set Working Directory > Choose Directory

dados <- read.csv('Logit-GraveFatal.csv', stringsAsFactors = TRUE,
                  fileEncoding = "UTF-8")

View(dados)                                 # Visualiza??o dos dados em janela separada
glimpse(dados)                              # Visualiza??o de um resumo dos dados



# Passo 3: An?lise das frequ?ncias das categorias da VD

table(dados$Cancer)

summary(dados)


# Passo 4: Checagem das categorias de refer?ncia

levels(dados$Cancer)  # N?o = categoria de refer?ncia

levels(dados$Hab_Fumar)  # N?o = categoria de refer?ncia


# Passo 5: Checagem dos pressupostos

## 1. Vari?vel dependente dicot?mica (categorias mutuamente exclusivas)
## 2. Independ?ncia das observa??es (sem medidas repetidas)


## Constru??o do modelo:

mod <- glm(Cancer ~ Estresse + Hab_Fumar,
           family = binomial(link = 'logit'), data = dados)


## 3. Aus?ncia de outliers/ pontos de alavancagem

plot(mod, which = 5)

summary(stdres(mod))


## 4. Aus?ncia de multicolinearidade

pairs.panels(dados)
### Multicolinearidade: r > 0.9 (ou 0.8)


vif(mod)
### Multicolinearidade: VIF > 10


## 5. Rela??o linear entre cada VI cont?nua e o logito da VD


### Intera??o entre a VI cont?nua e o seu log n?o significativa (Box-Tidwell)

intlog <- dados$Estresse * log(dados$Estresse)

dados$intlog <- intlog

modint <- glm(Cancer ~ Hab_Fumar + Estresse + intlog,
              family = binomial(link = 'logit'), data = dados)

summary(modint)


### Outra op??o:

#### C?lculo do logito

logito <- mod$linear.predictors

### Outra op??o para o c?lculo do logito:
# prob <- predict(mod, type = "response")
# logito <- log(prob/(1-prob))

dados$logito <- logito


#### An?lise da rela??o linear

ggplot(dados, aes(logito, Estresse)) +
  geom_point(size = 0.5, alpha = 0.5) +
  geom_smooth(method = "loess") +
  theme_classic()


# Passo 6: An?lise do modelo

## Overall effects

Anova(mod, type = 'II', test = "Wald")


## Efeitos espec?ficos

summary(mod)


## Obten??o das raz?es de chance com IC 95% (usando log-likelihood)

exp(cbind(OR = coef(mod), confint(mod)))


## Obten??o das raz?es de chance com IC 95% (usando erro padr?o = SPSS)

exp(cbind(OR = coef(mod), confint.default(mod)))



# Passo 7: Cria??o e an?lise de um segundo modelo

mod2 <- glm(Cancer ~ Hab_Fumar,
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
ClassLog(mod, dados$Cancer)
ClassLog(mod2, dados$Cancer)



####### Como modificar as categorias de refer?ncia? ########

levels(dados$Hab_Fumar)

dados$Hab_Fumar <- relevel(dados$Hab_Fumar, ref = "Sim")


### ATEN??O: ? necess?rio rodar o modelo novamente!


levels(dados$Cancer)

dados$Cancer <- relevel(dados$Cancer, ref = "Sim")

