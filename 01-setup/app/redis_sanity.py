"""
Testes de sanidade para Redis (Cache e Sessões).

Este módulo verifica se a conexão com o Redis está funcionando corretamente,
testando conectividade, operações básicas de SET/GET e performance.
"""

import time
import traceback
from typing import Dict, Any

from app.config import get_settings

try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False


def roundtrip() -> Dict[str, Any]:
    """
    Testa conectividade básica com Redis fazendo um roundtrip SET/GET.
    
    Returns:
        Dict[str, Any]: Resultado do teste com status e detalhes
    """
    settings = get_settings()
    
    # Verifica se redis está disponível
    if not REDIS_AVAILABLE:
        return {
            "status": "fail",
            "message": "redis não está instalado",
            "details": "Execute: poetry install",
            "error": "ImportError: redis"
        }
    
    # Verifica se Redis está configurado
    if not settings.has_redis_url:
        return {
            "status": "skipped",
            "message": "REDIS_URL não configurado",
            "details": "Configure REDIS_URL no .env ou inicie: make up",
            "error": None
        }
    
    try:
        # Cria cliente Redis
        client = redis.from_url(
            settings.REDIS_URL,
            socket_timeout=settings.REQUEST_TIMEOUT,
            socket_connect_timeout=settings.REQUEST_TIMEOUT,
            decode_responses=True  # Retorna strings em vez de bytes
        )
        
        # Testa conectividade com ping
        ping_start = time.time()
        ping_result = client.ping()
        ping_time = (time.time() - ping_start) * 1000  # em ms
        
        if not ping_result:
            return {
                "status": "fail",
                "message": "Redis não respondeu ao ping",
                "details": "Servidor pode estar down ou indisponível",
                "error": "Ping failed"
            }
        
        # Testa operação SET/GET
        test_key = "workshop:ping"
        test_value = f"test_{int(time.time())}"
        
        set_start = time.time()
        client.set(test_key, test_value, ex=60)  # Expira em 60 segundos
        set_time = (time.time() - set_start) * 1000
        
        get_start = time.time()
        retrieved_value = client.get(test_key)
        get_time = (time.time() - get_start) * 1000
        
        # Verifica se o valor foi armazenado e recuperado corretamente
        if retrieved_value != test_value:
            return {
                "status": "fail",
                "message": "Falha no roundtrip SET/GET",
                "details": f"Esperado: '{test_value}' | Recebido: '{retrieved_value}'",
                "error": "Data mismatch"
            }
        
        # Limpa chave de teste
        client.delete(test_key)
        
        return {
            "status": "ok",
            "message": "Redis funcionando corretamente",
            "details": f"Ping: {ping_time:.1f}ms | SET: {set_time:.1f}ms | GET: {get_time:.1f}ms",
            "error": None,
            "performance": {
                "ping_ms": round(ping_time, 1),
                "set_ms": round(set_time, 1),
                "get_ms": round(get_time, 1)
            }
        }
        
    except Exception as e:
        error_msg = str(e)
        
        # Trata erros específicos do Redis
        if "connection" in error_msg.lower() or "refused" in error_msg.lower():
            return {
                "status": "fail",
                "message": "Não foi possível conectar ao Redis",
                "details": "Verifique se o Redis está rodando: docker compose up -d",
                "error": error_msg,
                "suggestion": "Execute: make up"
            }
        elif "timeout" in error_msg.lower():
            return {
                "status": "fail",
                "message": "Timeout na conexão com Redis",
                "details": "Redis pode estar sobrecarregado ou indisponível",
                "error": error_msg
            }
        elif "authentication" in error_msg.lower() or "auth" in error_msg.lower():
            return {
                "status": "fail",
                "message": "Erro de autenticação com Redis",
                "details": "Verifique as credenciais na REDIS_URL",
                "error": error_msg
            }
        else:
            return {
                "status": "fail",
                "message": "Erro inesperado ao conectar com Redis",
                "details": f"Erro: {error_msg}",
                "error": error_msg,
                "traceback": traceback.format_exc()
            }


def check_info() -> Dict[str, Any]:
    """
    Obtém informações detalhadas sobre o Redis.
    
    Returns:
        Dict[str, Any]: Informações sobre configuração e estado do Redis
    """
    settings = get_settings()
    
    if not REDIS_AVAILABLE:
        return {
            "status": "fail",
            "message": "redis não disponível"
        }
    
    if not settings.has_redis_url:
        return {
            "status": "skipped",
            "message": "REDIS_URL não configurado"
        }
    
    try:
        client = redis.from_url(
            settings.REDIS_URL,
            socket_timeout=settings.REQUEST_TIMEOUT,
            decode_responses=True
        )
        
        # Obtém informações do servidor
        info = client.info()
        
        # Extrai informações relevantes
        relevant_info = {
            "version": info.get("redis_version", "unknown"),
            "mode": info.get("redis_mode", "unknown"),
            "uptime_seconds": info.get("uptime_in_seconds", 0),
            "connected_clients": info.get("connected_clients", 0),
            "used_memory_human": info.get("used_memory_human", "unknown"),
            "total_commands_processed": info.get("total_commands_processed", 0),
            "keyspace": {}
        }
        
        # Informações sobre databases
        for key, value in info.items():
            if key.startswith("db"):
                relevant_info["keyspace"][key] = value
        
        return {
            "status": "ok",
            "message": "Informações do Redis obtidas",
            "details": f"Redis {relevant_info['version']} | Uptime: {relevant_info['uptime_seconds']}s",
            "info": relevant_info
        }
        
    except Exception as e:
        return {
            "status": "fail",
            "message": "Erro ao obter informações do Redis",
            "error": str(e)
        }


