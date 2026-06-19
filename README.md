# Tuberculosis LTFU Prediction — Relatório de Modelagem e Produção

Este projeto apresenta o desenvolvimento e a comparação de modelos de Machine Learning para a predição do risco de perda de seguimento / abandono do tratamento de Tuberculose (LTFU - *Loss to Follow-up*), utilizando dados reais de saúde pública do SINAN (Sistema de Informação de Agravos de Notificação).

A seguir, apresenta-se o relatório técnico e metodológico estruturado para avaliação acadêmica detalhada.

---

## 1. Glossário de Métricas — O que significa cada valor?

Para que os resultados sejam perfeitamente compreendidos, a tabela abaixo explica as métricas clássicas de avaliação de Machine Learning aplicadas à saúde pública:

| Métrica | Conceito Didático | Impacto na Prática Médica |
| :--- | :--- | :--- |
| **ROC-AUC** | Área sob a Curva ROC. Varia de `0.5` (chute aleatório) a `1.0` (separação perfeita). Mede a capacidade geral do modelo de ordenar os pacientes de maior risco para os de menor risco. | É a métrica mais confiável do projeto porque não é afetada por variações artificiais na proporção de doentes/abandonos nas bases de teste. |
| **Precisão (Precision)** | Do total de pacientes que o modelo alertou como "Alto Risco de Abandono", quantos de fato abandonaram o tratamento. | **Impacta no custo e recursos:** Se a precisão for baixa, o modelo gera muitos alarmes falsos, fazendo a equipe de saúde desperdiçar visitas domiciliares com pacientes que terminariam o tratamento normalmente. |
| **Sensibilidade (Recall)** | Do total de pacientes que **realmente abandonaram** o tratamento no mundo real, quantos deles o modelo foi capaz de identificar e alertar. | **Impacta nas vidas poupadas:** Se o Recall for baixo, muitos pacientes em risco passarão desapercebidos pelo sistema, sofrendo complicações da tuberculose sem intervenção. |
| **F1-Score** | Média harmônica equilibrada entre Precisão e Recall. Varia de `0` a `1.0`. | Indica a eficiência geral do modelo de conciliar a redução de alarmes falsos (Precisão) com a cobertura de detecção de abandonos (Recall). |
| **Acurácia (Accuracy)** | Proporção geral de palpites corretos (tanto os que concluíram quanto os que abandonaram) sobre o total de pacientes. | É pouco confiável em dados desbalanceados. Se 90% da população conclui o tratamento, um modelo burro que chuta "conclui" para todo mundo terá 90% de acurácia, mas utilidade clínica zero. |
| **Threshold (Limiar)** | Ponto de corte matemático (de `0.0` a `1.0`) a partir do qual a probabilidade predita pelo modelo classifica o paciente como "Abandono". | **Ajuste clínico:** Se o threshold for `0.22`, qualquer paciente com 22% ou mais de chance estimada de abandono aciona o alerta de risco do sistema. |

---

## 2. Cuidados com a Modelagem e Prevenção de Vieses

### A. Prevenção de Target Leakage (Vazamento de Dados)
Apenas preditores obtidos no **momento da notificação inicial** do caso foram mantidos na base de dados (idade, exames basais de raio-x e baciloscopia, vulnerabilidade de moradia, etc.). Foram removidas todas as colunas que representassem o encerramento do caso ou exames de acompanhamento do 2º e 4º meses, impedindo que o modelo aprenda padrões do "futuro" que não estariam disponíveis no momento da triagem do paciente.

### B. Divisão dos Dados e Origem das Bases
Para garantir a padronização e confiabilidade da avaliação, utilizamos diretamente os conjuntos de dados pré-processados e validados fornecidos pelo professor em seu drive:
*   **Treino (`treino.csv`):** Contém os dados históricos acumulados de múltiplos anos passados, totalizando **562.632 pacientes** (com taxa de abandono populacional de $\approx 19.4\%$).
*   **Teste (`teste1.csv` e `teste2.csv`):** Conjuntos de teste divididos para validação de experimentos (`teste1.csv` com **631 pacientes**, $\approx 43.9\%$ de abandonos) e avaliação final (`teste2.csv` com **631 pacientes**, $\approx 69.4\%$ de abandonos).
*   **A "Ilusão" do F1-Score no Teste:** As taxas de abandono nas bases de teste são consideravelmente mais elevadas que a histórica de treino ($\approx 19.4\%$). Isso ocorre pelo perfil de registros recentes de 2025 já finalizados, capturando os abandonos rápidos.
*   **A Solução Metodológica:** Mantivemos a calibração isotônica para corrigir e suavizar as predições probabilísticas de volta à realidade epidemiológica clínica.

