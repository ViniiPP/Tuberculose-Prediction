# Comandos para Iniciar o Projeto (PC Vini)

Guia rápido com todos os comandos ordenados do zero para rodar o projeto no seu computador utilizando o **Git Bash**.

---

## 1. No Host (No Git Bash do Windows)

### Passo 1: Construir a Imagem Docker (Só se alterar o Dockerfile)
```bash
docker build -t projeto-tuberculose .
```

### Passo 2: Iniciar o Container Docker (Com porta 8000 e correção de caminho)
> [!IMPORTANT]
> Iniciamos o container já liberando a porta `8000` para que possamos rodar o backend dentro do Docker e evitar conflito de versão de bibliotecas (como o scikit-learn) com o Windows local.

```bash
MSYS_NO_PATHCONV=1 docker run -it -p 8000:8000 -v "/c/Users/Vinip/Desktop/projetoIA/tuberculosis-ltfu-prediction:/data" -w /data projeto-tuberculose
```

---

## 2. Dentro do Container Docker (No terminal do Passo 2)

### Passo 3: Preparação de Dados
```bash
python data-prep.py
```

### Passo 4: Treinar e Calibrar o Modelo Final
```bash
python pipeline/pipeline_final.py
```

### Passo 5: Rodar Análise de Features (SHAP)
```bash
python scripts/analise_features.py
```

### Passo 6: Gerar CSV do Teste 2 para o Dashboard
```bash
python gerar_csv.py
```

### Passo 7: Iniciar o Backend do App Médico (Dentro do Docker)
Após rodar os passos anteriores, inicie o servidor da API executando dentro do próprio container:
```bash
uvicorn app.backend.main:app --host 0.0.0.0 --port 8000
```
*(Esse comando vai segurar o terminal do Docker rodando o servidor).*

---

## 3. Visualizar no Navegador (No Windows)

*   **App do Médico:** Dobre-clique no arquivo `app/frontend/index.html` para abrir.
*   **Dashboard da Turma:** Dobre-clique no arquivo `siteDados/frontend/index.html` para abrir e arraste o arquivo `resultados_modelo.csv` gerado na raiz.

---

## Opção Alternativa: Rodar o Backend no Windows (Fora do Docker)
Se a versão do scikit-learn da sua `.venv` local for compatível com a do Docker, você pode rodar o backend fora do Docker abrindo um **novo terminal do Git Bash** no Windows e executando:
```bash
./.venv/Scripts/python.exe -m uvicorn app.backend.main:app --reload --port 8000
```
