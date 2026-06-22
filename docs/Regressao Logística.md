# Modelo: Regressão Logística (Baseline)

## Objetivo do Modelo
A Regressão Logística figura como um dos métodos lineares preditivos mais adotados historicamente. Sua implantação tem como objetivo construir a ***baseline* oficial** a pontuação mínima de viabilidade a qual servirá de lastro para validarmos se os outros modelos avançados justificam, de fato, a alocação de tempo computacional.

## Etapas Realizadas e Tratamentos
Toda base consumida precisou passar por processamento contínuo:
- Aplicação de completude nos valores ausentes (NaN) por intermédio de imputações (valor mais frequente ou iterativo nas características contínuas).
- Codificação posicional (*One-Hot-Encoding*) de variáveis em categorias fechadas para formatar perfeitamente colunas de peso numérico e independente para o preditor.

## Arquitetura, Regularização e Estratégias de Treinamento
Foi acionada uma formulação matemática linear em formato de probabilidade sigmoide:
- **Técnica de Regularização**: Uma penalidade L2 (Ridge) acoplada sob o fator paramétrico de $C=0.1$.
- **Estratégia de Treinamento e Pesos**: Diante da flagrante disparidade volumétrica onde os pacientes concluintes se sobressaem exponencialmente àqueles que abandonam as medicações de tuberculose, impusemos o parâmetro fundamental de balança `class_weight="balanced"`, dando forte relevo aos indícios da classe minoritária (Abandono) ao traçar os coeficientes.

## Escolha de Threshold e Explicabilidade
Pela própria limitação geométrica, o classificador linear concentrou probabilidades em eixos achatados. Após medições da curva ótima, alocou-se um threshold na casa estatística de **0.56**.

No campo prático, sua **explicabilidade é primorosa**: qualquer auditor da saúde consegue visualizar a fórmula direta, observando peso por peso onde determinada característica como Uso de Drogas ou Histórico de Prisão linearmente tracionou a porcentagem final do risco do paciente.

## Conclusão e Resultados
Como avaliado, esse método sofre forte impacto de restrição perante bases demasiadamente ricas e longínquas, resultando num brando *underfitting* por perder nuances combinadas que uma formulação estritamente em linha e soma falha ao absorver. 

### Resultados Obtidos
Abaixo, os resultados reais observados em cada fase de teste:

| Etapa de Avaliação | Acurácia | Precisão | Recall | F1-Score | ROC-AUC | Threshold Usado |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Treino** (Dados históricos) | $77.1\%$ | $43.0\%$ | $54.8\%$ | $48.2\%$ | **$0.7587$** | $0.56$ |
| **Teste 1** (1ª metade de 2025) | $73.2\%$ | $66.7\%$ | $78.0\%$ | $71.9\%$ | **$0.8133$** | $0.56$ |
| **Teste 2 Final** (2ª metade de 2025) | $77.3\%$ | $82.0\%$ | $86.3\%$ | $84.1\%$ | **$0.8193$** | $0.56$ |

---

### Pontos Positivos
*   **Simplicidade e Interpretabilidade:** Os coeficientes lineares indicam diretamente a direção do risco (ex: histórico de abandono anterior aumenta o risco linearmente).
*   **Extrema Rapidez:** Treinamento executado em poucos segundos.

### Pontos Negativos (Fragilidades)
*   **Underfitting:** O modelo linear assume que a relação entre os dados é puramente somatória, falhando em modelar interações não-lineares complexas de um dataset com 569 mil pacientes.
*   **Sensibilidade a NaNs:** O algoritmo linear exige imputação total dos dados vazios do SINAN. Caso o imputador insira dados incorretos, o erro propaga direto no coeficiente do modelo.
*   **Achatamento das probabilidades brutas:** Tendência a concentrar previsões nas faixas medianas, achatando a precisão real de diagnóstico no mundo real.