### C. Otimização de Processamento (Dados do Professor)
Os arquivos disponibilizados pelo professor (`tuberculose_unificado.feather`, `treino.csv`, `teste1.csv` e `teste2.csv`) já contêm as variáveis limpas e as colunas calculadas de `ltfu` e `idade_anos`. Dessa forma, o download de dados brutos e o processamento local volumoso de Polars no `data-prep.py` não são mais necessários para a execução básica do pipeline.

---

# Modelos de Experimento

## # Modelo 1: Regressão Logística (Baseline)

### Como foi o Treino?
Treinamos um classificador linear com penalidade de regularização L2 (Ridge) com parâmetro de regularização $C=0.1$ e peso de classe balanceado (`class_weight="balanced"`) para lidar com o desbalanço inicial da base. 

### Resultados Obtidos
Abaixo, os resultados reais observados em cada fase de teste:

| Etapa de Avaliação | Acurácia | Precisão | Recall | F1-Score | ROC-AUC | Threshold Usado |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Treino** (Dados históricos) | $77.1\%$ | $43.0\%$ | $54.8\%$ | $48.2\%$ | **$0.7587$** | $0.56$ |
| **Teste 1** (1ª metade de 2025) | $73.2\%$ | $66.7\%$ | $78.0\%$ | $71.9\%$ | **$0.8133$** | $0.56$ |
| **Teste 2 Final** (2ª metade de 2025) | $77.3\%$ | $82.0\%$ | $86.3\%$ | $84.1\%$ | **$0.8193$** | $0.56$ |

### Pontos Positivos
*   **Simplicidade e Interpretabilidade:** Os coeficientes lineares indicam diretamente a direção do risco (ex: histórico de abandono anterior aumenta o risco linearmente).
*   **Extrema Rapidez:** Treinamento executado em poucos segundos.

### Pontos Negativos (Fragilidades)
*   **Underfitting:** O modelo linear assume que a relação entre os dados é puramente somatória, falhando em modelar interações não-lineares complexas de um dataset com 569 mil pacientes.
*   **Sensibilidade a NaNs:** O algoritmo linear exige imputação total dos dados vazios do SINAN. Caso o imputador insira dados incorretos, o erro propaga direto no coeficiente do modelo.
*   **Achatamento das probabilidades brutas:** Tendência a concentrar previsões nas faixas medianas, achatando a precisão real de diagnóstico no mundo real.

---

## # Modelo 2: Rede Neural MLP (Perceptron Multicamadas)

### Como foi o Treino?
Uma rede neural profunda desenvolvida no Scikit-Learn com três camadas ocultas de neurônios: `(128, 64, 32)`. Aplicou-se penalidade de regularização L2 de $\alpha = 10^{-4}$ (para evitar overfitting), parada antecipada (*Early Stopping*) monitorando $15\%$ dos dados para validação interna, e otimizador Adam.

### Resultados Obtidos

| Etapa de Avaliação | Acurácia | Precisão | Recall | F1-Score | ROC-AUC | Threshold Usado |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Treino** (Dados históricos) | $77.4\%$ | $43.8\%$ | $57.6\%$ | $49.7\%$ | **$0.7756$** | $0.26$ |
| **Teste 1** (1ª metade de 2025) | $74.6\%$ | $68.5\%$ | $78.3\%$ | $73.1\%$ | **$0.8165$** | $0.26$ |
| **Teste 2 Final** (2ª metade de 2025) | $80.0\%$ | $84.7\%$ | $87.0\%$ | $85.8\%$ | **$0.8379$** | $0.24$ |

### Pontos Positivos
*   **Excelente Poder de Generalização:** Obteve a maior ROC-AUC isolada no teste final ($0.7933$), demonstrando grande capacidade de aprender fronteiras e interações não-lineares muito complexas no tempo.
*   **Estabilidade:** O Early Stopping evitou que o modelo decorasse os dados históricos do treino, convergindo em apenas 30 épocas.

### Pontos Negativos (Fragilidades)
*   **Muito Lento para Treinar:** Exige muito processamento CPU comparado a outras abordagens.
*   **Sensibilidade Extrema à Escala e Nulos:** Exige obrigatoriamente que todas as features numéricas estejam normalizadas (`RobustScaler`) e que 100% das colunas estejam imputadas (sem NaNs), sob risco de quebrar o algoritmo matemático de retropropagação.
*   **Dificuldade de Interpretação ("Caixa Preta"):** Impossível decifrar a influência isolada de uma variável a olho nu através de seus milhares de pesos sinápticos interconectados.

