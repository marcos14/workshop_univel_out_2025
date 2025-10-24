# ============================================
# DOCKERFILE - WORKSHOP LANGCHAIN + MCP + QDRANT
# ============================================
# Imagem Python com todas as dependências pré-instaladas

FROM python:3.11-slim

# Metadados da imagem
LABEL maintainer="Workshop Univel <workshop@univel.edu.br>"
LABEL description="Workshop LangChain + MCP + Qdrant - Ambiente Python"
LABEL version="0.1.0"

# Variáveis de ambiente para Python
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Instala dependências do sistema
RUN apt-get update && apt-get install -y \
    curl \
    git \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Instala Poetry
RUN pip install poetry==1.7.1

# Configura Poetry para não criar venv (já estamos em container)
RUN poetry config virtualenvs.create false

# Define diretório de trabalho
WORKDIR /app

# Copia arquivos de dependências
COPY pyproject.toml ./

# Instala dependências Python (apenas main, sem dev dependencies)
RUN poetry install --only main --no-interaction --no-ansi

# Copia código da aplicação
COPY . .

# Cria usuário não-root para segurança
RUN useradd --create-home --shell /bin/bash workshop && \
    chown -R workshop:workshop /app
USER workshop

# Define comando padrão
CMD ["python", "-c", "print('🎉 Workshop LangChain + MCP + Qdrant - Ambiente Python pronto!')"]