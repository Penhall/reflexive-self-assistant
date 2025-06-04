#!/usr/bin/env python3
"""
Teste rápido para verificar se qwen2:1.5b está funcionando
"""

import sys
import time
from pathlib import Path

# Adicionar path do projeto
sys.path.insert(0, str(Path(__file__).parent.parent))

def test_qwen_setup():
    """Teste completo do setup com qwen2:1.5b"""
    
    print("🧪 TESTE RÁPIDO: qwen2:1.5b Setup")
    print("=" * 50)
    
    # 1. Testar importações
    print("\n1️⃣ Testando importações...")
    try:
        from core.llm.llm_manager import llm_manager
        print("✅ LLM Manager importado")
    except Exception as e:
        print(f"❌ Erro de importação: {e}")
        return False
    
    # 2. Verificar status do sistema
    print("\n2️⃣ Verificando status do sistema...")
    try:
        status = llm_manager.get_system_status()
        print(f"✅ Status: {status['ready']}")
        print(f"   LLM Real: {status['using_real_llm']}")
        print(f"   Host: {status['host']}")
        print(f"   Modelos: {status['models_configured']}")
    except Exception as e:
        print(f"❌ Erro no status: {e}")
        return False
    
    # 3. Testar disponibilidade do Ollama
    print("\n3️⃣ Testando Ollama...")
    try:
        available = llm_manager.is_available()
        models = llm_manager.list_models()
        print(f"✅ Ollama disponível: {available}")
        print(f"   Modelos instalados: {len(models)}")
        for model in models:
            print(f"   • {model}")
            
        if "qwen2:1.5b" not in models and available:
            print("📥 qwen2:1.5b não encontrado. Instalando...")
            success = llm_manager.pull_model("qwen2:1.5b")
            print(f"   Instalação: {'✅' if success else '❌'}")
    except Exception as e:
        print(f"❌ Erro no Ollama: {e}")
    
    # 4. Teste de geração simples
    print("\n4️⃣ Testando geração de código...")
    try:
        start_time = time.time()
        response = llm_manager.generate_code("criar função que soma dois números")
        end_time = time.time()
        
        print(f"✅ Geração concluída em {end_time - start_time:.2f}s")
        print(f"   Modelo usado: {response.model}")
        print(f"   Sucesso: {response.success}")
        print(f"   Tokens: {response.context_tokens} + {response.response_tokens} = {response.tokens_used}")
        print(f"   Tempo de geração: {response.generation_time:.2f}s")
        
        # Mostrar preview do código
        preview = response.content[:150].replace('\n', '\\n')
        print(f"   Preview: {preview}...")
        
        # Verificar se é mock ou real
        if "mock" in response.model.lower():
            print("⚠️  Usando modo mock (Ollama pode estar offline)")
        else:
            print("🚀 Usando LLM real!")
            
    except Exception as e:
        print(f"❌ Erro na geração: {e}")
        return False
    
    # 5. Teste de memória/GraphRAG (opcional)
    print("\n5️⃣ Testando integração GraphRAG...")
    try:
        from memory.hybrid_store import HybridMemoryStore
        memory = HybridMemoryStore(enable_graphrag=True)
        print("✅ HybridMemoryStore inicializado")
        memory.close()
    except Exception as e:
        print(f"⚠️ GraphRAG não disponível: {e}")
    
    # 6. Resumo final
    print("\n" + "=" * 50)
    if llm_manager.is_mock:
        print("📋 RESULTADO: Sistema funcionando em MODO MOCK")
        print("💡 Para usar LLM real:")
        print("   1. Verifique se Ollama está rodando: ollama serve")
        print("   2. Instale qwen2:1.5b: ollama pull qwen2:1.5b")
    else:
        print("📋 RESULTADO: Sistema funcionando com LLM REAL! 🚀")
        print(f"   Modelo: {response.model}")
        print(f"   Performance: {response.generation_time:.2f}s")
    
    print("✅ Setup concluído!")
    return True

if __name__ == "__main__":
    success = test_qwen_setup()
    sys.exit(0 if success else 1)