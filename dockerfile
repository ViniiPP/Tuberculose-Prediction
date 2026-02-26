# Imagem base com Python 3.10
FROM python:3.10-slim

# Instalar dependências necessárias para compilar o pyreaddbc
RUN apt update && apt install -y \
    build-essential \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Instalar o PySUS
RUN pip install --no-cache-dir pysus

# Criar diretório de trabalho
WORKDIR /app

# Comando padrão ao entrar no container
CMD ["bash"]