# Como Executar o Projeto — Passo a Passo com Docker

Guia completo para configurar o ambiente e rodar o projeto do zero utilizando Docker.

---

## Passo 1 — Construir a Imagem Docker

Abra o terminal na pasta raiz do projeto no Windows (PowerShell) e execute o comando abaixo para construir a imagem Docker:

```bash
docker build -t projeto-tuberculose .
```

---

## Passo 2 — Iniciar o Container Docker

Inicie o container montando a pasta local do projeto como um volume e expondo a porta `8000` (necessária para rodar o backend da API sem conflito de versão de bibliotecas com o host):

**No Windows (PowerShell):**
```powershell
docker run -it -p 8000:8000 -v ${PWD}:/data -w /data projeto-tuberculose
```

**No Windows (CMD):**
```cmd
docker run -it -p 8000:8000 -v %cd%:/data -w /data projeto-tuberculose
```

**No Windows (Git Bash):**
```bash
MSYS_NO_PATHCONV=1 docker run -it -p 8000:8000 -v "/c/caminho/completo/do/seu/projeto:/data" -w /data projeto-tuberculose
```
*(Nota: No Git Bash, substitua `/c/caminho/completo/do/seu/projeto` pelo caminho absoluto da pasta do seu projeto na sua máquina).*

**No Linux / macOS:**
```bash
docker run -it -p 8000:8000 -v $(pwd):/data -w /data projeto-tuberculose
```

*Nota: Mantenha esse container aberto. Todos os comandos seguintes (passos 3 a 10) serão executados **dentro** deste container.*

---

## Passo 3 — Baixar e Unificar os Dados do SINAN (Se necessário)

Se você ainda não tiver o arquivo `tuberculose_unificado.feather` gerado na raiz:

```bash
python baixar_tuberculose_feather.py
```

---

## Passo 4 — Preparar e Dividir os Dados (Fatiamento Temporal)

Execute o script de preparação para filtrar a base de dados e criar as partições de treino e teste:

```bash
python data-prep.py
```

**O que faz:** Processa os dados de forma otimizada com Polars (Lazy & Streaming) e cria os arquivos `treino.csv`, `teste1.csv` e `teste2.csv` na raiz do projeto.

---

## Passo 5 — Treinar os Modelos de Experimento

Treine os modelos baseline de comparação dentro do container:

```bash
python scripts/regressao_logistica/treino_regressao.py
python scripts/rede_neural/treino_rede_neural.py
```

**O que faz:** Salva métricas de avaliação e gráficos em `resultados/regressao_logistica/` e `resultados/rede_neural/`.

---

## Passo 6 — Treinar e Calibrar o Modelo Final de Produção

Execute o script de produção para treinar o classificador final de HistGradientBoosting:

```bash
python pipeline/pipeline_final.py
```

**O que faz:** Salva o modelo calibrado final em `pipeline/modelo/`.

---

## Passo 7 — Rodar a Análise de Features (Explicabilidade / SHAP)

```bash
python scripts/analise_features.py
```

**O que faz:** Gera validação cruzada 5-fold, permutação de importância, gráficos de valores SHAP (beeswarm e barras) e curva de calibração em `resultados/analise/`.

---

## Passo 8 — Gerar o CSV para o Dashboard da Turma

Gere a planilha de predições que será carregada no dashboard dinâmico:

```bash
python gerar_csv.py
```

**O que faz:** Cria o arquivo `resultados_modelo.csv` com threshold de classificação ajustado para `0.26`.

---

## Passo 10 — Subir o Backend do App Médico

> [!TIP]
> **RECOMENDADO:** Para evitar erros de versão das bibliotecas Python (como conflitos no `scikit-learn` entre o Docker e o Windows local), o backend deve ser executado **dentro do Docker**.

### Método Recomendado — Executando dentro do Docker

Para rodar o backend dentro do Docker, você precisa expor a porta `8000` na hora de iniciar o container:

