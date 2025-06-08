# Usando uma imagem slim do Python
FROM python:3.11-slim

# Definindo o diretório de trabalho
WORKDIR /app

# Copiando apenas o requirements.txt primeiro para otimizar o cache de dependências
COPY requirements.txt .

# Instalando as dependências
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

# Copiando o restante dos arquivos da aplicação
COPY . .

# Copiando o script wait-for-it.sh e garantindo permissões
COPY wait-for-it.sh /wait-for-it.sh
RUN chmod +x /wait-for-it.sh

# Expondo a porta da API
EXPOSE 8010

# Comando de inicialização com factory
CMD ["/wait-for-it.sh", "db:5432", "--", "uvicorn", "app.main:create_app", "--factory", "--host", "0.0.0.0", "--port", "8010"]
