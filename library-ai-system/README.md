# 📚 Sistema de Biblioteca Inteligente com IA

> **Bibliotecária Virtual que conversa com livros em PDF usando LLM + Qdrant + PostgreSQL + MCP Server**

Uma demonstração completa das tecnologias modernas de IA aplicadas a uma biblioteca digital, onde usuários podem "conversar" com livros em PDF através de uma bibliotecária virtual inteligente.

## 🌟 Visão Geral

Este projeto demonstra a integração de múltiplas tecnologias avançadas:

- **🤖 LLM (OpenAI GPT-4)**: Conversa natural sobre conteúdo dos livros
- **🔍 Qdrant**: Banco vetorial para busca semântica em embeddings
- **💾 PostgreSQL + pgvector**: Dados estruturados e suporte a vetores
- **🔧 MCP Server**: Ferramentas especializadas para análise de dados
- **🐳 Docker**: Containerização completa do ambiente
- **⚡ FastAPI**: API REST moderna e performática

## 🏗️ Arquitetura do Sistema

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   FastAPI       │    │   PostgreSQL    │
│   (Futuro)      │◄──►│   Backend       │◄──►│   + pgvector    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌─────────────────┐    ┌─────────────────┐
                       │     Qdrant      │    │   MCP Server    │
                       │ Vector Database │    │   Analytics     │
                       └─────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌─────────────────┐
                       │  OpenAI API     │
                       │  GPT-4 + Ada-2  │
                       └─────────────────┘
```

## 🚀 Funcionalidades

### 📖 Gestão de Livros
- Upload de PDFs com extração automática de texto
- Processamento em chunks para embeddings
- Armazenamento de metadados (título, autor, gênero, etc.)
- Busca por conteúdo, título ou autor

### 💬 Chat Inteligente
- Conversa natural sobre qualquer livro da biblioteca
- Busca semântica no conteúdo dos livros
- Respostas contextualizadas citando fontes
- Histórico de conversas persistente

### 📊 Analytics Avançados (MCP Server)
- Estatísticas da biblioteca (livros mais consultados)
- Análise comportamental de usuários
- Identificação de tópicos populares
- Sistema de recomendações inteligentes

### 🔐 Sistema de Usuários
- Autenticação JWT
- Perfis individuais
- Rastreamento de interações
- Dados de privacidade (LGPD compliance)

## 🛠️ Stack Tecnológica

### Backend Core
- **Python 3.12** + **FastAPI**: Framework web moderno
- **SQLAlchemy**: ORM para modelagem de dados
- **Pydantic**: Validação e serialização

### Inteligência Artificial
- **OpenAI GPT-4**: Modelo de linguagem para chat
- **text-embedding-ada-002**: Geração de embeddings
- **Qdrant**: Banco vetorial para busca semântica

### Banco de Dados
- **PostgreSQL 16**: Dados estruturados
- **pgvector**: Extensão para suporte a vetores
- **Qdrant**: Armazenamento especializado de embeddings

### Análise de Dados
- **MCP (Model Context Protocol)**: Ferramentas para IA
- **Pandas**: Manipulação de dados
- **Psycopg2**: Conexão com PostgreSQL

### DevOps
- **Docker & Docker Compose**: Containerização
- **Uvicorn**: Servidor ASGI
- **Loguru**: Sistema de logs avançado

## 🐳 Instalação e Configuração

### Pré-requisitos
- Docker e Docker Compose
- Chave da API OpenAI
- Git

### 1. Clonar e Configurar

```bash
# Clonar o repositório (assumindo que está no projeto pai)
cd library-ai-system

# Configurar variáveis de ambiente
# Edite o docker-compose.yml e adicione sua OPENAI_API_KEY
```

### 2. Iniciar os Serviços

```bash
# Subir todos os serviços
docker-compose up -d

# Verificar se todos os serviços estão funcionando
docker-compose ps
```

### 3. Verificar Funcionamento

```bash
# API da biblioteca estará em:
http://localhost:8040

# Documentação da API:
http://localhost:8040/docs

# Interface do Qdrant:
http://localhost:6333/dashboard

