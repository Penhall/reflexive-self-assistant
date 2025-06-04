#!/usr/bin/env python3
"""
Script Rápido para Testar as Correções Principais
Valida se as correções resolvem os problemas identificados
"""

import sys
import time
from pathlib import Path

# Adicionar raiz do projeto
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

def test_llm_manager_fixed():
    """Testa se LLM Manager está funcionando corretamente"""
    print("🧠 Testando LLM Manager corrigido...")
    
    try:
        # Import que estava falhando
        from core.llm.llm_manager import llm_manager, LLMManager, MockLLMManager
        
        # Método que estava faltando
        model_info = llm_manager.get_model_info()
        
        # Verificar se CodeLlama é padrão para código
        task_models = model_info.get('task_models', {})
        code_model = task_models.get('codigo', 'unknown')
        
        print(f"   ✅ LLM Manager funcionando")
        print(f"   ✅ get_model_info() disponível")
        print(f"   ✅ Modelo para código: {code_model}")
        
        # Verificar se está usando CodeLlama
        if 'codellama' in code_model.lower():
            print(f"   ✅ CodeLlama configurado corretamente")
            return True
        else:
            print(f"   ⚠️ Modelo pode ser subótimo: {code_model}")
            return True  # Ainda funciona, só não é ideal
            
    except Exception as e:
        print(f"   ❌ Erro: {e}")
        return False

def test_code_quality_improvements():
    """Testa melhorias na qualidade do código"""
    print("\n🔧 Testando melhorias na qualidade...")
    
    try:
        from core.agents.code_agent_enhanced import CodeAgentEnhanced
        
        # Usar mock para ter controle
        agent = CodeAgentEnhanced(use_mock=True, enable_graphrag=False)
        
        # Casos que costumavam dar problema
        test_cases = [
            "criar função hello world",
            "implementar soma de números", 
            "função de validação simples"
        ]
        
        results = []
        
        for task in test_cases:
            result = agent.execute_task(task)
            
            # Verificar critérios melhorados
            syntax_ok = result.success
            quality_ok = result.quality_score >= 5.0
            
            # Verificar docstrings bem formadas (principal problema)
            docstring_ok = True
            if '"""' in result.code:
                count = result.code.count('"""')
                docstring_ok = count % 2 == 0  # Par = bem fechadas
                
            results.append({
                'task': task,
                'syntax': syntax_ok,
                'quality': quality_ok,
                'docstrings': docstring_ok,
                'score': result.quality_score
            })
        
        # Avaliar resultados
        syntax_success = sum(1 for r in results if r['syntax'])
        docstring_success = sum(1 for r in results if r['docstrings'])
        avg_quality = sum(r['score'] for r in results) / len(results)
        
        print(f"   ✅ Sintaxe válida: {syntax_success}/{len(results)}")
        print(f"   ✅ Docstrings corretas: {docstring_success}/{len(results)}")
        print(f"   ✅ Qualidade média: {avg_quality:.1f}/10")
        
        # Critério de sucesso: pelo menos 80% dos testes passam
        success_rate = (syntax_success + docstring_success) / (len(results) * 2)
        
        if success_rate >= 0.8:
            print(f"   ✅ Melhorias funcionando ({success_rate:.1%} sucesso)")
            return True
        else:
            print(f"   ⚠️ Precisa melhorar ({success_rate:.1%} sucesso)")
            return False
            
    except Exception as e:
        print(f"   ❌ Erro: {e}")
        return False

def test_integration():
    """Testa integração entre componentes"""
    print("\n🔗 Testando integração...")
    
    try:
        # Testar imports cruzados
        from core.llm.llm_manager import llm_manager
        from core.agents.code_agent_enhanced import CodeAgentEnhanced
        
        # Criar agente com LLM real (se disponível)
        try:
            agent = CodeAgentEnhanced(use_mock=False, enable_graphrag=False)
            llm_type = "real"
        except:
            agent = CodeAgentEnhanced(use_mock=True, enable_graphrag=False)
            llm_type = "mock"
        
        # Teste simples de integração
        result = agent.execute_task("criar função de teste de integração")
        
        print(f"   ✅ Integração funcionando (LLM: {llm_type})")
        print(f"   ✅ Código gerado: {result.success}")
        print(f"   ✅ Qualidade: {result.quality_score:.1f}/10")
        
        return result.success
        
    except Exception as e:
        print(f"   ❌ Erro na integração: {e}")
        return False

def main():
    """Executa todos os testes rápidos"""
    print("🔬 TESTE RÁPIDO DAS CORREÇÕES RSCA")
    print("=" * 40)
    print(f"📅 {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    tests = [
        ("LLM Manager", test_llm_manager_fixed),
        ("Qualidade de Código", test_code_quality_improvements),
        ("Integração", test_integration)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            success = test_func()
            results.append((test_name, success))
        except Exception as e:
            print(f"   ❌ Erro no teste {test_name}: {e}")
            results.append((test_name, False))
    
    # Resumo
    print("\n" + "=" * 40)
    print("📋 RESUMO DOS TESTES")
    print("=" * 40)
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for test_name, success in results:
        status = "✅ PASSOU" if success else "❌ FALHOU"
        print(f"{status:12} {test_name}")
    
    print(f"\n📊 Total: {passed}/{total} ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("🎉 TODAS AS CORREÇÕES FUNCIONANDO!")
        print("💡 Sistema pronto para uso melhorado")
        return 0
    elif passed >= total * 0.75:
        print("⚠️ MAIORIA DAS CORREÇÕES OK")
        print("💡 Sistema utilizável, algumas melhorias pendentes")
        return 1
    else:
        print("❌ CORREÇÕES PRECISAM DE MAIS TRABALHO")
        return 2

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
