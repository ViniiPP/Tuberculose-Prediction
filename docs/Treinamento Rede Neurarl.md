# Modelo: Rede Neural (MLP)

## Objetivo do Modelo
A Rede Neural do tipo Multilayer Perceptron (MLP) foi adotada neste projeto como forma de explorar até onde a complexidade de redes profundas consegue rastrear padrões sutis e não-lineares, superando arquiteturas simplistas na tentativa de apontar pacientes sob maior risco de abandono do tratamento.

## Etapas Realizadas e Tratamentos
Trabalhar com Redes Neurais requereu um pipeline matemático perfeitamente selado:
- Imputação mandante total (100% de preenchimento dos NaNs com `SimpleImputer` ou `IterativeImputer`), porque funções de ativação e backpropagation falham diante de valores vazios.
- Foram tratadas todas as distorções em grandeza (Escala). Usou-se `RobustScaler` assegurando o esmagamento simétrico dos picos, blindando o gradiente durante o treinamento.

## Arquitetura
Implementamos um classificador do Scikit-Learn composto por **três camadas ocultas consecutivas**, com a respectiva quantidade de neurônios: `(128, 64, 32)`. O decaimento de neurônios agrupa progressivamente as características (features) até o canal final de decisão.

## Técnicas de Regularização e Estratégias de Treinamento
Para precaver as camadas ocultas de viciarem exclusivamente no volume de anos passados e garantindo um generalismo superior:
- **Regularização**: L2 imposta com uma penalização de $\alpha = 10^{-4}$.
- **Otimizador**: Adam para atualização estocástica de alta responsividade de gradientes.
- **Estratégia Anti-overfitting**: Validação isolada de 15% dos dados, acompanhada do critério *Early Stopping* (que intercepta a rede por volta de sua 30ª época antes de superajustar ao conjunto de treino).

## Escolha de Threshold e Explicabilidade
O ponto de corte (threshold) eleito após validação oscilou na casa otimizada de **0.24**, potencializando o sensível F1-Score do sistema de alertas.

Como uma desvantagem clássica, os modelos complexos de múltiplas camadas denotam em sua **explicabilidade** uma severa opacidade "Caixa Preta". Dificultando aos médicos ler exatamente de qual neurônio e ativação específica um risco de um indivíduo provém.

## Conclusão e Resultados
Sendo o modelo mais oneroso em infraestrutura de treinamento, sua performance no teste final não-visto foi brilhante em discriminação genérica.

### Resultados Obtidos

| Etapa de Avaliação | Acurácia | Precisão | Recall | F1-Score | ROC-AUC | Threshold Usado |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Treino** (Dados históricos) | $77.4\%$ | $43.8\%$ | $57.6\%$ | $49.7\%$ | **$0.7756$** | $0.26$ |
| **Teste 1** (1ª metade de 2025) | $74.6\%$ | $68.5\%$ | $78.3\%$ | $73.1\%$ | **$0.8165$** | $0.26$ |
| **Teste 2 Final** (2ª metade de 2025) | $80.0\%$ | $84.7\%$ | $87.0\%$ | $85.8\%$ | **$0.8379$** | $0.24$ |

---

### Pontos Positivos
*   **Excelente Poder de Generalização:** Obteve a maior ROC-AUC isolada no teste final ($0.7933$), demonstrando grande capacidade de aprender fronteiras e interações não-lineares muito complexas no tempo.
*   **Estabilidade:** O Early Stopping evitou que o modelo decorasse os dados históricos do treino, convergindo em apenas 30 épocas.

### Pontos Negativos (Fragilidades)
*   **Muito Lento para Treinar:** Exige muito processamento CPU comparado a outras abordagens.
*   **Sensibilidade Extrema à Escala e Nulos:** Exige obrigatoriamente que todas as features numéricas estejam normalizadas (`RobustScaler`) e que 100% das colunas estejam imputadas (sem NaNs), sob risco de quebrar o algoritmo matemático de retropropagação.
*   **Dificuldade de Interpretação ("Caixa Preta"):** Impossível decifrar a influência isolada de uma variável a olho nu através de seus milhares de pesos sinápticos interconectados.