# Como Executar o Projeto — Passo a Passo com Docker

Guia completo para configurar o ambiente e rodar o projeto do zero utilizando Docker.

🔗 Voltar para o **[Guia Principal e Visão Geral do Projeto](../README.md)**

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

## Passo 3 — Dados do Professor (Pré-processados)

> [!NOTE]
> Os dados disponibilizados pelo professor (`treino.csv`, `teste1.csv`, `teste2.csv` e `tuberculose_unificado.feather`) já foram baixados e posicionados na raiz do projeto. Portanto, os scripts de download (`baixar_tuberculose_feather.py`) e preparação (`data-prep.py`) **não precisam ser executados**.

---

## Passo 4 — Treinar os Modelos de Experimento

Treine os modelos baseline de comparação dentro do container:

```bash
python scripts/regressao_logistica/treino_regressao.py
python scripts/rede_neural/treino_rede_neural.py
```

**O que faz:** Salva métricas de avaliação e gráficos em `resultados/regressao_logistica/` e `resultados/rede_neural/`.

---

## Passo 5 — Treinar e Calibrar o Modelo Final de Produção

Execute o script de produção para treinar o classificador final de HistGradientBoosting:

```bash
python pipeline/pipeline_final.py
```

**O que faz:** Salva o modelo calibrado final em `pipeline/modelo/`.

---

## Passo 6 — Rodar a Análise de Features (Explicabilidade / SHAP)

```bash
python scripts/analise_features.py
```

**O que faz:** Gera validação cruzada 5-fold, permutação de importância, gráficos de valores SHAP (beeswarm e barras) e curva de calibração em `resultados/analise/`.

---

## Passo 7 — Gerar o CSV para o Dashboard da Turma

Gere a planilha de predições do modelo final para carregar no dashboard dinâmico:

```bash
python gerar_csv.py
```

**O que faz:** Cria ou calcula e sobrescreve o arquivo `resultados_modelo.csv` na raiz do projeto com as predições do modelo final de produção.

---

## Passo 8 — Subir o Backend do App Médico

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

## Passo 9 — Abrir as Interfaces no Navegador

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
python scripts/regressao_logistica/treino_regressao.py
python scripts/rede_neural/treino_rede_neural.py
python pipeline/pipeline_final.py
python scripts/analise_features.py
python gerar_csv.py                           # Gerar CSV para o dashboard (Modelo Final)

# Iniciar o backend (dentro do Container)
uvicorn app.backend.main:app --host 0.0.0.0 --port 8000
```

---

# Estrutura do Projeto

Consulte a estrutura completa e suas explicações aprofundadas no README raiz ou através dos novos documentos elaborados em `/docs/` para entendimento algorítmico do fluxo.



