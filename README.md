# Projeto de Machine Learning para Previsão de Abandono de Tratamento de Tuberculose

Este projeto foi desenvolvido para alunos de um nanodegree, com o objetivo de fornecer um ambiente prático para o treinamento e teste de modelos de Machine Learning. O desafio é prever a probabilidade de um paciente abandonar o tratamento de tuberculose (LTFU - Loss to Follow-up).

## Estrutura do Projeto

O projeto é dividido em algumas etapas principais, que são executadas em um ambiente Docker para garantir a reprodutibilidade.

1.  **Download dos Dados:** O script `baixar_tuberculose_feather.py` baixa os dados de tuberculose do banco de dados SINAN.
2.  **Preparação dos Dados:** O script `data-prep.py` processa os dados brutos, limpando-os e dividindo-os em três conjuntos: `treino.csv`, `teste1.csv`, e `teste2.csv`.
3.  **Modelagem:** Os alunos usarão os arquivos CSV para treinar e avaliar seus modelos de Machine Learning.

## Pré-requisitos

Para executar este projeto, você precisará ter o Docker e o WSL (Windows Subsystem for Linux) instalados e configurados em sua máquina.

-   **Docker:** [Instruções de instalação](https://docs.docker.com/get-docker/)
-   **WSL:** [Instruções de instalação](https://docs.microsoft.com/en-us/windows/wsl/install)

## Passo a Passo

### 1. Construindo a Imagem Docker

Abra um terminal (de preferência no WSL) e navegue até a pasta raiz do projeto. Em seguida, execute o seguinte comando para construir a imagem Docker:

```bash
docker build -t projeto-tuberculose .
```

### 2. Executando o Container Docker

Após a construção da imagem, execute o seguinte comando para iniciar um container a partir da imagem. Este comando também monta o diretório atual do projeto no diretório `/data` dentro do container, permitindo que os scripts acessem e salvem os arquivos diretamente na sua máquina.

```bash
docker run -it -v "$(pwd):/data" projeto-tuberculose
```

### 3. Executando os Scripts Python

Dentro do container, você pode executar os scripts Python para baixar e preparar os dados.

Primeiro, execute o script para baixar os dados:

```bash
python baixar_tuberculose_feather.py
```

Este script irá baixar os dados e criar o arquivo `tuberculose_unificado.feather`.

Em seguida, execute o script para preparar os dados:

```bash
python data-prep.py
```

Este script irá processar o arquivo `tuberculose_unificado.feather` e gerar os seguintes arquivos CSV:

-   `treino.csv`: Dados para treinar seu modelo.
-   `teste1.csv`: Dados para a primeira rodada de testes do seu modelo.
-   `teste2.csv`: Dados para a segunda rodada de testes, que podem ser usados após incorporar os dados de `teste1.csv` ao conjunto de treinamento.

## Desafio de Modelagem

O principal objetivo deste projeto é construir um modelo de Machine Learning que possa prever o abandono do tratamento de tuberculose (coluna `ltfu`).

1.  **Treinamento Inicial:** Use o arquivo `treino.csv` para treinar seu modelo.
2.  **Primeira Avaliação:** Use o arquivo `teste1.csv` para avaliar o desempenho do seu modelo.
3.  **Re-treinamento e Avaliação Final:** Incorpore os dados de `teste1.csv` ao seu conjunto de treinamento e, em seguida, use `teste2.csv` para uma avaliação final do seu modelo.

## Arquivos Processados

Neste repositório, estão os códigos de donwload e pré-processamento dos dados. Os arquivos resultantes da execução do código você encontra em:

https://drive.google.com/drive/folders/13BOVwEUAK8QolcCXbvhkNtaSci3sECEd?usp=sharing

## Dicionário de Dados

Para entender o significado de cada coluna nos arquivos de dados, consulte a documentação oficial do SINAN na pasta `docs-sinan`.
