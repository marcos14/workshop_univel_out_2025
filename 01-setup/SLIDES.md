# SLIDES.md - Workshop LangChain + MCP + Qdrant

Este arquivo contém o conteúdo estruturado para os slides do módulo introdutório do workshop. Use este conteúdo como base para criar sua apresentação.

---

## Slide 1 — Título e Objetivos

### 🎯 Workshop LangChain + MCP + Qdrant
**Módulo 01: Setup e Fundamentos**

**Objetivos Práticos:**
• Configurar ambiente completo de desenvolvimento (Python, Docker, dependências)
• Validar conectividade com todos os serviços (LLM, Qdrant, Redis) via testes automatizados

**O que você vai sair sabendo:**
- Ambiente 100% funcional para desenvolvimento de aplicações inteligentes
- Compreensão da arquitetura e papel de cada componente na stack

---

## Slide 2 — Arquitetura Macro

### 🏗️ Visão Geral da Arquitetura

```
[APLICAÇÃO] ↔ [LANGCHAIN] ↔ [LLM (OpenAI)]
     ↓              ↓
[QDRANT]        [REDIS]
(Vetores)       (Cache)
     ↑
[MCP Protocol]*
```

**Fluxo de dados:**
• **LangChain**: Orquestra interações entre LLM e ferramentas externas
• **Qdrant**: Armazena embeddings para busca semântica (RAG)
• **Redis**: Cache para sessões e respostas frequentes
• **MCP**: Conectores padronizados com sistemas externos (módulos futuros)

*MCP será aprofundado nos próximos módulos — hoje focamos no setup base.

---

## Slide 3 — O que é LangChain (Rápido)

### 🦜 LangChain em 60 Segundos

**Framework para aplicações com LLMs:**

• **Chains**: Sequências de operações (prompt → LLM → parser → ação)
• **Agents**: LLMs que decidem quais ferramentas usar e quando
• **Tools**: Integrações com APIs, bancos de dados, calculadoras, etc.
• **Memory**: Contexto persistente entre interações (conversas, RAG)

**Por que usar?**
- Abstrai complexidade de integração com múltiplos LLMs
- Padrões testados para casos comuns (RAG, chatbots, summarização)
- Ecossistema rico de integrações prontas

---

## Slide 4 — Qdrant em 30s

### 🗃️ Qdrant: Banco Vetorial de Alta Performance

**Conceitos fundamentais:**
• **Embeddings**: Representações numéricas de texto/dados (vetores)
• **Similaridade**: Busca por proximidade vetorial (cosine, euclidean)
• **Metadados**: Filtros adicionais combinados com busca vetorial
• **Collections**: Organizações lógicas de vetores com esquemas específicos

**Casos de uso:**
- Busca semântica em documentos
- Recomendações baseadas em similaridade
- RAG (Retrieval-Augmented Generation)
- Classificação e clustering de conteúdo

---

## Slide 5 — Setup que Faremos Agora

### ⚙️ Configuração Passo a Passo

**1. Environment Setup:**
• Poetry para gestão de dependências Python
• Arquivo .env para credenciais e configurações

**2. Docker Services:**
• Qdrant: Vector database (porta 6333)
• Redis: Cache e sessões (porta 6379)

**3. Verificações Automáticas:**
• Python >= 3.10 ✓
• Conectividade com OpenAI ✓
• Qdrant operacional ✓
• Redis funcionando ✓

**Comandos principais:** `make bootstrap` → `make up` → `make check`

---

## Slide 6 — Critérios de Pronto

### ✅ Como Saber que Está Funcionando

**Verificações OBRIGATÓRIAS:**
• ✅ Python 3.10+ instalado e detectado
• ✅ Dependências instaladas via Poetry
• ✅ Qdrant conectado e listando coleções
• ✅ Arquivo .env configurado corretamente

**Verificações RECOMENDADAS:**
• ⭐ OpenAI API respondendo com "OK"
• ⭐ Redis executando operações SET/GET
• ⭐ Qdrant Dashboard acessível (http://localhost:6333/dashboard)

**Comando final:** `make check` deve retornar exit code 0

**🚀 Se tudo ✅ → Próximo módulo: 02-embeddings**

---

## 💡 Dicas para Apresentação

### Timing Sugerido (20 minutos total):
- **Slide 1-2**: 3 minutos (contexto e visão geral)
- **Slide 3-4**: 4 minutos (conceitos técnicos)
- **Slide 5**: 5 minutos (demonstração ao vivo dos comandos)
- **Slide 6**: 3 minutos (critérios de sucesso)
- **Q&A**: 5 minutos

### Demonstrações ao Vivo:
1. **Terminal 1**: `make bootstrap` (mostre a saída)
2. **Terminal 2**: `make up` (mostre containers iniciando)
3. **Browser**: Qdrant Dashboard (http://localhost:6333/dashboard)
4. **Terminal 3**: `make check` (mostre report completo)

### Pontos de Atenção:
- Enfatize que este módulo é **100% setup** — nada de LLM complexo ainda
- Mencione que MCP é para módulos futuros (não confundir)
- Destaque a importância dos testes automáticos para debug
- Prepare troubleshooting para problemas comuns (porta ocupada, proxy, etc.)

---

*Slides preparados para Workshop LangChain + MCP + Qdrant | Módulo 01*