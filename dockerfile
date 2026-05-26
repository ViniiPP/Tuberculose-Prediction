# Imagem base com Python 3.10
FROM python:3.10-slim

# Instalar dependências necessárias para compilar o pyreaddbc
RUN apt update && apt install -y \
    build-essential \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Instalar o PySUS e dependências de Machine Learning
RUN pip install --no-cache-dir pysus==0.15.0 polars scikit-learn matplotlib joblib shap pandas fastapi uvicorn

# Criar diretório de trabalho
WORKDIR /app

# Comando padrão ao entrar no container
CMD ["bash"]