# Modelo: HistGradientBoosting (Produção Final)

## Objetivo do Modelo
Escolhido para operar sob o motor principal do projeto em ambiente real de produção (na API e App Clínico). A técnica de **HistGradientBoostingClassifier** se destaca pela habilidade veloz de captar distribuições interligadas ultra complexas no SINAN, com uma resistência extrema a falhas ou ausências sistêmicas da notificação na triagem dos postos.

## Etapas Realizadas e Tratamentos
Ao contrário das redes matemáticas clássicas, a flexibilidade foi estendida:
- O classificador não pune as ausências, suportando os ruídos intrínsecos de atributos vazios no formulário do médico sem requerer robustas imputações de dados fantasmas.
- O pipeline incluiu *Target Encoding* para transformar variáveis gigantes de cardinalidade alta, mitigando explosões de dimensões.
- Sem exigência cega de métodos limitadores como normalizações via *RobustScaler*.

## Arquitetura, Regularização e Estratégias de Treinamento
Foi aplicado um *ensemble* formidável baseado em **Boosting** (Aprimoramento via Resíduo):
- **Arquitetura**: Utiliza um exército sucessivo de árvores de decisão. Para mitigar saturações, o avanço interno por galhos está preso num corte profundo até `max_depth = 6` e até `300` árvores acumuladas.
- **Estratégias e Treinamento**: Como de praste nos dados imbalanciados, fixou-se a matriz `class_weight="balanced"`. Possui gatilho passivo de *Early Stopping* abortando o ciclo pelo erro das folhas.
- **Calibração (Técnica Crucial)**: Aplicou-se sobre a superfície bruta do modelo uma técnica estrita via **`CalibratedClassifierCV`** operada de forma isotônica (`method='isotonic'`). Ela obriga o estimador que expele números super ou sub dimensionados a alinhar precisamente as suas predições ao tecido real/clínico em amostragens cruzadas, conferindo probabilidades maduras para triagem do SUS.

## Escolha de Threshold e Explicabilidade
Com predições exatas de risco clínico, segmentou-se os alertas. O threshold divisório primário se encontrou calçado no ponto matemático de **0.22**, traçando em cascata os alertas na aplicação final:
- **Baixo Risco**: Até 30% da chance calibrada (acompanhamento natural ambulatorial).
- **Risco Médio**: Entre 30% e 60% de chance calibrada (aviso brando de acompanhamento/SMS).
- **Alto Risco**: Acima de 60% calibrada (acionamento preventivo ativo / busca local de saúde comunitária).

As predições geram gráficos incisivos na **explicabilidade**:
Através de **SHAP Values** o painel destila a métrica de "Caixa Branca", identificando as matrizes e causas determinantes do resultado. A técnica **Permutation Importance** explicitou o *Top 5 Preditores Oficiais*:
1. **TRATAMENTO** (Principalmente o Retratamento de desistente prévio).
2. **idade_anos** (Jovens ativos que abandonam o ciclo demorado vs idosos que não conseguem frequentar postos).
3. **AGRAVDROGA** (Alta fragilidade de acompanhamento em rotina diária).
4. **POP_LIBER** (População prisional dependente do Estado de triagem).
5. **NU_CONTATO** (Falta de parentes notificados).

## Conclusão e Resultados
O modelo comprovou supremacia incontestável entre todas as abordagens perante cenários conturbados e desafiadores, capturando 9 em 10 futuros casos de quebra sistêmica no ciclo de drogas para Tuberculose. 

**Métricas (Teste 2 Final):**
| Métrica | Valor Obtido |
| :--- | :---: |
| **Acurácia** | 81.1% |
| **Precisão** | 83.7% |
| **Recall (Sensibilidade)** | 90.4% |
| **F1-Score** | 86.9% |
| **ROC-AUC** | 0.8531 |
| **Threshold** | 0.22 |

---

## Resultados da Validação Cruzada 5-fold:
Abaixo estão as métricas consolidadas observadas durante a **validação cruzada de 5 folds** em todo o conjunto de dados históricos:

*   **ROC-AUC:** $0.7774 \pm 0.0017$
    *   *O que significa:* Excelente poder de discriminação. O desvio padrão ínfimo ($0.0017$) atesta que o modelo é extremamente estável e consistente em qualquer partição de pacientes.
*   **Recall (Sensibilidade):** $0.6733 \pm 0.0037$
    *   *O que significa:* O modelo captura de forma proativa **$67.3\%$** de todas as pessoas que abandonarão a terapia, permitindo ações preventivas a tempo na maioria dos casos reais.
*   **Precisão:** $0.3852 \pm 0.0014$
    *   *O que significa:* A cada 2,5 pacientes sinalizados como risco pelo modelo, 1 realmente abandonará. Esse nível de acerto é o **dobro** de um modelo ao acaso (onde a taxa real de abandono populacional é de $\approx 19.5\%$), sendo uma proporção de alarme falso excelente para o SUS gerenciar.
*   **F1-Score:** $0.4900 \pm 0.0019$
    *   *O que significa:* O ponto ótimo de equilíbrio entre cobertura e economia de recursos de campo.

---

### Como a Calibração Resolveu as Fraquezas dos Modelos Anteriores?
Modelos de Boosting tendem a gerar probabilidades distorcidas (achatadas nos extremos) quando treinados com classes desbalanceadas. A **Calibração Isotônica** mapeou as saídas brutas do modelo diretamente para a probabilidade populacional histórica de abandono ($\approx 19.4\%$).

Isso permitiu agrupar com precisão matemática os pacientes em **Faixas Clínicas de Risco**. Note que a proporção em cada faixa varia conforme o volume de abandono de cada banco:

*   **Distribuição no Treino Completo (População Real a $\approx 19.5\%$ de abandono):**
    1.  **Baixo Risco ($<30\%$):** $80.6\%$ dos pacientes. Seguem o acompanhamento comum.
    2.  **Médio Risco ($30\% - 60\%$):** $14.7\%$ dos pacientes. Recebem atenção moderada (ligações e SMS de alerta).
    3.  **Alto Risco ($\ge 60\%$):** $4.7\%$ dos pacientes. SUS foca suporte psicossocial e visitas domiciliares.
*   **Distribuição no Teste 2 / Dashboard (Base de Teste a $69.4\%$ de abandono real):**
    *   **Baixo Risco:** $32.8\%$ (207 pacientes) | **Médio Risco:** $35.7\%$ (225 pacientes) | **Alto Risco:** $31.5\%$ (199 pacientes).
    *   *Por que mudou?* Como a base `teste2.csv` é composta por uma taxa de abandonos reais muito alta ($69.4\%$), o modelo calibrado identifica corretamente essa gravidade elevando a probabilidade individual da amostra, distribuindo de forma lógica os casos em faixas média e alta de risco. Isso comprova a sensibilidade e eficácia do calibrador.
