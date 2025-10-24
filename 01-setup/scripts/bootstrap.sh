#!/bin/bash

# ============================================
# BOOTSTRAP SCRIPT - WORKSHOP LANGCHAIN + MCP + QDRANT
# ============================================
# Script de configuração inicial do ambiente de desenvolvimento
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

print_header "WORKSHOP LANGCHAIN + MCP + QDRANT - BOOTSTRAP"

print_info "Verificando requisitos do sistema..."

# Verifica se estamos no diretório correto
if [ ! -f "pyproject.toml" ]; then
    print_error "Arquivo pyproject.toml não encontrado!"
    print_error "Execute este script a partir da pasta raiz do projeto (01-setup)"
    exit 1
fi

# Verifica Python
if ! command -v python &> /dev/null && ! command -v python3 &> /dev/null; then
    print_error "Python não encontrado!"
    print_error "Instale Python 3.10+ antes de continuar."
    exit 1
fi

# Determina comando Python correto
PYTHON_CMD="python"
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
fi

# Verifica versão do Python
PYTHON_VERSION=$($PYTHON_CMD --version 2>&1 | cut -d' ' -f2)
PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d'.' -f1)
PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d'.' -f2)

if [ "$PYTHON_MAJOR" -lt 3 ] || ([ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 10 ]); then
    print_error "Python $PYTHON_VERSION detectado. É necessário Python 3.10 ou superior."
    print_info "Versão atual: $PYTHON_VERSION"
    print_info "Mínima requerida: 3.10.0"
    exit 1
fi

print_success "Python $PYTHON_VERSION detectado ✓"

# ==========================================
# VERIFICAÇÃO E INSTALAÇÃO DO POETRY
# ==========================================

print_info "Verificando Poetry..."

if ! command -v poetry &> /dev/null; then
    print_warning "Poetry não encontrado. Instalando..."
    
    # Instala Poetry
    if command -v curl &> /dev/null; then
        curl -sSL https://install.python-poetry.org | $PYTHON_CMD -
    else
        print_error "curl não encontrado. Instale Poetry manualmente:"
        print_info "https://python-poetry.org/docs/#installation"
        exit 1
    fi
    
    # Adiciona Poetry ao PATH (temporariamente)
    export PATH="$HOME/.local/bin:$PATH"
    
    if ! command -v poetry &> /dev/null; then
        print_error "Falha na instalação do Poetry."
        print_info "Instale manualmente: https://python-poetry.org/docs/#installation"
        print_info "Em seguida, adicione ao PATH e execute este script novamente."
        exit 1
    fi
    
    print_success "Poetry instalado com sucesso!"
else
    POETRY_VERSION=$(poetry --version 2>&1 | cut -d' ' -f3)
    print_success "Poetry $POETRY_VERSION detectado ✓"
fi

# ==========================================
# CONFIGURAÇÃO DO POETRY
# ==========================================

print_info "Configurando Poetry para criar venv local..."

# Configura Poetry para criar .venv na pasta do projeto
poetry config virtualenvs.in-project true
poetry config virtualenvs.prefer-active-python true

print_success "Configuração do Poetry atualizada ✓"

# ==========================================
# INSTALAÇÃO DE DEPENDÊNCIAS
# ==========================================

print_header "INSTALAÇÃO DE DEPENDÊNCIAS"

print_info "Instalando dependências Python via Poetry..."
print_info "Isso pode levar alguns minutos na primeira execução..."

if poetry install; then
    print_success "Dependências instaladas com sucesso!"
else
    print_error "Falha na instalação das dependências."
    print_info "Tente executar manualmente: poetry install"
    exit 1
fi

# ==========================================
# CONFIGURAÇÃO DO ARQUIVO .ENV
# ==========================================

print_header "CONFIGURAÇÃO DO AMBIENTE"

if [ ! -f ".env" ]; then
    print_info "Criando arquivo .env a partir do template..."
    
    if [ -f ".env.example" ]; then
        cp ".env.example" ".env"
        print_success "Arquivo .env criado!"
        print_warning "⚠️  IMPORTANTE: Configure suas chaves API no arquivo .env"
        print_info "   - Edite o arquivo .env"
        print_info "   - Adicione sua OPENAI_API_KEY"
        print_info "   - Ajuste URLs se necessário"
    else
        print_error "Arquivo .env.example não encontrado!"
        exit 1
    fi
else
    print_info "Arquivo .env já existe. Pulando criação."
fi

# ==========================================
# VERIFICAÇÃO FINAL
# ==========================================

print_header "VERIFICAÇÃO FINAL"

# Verifica se o ambiente virtual foi criado
if [ -d ".venv" ]; then
    print_success "Ambiente virtual criado em .venv/"
else
    print_warning "Ambiente virtual não encontrado. Poetry pode estar usando cache global."
fi

# Informações de ativação do ambiente
print_info "Para ativar o ambiente virtual manualmente:"
if [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "win32" ]]; then
    print_info "   .venv\\Scripts\\activate"
else
    print_info "   source .venv/bin/activate"
fi

print_info "Ou use Poetry: poetry shell"

# ==========================================
# RESUMO E PRÓXIMOS PASSOS
# ==========================================

print_header "BOOTSTRAP CONCLUÍDO COM SUCESSO!"

print_success "✅ Python $PYTHON_VERSION configurado"
print_success "✅ Poetry configurado e dependências instaladas"
print_success "✅ Arquivo .env criado"
print_success "✅ Ambiente pronto para desenvolvimento"

echo ""
print_info "🚀 PRÓXIMOS PASSOS:"
echo ""
print_info "1. Configure suas chaves API:"
print_info "   📝 Edite o arquivo .env"
print_info "   🔑 Adicione sua OPENAI_API_KEY"
echo ""
print_info "2. Inicie os serviços auxiliares:"
print_info "   🐳 make up (ou docker compose up -d)"
echo ""
print_info "3. Execute as verificações:"
print_info "   🔍 make check"
echo ""
print_info "4. Se tudo estiver ✅, continue para o próximo módulo!"

print_header "PRONTO PARA O WORKSHOP! 🎉"