1. Se você já tem um container rodando, digite `exit` para sair dele.
2. Inicie o container novamente expondo a porta `8000` (utilize o comando adequado para o seu terminal):
   
   **No Windows (Git Bash):**
   ```bash
   MSYS_NO_PATHCONV=1 docker run -it -p 8000:8000 -v "/c/Users/Vinip/Desktop/projetoIA/tuberculosis-ltfu-prediction:/data" -w /data projeto-tuberculose
   ```
   **No Windows (PowerShell):**
   ```powershell
   docker run -it -p 8000:8000 -v ${PWD}:/data -w /data projeto-tuberculose
   ```

3. Dentro do terminal do Docker que se abriu, inicie o servidor:
   ```bash
   uvicorn app.backend.main:app --host 0.0.0.0 --port 8000
   ```

---

### Método Alternativo — Executando fora do Docker (no Windows local)

Se você preferir rodar no Windows utilizando sua `.venv` local (e as versões de bibliotecas forem compatíveis), abra um **novo terminal do Windows** na pasta raiz do projeto e execute:

**No Windows (Git Bash):**
```bash
./.venv/Scripts/python.exe -m uvicorn app.backend.main:app --reload --port 8000
```

**No Windows (PowerShell):**
```powershell
.\.venv\Scripts\python.exe -m uvicorn app.backend.main:app --reload --port 8000
```

---

## Passo 10 — Abrir as Interfaces no Navegador

| Interface | Arquivo para abrir |
|---|---|
| App do Médico | `app/frontend/index.html` |
| Dashboard de Apresentação (turma) | `siteDados/frontend/index.html` |

* No **dashboard**, arraste e solte o arquivo `resultados_modelo.csv` gerado na raiz.
* No **app médico**, utilize o formulário para enviar dados de pacientes ao backend e obter a predição de risco em tempo real.

---

## Resumo dos Comandos no Container

```bash
# Construir e rodar (no Host Windows)
docker build -t projeto-tuberculose .

# Iniciar o container (PowerShell)
docker run -it -p 8000:8000 -v ${PWD}:/data -w /data projeto-tuberculose

# Iniciar o container (Git Bash Windows)
MSYS_NO_PATHCONV=1 docker run -it -p 8000:8000 -v "/c/Users/Vinip/Desktop/projetoIA/tuberculosis-ltfu-prediction:/data" -w /data projeto-tuberculose

# Comandos de treino e execução (dentro do Container)
python data-prep.py
python scripts/regressao_logistica/treino_regressao.py
python scripts/rede_neural/treino_rede_neural.py
python pipeline/pipeline_final.py
python scripts/analise_features.py
python gerar_csv.py

# Iniciar o backend (dentro do Container)
uvicorn app.backend.main:app --host 0.0.0.0 --port 8000
```

---

---

# Estrutura do Projeto

Descrição de cada arquivo e pasta na raiz do projeto.

---

## Arquivos na raiz

| Arquivo | Descrição |
|---|---|
| `treino.csv` | Conjunto de treino principal — dados históricos do SINAN limpos e filtrados pelo `data-prep.py` |
| `teste1.csv` | Conjunto de validação — usado para avaliar os modelos durante o desenvolvimento |
| `teste2.csv` | Conjunto de teste final — avaliação definitiva do modelo; só é visto no passo de retreino |
| `gerar_csv.py` | Script que usa o modelo de produção para gerar o `resultados_modelo.csv` do dashboard |
| `data-prep.py` | Script do professor que limpa, filtra e divide os dados do SINAN nos 3 CSVs |
| `baixar_tuberculose_feather.py` | Script auxiliar para baixar os dados brutos do SINAN em formato feather |
| `resultados_modelo.csv` | Arquivo gerado pelo `gerar_csv.py` — saída do modelo sobre o teste2, usado no dashboard |
| `IA.md` | Documento de briefing do projeto — objetivos, regras e escopo definidos pelo professor |
| `README.md` | README principal do projeto (visão geral) |
| `.gitignore` | Arquivos ignorados pelo Git (dados brutos, modelos serializados, `.venv`) |
| `dockerfile` | Configuração Docker para containerização (criado pelo professor, não usado localmente) |

---

## Pastas na raiz

### `pipeline/`
Módulo central do projeto — tudo que envolve pré-processamento e produção.

