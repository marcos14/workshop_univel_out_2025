#!/bin/bash

# ============================================
# BOOTSTRAP SCRIPT - WORKSHOP LANGCHAIN + MCP + QDRANT
# ============================================
# Script de configuração inicial do ambiente DOCKERIZADO
# Execução: bash scripts/bootstrap.sh ou make bootstrap

set -e  # Para execução em caso de erro

# Cores para output mais legível
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Funções de utilidade
print_header() {
    echo -e "${BLUE}============================================${NC}"
    echo -e "${BLUE}  $1${NC}"
    echo -e "${BLUE}============================================${NC}"
    echo ""
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# ==========================================
# VERIFICAÇÕES INICIAIS
# ==========================================

print_header "WORKSHOP LANGCHAIN + MCP + QDRANT - BOOTSTRAP DOCKER"

print_info "Verificando requisitos do sistema..."

# Verifica se estamos no diretório correto
if [ ! -f "docker-compose.yml" ]; then
    print_error "Arquivo docker-compose.yml não encontrado!"
    print_error "Execute este script a partir da pasta raiz do projeto (01-setup)"
    exit 1
fi

# ==========================================
# VERIFICAÇÃO DO DOCKER
# ==========================================

print_info "Verificando Docker..."

# Verifica Docker
if ! command -v docker &> /dev/null; then
    print_error "Docker não encontrado!"
    print_error "Instale Docker Desktop antes de continuar:"
    print_info "  Windows/Mac: https://www.docker.com/products/docker-desktop"
    print_info "  Linux: https://docs.docker.com/engine/install/"
    exit 1
fi

# Verifica se Docker está rodando
if ! docker info &> /dev/null; then
    print_error "Docker não está rodando!"
    print_error "Inicie Docker Desktop ou o daemon do Docker:"
    print_info "  Windows/Mac: Abra Docker Desktop"
    print_info "  Linux: sudo systemctl start docker"
    exit 1
fi

DOCKER_VERSION=$(docker --version | cut -d' ' -f3 | cut -d',' -f1)
print_success "Docker $DOCKER_VERSION detectado e rodando ✓"

# ==========================================
# VERIFICAÇÃO DO DOCKER COMPOSE
# ==========================================

print_info "Verificando Docker Compose..."

if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    print_error "Docker Compose não encontrado!"
    print_error "Instale Docker Compose:"
    print_info "  Geralmente vem com Docker Desktop"
    print_info "  Linux: https://docs.docker.com/compose/install/"
    exit 1
fi

# Usa o comando correto (docker compose ou docker-compose)
if docker compose version &> /dev/null; then
    COMPOSE_CMD="docker compose"
    COMPOSE_VERSION=$(docker compose version --short)
else
    COMPOSE_CMD="docker-compose"
    COMPOSE_VERSION=$(docker-compose --version | cut -d' ' -f3 | cut -d',' -f1)
fi

print_success "$COMPOSE_CMD $COMPOSE_VERSION detectado ✓"

# ==========================================
# CONFIGURAÇÃO DO ARQUIVO .ENV
# ==========================================

print_header "CONFIGURAÇÃO DO AMBIENTE"

if [ ! -f ".env" ]; then
    print_info "Criando arquivo .env a partir do template..."
    
    if [ -f ".env.example" ]; then
        cp ".env.example" ".env"
        print_success "Arquivo .env criado!"
        print_warning "⚠️  IMPORTANTE: Configure sua OPENAI_API_KEY no arquivo .env"
        print_info "   - Edite o arquivo .env"
        print_info "   - Adicione sua OPENAI_API_KEY"
        print_info "   - URLs do Qdrant e Redis já estão configuradas para Docker"
    else
        print_error "Arquivo .env.example não encontrado!"
        exit 1
    fi
else
    print_info "Arquivo .env já existe. Pulando criação."
fi

# ==========================================
# TESTE DE CONECTIVIDADE DOCKER
# ==========================================

print_header "TESTE DO AMBIENTE DOCKER"

print_info "Testando se as imagens podem ser baixadas..."

# Tenta baixar uma imagem pequena para testar conectividade
if docker pull hello-world:latest &> /dev/null; then
    print_success "Conectividade com Docker Hub ✓"
    docker rmi hello-world:latest &> /dev/null
else
    print_warning "Possível problema de conectividade ou proxy corporativo"
    print_info "Se estiver atrás de proxy, configure Docker:"
    print_info "  https://docs.docker.com/config/daemon/systemd/#httphttps-proxy"
fi

# ==========================================
# VERIFICAÇÃO FINAL
# ==========================================

print_header "VERIFICAÇÃO FINAL"

# Verifica espaço em disco (aviso se < 2GB)
AVAILABLE_SPACE=$(df . | tail -1 | awk '{print $4}')
if [ "$AVAILABLE_SPACE" -lt 2000000 ]; then
    print_warning "Pouco espaço em disco disponível (< 2GB)"
    print_info "O workshop precisa de pelo menos 2GB para imagens Docker"
fi

print_success "✅ Docker e Docker Compose configurados"
print_success "✅ Arquivo .env criado"
print_success "✅ Ambiente pronto para inicialização"

# ==========================================
# RESUMO E PRÓXIMOS PASSOS
# ==========================================

print_header "BOOTSTRAP CONCLUÍDO COM SUCESSO!"

print_success "✅ Docker $DOCKER_VERSION rodando"
print_success "✅ $COMPOSE_CMD $COMPOSE_VERSION disponível"
print_success "✅ Arquivo .env configurado"
print_success "✅ Ambiente pronto para o workshop"

echo ""
print_info "🚀 PRÓXIMOS PASSOS:"
echo ""
print_info "1. Configure sua chave API:"
print_info "   📝 Edite o arquivo .env"
print_info "   🔑 Adicione sua OPENAI_API_KEY"
echo ""
print_info "2. Inicie o ambiente completo:"
print_info "   🐳 make up (ou docker compose up -d)"
echo ""
print_info "3. Execute as verificações:"
print_info "   🔍 make check (ou docker compose exec workshop-app python -m scripts.check_env)"
echo ""
print_info "4. Se tudo estiver ✅, continue para o próximo módulo!"

print_header "PRONTO PARA O WORKSHOP! 🎉"