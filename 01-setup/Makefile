# ============================================
# MAKEFILE - WORKSHOP LANGCHAIN + MCP + QDRANT
# ============================================
# Comandos para automação do ambiente de desenvolvimento

.PHONY: help bootstrap up down check lint test clean install status logs

# Target padrão - mostra ajuda
help:
	@echo "==================================================="
	@echo "  WORKSHOP LANGCHAIN + MCP + QDRANT - COMANDOS"
	@echo "==================================================="
	@echo ""
	@echo "Configuração inicial:"
	@echo "  bootstrap    - Instala dependências e configura ambiente"
	@echo "  install      - Instala apenas as dependências Python"
	@echo ""
	@echo "Docker (serviços auxiliares):"
	@echo "  up           - Inicia Qdrant e Redis"
	@echo "  down         - Para os serviços"
	@echo "  status       - Mostra status dos containers"
	@echo "  logs         - Mostra logs dos serviços"
	@echo ""
	@echo "Verificações e testes:"
	@echo "  check        - Executa verificações de sanidade"
	@echo "  lint         - Verifica formatação do código"
	@echo "  test         - Executa testes (quando disponíveis)"
	@echo ""
	@echo "Utilitários:"
	@echo "  clean        - Remove arquivos temporários"
	@echo ""

# ==========================================
# CONFIGURAÇÃO INICIAL
# ==========================================

bootstrap:
	@echo "🚀 Iniciando configuração do ambiente..."
	@echo "📋 Executando script de bootstrap..."
	@bash scripts/bootstrap.sh
	@echo "✅ Bootstrap concluído!"
	@echo ""
	@echo "Próximos passos:"
	@echo "1. Configure suas chaves no arquivo .env"
	@echo "2. Execute: make up (para iniciar serviços)"
	@echo "3. Execute: make check (para verificar tudo)"

install:
	@echo "📦 Instalando dependências Python..."
	@poetry install
	@echo "✅ Dependências instaladas!"

# ==========================================
# DOCKER SERVICES
# ==========================================

up:
	@echo "🐳 Iniciando serviços (Qdrant + Redis)..."
	@docker compose up -d
	@echo "⏳ Aguardando serviços ficarem prontos..."
	@sleep 10
	@echo "🌐 Serviços disponíveis:"
	@echo "   - Qdrant Dashboard: http://localhost:6333/dashboard"
	@echo "   - Qdrant API: http://localhost:6333"
	@echo "   - Redis: localhost:6379"
	@echo "✅ Serviços iniciados!"

down:
	@echo "🛑 Parando serviços..."
	@docker compose down
	@echo "✅ Serviços parados!"

status:
	@echo "📊 Status dos serviços:"
	@docker compose ps

logs:
	@echo "📋 Logs dos serviços (Ctrl+C para sair):"
	@docker compose logs -f

# ==========================================
# VERIFICAÇÕES E TESTES
# ==========================================

check:
	@echo "🔍 Executando verificações de sanidade..."
	@poetry run python -m scripts.check_env
	@echo ""

lint:
	@echo "🧹 Verificando formatação do código..."
	@poetry run ruff check .
	@echo "✅ Código formatado corretamente!"

test:
	@echo "🧪 Executando testes..."
	@poetry run pytest -q
	@echo "✅ Testes concluídos!"

# ==========================================
# UTILITÁRIOS
# ==========================================

clean:
	@echo "🧹 Limpando arquivos temporários..."
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete 2>/dev/null || true
	@find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name ".ruff_cache" -exec rm -rf {} + 2>/dev/null || true
	@echo "✅ Limpeza concluída!"

# ==========================================
# COMANDOS AVANÇADOS
# ==========================================

# Reset completo do ambiente
reset: down clean
	@echo "🔄 Resetando ambiente completo..."
	@docker compose down -v
	@rm -f .env
	@echo "✅ Reset concluído! Execute 'make bootstrap' para reconfigurar."

# Backup dos dados
backup:
	@echo "💾 Criando backup dos dados..."
	@mkdir -p backups
	@docker compose exec qdrant tar czf - /qdrant/storage > backups/qdrant-$(shell date +%Y%m%d-%H%M%S).tar.gz
	@echo "✅ Backup salvo em backups/"

# Informações do ambiente
info:
	@echo "ℹ️  Informações do ambiente:"
	@echo "Python: $(shell python --version 2>&1 || echo 'Não encontrado')"
	@echo "Poetry: $(shell poetry --version 2>&1 || echo 'Não encontrado')"
	@echo "Docker: $(shell docker --version 2>&1 || echo 'Não encontrado')"
	@echo "Docker Compose: $(shell docker compose version 2>&1 || echo 'Não encontrado')"