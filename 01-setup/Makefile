# ============================================
# MAKEFILE - WORKSHOP LANGCHAIN + MCP + QDRANT
# ============================================
# Comandos para automação do ambiente containerizado

.PHONY: help bootstrap up down check lint test clean build logs shell

# Target padrão - mostra ajuda
help:
	@echo "==================================================="
	@echo "  WORKSHOP LANGCHAIN + MCP + QDRANT - COMANDOS"
	@echo "==================================================="
	@echo ""
	@echo "Configuração inicial:"
	@echo "  bootstrap    - Verifica Docker e configura ambiente"
	@echo "  build        - Constrói imagens Docker"
	@echo ""
	@echo "Ambiente (todos os serviços):"
	@echo "  up           - Inicia todo o ambiente (app + qdrant + redis)"
	@echo "  down         - Para todos os serviços"
	@echo "  logs         - Mostra logs de todos os serviços"
	@echo "  status       - Mostra status dos containers"
	@echo ""
	@echo "Desenvolvimento:"
	@echo "  shell        - Abre shell no container Python"
	@echo "  check        - Executa verificações de sanidade"
	@echo "  lint         - Verifica formatação do código"
	@echo "  test         - Executa testes"
	@echo ""
	@echo "Utilitários:"
	@echo "  clean        - Remove containers e volumes"
	@echo "  rebuild      - Reconstrói tudo do zero"
	@echo ""

# ==========================================
# CONFIGURAÇÃO INICIAL
# ==========================================

bootstrap:
	@echo "🚀 Verificando ambiente Docker..."
	@bash scripts/bootstrap.sh
	@echo "✅ Bootstrap concluído!"
	@echo ""
	@echo "Próximos passos:"
	@echo "1. Configure suas chaves no arquivo .env"
	@echo "2. Execute: make up (para iniciar ambiente)"
	@echo "3. Execute: make check (para verificar tudo)"

build:
	@echo "� Construindo imagens Docker..."
	@docker compose build --no-cache
	@echo "✅ Imagens construídas!"

rebuild: clean build up
	@echo "🔄 Ambiente reconstruído completamente!"

# ==========================================
# GERENCIAMENTO DO AMBIENTE
# ==========================================

up:
	@echo "🐳 Iniciando ambiente completo..."
	@docker compose up -d
	@echo "⏳ Aguardando serviços ficarem prontos..."
	@sleep 15
	@echo "🌐 Ambiente disponível:"
	@echo "   - Qdrant Dashboard: http://localhost:6333/dashboard"
	@echo "   - Qdrant API: http://localhost:6333"
	@echo "   - Redis: localhost:6379"
	@echo "   - Shell Python: make shell"
	@echo "✅ Ambiente iniciado!"

down:
	@echo "🛑 Parando ambiente..."
	@docker compose down
	@echo "✅ Ambiente parado!"

logs:
	@echo "� Logs do ambiente (Ctrl+C para sair):"
	@docker compose logs -f

status:
	@echo "� Status dos serviços:"
	@docker compose ps

# ==========================================
# DESENVOLVIMENTO
# ==========================================

shell:
	@echo "🐚 Abrindo shell no container Python..."
	@docker compose exec workshop-app bash

check:
	@echo "🔍 Executando verificações de sanidade..."
	@docker compose exec workshop-app python -m scripts.check_env
	@echo ""

lint:
	@echo "🧹 Verificando formatação do código..."
	@docker compose exec workshop-app ruff check .
	@echo "✅ Código verificado!"

test:
	@echo "🧪 Executando testes..."
	@docker compose exec workshop-app pytest -q
	@echo "✅ Testes concluídos!"

# ==========================================
# UTILITÁRIOS
# ==========================================

clean:
	@echo "🧹 Removendo containers e volumes..."
	@docker compose down -v --remove-orphans
	@docker system prune -f
	@echo "✅ Limpeza concluída!"

# ==========================================
# COMANDOS ESPECÍFICOS
# ==========================================

# Executa comando Python no container
python-exec:
	@docker compose exec workshop-app python $(CMD)

# Instala pacote Python no container
install-package:
	@docker compose exec workshop-app pip install $(PACKAGE)

# Backup dos dados
backup:
	@echo "💾 Criando backup dos dados..."
	@mkdir -p backups
	@docker compose exec qdrant tar czf - /qdrant/storage > backups/qdrant-$(shell date +%Y%m%d-%H%M%S).tar.gz
	@echo "✅ Backup salvo em backups/"

# Informações do ambiente
info:
	@echo "ℹ️  Informações do ambiente:"
	@echo "Docker: $(shell docker --version 2>&1 || echo 'Não encontrado')"
	@echo "Docker Compose: $(shell docker compose version 2>&1 || echo 'Não encontrado')"
	@echo ""
	@echo "Containers ativos:"
	@docker compose ps --format "table {{.Name}}\t{{.Status}}\t{{.Ports}}" 2>/dev/null || echo "Nenhum container ativo"

# Reset completo do ambiente
reset: clean
	@echo "🔄 Resetando ambiente completo..."
	@docker volume prune -f
	@rm -f .env
	@echo "✅ Reset concluído! Execute 'make bootstrap' para reconfigurar."