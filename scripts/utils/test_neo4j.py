#!/usr/bin/env python3
"""
Script simples para testar Neo4j e GraphRAG
"""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.append(str(PROJECT_ROOT))

def test_neo4j_basic():
    """Teste básico do Neo4j"""
    print("🧪 Testando conexão básica com Neo4j...")
    
    try:
        from neo4j import GraphDatabase
        
        driver = GraphDatabase.driver(
            "bolt://localhost:7687",
            auth=("neo4j", "reflexive123")
        )
        
        with driver.session() as session:
            result = session.run("RETURN 'Hello Neo4j' AS message")
            message = result.single()["message"]
            print(f"✅ Neo4j conectado: {message}")
        
        driver.close()
        return True
        
    except Exception as e:
        print(f"❌ Erro na conexão básica: {e}")
        return False

def test_graph_memory():
    """Teste do GraphMemory"""
    print("🧪 Testando GraphMemory...")
    
    try:
        from memory.graph_rag.graph_interface import GraphMemory
        
        graph = GraphMemory()
        
        # Teste básico
        categories = graph.get_categories_and_counts()
        print(f"✅ GraphMemory funcionando")
        print(f"📊 Categorias encontradas: {len(categories)}")
        
        # Teste de inserção
        graph.register_pattern(
            "test_reaction", 
            "test_pattern", 
            "test_category", 
            "TestAgent"
        )
        print("✅ Inserção de padrão funcionando")
        
        graph.close()
        return True
        
    except Exception as e:
        print(f"❌ Erro no GraphMemory: {e}")
        return False

def test_hybrid_memory():
    """Teste do HybridMemoryStore"""
    print("🧪 Testando HybridMemoryStore...")
    
    try:
        from memory.hybrid_store import HybridMemoryStore
        
        store = HybridMemoryStore(enable_graphrag=True)
        
        if store.enable_graphrag:
            print("✅ HybridMemoryStore com GraphRAG ativo")
        else:
            print("⚠️ HybridMemoryStore em modo mock")
        
        store.close()
        return True
        
    except Exception as e:
        print(f"❌ Erro no HybridMemoryStore: {e}")
        return False

def test_reflection_agent():
    """Teste do ReflectionAgent"""
    print("🧪 Testando ReflectionAgent...")
    
    try:
        from core.agents.reflection_agent import ReflectionAgent
        
        agent = ReflectionAgent()
        
        # Verificar se MD logging está desabilitado
        md_logging = getattr(agent, 'enable_md_logging', True)
        
        if md_logging:
            print("⚠️ MD logging ainda habilitado")
            return False
        else:
            print("✅ ReflectionAgent funcionando sem MD logging")
        
        # Verificar GraphRAG
        using_mock = getattr(agent, 'using_mock', True)
        
        if using_mock:
            print("⚠️ ReflectionAgent usando mock (Neo4j não disponível)")
        else:
            print("✅ ReflectionAgent usando GraphRAG real")
        
        agent.close()
        return True
        
    except Exception as e:
        print(f"❌ Erro no ReflectionAgent: {e}")
        return False

def test_settings():
    """Teste das configurações"""
    print("🧪 Testando configurações...")
    
    try:
        from config.settings import LEGACY_FEATURES
        
        md_enabled = LEGACY_FEATURES.get('enable_analysis_history_md', True)
        
        if md_enabled:
            print("⚠️ analysis_history.md ainda habilitado nas configurações")
            return False
        else:
            print("✅ analysis_history.md desabilitado nas configurações")
            return True
        
    except ImportError:
        print("⚠️ Configurações não encontradas - usando padrões")
        return True
    except Exception as e:
        print(f"❌ Erro nas configurações: {e}")
        return False

def main():
    """Executa todos os testes"""
    print("🔬 BATERIA DE TESTES - Sistema RSCA")
    print("=" * 50)
    
    tests = [
        ("Configurações", test_settings),
        ("Neo4j Básico", test_neo4j_basic),
        ("GraphMemory", test_graph_memory),
        ("HybridMemoryStore", test_hybrid_memory),
        ("ReflectionAgent", test_reflection_agent)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        print(f"\n📝 {test_name}:")
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"❌ Erro inesperado: {e}")
            results[test_name] = False
    
    print("\n" + "=" * 50)
    print("📊 RESUMO DOS TESTES:")
    
    for test_name, passed in results.items():
        status = "✅ PASSOU" if passed else "❌ FALHOU"
        print(f"• {test_name:<20} {status}")
    
    total_tests = len(results)
    passed_tests = sum(results.values())
    
    print(f"\n🎯 RESULTADO FINAL: {passed_tests}/{total_tests} testes passaram")
    
    if passed_tests == total_tests:
        print("🎉 TODOS OS TESTES PASSARAM!")
        print("✅ Sistema funcionando corretamente")
    elif passed_tests >= total_tests - 1:
        print("✅ Sistema funcionando (com pequenos avisos)")
    else:
        print("⚠️ Sistema com problemas - verificar falhas acima")
    
    print("\n💡 PRÓXIMOS PASSOS:")
    
    if not results.get("Neo4j Básico", False):
        print("1. Configure Neo4j: python scripts/setup_neo4j.py")
    
    if not results.get("ReflectionAgent", False):
        print("2. Verifique imports do ReflectionAgent")
    
    if passed_tests >= 3:
        print("3. Execute ciclo de teste: python core/main.py")
        print("4. Monitore dashboard: streamlit run interface/dashboard/streamlit_app.py")
    
    return passed_tests >= 3  # Sucesso se pelo menos 3 testes passaram

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)