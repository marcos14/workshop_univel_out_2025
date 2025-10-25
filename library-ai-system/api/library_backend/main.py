from fastapi import FastAPI, File, UploadFile, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
import os
import logging
from contextlib import asynccontextmanager

from .database import get_db, create_tables
from .routes import books, chat, auth, users, tasks
from .services.qdrant_service import QdrantService

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

security = HTTPBearer()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle events para inicialização e cleanup"""
    # Startup
    logger.info("🚀 Iniciando Biblioteca AI System...")
    
    # Criar tabelas do banco de dados
    create_tables()
    logger.info("✅ Tabelas do banco de dados criadas/verificadas")
    
    # TEMPORARIAMENTE DESABILITADO: Inicialização do Qdrant (causa travamento)
    # qdrant_service = QdrantService()
    # await qdrant_service.initialize()
    # logger.info("✅ Qdrant inicializado")
    logger.info("⚠️ Qdrant temporariamente desabilitado para evitar travamento")
    
    # Criar diretórios necessários
    os.makedirs(os.getenv("UPLOAD_DIR", "/app/uploads"), exist_ok=True)
    os.makedirs(os.getenv("LOG_DIR", "/app/logs"), exist_ok=True)
    
    logger.info("🎉 Sistema iniciado com sucesso!")
    
    yield
    
    # Shutdown
    logger.info("🔄 Encerrando sistema...")

# Criar aplicação FastAPI
app = FastAPI(
    title="Biblioteca AI System",
    description="Sistema de biblioteca inteligente com IA para conversar com livros em PDF",
    version="1.0.0",
    lifespan=lifespan
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Em produção, especificar domínios
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check
@app.get("/health")
async def health_check():
    """Endpoint de verificação de saúde do sistema"""
    return {"status": "healthy", "service": "Library AI System"}

# Incluir rotas
app.include_router(auth.router, prefix="/auth", tags=["Autenticação"])
app.include_router(users.router, prefix="/users", tags=["Usuários"])
app.include_router(books.router, prefix="/books", tags=["Livros"])
app.include_router(chat.router, prefix="/chat", tags=["Chat com IA"])
app.include_router(tasks.router, prefix="/tasks", tags=["Tasks Assíncronas"])

# Rota de boas-vindas
@app.get("/")
async def root():
    """Endpoint raiz com informações do sistema"""
    return {
        "message": "🤖 Biblioteca AI System - Bibliotecária Virtual",
        "description": "Sistema inteligente para conversar com livros em PDF usando IA",
        "features": [
            "📚 Upload e processamento de PDFs",
            "🔍 Busca semântica em livros",
            "💬 Chat com IA sobre conteúdo dos livros",
            "📊 Recomendações personalizadas",
            "📈 Analytics de interações"
        ],
        "endpoints": {
            "health": "/health",
            "docs": "/docs",
            "auth": "/auth",
            "books": "/books",
            "chat": "/chat"
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)