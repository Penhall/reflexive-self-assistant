# Dockerfile para Reflexive Self Coding Assistant
FROM python:3.11-slim

# Configurar diretório de trabalho
WORKDIR /app

# Instalar dependências do sistema
RUN apt-get update && apt-get install -y \
    git \
    curl \
    build-essential \
    netcat-openbsd \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements e instalar dependências Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código da aplicação
COPY . .

# Criar diretórios necessários
RUN mkdir -p data logs exports/identities exports/reports

# Configurar variáveis de ambiente
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Expor portas
EXPOSE 8501 8080

# Script de inicialização
COPY infrastructure/start.sh /start.sh
RUN chmod +x /start.sh

# Comando padrão
CMD ["/start.sh"]