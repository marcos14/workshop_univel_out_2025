"""
Testes de sanidade para LLM (Large Language Model).

Este módulo verifica se a integração com o LLM está funcionando corretamente,
testando a conectividade e resposta básica do modelo.
"""

import traceback
from typing import Dict, Any

from app.config import get_settings

try:
    from langchain_openai import ChatOpenAI
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False


def hello() -> Dict[str, Any]:
    """
    Testa conectividade básica com o LLM.
    
    Envia um prompt simples e verifica se a resposta contém "OK".
    
    Returns:
        Dict[str, Any]: Resultado do teste com status e detalhes
    """
    settings = get_settings()
    
    # Verifica se LangChain está disponível
    if not LANGCHAIN_AVAILABLE:
        return {
            "status": "fail",
            "message": "LangChain não está instalado",
            "details": "Execute: poetry install",
            "error": "ImportError: langchain_openai"
        }
    
    # Verifica se a chave está configurada
    if not settings.has_openai_key:
        return {
            "status": "skipped",
            "message": "OPENAI_API_KEY não configurado",
            "details": "Configure a chave no arquivo .env para testar o LLM",
            "error": None
        }
    
    try:
        # Cria cliente OpenAI com modelo barato para testes
        llm = ChatOpenAI(
            model="gpt-4o-mini",  # Modelo mais barato para testes
            temperature=0,        # Resposta determinística
            api_key=settings.OPENAI_API_KEY,
            timeout=settings.REQUEST_TIMEOUT
        )
        
        # Prompt simples para teste
        prompt = "Responda exatamente 'OK' para confirmar que está funcionando."
        
        # Envia prompt e obtém resposta
        response = llm.invoke(prompt)
        response_text = response.content.strip()
        
        # Verifica se a resposta contém "OK"
        if "OK" in response_text.upper():
            return {
                "status": "ok",
                "message": "LLM respondeu corretamente",
                "details": f"Modelo: gpt-4o-mini | Resposta: '{response_text}'",
                "error": None,
                "response": response_text
            }
        else:
            return {
                "status": "fail",
                "message": "LLM não respondeu conforme esperado",
                "details": f"Esperado: 'OK' | Recebido: '{response_text}'",
                "error": "Resposta inesperada",
                "response": response_text
            }
            
    except Exception as e:
        error_msg = str(e)
        
        # Trata erros específicos da OpenAI
        if "authentication" in error_msg.lower() or "401" in error_msg:
            return {
                "status": "fail",
                "message": "Erro de autenticação com OpenAI",
                "details": "Verifique se a OPENAI_API_KEY está correta",
                "error": error_msg
            }
        elif "rate_limit" in error_msg.lower() or "429" in error_msg:
            return {
                "status": "fail",
                "message": "Limite de requisições excedido",
                "details": "Aguarde alguns minutos e tente novamente",
                "error": error_msg
            }
        elif "timeout" in error_msg.lower():
            return {
                "status": "fail",
                "message": "Timeout na conexão com OpenAI",
                "details": "Verifique sua conexão com a internet",
                "error": error_msg
            }
        else:
            return {
                "status": "fail",
                "message": "Erro inesperado ao conectar com LLM",
                "details": f"Erro: {error_msg}",
                "error": error_msg,
                "traceback": traceback.format_exc()
            }


def test_different_prompts() -> Dict[str, Any]:
    """
    Testa o LLM com diferentes tipos de prompts para validação mais robusta.
    
    Returns:
        Dict[str, Any]: Resultado dos testes múltiplos
    """
    settings = get_settings()
    
    if not settings.has_openai_key:
        return {
            "status": "skipped",
            "message": "OPENAI_API_KEY não configurado",
            "tests": []
        }
    
    if not LANGCHAIN_AVAILABLE:
        return {
            "status": "fail",
            "message": "LangChain não disponível",
            "tests": []
        }
    
    try:
        llm = ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0,
            api_key=settings.OPENAI_API_KEY,
            timeout=settings.REQUEST_TIMEOUT
        )
        
        # Diferentes prompts para teste
        test_prompts = [
            {
                "name": "Matemática simples",
                "prompt": "Quanto é 2 + 2? Responda apenas o número.",
                "expected": "4"
            },
            {
                "name": "Pergunta sobre LangChain",
                "prompt": "O que é LangChain? Responda em uma frase.",
                "expected": "langchain"  # Deve conter a palavra
            },
            {
                "name": "Instrução JSON",
                "prompt": "Responda em formato JSON: {'status': 'working'}",
                "expected": "status"  # Deve conter a palavra
            }
        ]
        
        results = []
        all_passed = True
        
        for test in test_prompts:
            try:
                response = llm.invoke(test["prompt"])
                response_text = response.content.strip()
                
                # Verifica se a resposta contém o esperado
                passed = test["expected"].lower() in response_text.lower()
                all_passed &= passed
                
                results.append({
                    "name": test["name"],
                    "prompt": test["prompt"],
                    "response": response_text,
                    "expected": test["expected"],
                    "passed": passed
                })
                
            except Exception as e:
                all_passed = False
                results.append({
                    "name": test["name"],
                    "prompt": test["prompt"],
                    "response": None,
                    "expected": test["expected"],
                    "passed": False,
                    "error": str(e)
                })
        
        return {
            "status": "ok" if all_passed else "partial",
            "message": f"Testes concluídos: {sum(1 for r in results if r['passed'])}/{len(results)} passaram",
            "tests": results,
            "all_passed": all_passed
        }
        
    except Exception as e:
        return {
            "status": "fail",
            "message": "Erro geral nos testes múltiplos",
            "error": str(e),
            "tests": []
        }


if __name__ == "__main__":
    """Execução direta para teste rápido."""
    print("🧠 Testando conectividade com LLM...")
    print()
    
    # Teste básico
    result = hello()
    
    print(f"Status: {result['status']}")
    print(f"Mensagem: {result['message']}")
    print(f"Detalhes: {result['details']}")
    
    if result['error']:
        print(f"Erro: {result['error']}")
    
    print()
    
    # Testes múltiplos se o básico passou
    if result['status'] == 'ok':
        print("🔄 Executando testes adicionais...")
        multi_result = test_different_prompts()
        
        print(f"Status: {multi_result['status']}")
        print(f"Mensagem: {multi_result['message']}")
        
        for test in multi_result['tests']:
            status_icon = "✅" if test['passed'] else "❌"
            print(f"   {status_icon} {test['name']}")
            if 'error' in test:
                print(f"      Erro: {test['error']}")
    
    print("\n" + "="*50)