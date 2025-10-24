"""
Script de verificação do ambiente - Workshop LangChain + MCP + Qdrant.

Este script executa todas as verificações de sanidade para garantir que
o ambiente está corretamente configurado e funcionando.
"""

import sys
import platform
from typing import Dict, Any, List

from app.config import get_settings, validate_environment
from app import llm_sanity, qdrant_sanity, redis_sanity


def check_python_version() -> Dict[str, Any]:
    """
    Verifica se a versão do Python atende aos requisitos mínimos.
    
    Returns:
        Dict[str, Any]: Resultado da verificação da versão Python
    """
    version_info = sys.version_info
    current_version = f"{version_info.major}.{version_info.minor}.{version_info.micro}"
    
    # Requisito mínimo: Python 3.10
    min_major, min_minor = 3, 10
    
    if version_info.major < min_major or (version_info.major == min_major and version_info.minor < min_minor):
        return {
            "status": "fail",
            "message": f"Python {current_version} detectado",
            "details": f"Mínimo requerido: {min_major}.{min_minor}.0",
            "requirement": "Python >= 3.10",
            "current": current_version
        }
    
    return {
        "status": "ok",
        "message": f"Python {current_version} ✓",
        "details": f"Sistema: {platform.system()} {platform.release()}",
        "requirement": "Python >= 3.10",
        "current": current_version
    }


def print_header():
    """Imprime cabeçalho do script."""
    print("=" * 70)
    print("  WORKSHOP LANGCHAIN + MCP + QDRANT - VERIFICAÇÃO DO AMBIENTE")
    print("=" * 70)
    print()


def print_section(title: str):
    """Imprime título de seção."""
    print(f"\n🔍 {title}")
    print("-" * (len(title) + 4))


def print_result(check_name: str, result: Dict[str, Any], required: bool = True):
    """
    Imprime resultado de uma verificação de forma padronizada.
    
    Args:
        check_name: Nome da verificação
        result: Resultado da verificação
        required: Se a verificação é obrigatória
    """
    status = result["status"]
    message = result["message"]
    details = result.get("details", "")
    
    # Determina ícone baseado no status
    if status == "ok":
        icon = "✅"
        color = ""
    elif status == "skipped":
        icon = "⏭️ "
        color = ""
    elif status == "fail":
        icon = "❌"
        color = ""
    else:
        icon = "⚠️ "
        color = ""
    
    # Imprime resultado
    requirement_text = " (OBRIGATÓRIO)" if required else " (OPCIONAL)"
    print(f"{icon} {check_name}{requirement_text}")
    print(f"   {message}")
    
    if details:
        print(f"   {details}")
    
    # Imprime erro se presente
    if result.get("error"):
        print(f"   Erro: {result['error']}")
    
    # Imprime sugestão se presente
    if result.get("suggestion"):
        print(f"   💡 {result['suggestion']}")


def run_all_checks() -> tuple[bool, Dict[str, Any]]:
    """
    Executa todas as verificações de sanidade.
    
    Returns:
        tuple: (success, results_summary)
    """
    print_header()
    
    results = {}
    
    # ==========================================
    # VERIFICAÇÕES BÁSICAS
    # ==========================================
    print_section("VERIFICAÇÕES BÁSICAS")
    
    # Python
    python_result = check_python_version()
    print_result("Python", python_result, required=True)
    results["python"] = python_result
    
    # Configuração
    settings = get_settings()
    is_valid, config_errors = validate_environment()
    
    config_result = {
        "status": "ok" if is_valid else "fail",
        "message": "Configuração validada" if is_valid else "Problemas na configuração",
        "details": f"Arquivo .env {'✓' if settings else '❌'}",
        "errors": config_errors if not is_valid else None
    }
    print_result("Configuração", config_result, required=True)
    results["config"] = config_result
    
    if config_errors:
        print("   Problemas encontrados:")
        for error in config_errors:
            print(f"     • {error}")
    
    # ==========================================
    # VERIFICAÇÕES DE SERVIÇOS
    # ==========================================
    print_section("VERIFICAÇÕES DE SERVIÇOS")
    
    # Qdrant (obrigatório)
    print("🗃️  Testando Qdrant...")
    qdrant_result = qdrant_sanity.check_connection()
    print_result("Qdrant", qdrant_result, required=True)
    results["qdrant"] = qdrant_result
    
    # Redis (opcional)
    print("\n🔄 Testando Redis...")
    redis_result = redis_sanity.roundtrip()
    print_result("Redis", redis_result, required=False)
    results["redis"] = redis_result
    
    # LLM (recomendado)
    print("\n🧠 Testando LLM...")
    llm_result = llm_sanity.hello()
    print_result("LLM (OpenAI)", llm_result, required=False)
    results["llm"] = llm_result
    
    # ==========================================
    # RESUMO FINAL
    # ==========================================
    print_section("RESUMO FINAL")
    
    # Conta sucessos e falhas
    critical_checks = ["python", "config", "qdrant"]  # Verificações críticas
    optional_checks = ["redis", "llm"]  # Verificações opcionais
    
    critical_passed = all(results[check]["status"] == "ok" for check in critical_checks)
    optional_passed = sum(1 for check in optional_checks if results[check]["status"] == "ok")
    optional_skipped = sum(1 for check in optional_checks if results[check]["status"] == "skipped")
    
    print(f"📊 CRÍTICOS: {len([c for c in critical_checks if results[c]['status'] == 'ok'])}/{len(critical_checks)} ✅")
    print(f"📊 OPCIONAIS: {optional_passed}/{len(optional_checks)} ✅ ({optional_skipped} pulados)")
    
    if critical_passed:
        print("\n🎉 AMBIENTE PRONTO PARA O WORKSHOP!")
        print("   Todos os componentes críticos estão funcionando.")
        
        if optional_passed < len(optional_checks):
            print("\n💡 RECOMENDAÇÕES:")
            if results["llm"]["status"] != "ok":
                print("   • Configure OPENAI_API_KEY para testar LLM")
            if results["redis"]["status"] != "ok":
                print("   • Execute 'make up' para iniciar Redis")
        
        print("\n🚀 PRÓXIMOS PASSOS:")
        print("   1. Continue para o módulo 02-embeddings")
        print("   2. Ou explore os dados do Qdrant: http://localhost:6333/dashboard")
        
    else:
        print("\n❌ AMBIENTE NÃO ESTÁ PRONTO")
        print("   Resolva os problemas críticos antes de continuar.")
        
        failed_critical = [check for check in critical_checks if results[check]["status"] != "ok"]
        print(f"\n🔧 RESOLVA PRIMEIRO:")
        for check in failed_critical:
            print(f"   • {check.upper()}: {results[check]['message']}")
    
    return critical_passed, results


def main():
    """Função principal do script."""
    try:
        success, results = run_all_checks()
        
        # Exit code baseado no sucesso das verificações críticas
        exit_code = 0 if success else 1
        
        print(f"\n{'='*70}")
        print(f"Exit code: {exit_code} ({'SUCCESS' if success else 'FAILURE'})")
        
        sys.exit(exit_code)
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Verificação interrompida pelo usuário.")
        sys.exit(130)
        
    except Exception as e:
        print(f"\n❌ Erro inesperado durante verificação: {e}")
        import traceback
        print("\nTraceback completo:")
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()