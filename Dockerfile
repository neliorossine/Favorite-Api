# Imagem base leve com Python 3.11
FROM python:3.11-slim

# Define o diretório de trabalho
WORKDIR /app

# Evita prompt de timezone/locales
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app

# Instala dependências do sistema necessárias
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copia apenas o requirements.txt para aproveitar cache de build
COPY requirements.txt .

# Instala dependências do Python
RUN pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Copia o restante da aplicação
COPY . .

# Copia o script de espera por serviços (e dá permissão)
COPY wait-for-it.sh /wait-for-it.sh
RUN chmod +x /wait-for-it.sh

# Expondo porta da API FastAPI
EXPOSE 8010

# Comando de inicialização (aguarda banco antes de iniciar a API)
CMD ["/wait-for-it.sh", "db:5432", "--", "uvicorn", "app.main:create_app", "--factory", "--host", "0.0.0.0", "--port", "8010"]