def test_performance() -> Dict[str, Any]:
    """
    Testa performance básica do Redis com múltiplas operações.
    
    Returns:
        Dict[str, Any]: Resultado dos testes de performance
    """
    settings = get_settings()
    
    if not REDIS_AVAILABLE or not settings.has_redis_url:
        return {
            "status": "skipped",
            "message": "Redis não disponível ou não configurado"
        }
    
    try:
        client = redis.from_url(
            settings.REDIS_URL,
            socket_timeout=settings.REQUEST_TIMEOUT,
            decode_responses=True
        )
        
        # Número de operações para teste
        num_operations = 100
        test_prefix = f"workshop:perf:{int(time.time())}"
        
        # Teste de SET
        set_start = time.time()
        for i in range(num_operations):
            client.set(f"{test_prefix}:{i}", f"value_{i}", ex=300)  # 5 minutos
        set_total = time.time() - set_start
        
        # Teste de GET
        get_start = time.time()
        for i in range(num_operations):
            client.get(f"{test_prefix}:{i}")
        get_total = time.time() - get_start
        
        # Teste de DELETE
        delete_start = time.time()
        keys_to_delete = [f"{test_prefix}:{i}" for i in range(num_operations)]
        client.delete(*keys_to_delete)
        delete_total = time.time() - delete_start
        
        # Calcula estatísticas
        set_avg = (set_total / num_operations) * 1000  # ms por operação
        get_avg = (get_total / num_operations) * 1000
        delete_avg = (delete_total / num_operations) * 1000
        
        return {
            "status": "ok",
            "message": f"Performance testada com {num_operations} operações",
            "details": f"SET: {set_avg:.2f}ms/op | GET: {get_avg:.2f}ms/op | DEL: {delete_avg:.2f}ms/op",
            "performance": {
                "operations_count": num_operations,
                "set_total_ms": round(set_total * 1000, 2),
                "get_total_ms": round(get_total * 1000, 2),
                "delete_total_ms": round(delete_total * 1000, 2),
                "set_avg_ms": round(set_avg, 2),
                "get_avg_ms": round(get_avg, 2),
                "delete_avg_ms": round(delete_avg, 2)
            }
        }
        
    except Exception as e:
        return {
            "status": "fail",
            "message": "Erro no teste de performance",
            "error": str(e)
        }


if __name__ == "__main__":
    """Execução direta para teste rápido."""
    print("🔄 Testando conectividade com Redis...")
    print()
    
    # Teste básico de roundtrip
    result = roundtrip()
    
    print(f"Status: {result['status']}")
    print(f"Mensagem: {result['message']}")
    print(f"Detalhes: {result['details']}")
    
    if result['status'] == 'ok' and 'performance' in result:
        perf = result['performance']
        print(f"Performance:")
        print(f"   Ping: {perf['ping_ms']}ms")
        print(f"   SET: {perf['set_ms']}ms")
        print(f"   GET: {perf['get_ms']}ms")
    
    if result['error']:
        print(f"Erro: {result['error']}")
        if 'suggestion' in result:
            print(f"Sugestão: {result['suggestion']}")
    
    print()
    
    # Informações do servidor se conectado
    if result['status'] == 'ok':
        print("ℹ️  Obtendo informações do Redis...")
        info_result = check_info()
        
        print(f"Status: {info_result['status']}")
        print(f"Mensagem: {info_result['message']}")
        
        if 'info' in info_result:
            info = info_result['info']
            print(f"   Versão: {info['version']}")
            print(f"   Uptime: {info['uptime_seconds']}s")
            print(f"   Clientes conectados: {info['connected_clients']}")
            print(f"   Memória usada: {info['used_memory_human']}")
        
        print()
        
        # Teste de performance
        print("⚡ Testando performance...")
        perf_result = test_performance()
        
        print(f"Status: {perf_result['status']}")
        print(f"Mensagem: {perf_result['message']}")
        
        if 'performance' in perf_result:
            perf = perf_result['performance']
            print(f"   Operações: {perf['operations_count']}")
            print(f"   SET médio: {perf['set_avg_ms']}ms")
            print(f"   GET médio: {perf['get_avg_ms']}ms")
            print(f"   DELETE médio: {perf['delete_avg_ms']}ms")
    
    print("\n" + "="*50)