| Arquivo | O que faz |
|---|---|
| `preditores.py` | **Ponto único de verdade** das variáveis. Define quais colunas entram no modelo (21 preditores), o nome da variável-alvo e os thresholds de risco (30% = baixo, 60% = alto) |
| `preprocessor.py` | Transforma os dados brutos do SINAN em features numéricas para o modelo. Cuida de: encoding binário (1=Sim, 2=Não), imputação de valores faltantes, escalonamento, OHE e TargetEncoder para UF |
| `pipeline_final.py` | Treina o modelo de produção com todos os dados. Compara RandomForest vs HistGradientBoosting por cross-validation, usa o vencedor com calibração de probabilidades (`CalibratedClassifierCV`). Também expõe a função `predict(dados)` usada pelo backend |
| `__init__.py` | Marca a pasta como módulo Python para facilitar os imports |
| `modelo/` | Pasta gerada após rodar `pipeline_final.py`. Contém os arquivos `.joblib` do preprocessador e do modelo treinado |

---

### `scripts/`
Scripts de experimento e análise — **não são usados em produção**, servem para desenvolvimento, comparação e apresentação dos resultados.

| Arquivo/Pasta | O que faz |
|---|---|
| `regressao_logistica/treino_regressao.py` | Treina e avalia a **Regressão Logística** como modelo baseline. Usa regularização L2 (`C=0.1`), `class_weight="balanced"` e busca o threshold ideal por F1-score. Gera curvas ROC, matrizes de confusão e métricas em `resultados/regressao_logistica/` |
| `rede_neural/treino_rede_neural.py` | Treina e avalia a **Rede Neural (MLPClassifier)** com camadas `(128, 64, 32)`, regularização L2 e early stopping. Segue o mesmo fluxo do baseline: avalia em teste1, retreina, avalia em teste2. Gera curvas de aprendizado e métricas em `resultados/rede_neural/` |
| `analise_features.py` | Gera análises avançadas sobre o modelo final: **SHAP values** (importância e direção de cada feature), **Permutation Importance**, **validação cruzada 5-fold** e **curva de calibração**. Todos os gráficos vão para `resultados/analise/` |

---

### `app/`
Interface clínica para uso do médico em consulta.

| Arquivo/Pasta | O que faz |
|---|---|
| `frontend/index.html` | Página da interface médica. TailwindCSS + Lucide Icons. Formulário com 4 seções: dados do paciente, dados clínicos, agravidades e acompanhamento |
| `frontend/app.js` | Lógica da interface médica. Coleta dados do formulário, envia para o backend (`/predict`), exibe o resultado com gauge animado e salva histórico no navegador (`localStorage`) |
| `backend/main.py` | API FastAPI. Expõe o endpoint `POST /predict` que recebe os dados do paciente e retorna probabilidade e nível de risco usando o modelo de produção |

---

### `siteDados/`
Dashboard de apresentação para a turma.

| Arquivo | O que faz |
|---|---|
| `frontend/index.html` | Página do dashboard. TailwindCSS + Lucide Icons. Zona de drag-and-drop para o CSV |
| `frontend/app.js` | Carrega o CSV, calcula métricas técnicas em tempo real (Precisão, Recall, F1, Acurácia) e renderiza: KPIs, distribuição de risco (pizza + barras), histograma de probabilidades, acertos por nível de risco, real vs previsto e tabela paginada |

---

### `resultados/`
Saídas geradas pelos scripts de treino e análise.

| Subpasta | Conteúdo |
|---|---|
| `regressao_logistica/` | Métricas CSV, curvas ROC e matrizes de confusão da regressão logística |
| `rede_neural/` | Métricas CSV, curvas de aprendizado, ROC e matrizes da rede neural |
| `analise/` | Gerada após `analise_features.py`: SHAP beeswarm, SHAP barras, permutation importance, curva de calibração |

---

### `docs-sinan/`
Documentação oficial do SINAN fornecida pelo professor:
- Caderno de análise da tuberculose
- Dicionário de dados
- Fichas de notificação e acompanhamento
- Instrucional de preenchimento

---

### `.venv/`
Ambiente virtual Python local. Não é versionado pelo Git.


