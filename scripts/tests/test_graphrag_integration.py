# scripts/tests/test_graphrag_integration.py
"""
Suíte de Testes Completa para GraphRAG Integration
Valida se o sistema está aprendendo e melhorando
"""

import sys
import time
import json
import yaml
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any

# Adicionar paths
sys.path.append(str(Path(__file__).parent.parent.parent))

from core.agents.code_agent_enhanced import CodeAgentEnhanced
from memory.hybrid_store import HybridMemoryStore
from memory.pattern_discovery import PatternDiscoveryEngine
from config.paths import IDENTITY_STATE, MEMORY_LOG


class GraphRAGTestSuite:
    """Suite de testes para validar funcionalidades GraphRAG"""
    
    def __init__(self):
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "tests": {},
            "summary": {},
            "performance_metrics": {}
        }
        
    def run_all_tests(self) -> Dict[str, Any]:
        """Executa todos os testes de integração GraphRAG"""
        print("🧪 INICIANDO TESTES DE INTEGRAÇÃO GRAPHRAG")
        print("=" * 60)
        
        start_time = time.time()
        
        # Testes básicos de conectividade
        self.test_database_connectivity()
        self.test_hybrid_storage()
        
        # Testes de funcionalidade
        self.test_experience_storage()
        self.test_similarity_search()
        self.test_pattern_discovery()
        
        # Testes de aprendizado
        self.test_learning_improvement()
        self.test_recommendation_system()
        
        # Testes de compatibilidade
        self.test_yaml_compatibility()
        self.test_symbolic_integration()
        
        # Testes de performance
        self.test_performance_metrics()
        
        # Compilar resultados
        total_time = time.time() - start_time
        self.compile_results(total_time)
        
        return self.results
    
    def test_database_connectivity(self):
        """Testa conectividade com Neo4j e ChromaDB"""
        test_name = "database_connectivity"
        print(f"\n🔌 Teste: {test_name}")
        
        try:
            memory = HybridMemoryStore(enable_graphrag=True)
            
            # Testar Neo4j
            neo4j_ok = False
            if memory.enable_graphrag and hasattr(memory, 'neo4j'):
                with memory.neo4j.session() as session:
                    result = session.run("RETURN 'Connected' as status")
                    neo4j_ok = result.single()['status'] == 'Connected'
            
            # Testar ChromaDB
            chroma_ok = False
            if memory.enable_graphrag and hasattr(memory, 'chroma_client'):
                collections = memory.chroma_client.list_collections()
                chroma_ok = True
            
            memory.close()
            
            success = neo4j_ok and chroma_ok
            self.results["tests"][test_name] = {
                "success": success,
                "neo4j_connected": neo4j_ok,
                "chromadb_connected": chroma_ok,
                "message": "✅ Bancos conectados" if success else "❌ Problemas de conectividade"
            }
            
            print(f"   Neo4j: {'✅' if neo4j_ok else '❌'}")
            print(f"   ChromaDB: {'✅' if chroma_ok else '❌'}")
            
        except Exception as e:
            self.results["tests"][test_name] = {
                "success": False,
                "error": str(e),
                "message": f"❌ Erro de conectividade: {e}"
            }
            print(f"   ❌ Erro: {e}")
    
    def test_hybrid_storage(self):
        """Testa armazenamento híbrido YAML + GraphRAG"""
        test_name = "hybrid_storage"
        print(f"\n💾 Teste: {test_name}")
        
        try:
            memory = HybridMemoryStore(enable_graphrag=True)
            
            # Criar experiência de teste
            from memory.hybrid_store import CodingExperience
            test_exp = CodingExperience(
                id="test_hybrid_001",
                task_description="teste de armazenamento híbrido",
                code_generated="def test(): return 'hybrid_test'",
                quality_score=8.5,
                execution_success=True,
                agent_name="CodeAgent",
                llm_model="test_model",
                timestamp=datetime.now(),
                context={"test": True},
                yaml_cycle=1
            )
            
            # Armazenar
            storage_success = memory.store_experience(test_exp)
            
            # Verificar YAML
            yaml_updated = False
            try:
                with open(IDENTITY_STATE, 'r') as f:
                    identity_data = yaml.safe_load(f)
                    yaml_updated = 'CodeAgent' in identity_data
            except:
                pass
            
            # Verificar GraphRAG
            graphrag_stored = False
            if memory.enable_graphrag:
                similar = memory.retrieve_similar_experiences("teste", k=1)
                graphrag_stored = len(similar) > 0
            
            memory.close()
            
            success = storage_success and yaml_updated
            self.results["tests"][test_name] = {
                "success": success,
                "storage_success": storage_success,
                "yaml_updated": yaml_updated,
                "graphrag_stored": graphrag_stored,
                "message": "✅ Armazenamento híbrido funcional" if success else "❌ Problemas no armazenamento"
            }
            
            print(f"   Armazenamento: {'✅' if storage_success else '❌'}")
            print(f"   YAML atualizado: {'✅' if yaml_updated else '❌'}")
            print(f"   GraphRAG: {'✅' if graphrag_stored else '❌'}")
            
        except Exception as e:
            self.results["tests"][test_name] = {
                "success": False,
                "error": str(e),
                "message": f"❌ Erro no armazenamento: {e}"
            }
            print(f"   ❌ Erro: {e}")
    
    def test_experience_storage(self):
        """Testa armazenamento e recuperação de experiências"""
        test_name = "experience_storage"
        print(f"\n📚 Teste: {test_name}")
        
        try:
            agent = CodeAgentEnhanced(use_mock=True, enable_graphrag=True)
            
            # Gerar múltiplas experiências
            test_tasks = [
                "criar função que soma dois números",
                "criar função que multiplica valores",
                "criar função de validação de email"
            ]
            
            experiences = []
            for task in test_tasks:
                result = agent.execute_task(task)
                experiences.append({
                    "task": task,
                    "success": result.success,
                    "quality": result.quality_score,
                    "has_experience_id": hasattr(result, 'experience_id') and result.experience_id is not None
                })
                time.sleep(0.5)  # Pequena pausa
            
            #