# MCP Server logs:
docker-compose logs library-mcp-server
```

## 📡 Endpoints da API

### Autenticação
- `POST /auth/register` - Registrar usuário
- `POST /auth/login` - Login do usuário

### Livros
- `POST /books/upload` - Upload de PDF
- `GET /books/` - Listar livros (com busca e filtros)
- `GET /books/{id}` - Detalhes de um livro
- `DELETE /books/{id}` - Deletar livro

### Chat IA
- `POST /chat/conversations` - Criar conversa
- `GET /chat/conversations` - Listar conversas
- `GET /chat/conversations/{id}` - Ver conversa
- `POST /chat/conversations/{id}/messages` - Enviar mensagem
- `DELETE /chat/conversations/{id}` - Deletar conversa

### Usuários
- `GET /users/me` - Dados do usuário logado

## 🤖 Como Funciona a IA

### 1. Processamento de PDFs
```
PDF Upload → Extração de Texto → Divisão em Chunks → 
Geração de Embeddings (OpenAI) → Armazenamento no Qdrant
```

### 2. Chat Inteligente
```
Pergunta do Usuário → Embedding da Pergunta → 
Busca Semântica no Qdrant → Contexto Relevante → 
GPT-4 + Contexto → Resposta Fundamentada
```

### 3. MCP Server Analytics
```
Dados do PostgreSQL → Análise com Pandas → 
Ferramentas MCP → Insights para IA
```

## 🔧 Ferramentas MCP Disponíveis

### `get_library_stats`
Estatísticas gerais da biblioteca digital
- Total de livros e usuários
- Livros mais populares
- Atividade recente

### `search_books_by_content`
Busca avançada em livros
- Por conteúdo, título ou autor
- Busca em metadados e texto completo

### `analyze_user_behavior`
Análise comportamental
- Padrões de leitura
- Livros favoritos
- Temas de interesse

### `get_popular_topics`
Tendências e tópicos populares
- Gêneros em alta
- Livros mais ativos
- Análise de engajamento

### `get_recommendation_insights`
Sistema de recomendações
- Baseado em preferências do usuário
- Livros similares
- Autores para explorar

## 💡 Casos de Uso

### Para Estudantes
- "Quais livros falam sobre inteligência artificial?"
- "Me explique o conceito de machine learning neste livro"
- "Encontre exercícios de cálculo nos meus PDFs"

### Para Pesquisadores
- "Compare as abordagens destes três autores sobre o tema X"
- "Que livros citam este conceito específico?"
- "Mostre as principais teorias sobre Y"

### Para Bibliotecários
- Análise de quais livros são mais consultados
- Identificação de lacunas na coleção
- Recomendações personalizadas para usuários

## 📊 Modelo de Dados

### Principais Entidades
- **Users**: Usuários do sistema
- **Books**: Metadados dos livros
- **Authors**: Informações dos autores
- **BookChunks**: Fragmentos de texto para busca
- **Conversations**: Histórico de conversas
- **Messages**: Mensagens individuais do chat
- **UserBookInteractions**: Rastreamento de interações

### Relacionamentos
```sql
Users 1:N Conversations 1:N Messages
Books 1:N BookChunks (com embeddings no Qdrant)
Books N:M Authors (via BookAuthors)
Users N:M Books (via UserBookInteractions)
```

## 🔐 Segurança e Privacidade

- **Autenticação JWT** com tokens seguros
- **Hashing bcrypt** para senhas
- **Isolamento de dados** por usuário
- **Logs de auditoria** para compliance
- **Dados anonimizados** para analytics

## 🚀 Próximos Passos

- [ ] Interface web responsiva
- [ ] Upload de múltiplos arquivos
- [ ] Suporte a outros formatos (EPUB, TXT)
- [ ] Sistema de citações automáticas
- [ ] Integração com bibliotecas digitais
- [ ] API pública para desenvolvedores

## 🧪 Testes e Desenvolvimento

```bash
# Logs da API
docker-compose logs -f library-api

# Logs do MCP Server
docker-compose logs -f library-mcp-server

# Acessar container da API
docker-compose exec library-api bash

# Reiniciar apenas um serviço
docker-compose restart library-api
```

## 🤝 Contribuição

Este projeto é uma demonstração das capacidades de integração entre:
- **LLMs** para processamento de linguagem natural
- **Bancos vetoriais** para busca semântica
- **Protocolos MCP** para ferramentas de IA
- **Containerização** para deploy fácil

Ideal para:
- Estudos sobre RAG (Retrieval-Augmented Generation)
- Proof of concepts com IA
- Sistemas de conhecimento empresarial
- Projetos acadêmicos avançados

## 📄 Licença

Este projeto é uma demonstração educacional e pode ser usado como base para projetos comerciais ou acadêmicos.

---

**🎯 Objetivo**: Demonstrar como integrar múltiplas tecnologias de IA de forma prática e escalável, criando uma experiência única de "conversar com livros".

**🏷️ Tags**: `#AI` `#LLM` `#VectorDatabase` `#RAG` `#FastAPI` `#Docker` `#MCP` `#OpenAI` `#Qdrant` `#PostgreSQL`