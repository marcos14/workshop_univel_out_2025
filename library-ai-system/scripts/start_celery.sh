#!/bin/bash

# Script para inicializar o Celery Worker
echo "🚀 Iniciando Celery Worker..."

# Aguardar Redis estar disponível
echo "⏳ Aguardando Redis..."
while ! nc -z redis 6379; do
  sleep 1
done
echo "✅ Redis disponível!"

# Aguardar API estar disponível (opcional)
echo "⏳ Aguardando API..."
while ! nc -z api 8000; do
  sleep 1
done
echo "✅ API disponível!"

# Iniciar Celery Worker
echo "🔄 Iniciando Celery Worker..."
cd /app && celery -A library_backend.celery_app worker --loglevel=info --concurrency=2

echo "❌ Celery Worker parou"