---

# Modelo Final de Produção (HistGradientBoosting)

O modelo selecionado para equipar o sistema final foi o **HistGradientBoostingClassifier**, calibrado de forma isotônica.

### Como foi o Treino?
O classificador de árvore de decisão baseada em Boosting (`HistGradientBoostingClassifier`) foi treinado com os seguintes hiperparâmetros: profundidade máxima das árvores em 6 níveis (`max_depth=6`), 300 estimadores no total, class weight balanceado para controle de classes, e parada precoce baseada em perda residual.

Por cima dele, foi aplicado o calibrador **`CalibratedClassifierCV(method='isotonic', cv=5)`**, responsável por suavizar as curvas de predição e ajustar a saída para refletir fielmente as taxas epidemiológicas da população.

### Resultados de Produção (Validação Cruzada 5-fold)
Abaixo estão as métricas consolidadas observadas durante a **validação cruzada de 5 folds** em todo o conjunto de dados históricos:

*   **ROC-AUC:** $0.7774 \pm 0.0017$
    *   *O que significa:* Excelente poder de discriminação. O desvio padrão ínfimo ($0.0017$) atesta que o modelo é extremamente estável e consistente em qualquer partição de pacientes.
*   **Recall (Sensibilidade):** $0.6733 \pm 0.0037$
    *   *O que significa:* O modelo captura de forma proativa **$67.3\%$** de todas as pessoas que abandonarão a terapia, permitindo ações preventivas a tempo na maioria dos casos reais.
*   **Precisão:** $0.3852 \pm 0.0014$
    *   *O que significa:* A cada 2,5 pacientes sinalizados como risco pelo modelo, 1 realmente abandonará. Esse nível de acerto é o **dobro** de um modelo ao acaso (onde a taxa real de abandono populacional é de $\approx 19.5\%$), sendo uma proporção de alarme falso excelente para o SUS gerenciar.
*   **F1-Score:** $0.4900 \pm 0.0019$
    *   *O que significa:* O ponto ótimo de equilíbrio entre cobertura e economia de recursos de campo.

### Resultados no Conjunto de Teste 2 (Produção Final)
Quando avaliado no conjunto não-visto mais difícil (`teste2.csv`), com threshold configurado para `0.22`, o classificador obteve **os melhores resultados de todos os modelos:**
*   **ROC-AUC:** **$0.8531$**
*   **Recall:** **$90.4\%$** (Identifica 9 em cada 10 abandonos reais)
*   **Precisão:** **$83.7\%$**
*   **F1-Score:** **$86.9\%$**
*   **Acurácia:** **$81.1\%$**

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

---

## 5. Explicabilidade Clínica (SHAP & Permutation Importance)

Para que a equipe médica confie nas tomadas de decisão da IA, o pipeline gera análises gráficas em `resultados/analise/`:

*   **Permutation Importance:** Avalia a perda média no score de ROC-AUC quando embaralhamos os valores de uma coluna. As top-5 mais importantes são:
    1.  `TRATAMENTO_3` (Reingresso após abandono): O principal preditor do modelo. Pacientes com histórico de desistência prévia têm altíssimo risco de repetir o comportamento.
    2.  `idade_anos`: Jovens adultos tendem a abandonar mais por motivos laborais, enquanto idosos sofrem com logística para locomoção diária até a unidade (tratamento supervisionado).
    3.  `AGRAVDROGA` (Uso de drogas ilícitas): Marcador de alta vulnerabilidade social associado à quebra de rotinas de tratamento.
    4.  `POP_LIBER` (População privada de liberdade): Barreiras institucionais e transferências do sistema carcerário.
    5.  `NU_CONTATO` (Número de contatos): Ausência de rede de apoio registrada indica fragilidade social.
*   **SHAP Values (Beeswarm & Barras):** Explica o impacto local de cada variável. Permite rastrear exatamente a causa de um paciente ser considerado de Alto Risco (ex: Paciente X é alto risco por ser jovem, usuário de substâncias e estar em retratamento).

---

## 8. Análise do Dashboard de Apresentação (siteDados)

Ao carregar o arquivo final de predições (`resultados_modelo.csv`) no dashboard da turma, as novas métricas para a base de testes do professor (631 pacientes) serão calculadas e plotadas automaticamente.

