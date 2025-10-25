# Comandos de Teste para o Sistema de Biblioteca IA

## 🚀 Startup e Verificação

```bash
# Navegar para o diretório do projeto
cd library-ai-system

# Iniciar todos os serviços
docker-compose up -d

# Verificar se todos os serviços estão rodando
docker-compose ps

# Verificar logs
docker-compose logs -f library-api
```

## 🔧 Configuração Inicial

### 1. Verificar se API está funcionando
```bash
curl http://localhost:8040/health
# Esperado: {"status": "healthy", "service": "Library AI System"}
```

### 2. Verificar Qdrant
```bash
curl http://localhost:6333/health
# Esperado: resposta OK do Qdrant
```

## 👤 Testes de Autenticação

### 1. Registrar usuário
```bash
curl -X POST "http://localhost:8040/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "João Silva",
    "email": "joao@exemplo.com",
    "password": "senha123"
  }'
```

### 2. Fazer login
```bash
curl -X POST "http://localhost:8040/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "joao@exemplo.com",
    "password": "senha123"
  }'
```

**Salve o token retornado para usar nos próximos comandos:**
```bash
export TOKEN="seu_token_aqui"
```

## 📚 Testes de Upload de Livros

### 1. Verificar usuário logado
```bash
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8040/users/me
```

### 2. Upload de PDF (substitua pelo caminho real do seu PDF)
```bash
curl -X POST "http://localhost:8040/books/upload" \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@/caminho/para/seu/livro.pdf" \
  -F "title=Título do Livro" \
  -F "genre=Ficção" \
  -F "description=Descrição do livro" \
  -F "author_names[]=Nome do Autor"
```

### 3. Listar livros
```bash
curl -H "Authorization: Bearer $TOKEN" \
  "http://localhost:8040/books/"
```

### 4. Buscar livros
```bash
curl -H "Authorization: Bearer $TOKEN" \
  "http://localhost:8040/books/?search=título&genre=Ficção"
```

## 💬 Testes de Chat

### 1. Criar conversa
```bash
curl -X POST "http://localhost:8040/chat/conversations" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Conversa sobre IA"
  }'
```

**Salve o conversation_id retornado:**
```bash
export CONV_ID="id_da_conversa"
```

### 2. Enviar mensagem
```bash
curl -X POST "http://localhost:8040/chat/conversations/$CONV_ID/messages" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "Quais livros falam sobre inteligência artificial?"
  }'
```

### 3. Ver histórico da conversa
```bash
curl -H "Authorization: Bearer $TOKEN" \
  "http://localhost:8040/chat/conversations/$CONV_ID"
```

### 4. Listar todas as conversas
```bash
curl -H "Authorization: Bearer $TOKEN" \
  "http://localhost:8040/chat/conversations"
```

## 📊 Testes do MCP Server

### 1. Verificar se MCP Server está rodando
```bash
docker-compose logs library-mcp-server
```

### 2. Testar ferramentas MCP (via API interna)
```bash
# Conectar ao container do MCP Server
docker-compose exec library-mcp-server python -c "
from library_mcp_server import get_library_stats, AnalysisRequest
print(get_library_stats(AnalysisRequest(period_days=30)))
"
```

## 🔍 Testes de Busca Semântica

### 1. Fazer pergunta específica sobre conteúdo
```bash
curl -X POST "http://localhost:8040/chat/conversations/$CONV_ID/messages" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "Me explique o conceito de machine learning presente nos livros"
  }'
```

### 2. Buscar por tópico específico
```bash
curl -X POST "http://localhost:8040/chat/conversations/$CONV_ID/messages" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "Que livros tratam de redes neurais?"
  }'
```

## 🗃️ Verificação de Dados

### 1. Conectar ao PostgreSQL
```bash
docker-compose exec library-pg psql -U postgres -d library_db
```

### 2. Consultas úteis no banco
```sql
-- Ver usuários
SELECT * FROM users;

-- Ver livros
SELECT id, title, processed FROM books;

-- Ver chunks processados
SELECT book_id, COUNT(*) FROM book_chunks GROUP BY book_id;

-- Ver conversas
SELECT id, title, created_at FROM conversations;

-- Ver interações
SELECT user_id, book_id, interaction_type, COUNT(*) 
FROM user_book_interactions 
GROUP BY user_id, book_id, interaction_type;
```

### 3. Verificar Qdrant
```bash
# Acessar dashboard do Qdrant
# http://localhost:6333/dashboard

# Ou via API
curl "http://localhost:6333/collections/library_books"
```

## 🧪 Cenários de Teste Avançados

### 1. Upload de múltiplos livros
```bash
# Upload de livro técnico
curl -X POST "http://localhost:8040/books/upload" \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@livro_tecnico.pdf" \
  -F "title=Introdução à IA" \
  -F "genre=Técnico" \
  -F "author_names[]=Alan Turing"

# Upload de livro de ficção
curl -X POST "http://localhost:8040/books/upload" \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@livro_ficcao.pdf" \
  -F "title=1984" \
  -F "genre=Ficção" \
  -F "author_names[]=George Orwell"
```

### 2. Teste de conversa contextual
```bash
# Primeira pergunta
curl -X POST "http://localhost:8040/chat/conversations/$CONV_ID/messages" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"content": "Quais são os principais conceitos de IA mencionados?"}'

# Segunda pergunta (contextual)
curl -X POST "http://localhost:8040/chat/conversations/$CONV_ID/messages" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"content": "E como esses conceitos se relacionam com o que George Orwell escreveu?"}'
```

### 3. Teste de recomendações
```bash
# Após várias interações, testar recomendações via MCP
docker-compose exec library-mcp-server python -c "
from library_mcp_server import get_recommendation_insights, UserAnalysisRequest
print(get_recommendation_insights(UserAnalysisRequest(user_id=1)))
"
```

## 🐛 Troubleshooting

### 1. Reiniciar serviços individualmente
```bash
# Reiniciar apenas a API
docker-compose restart library-api

# Reiniciar apenas o Qdrant
docker-compose restart library-qdrant
```

### 2. Ver logs detalhados
```bash
# Logs da API
docker-compose logs -f library-api

# Logs do PostgreSQL
docker-compose logs library-pg

# Logs do Qdrant
docker-compose logs library-qdrant
```

### 3. Verificar volumes e dados
```bash
# Verificar se volumes estão criados
docker volume ls | grep library

# Verificar espaço em disco
df -h
```

### 4. Limpar e reiniciar tudo
```bash
# Parar todos os serviços
docker-compose down

# Remover volumes (CUIDADO: apaga todos os dados)
docker-compose down -v

# Recriar tudo
docker-compose up -d --build
```

## 📈 Métricas de Sucesso

- ✅ Todos os serviços sobem sem erro
- ✅ Upload de PDF funciona e processa embeddings
- ✅ Chat responde com contexto dos livros
- ✅ Busca semântica retorna resultados relevantes
- ✅ MCP Server fornece analytics úteis
- ✅ Histórico de conversas é persistido

## 🎯 Testes de Performance

```bash
# Teste de carga básico (requer 'ab' instalado)
ab -n 100 -c 10 http://localhost:8040/health

# Teste de upload múltiplo
for i in {1..5}; do
  curl -X POST "http://localhost:8040/books/upload" \
    -H "Authorization: Bearer $TOKEN" \
    -F "file=@teste_$i.pdf" \
    -F "title=Livro Teste $i" &
done
wait
```