"""
Testes de sanidade para Qdrant (Vector Database).

Este módulo verifica se a conexão com o Qdrant está funcionando corretamente,
testando conectividade, listagem de coleções e operações básicas.
"""

import traceback
from typing import Dict, Any, List

from app.config import get_settings

try:
    from qdrant_client import QdrantClient
    from qdrant_client.http.exceptions import UnexpectedResponse
    QDRANT_AVAILABLE = True
except ImportError:
    QDRANT_AVAILABLE = False


def check_connection() -> Dict[str, Any]:
    """
    Verifica a conectividade básica com o Qdrant.
    
    Tenta conectar e listar coleções existentes.
    
    Returns:
        Dict[str, Any]: Resultado do teste com status e detalhes
    """
    settings = get_settings()
    
    # Verifica se qdrant-client está disponível
    if not QDRANT_AVAILABLE:
        return {
            "status": "fail",
            "message": "qdrant-client não está instalado",
            "details": "Execute: poetry install",
            "error": "ImportError: qdrant_client"
        }
    
    try:
        # Cria cliente Qdrant
        client = QdrantClient(
            url=settings.QDRANT_URL,
            api_key=settings.QDRANT_API_KEY if settings.has_qdrant_key else None,
            timeout=settings.REQUEST_TIMEOUT
        )
        
        # Testa conectividade listando coleções
        collections = client.get_collections()
        collection_names = [col.name for col in collections.collections]
        
        return {
            "status": "ok",
            "message": "Conectado ao Qdrant com sucesso",
            "details": f"URL: {settings.QDRANT_URL} | Coleções: {len(collection_names)}",
            "error": None,
            "collections": collection_names,
            "total_collections": len(collection_names)
        }
        
    except Exception as e:
        error_msg = str(e)
        
        # Trata erros específicos do Qdrant
        if "connection" in error_msg.lower() or "refused" in error_msg.lower():
            return {
                "status": "fail",
                "message": "Não foi possível conectar ao Qdrant",
                "details": f"Verifique se o serviço está rodando: docker compose up -d",
                "error": error_msg,
                "suggestion": "Execute: make up"
            }
        elif "timeout" in error_msg.lower():
            return {
                "status": "fail",
                "message": "Timeout na conexão com Qdrant",
                "details": "O Qdrant pode estar inicializando. Aguarde alguns segundos.",
                "error": error_msg
            }
        elif "authentication" in error_msg.lower() or "401" in error_msg:
            return {
                "status": "fail",
                "message": "Erro de autenticação com Qdrant",
                "details": "Verifique a QDRANT_API_KEY no arquivo .env",
                "error": error_msg
            }
        elif "404" in error_msg or "not found" in error_msg.lower():
            return {
                "status": "fail",
                "message": "Qdrant não encontrado na URL configurada",
                "details": f"Verifique QDRANT_URL: {settings.QDRANT_URL}",
                "error": error_msg
            }
        else:
            return {
                "status": "fail",
                "message": "Erro inesperado ao conectar com Qdrant",
                "details": f"Erro: {error_msg}",
                "error": error_msg,
                "traceback": traceback.format_exc()
            }


def check_health() -> Dict[str, Any]:
    """
    Verifica o status de saúde do Qdrant.
    
    Returns:
        Dict[str, Any]: Informações detalhadas sobre o estado do Qdrant
    """
    settings = get_settings()
    
    if not QDRANT_AVAILABLE:
        return {
            "status": "fail",
            "message": "qdrant-client não disponível"
        }
    
    try:
        client = QdrantClient(
            url=settings.QDRANT_URL,
            api_key=settings.QDRANT_API_KEY if settings.has_qdrant_key else None,
            timeout=settings.REQUEST_TIMEOUT
        )
        
        # Obtém informações sobre as coleções
        collections = client.get_collections()
        
        # Obtém informações sobre cada coleção
        collection_details = []
        for collection in collections.collections:
            try:
                info = client.get_collection(collection.name)
                collection_details.append({
                    "name": collection.name,
                    "vectors_count": info.vectors_count,
                    "indexed_vectors_count": info.indexed_vectors_count,
                    "points_count": info.points_count,
                    "status": info.status
                })
            except Exception as e:
                collection_details.append({
                    "name": collection.name,
                    "error": str(e)
                })
        
        return {
            "status": "ok",
            "message": "Qdrant operacional",
            "details": f"Servidor funcionando com {len(collections.collections)} coleções",
            "collections": collection_details,
            "total_collections": len(collections.collections)
        }
        
    except Exception as e:
        return {
            "status": "fail",
            "message": "Erro ao verificar saúde do Qdrant",
            "error": str(e)
        }