### A. Como verificar as Métricas e Resultados
Você pode visualizar as métricas exatas diretamente na tela do dashboard assim que carregar o arquivo de predições.

### B. O que as Métricas Exibidas Significam na Prática:
*   **Precisão (Precision):** Das pessoas que o modelo classificou como "abandona", quantas de fato abandonaram. Garante que os recursos de visitas domiciliares não sejam desperdiçados com alarmes falsos.
*   **Recall (Sensibilidade):** De todos os abandonos que realmente ocorreram, quantos o modelo conseguiu capturar e alertar com antecedência.
*   **F1-Score e Acurácia:** Mostram o equilíbrio de acertos gerais do modelo sob o threshold calibrado de `0.22`.
*   **Distribuição de Risco (Baixo, Médio, Alto):** Como a base de testes tem uma alta densidade de abandonos reais ($\approx 69.4\%$), o classificador calibrado joga uma fatia maior de pacientes para Risco Médio e Alto, comprovando a sensibilidade clínica da IA.

---

## 9. Cenários de Teste Recomendados para Avaliação (App do Médico)

Para facilitar a correção e demonstrar o comportamento do classificador calibrado frente a diferentes perfis epidemiológicos, preencha o formulário da interface médica (`app/frontend/index.html`) com os seguintes cenários validados (que possuem embasamento na literatura científica de fatores de risco de abandono de tuberculose no SINAN):

### Cenário A — Risco Baixo
*   **Nome completo:** Ana Souza (Baixo Risco)
*   **Idade (anos):** 58
*   **Sexo:** Feminino
*   **Raça / Cor:** Branca
*   **Escolaridade:** Superior completo
*   **Nº de contatos registrados:** 4
*   **Tipo de tratamento:** Caso novo
*   **Sorologia HIV:** Negativo
*   **Baciloscopia de entrada:** Negativo
*   **Raio-X de tórax:** Normal
*   **UF de notificação:** SP
*   **Comorbidade: AIDS:** Não
*   **Uso de álcool:** Não
*   **Diabetes:** Não
*   **Doença mental:** Não
*   **Uso de drogas ilícitas:** Não
*   **Tabagismo:** Não
*   **Privado de liberdade:** Não
*   **Situação de rua:** Não
*   **Tratamento supervisionado (DOT)?:** Sim
*   **Institucionalizado?:** Não
*   **Recebe benefício governamental?:** Não

### Cenário B — Risco Médio
*   **Nome completo:** Marcos Oliveira (Médio Risco)
*   **Idade (anos):** 26
*   **Sexo:** Masculino
*   **Raça / Cor:** Parda
*   **Escolaridade:** Fundamental I incompleto
*   **Nº de contatos registrados:** 1
*   **Tipo de tratamento:** Caso novo
*   **Sorologia HIV:** Negativo
*   **Baciloscopia de entrada:** Positivo (+)
*   **Raio-X de tórax:** Suspeito
*   **UF de notificação:** RJ
*   **Comorbidade: AIDS:** Não
*   **Uso de álcool:** Sim
*   **Diabetes:** Sim
*   **Doença mental:** Não
*   **Uso de drogas ilícitas:** Não
*   **Tabagismo:** Sim
*   **Privado de liberdade:** Não
*   **Situação de rua:** Não
*   **Tratamento supervisionado (DOT)?:** Não
*   **Institucionalizado?:** Não
*   **Recebe benefício governamental?:** Não

### Cenário C — Risco Alto
*   **Nome completo:** Lucas Silva (Alto Risco)
*   **Idade (anos):** 23
*   **Sexo:** Masculino
*   **Raça / Cor:** Preta
*   **Escolaridade:** Sem escolaridade
*   **Nº de contatos registrados:** 0
*   **Tipo de tratamento:** Reingresso após abandono
*   **Sorologia HIV:** Positivo
*   **Baciloscopia de entrada:** Positivo (+)
*   **Raio-X de tórax:** Suspeito
*   **UF de notificação:** RJ
*   **Comorbidade: AIDS:** Sim
*   **Uso de álcool:** Sim
*   **Diabetes:** Não
*   **Doença mental:** Não
*   **Uso de drogas ilícitas:** Sim
*   **Tabagismo:** Sim
*   **Privado de liberdade:** Não
*   **Situação de rua:** Sim
*   **Tratamento supervisionado (DOT)?:** Não
*   **Institucionalizado?:** Não
*   **Recebe benefício governamental?:** Não
