# 01-setup — Fundamentos e Primeiros Testes

Bem-vindo ao **Workshop LangChain + MCP + Qdrant**! Este é o primeiro módulo, onde você vai configurar todo o ambiente de desenvolvimento **totalmente containerizado** e executar os primeiros testes para garantir que tudo está funcionando perfeitamente.

## 🎯 Contexto e Objetivos

Neste workshop, você vai aprender a construir aplicações inteligentes combinando três tecnologias poderosas:

- **LangChain**: Framework para desenvolvimento de aplicações com LLMs (Large Language Models), oferecendo abstrações para chains, agents, tools e memory management
- **MCP (Model Context Protocol)**: Protocolo emergente para padronizar comunicação entre LLMs e sistemas externos, permitindo integração transparente de dados e ferramentas
- **Qdrant**: Banco de dados vetorial de alta performance, especializado em busca por similaridade e operações com embeddings

Este módulo (01-setup) foca exclusivamente em **preparar o ambiente containerizado** e **validar a conectividade** com todos os serviços. Você vai usar Docker para executar todo o ambiente, incluindo Python, dependências, Qdrant e Redis.

**Por que Docker?** Elimina problemas de instalação de Python, Poetry e dependências. Todo participante terá exatamente o mesmo ambiente, independente do sistema operacional. É a stack perfeita para workshops técnicos onde o foco deve ser no aprendizado, não na configuração.

## 📋 Requisitos

Antes de começar, certifique-se de ter instalado **APENAS**:

- **Docker Desktop** (Windows/Mac) ou **Docker Engine** (Linux)
- **Docker Compose** (geralmente incluído no Docker Desktop)
- **Conexão com internet** (para download de imagens e APIs)

### ⚠️ Não é necessário instalar:
- ❌ Python (será executado no container)
- ❌ Poetry (será executado no container)  
- ❌ Dependências Python (todas no container)
- ❌ Qdrant local (roda no container)
- ❌ Redis local (roda no container)

### Ferramentas Opcionais (Recomendadas)
- **VS Code** com extensão Docker
- **Postman/Insomnia** para testar APIs REST

## 🚀 Passo a Passo

### 1. Verificação e Configuração Inicial

Execute o comando de bootstrap que irá verificar o Docker e configurar o ambiente:

```bash
make bootstrap
```

Este comando vai:
- ✅ Verificar se Docker e Docker Compose estão instalados e rodando
- ✅ Testar conectividade com Docker Hub
- ✅ Criar arquivo `.env` a partir do template
- ✅ Exibir próximos passos

### 2. Configurar Credenciais

Após o bootstrap, edite o arquivo `.env` e configure suas chaves:

```bash
# No Windows
notepad .env

# No Linux/macOS
nano .env
```

