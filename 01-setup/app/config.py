"""
Módulo de configuração do workshop - Carregamento e validação de variáveis de ambiente.

Este módulo centraliza toda a configuração da aplicação, carregando variáveis
de ambiente do arquivo .env e validando-as usando Pydantic.
"""

import os
from functools import lru_cache
from typing import Optional

from dotenv import load_dotenv
from pydantic import BaseModel, Field


# Carrega variáveis de ambiente do arquivo .env
load_dotenv()


class Settings(BaseModel):
    """
    Configurações da aplicação com validação via Pydantic.
    
    Todas as configurações são carregadas de variáveis de ambiente,
    permitindo fácil customização sem alteração de código.
    """
    
    # ==========================================
    # LLM (Large Language Model)
    # ==========================================
    OPENAI_API_KEY: Optional[str] = Field(
        default=None,
        description="Chave da API OpenAI para testes de LLM"
    )
    
    # ==========================================
    # QDRANT (Vector Database)
    # ==========================================
    QDRANT_URL: str = Field(
        default="http://localhost:6333",
        description="URL do servidor Qdrant"
    )
    
    QDRANT_API_KEY: Optional[str] = Field(
        default=None,
        description="Chave de API do Qdrant (opcional para desenvolvimento local)"
    )
    
    # ==========================================
    # REDIS (Cache e Sessões)
    # ==========================================
    REDIS_URL: Optional[str] = Field(
        default="redis://localhost:6379/0",
        description="URL de conexão com Redis"
    )
    
    # ==========================================
    # CONFIGURAÇÕES GERAIS
    # ==========================================
    LOG_LEVEL: str = Field(
        default="INFO",
        description="Nível de log (DEBUG, INFO, WARNING, ERROR)"
    )
    
    REQUEST_TIMEOUT: int = Field(
        default=30,
        description="Timeout para requisições externas em segundos"
    )
    
    class Config:
        """Configurações do Pydantic."""
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True
        
        # Permite campos extras (flexibilidade para desenvolvimento)
        extra = "allow"
    
    def __str__(self) -> str:
        """Representação string das configurações (sem expor segredos)."""
        return (
            f"Settings("
            f"QDRANT_URL={self.QDRANT_URL}, "
            f"REDIS_URL={self.REDIS_URL}, "
            f"LOG_LEVEL={self.LOG_LEVEL}, "
            f"OPENAI_API_KEY={'***' if self.OPENAI_API_KEY else 'None'}"
            f")"
        )
    
    @property
    def has_openai_key(self) -> bool:
        """Verifica se a chave OpenAI está configurada."""
        return bool(self.OPENAI_API_KEY and self.OPENAI_API_KEY.strip())
    
    @property
    def has_qdrant_key(self) -> bool:
        """Verifica se a chave Qdrant está configurada."""
        return bool(self.QDRANT_API_KEY and self.QDRANT_API_KEY.strip())
    
    @property
    def has_redis_url(self) -> bool:
        """Verifica se a URL do Redis está configurada."""
        return bool(self.REDIS_URL and self.REDIS_URL.strip())


@lru_cache()
def get_settings() -> Settings:
    """
    Retorna as configurações da aplicação com cache.
    
    Usa @lru_cache para garantir que as configurações sejam carregadas
    apenas uma vez durante a execução da aplicação.
    
    Returns:
        Settings: Instância das configurações validadas
    """
    return Settings()


def validate_environment() -> tuple[bool, list[str]]:
    """
    Valida se o ambiente está corretamente configurado.
    
    Returns:
        tuple: (is_valid, error_messages)
            - is_valid: True se todas as configurações obrigatórias estão presentes
            - error_messages: Lista de mensagens de erro (vazia se válido)
    """
    errors = []
    settings = get_settings()
    
    # Verifica se arquivo .env existe
    if not os.path.exists(".env"):
        errors.append("Arquivo .env não encontrado. Execute 'make bootstrap' primeiro.")
    
    # Qdrant é obrigatório para o workshop
    if not settings.QDRANT_URL:
        errors.append("QDRANT_URL não configurado no arquivo .env")
    
    # OpenAI é recomendado mas não obrigatório
    if not settings.has_openai_key:
        errors.append("OPENAI_API_KEY não configurado (testes de LLM serão pulados)")
    
    # Valida formato da URL do Redis se configurada
    if settings.REDIS_URL and not settings.REDIS_URL.startswith("redis://"):
        errors.append("REDIS_URL deve começar com 'redis://'")
    
    return len(errors) == 0, errors


def print_configuration_summary():
    """
    Imprime um resumo das configurações carregadas.
    
    Útil para debug e verificação do ambiente.
    """
    settings = get_settings()
    
    print("=" * 50)
    print("  CONFIGURAÇÕES DO WORKSHOP")
    print("=" * 50)
    print(f"🔧 LOG_LEVEL: {settings.LOG_LEVEL}")
    print(f"⏱️  REQUEST_TIMEOUT: {settings.REQUEST_TIMEOUT}s")
    print()
    print("🧠 LLM (Large Language Model):")
    print(f"   OpenAI API Key: {'✅ Configurado' if settings.has_openai_key else '❌ Não configurado'}")
    print()
    print("🗃️  QDRANT (Vector Database):")
    print(f"   URL: {settings.QDRANT_URL}")
    print(f"   API Key: {'✅ Configurado' if settings.has_qdrant_key else '❌ Não configurado'}")
    print()
    print("🔄 REDIS (Cache):")
    print(f"   URL: {settings.REDIS_URL if settings.has_redis_url else '❌ Não configurado'}")
    print("=" * 50)


if __name__ == "__main__":
    # Execução direta do módulo para teste
    print("🔍 Testando configurações...")
    print()
    
    try:
        settings = get_settings()
        print("✅ Configurações carregadas com sucesso!")
        print()
        print_configuration_summary()
        
        print()
        is_valid, errors = validate_environment()
        
        if is_valid:
            print("✅ Ambiente configurado corretamente!")
        else:
            print("⚠️  Problemas encontrados:")
            for error in errors:
                print(f"   - {error}")
                
    except Exception as e:
        print(f"❌ Erro ao carregar configurações: {e}")