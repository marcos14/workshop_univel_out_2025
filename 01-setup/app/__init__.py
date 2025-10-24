"""
Módulo principal da aplicação do workshop LangChain + MCP + Qdrant.

Este package contém toda a lógica da aplicação, incluindo:
- Configurações (config.py)
- Testes de sanidade dos serviços (llm_sanity.py, qdrant_sanity.py, redis_sanity.py)
- Utilitários e helpers

Versão: 01-setup - Fundamentos e Primeiros Testes
"""

__version__ = "0.1.0"
__author__ = "Workshop Univel"
__description__ = "Workshop técnico: LangChain + MCP + Qdrant"

# Facilita importações diretas
from .config import get_settings, Settings

__all__ = ["get_settings", "Settings"]