**Configurações obrigatórias:**
- `OPENAI_API_KEY`: Sua chave da OpenAI (obtenha em https://platform.openai.com/api-keys)

**Configurações automáticas (já configuradas):**
- `QDRANT_URL=http://qdrant:6333` (URL interna do Docker)
- `REDIS_URL=redis://redis:6379/0` (URL interna do Docker)

### 3. Iniciar Ambiente Completo

Inicie todo o ambiente containerizado (Python + Qdrant + Redis):

```bash
make up
```

Este comando vai:
- 🔨 Construir imagem Python com todas as dependências
- 🐳 Baixar e iniciar container do Qdrant na porta 6333
- 🐳 Baixar e iniciar container do Redis na porta 6379
- ⏳ Aguardar todos os serviços ficarem prontos (health checks)
- 🌐 Exibir URLs de acesso

**URLs dos serviços:**
- Qdrant Dashboard: http://localhost:6333/dashboard
- Qdrant API: http://localhost:6333
- Redis: localhost:6379

### 4. Executar Verificações de Sanidade

Execute o script de verificação completa do ambiente:

```bash
make check
```

Este comando vai verificar **dentro dos containers**:
- ✅ **Python**: Versão >= 3.10
- ✅ **Configuração**: Arquivo .env e variáveis obrigatórias
- ✅ **Qdrant**: Conectividade e listagem de coleções
- ✅ **Redis**: Operações SET/GET e performance
- ✅ **LLM**: Conectividade com OpenAI e resposta básica

## 🔧 Comandos Úteis

```bash
# Configuração inicial
make bootstrap          # Verifica Docker e configura ambiente
make build              # Constrói imagens Docker

# Gerenciamento do ambiente
make up                 # Inicia ambiente completo (app + qdrant + redis)
make down               # Para todos os serviços
make logs               # Mostra logs de todos os serviços
make status             # Mostra status dos containers

# Desenvolvimento
make shell              # Abre shell no container Python
make check              # Executa verificações de sanidade
make lint               # Verifica formatação do código
make test               # Executa testes

# Utilitários
make clean              # Remove containers e volumes
make rebuild            # Reconstrói tudo do zero
make info               # Mostra informações do ambiente
make help               # Lista todos os comandos
```

## 🐚 Desenvolvimento Interativo

Para trabalhar com Python interativamente, use:

```bash
# Abre shell bash no container Python
make shell

# Dentro do container, você pode:
python -m scripts.check_env
python -c "from app.config import get_settings; print(get_settings())"
python -c "from app.llm_sanity import hello; print(hello())"

# Instalar pacotes adicionais (temporariamente)
pip install nome-do-pacote
```

## 🚨 Troubleshooting

### Problemas Comuns

**"Docker não encontrado" ou "Docker não está rodando"**
```bash
# Verifique se Docker Desktop está instalado e iniciado
docker --version
docker info

# Windows/Mac: Abra Docker Desktop
# Linux: sudo systemctl start docker
```

**"Porta 6333 já está em uso"**
```bash
# Verifique processos usando a porta:
lsof -i :6333          # Linux/macOS
netstat -ano | findstr :6333    # Windows

# Pare containers existentes:
docker compose down
docker stop $(docker ps -q --filter "publish=6333")
```

**"Erro de conectividade com Qdrant"**
```bash
# Verifique se todos os containers estão rodando:
docker compose ps

# Veja logs específicos:
docker compose logs qdrant
docker compose logs workshop-app

# Reinicie ambiente:
make down && make up
```

**"OpenAI API Key inválida"**
- Verifique se a chave está correta no arquivo `.env`
- Confirme que a chave tem créditos disponíveis
- Teste a chave diretamente: https://platform.openai.com/playground

**"Erro de build da imagem Docker"**
```bash
# Limpe cache e reconstrua:
make clean
make rebuild

# Ou force rebuild:
docker compose build --no-cache
```

**"Proxy corporativo"**
```bash
# Configure proxy para Docker Desktop:
# Settings > Resources > Proxies

# Para Docker CLI:
export HTTP_PROXY=http://proxy.empresa.com:8080
export HTTPS_PROXY=http://proxy.empresa.com:8080
```

### Verificação Manual

Se o `make check` falhar, você pode testar componentes individualmente:

```bash
# Acesse o shell do container
make shell

# Dentro do container, teste cada componente:
python -c "from app.config import get_settings; print(get_settings())"
python -c "from app.qdrant_sanity import check_connection; print(check_connection())"
python -c "from app.redis_sanity import roundtrip; print(roundtrip())"
python -c "from app.llm_sanity import hello; print(hello())"
```

### Debug Avançado

```bash
# Logs detalhados de um serviço específico
docker compose logs -f qdrant
docker compose logs -f redis
docker compose logs -f workshop-app

# Status detalhado dos containers
docker compose ps --format "table {{.Name}}\t{{.Status}}\t{{.Ports}}"

# Informações de rede
docker network ls
docker network inspect workshop-network

# Espaço em disco
docker system df
```

## ✅ Checklist de Sucesso

Você está pronto para o próximo módulo quando:

- [ ] `make bootstrap` executou sem erros (Docker verificado)
- [ ] Arquivo `.env` configurado com `OPENAI_API_KEY`
- [ ] `make up` iniciou todos os containers com sucesso
- [ ] `make check` reporta todas as verificações críticas como ✅
- [ ] Qdrant Dashboard acessível em http://localhost:6333/dashboard
- [ ] Shell do container funciona (`make shell`)

### Verificações Obrigatórias ✅
- **Docker funcionando**: Docker Desktop rodando e responsivo
- **Containers ativos**: `docker compose ps` mostra todos os serviços UP
- **Qdrant operacional**: Dashboard acessível e API respondendo

### Verificações Recomendadas ⭐
- **OpenAI configurado**: Para testes de LLM (pode ser configurado depois)
- **Redis funcionando**: Para cache e sessões (opcional para este módulo)

## 🗂️ Estrutura do Projeto

```
01-setup/
├── README.md              # Este arquivo
├── SLIDES.md              # Base para apresentação
├── Dockerfile             # Imagem Python com dependências
├── docker-compose.yml     # Orquestração de serviços
├── pyproject.toml         # Configuração Poetry e dependências
├── .env.example           # Template de variáveis de ambiente
├── .gitignore             # Arquivos ignorados pelo Git
├── Makefile               # Comandos de automação
├── scripts/
│   ├── bootstrap.sh       # Script de configuração inicial
│   └── check_env.py       # Verificações de sanidade
└── app/
    ├── __init__.py        # Package principal
    ├── config.py          # Configurações e validação
    ├── llm_sanity.py      # Testes do LLM/OpenAI
    ├── qdrant_sanity.py   # Testes do Qdrant
    └── redis_sanity.py    # Testes do Redis
```

## 🔗 Próximos Módulos

Após completar este setup com sucesso, você estará pronto para:

- **02-embeddings**: Criação e manipulação de vetores semânticos
- **03-rag**: Implementação de Retrieval-Augmented Generation
- **04-mcp-agent**: Integração com Model Context Protocol
- **05-final-demo**: Aplicação completa integrando todos os conceitos

## 📚 Referências Úteis

- [LangChain Documentation](https://python.langchain.com/)
- [Qdrant Documentation](https://qdrant.tech/documentation/)
- [OpenAI API Reference](https://platform.openai.com/docs)
- [Poetry Documentation](https://python-poetry.org/docs/)
- [Docker Compose Reference](https://docs.docker.com/compose/)

---

**🎉 Parabéns!** Você configurou com sucesso o ambiente **containerizado** para o workshop. Agora é hora de partir para a criação de embeddings e implementação de busca semântica!

**🐳 Vantagens da Abordagem Docker:**
- ✅ Ambiente idêntico para todos os participantes
- ✅ Sem problemas de instalação de Python/Poetry
- ✅ Isolamento completo de dependências
- ✅ Setup rápido e confiável
- ✅ Fácil reset e limpeza

---

*Workshop LangChain + MCP + Qdrant | Universidade Univel | Módulo 01 - Setup e Fundamentos | Versão Docker*