def test_basic_operations() -> Dict[str, Any]:
    """
    Testa operações básicas do Qdrant (criar/deletar coleção de teste).
    
    Returns:
        Dict[str, Any]: Resultado dos testes de operações básicas
    """
    settings = get_settings()
    test_collection = "workshop_test_collection"
    
    if not QDRANT_AVAILABLE:
        return {
            "status": "skipped",
            "message": "qdrant-client não disponível"
        }
    
    try:
        client = QdrantClient(
            url=settings.QDRANT_URL,
            api_key=settings.QDRANT_API_KEY if settings.has_qdrant_key else None,
            timeout=settings.REQUEST_TIMEOUT
        )
        
        operations_log = []
        
        # Limpa coleção de teste se existir
        try:
            client.delete_collection(test_collection)
            operations_log.append("✅ Limpeza de coleção existente")
        except:
            operations_log.append("ℹ️  Nenhuma coleção anterior para limpar")
        
        # Cria coleção de teste
        try:
            from qdrant_client.models import Distance, VectorParams
            
            client.create_collection(
                collection_name=test_collection,
                vectors_config=VectorParams(size=4, distance=Distance.COSINE)
            )
            operations_log.append("✅ Criação de coleção")
        except Exception as e:
            operations_log.append(f"❌ Falha na criação: {str(e)}")
            raise
        
        # Verifica se a coleção foi criada
        try:
            info = client.get_collection(test_collection)
            operations_log.append(f"✅ Verificação da coleção: {info.status}")
        except Exception as e:
            operations_log.append(f"❌ Falha na verificação: {str(e)}")
            raise
        
        # Remove coleção de teste
        try:
            client.delete_collection(test_collection)
            operations_log.append("✅ Remoção da coleção de teste")
        except Exception as e:
            operations_log.append(f"⚠️ Falha na remoção: {str(e)}")
        
        return {
            "status": "ok",
            "message": "Operações básicas funcionando",
            "operations": operations_log,
            "details": "Criação, verificação e remoção de coleção bem-sucedidas"
        }
        
    except Exception as e:
        return {
            "status": "fail",
            "message": "Falha nas operações básicas",
            "operations": operations_log,
            "error": str(e)
        }


if __name__ == "__main__":
    """Execução direta para teste rápido."""
    print("🗃️  Testando conectividade com Qdrant...")
    print()
    
    # Teste de conexão
    result = check_connection()
    
    print(f"Status: {result['status']}")
    print(f"Mensagem: {result['message']}")
    print(f"Detalhes: {result['details']}")
    
    if result['status'] == 'ok':
        print(f"Coleções encontradas: {result['collections']}")
    
    if result['error']:
        print(f"Erro: {result['error']}")
        if 'suggestion' in result:
            print(f"Sugestão: {result['suggestion']}")
    
    print()
    
    # Teste de saúde se a conexão passou
    if result['status'] == 'ok':
        print("🏥 Verificando saúde do Qdrant...")
        health_result = check_health()
        
        print(f"Status: {health_result['status']}")
        print(f"Mensagem: {health_result['message']}")
        
        if 'collections' in health_result:
            for col in health_result['collections']:
                if 'error' not in col:
                    print(f"   📁 {col['name']}: {col['points_count']} pontos")
                else:
                    print(f"   ❌ {col['name']}: {col['error']}")
        
        print()
        
        # Teste de operações básicas
        print("⚙️  Testando operações básicas...")
        ops_result = test_basic_operations()
        
        print(f"Status: {ops_result['status']}")
        print(f"Mensagem: {ops_result['message']}")
        
        if 'operations' in ops_result:
            for op in ops_result['operations']:
                print(f"   {op}")
    
    print("\n" + "="*50)