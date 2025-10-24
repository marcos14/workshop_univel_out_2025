# 01-setup — Fundamentos e Primeiros Testes

Bem-vindo ao **Workshop LangChain + MCP + Qdrant**! Este é o primeiro módulo, onde você vai configurar todo o ambiente de desenvolvimento e executar os primeiros testes para garantir que tudo está funcionando perfeitamente.

## 🎯 Contexto e Objetivos

Neste workshop, você vai aprender a construir aplicações inteligentes combinando três tecnologias poderosas:

- **LangChain**: Framework para desenvolvimento de aplicações com LLMs (Large Language Models), oferecendo abstrações para chains, agents, tools e memory management
- **MCP (Model Context Protocol)**: Protocolo emergente para padronizar comunicação entre LLMs e sistemas externos, permitindo integração transparente de dados e ferramentas
- **Qdrant**: Banco de dados vetorial de alta performance, especializado em busca por similaridade e operações com embeddings

Este módulo (01-setup) foca exclusivamente em **preparar o ambiente** e **validar a conectividade** com todos os serviços. Você vai instalar dependências, configurar credenciais, subir serviços auxiliares via Docker e executar verificações automáticas de sanidade.

**Por que essa stack?** A combinação LangChain + Qdrant permite construir sistemas RAG (Retrieval-Augmented Generation) robustos, enquanto o MCP adiciona uma camada de integração padronizada com sistemas corporativos. É a stack perfeita para aplicações empresariais que precisam de memória semântica e integração com dados externos.

## 📋 Requisitos

Antes de começar, certifique-se de ter instalado:

- **Python 3.10+** (verifique com `python --version`)
- **Docker + Docker Compose** (para Qdrant e Redis)
- **Poetry** (gerenciador de dependências Python - será instalado automaticamente se necessário)
- **Git** (para clonar repositórios)
- **Conexão com internet** (para download de dependências e APIs)

### Ferramentas Opcionais (Recomendadas)
- **VS Code** com extensões Python e Docker
- **Postman/Insomnia** para testar APIs REST
- **Redis CLI** para debug do cache

## 🚀 Passo a Passo

### 1. Configuração Inicial Automática

Execute o comando de bootstrap que irá instalar todas as dependências e configurar o ambiente:

```bash
make bootstrap
```

Este comando vai:
- ✅ Verificar se Python 3.10+ está instalado
- ✅ Instalar Poetry (se necessário)
- ✅ Criar ambiente virtual Python
- ✅ Instalar todas as dependências do projeto
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

**Configurações que funcionam por padrão:**
- `QDRANT_URL=http://localhost:6333` (para Docker local)
- `REDIS_URL=redis://localhost:6379/0` (para Docker local)

### 3. Iniciar Serviços Auxiliares

Suba o Qdrant e Redis usando Docker Compose:

```bash
make up
```

Este comando vai:
- 🐳 Baixar e iniciar container do Qdrant na porta 6333
- 🐳 Baixar e iniciar container do Redis na porta 6379
- ⏳ Aguardar serviços ficarem prontos (health checks)
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

Este comando vai verificar:
- ✅ **Python**: Versão >= 3.10
- ✅ **Configuração**: Arquivo .env e variáveis obrigatórias
- ✅ **Qdrant**: Conectividade e listagem de coleções
- ✅ **Redis**: Operações SET/GET e performance
- ✅ **LLM**: Conectividade com OpenAI e resposta básica

## 🔧 Comandos Úteis

```bash
# Configuração inicial
make bootstrap          # Instala dependências e configura ambiente
make install            # Instala apenas dependências Python

# Gerenciamento de serviços
make up                 # Inicia Qdrant e Redis
make down               # Para os serviços
make status             # Mostra status dos containers
make logs               # Mostra logs dos serviços

# Verificações e qualidade
make check              # Executa verificações de sanidade
make lint               # Verifica formatação do código
make test               # Executa testes (quando disponíveis)

# Utilitários
make clean              # Remove arquivos temporários
make info               # Mostra informações do ambiente
make help               # Lista todos os comandos
```

## 🚨 Troubleshooting

### Problemas Comuns

**"Poetry não encontrado"**
```bash
# Instale manualmente:
curl -sSL https://install.python-poetry.org | python3 -
# Adicione ao PATH e reinicie o terminal
```

**"Porta 6333 já está em uso"**
```bash
# Verifique processos usando a porta:
lsof -i :6333          # Linux/macOS
netstat -ano | findstr :6333    # Windows

# Pare container existente:
docker stop $(docker ps -q --filter "publish=6333")
```

**"Erro de conexão com Qdrant"**
```bash
# Verifique se o container está rodando:
docker compose ps

# Veja logs do Qdrant:
docker compose logs qdrant

# Reinicie serviços:
make down && make up
```

**"OpenAI API Key inválida"**
- Verifique se a chave está correta no arquivo `.env`
- Confirme que a chave tem créditos disponíveis
- Teste a chave diretamente: https://platform.openai.com/playground

**"Erro de proxy corporativo"**
```bash
# Configure proxy para Docker:
export HTTP_PROXY=http://proxy.empresa.com:8080
export HTTPS_PROXY=http://proxy.empresa.com:8080

# Configure proxy para Poetry:
poetry config http-basic.pypi username password
```

### Verificação Manual

Se o `make check` falhar, você pode testar componentes individualmente:

```bash
# Teste Python e configuração
poetry run python -c "from app.config import get_settings; print(get_settings())"

# Teste Qdrant
poetry run python -c "from app.qdrant_sanity import check_connection; print(check_connection())"

# Teste Redis  
poetry run python -c "from app.redis_sanity import roundtrip; print(roundtrip())"

# Teste LLM
poetry run python -c "from app.llm_sanity import hello; print(hello())"
```

## ✅ Checklist de Sucesso

Você está pronto para o próximo módulo quando:

- [ ] `make bootstrap` executou sem erros
- [ ] Arquivo `.env` configurado com `OPENAI_API_KEY`
- [ ] `make up` iniciou Qdrant e Redis com sucesso
- [ ] `make check` reporta todas as verificações críticas como ✅
- [ ] Qdrant Dashboard acessível em http://localhost:6333/dashboard
- [ ] Todos os imports Python funcionando (`poetry run python -c "import app"`)

### Verificações Obrigatórias ✅
- **Python >= 3.10**: Versão mínima para compatibilidade
- **Configuração válida**: Arquivo .env presente e variáveis carregadas
- **Qdrant conectado**: Banco vetorial acessível e operacional

### Verificações Recomendadas ⭐
- **OpenAI configurado**: Para testes de LLM (pode ser configurado depois)
- **Redis funcionando**: Para cache e sessões (opcional para este módulo)

## 🗂️ Estrutura do Projeto

```
01-setup/
├── README.md              # Este arquivo
├── SLIDES.md              # Base para apresentação
├── pyproject.toml         # Configuração Poetry e dependências
├── .env.example           # Template de variáveis de ambiente
├── .gitignore             # Arquivos ignorados pelo Git
├── Makefile               # Comandos de automação
├── docker-compose.yml     # Serviços Qdrant + Redis
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

**🎉 Parabéns!** Você configurou com sucesso o ambiente para o workshop. Agora é hora de partir para a criação de embeddings e implementação de busca semântica!

---

*Workshop LangChain + MCP + Qdrant | Universidade Univel | Módulo 01 - Setup e Fundamentos*