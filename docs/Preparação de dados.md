# Preparação de Dados

Este documento descreve as etapas de preparação e processamento dos dados utilizados no projeto de previsão de perda de seguimento (LTFU) em casos de tuberculose.

## Origem dos Dados
Os dados foram originados do SINAN (Sistema de Informação de Agravos de Notificação) e disponibilizados pré-processados no Google Drive do professor. Para treinamento e testes dos modelos, a base foi dividida em três conjuntos:
- **`treino.csv`**: Dados históricos com o maior volume de registros.
- **`teste1.csv`**: Primeira metade dos casos recentes, utilizado para avaliação durante a validação.
- **`teste2.csv`**: Segunda metade dos casos recentes, reservado para o teste de performance final.

## Seleção de Variáveis
Foi aplicada uma política rigorosa para prevenção de *Target Leakage* (Vazamento de Dados). Apenas variáveis e características disponíveis no **momento da notificação inicial** do paciente foram mantidas, removendo exames de acompanhamento futuro que não estariam disponíveis em cenários reais para a predição.

As variáveis selecionadas para o projeto (configuradas no arquivo `pipeline/preditores.py`) são classificadas em:

**Preditores Numéricos:**
- `idade_anos`: Idade do paciente em anos.
- `NU_CONTATO`: Número de contatos registrados na rede de apoio.

**Preditores Categóricos:**
- `CS_SEXO`: Sexo do paciente.
- `CS_RACA`: Raça/Cor.
- `HIV`: Sorologia para HIV.
- `BACILOSC_E`: Baciloscopia de entrada.
- `RAIOX_TORA`: Raio-X de tórax.
- `TRATAMENTO`: Tipo de tratamento (Ex: caso novo, reingresso após abandono).
- `SG_UF_NOT`: UF de notificação.

**Preditores Ordinais:**
- `CS_ESCOL_N`: Nível de escolaridade.

**Preditores Binários:**
- `TRAT_SUPER`: Tratamento supervisionado (DOT).
- `INSTITUCIO`: Institucionalizado.
- `AGRAVAIDS`: Comorbidade - AIDS.
- `AGRAVALCOO`: Uso de álcool.
- `AGRAVDIABE`: Diabetes.
- `AGRAVDOENC`: Doença mental.
- `AGRAVDROGA`: Uso de drogas ilícitas.
- `AGRAVTABAC`: Tabagismo.
- `POP_LIBER`: População privada de liberdade.
- `POP_RUA`: Situação de rua.
- `BENEF_GOV`: Recebe benefício governamental.

## Tratamento de Valores Ausentes e Inconsistentes

1. **Inconsistências e Vazios**:
   - As marcações de formulário "9" (Ignorado) foram logicamente remapeadas para valores nulos (`NaN`).
   - Nos pipelines de machine learning, adotou-se o uso rigoroso de imputações. Para numéricas, foi utilizado o `IterativeImputer`; e para preenchimentos vitais do formato categórico/binário aplicamos `SimpleImputer` com a premissa de maior frequência populacional. Categorias raras (menores que 1%) foram isoladas pela classe unificada `__raro__`.

2. **Conversão de Valores Binários**:
   - Os dados originalmente descritos por "1=Sim, 2=Não, 9=Ignorado", foram padronizados para base matemática real: `1` denota classe Positiva ("Sim") e `0` denota a Negativa ("Não").

3. **Tratamento de Outliers e Escalonamento**:
   - O projeto aplicou o processo de Robust Scaling (`RobustScaler`) em determinados canais, o que ajuda na estabilidade e blindagem da presença exacerbada de valores errantes *outliers* antes do envio à camada neural de algoritmos sensíveis, e codificações como OHE (One-Hot-Encoding) ou Target Encoding para lidar com dimensões altas (como as UFs).

4. **Salvamento dos Dados Processados**:
   - Todo fluxo de pré-processamento consolida em arquivos eficientes disponibilizados na raiz do repositório como o `tuberculose_unificado.feather` ou nos splits formatados `treino.csv`, `teste1.csv` e `teste2.csv`.
