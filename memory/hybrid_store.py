# memory/hybrid_store.py
"""
Sistema de Memória Híbrida - Preserva YAML atual + adiciona GraphRAG
Estratégia: Compatibilidade total com sistema existente
"""

import yaml
import json
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from pathlib import Path

from neo4j import GraphDatabase
import chromadb
from sentence_transformers import SentenceTransformer

from config.paths import (
    IDENTITY_STATE, MEMORY_LOG, CYCLE_HISTORY,
    SYMBOLIC_TIMELINE, EMOTIONAL_STATE
)

@dataclass
class CodingExperience:
    """Estrutura padronizada para experiências de codificação"""
    id: str
    task_description: str
    code_generated: str
    quality_score: float
    execution_success: bool
    agent_name: str
    llm_model: str
    timestamp: datetime
    context: Dict[str, Any]
    yaml_cycle: int  # Conecta com sistema atual

class HybridMemoryStore:
    """
    Armazena experiências tanto em YAML (compatibilidade) quanto em GraphRAG (evolução)
    """
    
    def __init__(self, enable_graphrag: bool = True):
        self.enable_graphrag = enable_graphrag
        
        # Sistema YAML atual (preservado)
        self.yaml_paths = {
            'identity': IDENTITY_STATE,
            'memory': MEMORY_LOG, 
            'history': CYCLE_HISTORY,
            'timeline': SYMBOLIC_TIMELINE,
            'emotional': EMOTIONAL_STATE
        }
        
        # GraphRAG (novo)
        if enable_graphrag:
            self._setup_graphrag()
        
        # Embeddings para similaridade
        self.encoder = SentenceTransformer('all-MiniLM-L6-v2')
        
    def _setup_graphrag(self):
        """Inicializa conexões Neo4j e ChromaDB"""
        try:
            # Neo4j
            self.neo4j = GraphDatabase.driver(
                "bolt://localhost:7687",
                auth=("neo4j", "rsca_secure_2025")
            )
            
            # ChromaDB
            self.chroma_client = chromadb.HttpClient(
                host="localhost",
                port=8000,
                headers={"X-Chroma-Token": "rsca_chroma_secret_2025"}
            )
            
            # Collection para experiências de código
            self.experiences_collection = self.chroma_client.get_or_create_collection(
                name="coding_experiences",
                metadata={"description": "RSCA coding experiences with embeddings"}
            )
            
            print("✅ GraphRAG conectado: Neo4j + ChromaDB")
            
        except Exception as e:
            print(f"⚠️ GraphRAG não disponível: {e}")
            self.enable_graphrag = False
    
    def store_experience(self, experience: CodingExperience) -> bool:
        """
        Armazena experiência em ambos os sistemas:
        1. YAML (compatibilidade com sistema atual)
        2. GraphRAG (capacidades avançadas)
        """
        success_yaml = self._store_yaml_compatible(experience)
        success_graph = True
        
        if self.enable_graphrag:
            success_graph = self._store_graphrag(experience)
        
        return success_yaml and success_graph
    
    def _store_yaml_compatible(self, exp: CodingExperience) -> bool:
        """Atualiza arquivos YAML existentes mantendo compatibilidade"""
        try:
            # 1. Atualizar identity_state.yaml
            identity = self._load_yaml(self.yaml_paths['identity'])
            
            if exp.agent_name not in identity:
                identity[exp.agent_name] = {}
            
            agent_identity = identity[exp.agent_name]
            agent_identity.update({
                'last_adaptation': exp.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
                'total_experiences': agent_identity.get('total_experiences', 0) + 1,
                'avg_quality_score': self._update_avg_quality(agent_identity, exp.quality_score),
                'consistency_level': self._calculate_consistency(agent_identity, exp.quality_score)
            })
            
            self._save_yaml(self.yaml_paths['identity'], identity)
            
            # 2. Atualizar memory_log.yaml
            memory = self._load_yaml(self.yaml_paths['memory'])
            
            if exp.agent_name not in memory:
                memory[exp.agent_name] = {
                    'ciclos_totais': 0,
                    'consistencia': {'Alta': 0, 'Moderada': 0, 'Baixa': 0},
                    'traços_frequentes': [],
                    'marcos': []
                }
            
            memory[exp.agent_name]['ciclos_totais'] += 1
            consistency = agent_identity.get('consistency_level', 'Moderada')
            memory[exp.agent_name]['consistencia'][consistency] += 1
            
            self._save_yaml(self.yaml_paths['memory'], memory)
            
            # 3. Atualizar cycle_history.json
            history = self._load_json(self.yaml_paths['history'])
            
            if exp.agent_name not in history:
                history[exp.agent_name] = []
            
            # Extrair padrão da experiência
            pattern = self._extract_pattern_from_code(exp.code_generated, exp.task_description)
            history[exp.agent_name].append(pattern)
            
            # Manter apenas últimos 5 padrões
            if len(history[exp.agent_name]) > 5:
                history[exp.agent_name] = history[exp.agent_name][-5:]
            
            self._save_json(self.yaml_paths['history'], history)
            
            return True
            
        except Exception as e:
            print(f"❌ Erro ao salvar YAML: {e}")
            return False
    
    def _store_graphrag(self, exp: CodingExperience) -> bool:
        """Armazena experiência no sistema GraphRAG"""
        try:
            # 1. Gerar embedding
            text_to_embed = f"{exp.task_description} {exp.code_generated}"
            embedding = self.encoder.encode(text_to_embed).tolist()
            
            # 2. Armazenar em ChromaDB
            self.experiences_collection.add(
                documents=[exp.code_generated],
                embeddings=[embedding],
                metadatas=[{
                    "experience_id": exp.id,
                    "task": exp.task_description,
                    "quality": exp.quality_score,
                    "agent": exp.agent_name,
                    "timestamp": exp.timestamp.isoformat(),
                    "yaml_cycle": exp.yaml_cycle
                }],
                ids=[exp.id]
            )
            
            # 3. Criar nós e relações em Neo4j
            with self.neo4j.session() as session:
                session.run("""
                    MERGE (exp:Experience {id: $exp_id})
                    SET exp.task_description = $task,
                        exp.quality_score = $quality,
                        exp.execution_success = $success,
                        exp.timestamp = datetime($timestamp),
                        exp.agent_name = $agent,
                        exp.llm_model = $llm_model,
                        exp.yaml_cycle = $yaml_cycle
                    
                    MERGE (task:Task {id: $task_id})
                    SET task.description = $task,
                        task.domain = $domain
                    
                    MERGE (code:Code {hash: $code_hash})
                    SET code.content = $code,
                        code.language = "python",
                        code.syntax_valid = $syntax_valid
                    
                    MERGE (agent:Agent {name: $agent})
                    SET agent.total_experiences = COALESCE(agent.total_experiences, 0) + 1,
                        agent.avg_quality_score = $avg_quality
                    
                    CREATE (exp)-[:EXECUTED_TASK]->(task)
                    CREATE (exp)-[:GENERATED_CODE]->(code)
                    CREATE (exp)-[:PERFORMED_BY]->(agent)
                """, 
                    exp_id=exp.id,
                    task=exp.task_description,
                    quality=exp.quality_score,
                    success=exp.execution_success,
                    timestamp=exp.timestamp.isoformat(),
                    agent=exp.agent_name,
                    llm_model=exp.llm_model,
                    yaml_cycle=exp.yaml_cycle,
                    task_id=f"task_{hash(exp.task_description)}",
                    domain=self._extract_domain(exp.task_description),
                    code_hash=f"code_{hash(exp.code_generated)}",
                    code=exp.code_generated,
                    syntax_valid=exp.execution_success,
                    avg_quality=exp.quality_score
                )
            
            return True
            
        except Exception as e:
            print(f"❌ Erro ao salvar GraphRAG: {e}")
            return False
    
    def retrieve_similar_experiences(self, query: str, k: int = 5) -> List[Dict]:
        """
        Busca experiências similares usando tanto YAML quanto GraphRAG
        """
        results = []
        
        # 1. Busca no sistema YAML atual (compatibilidade)
        yaml_results = self._search_yaml_experiences(query)
        results.extend(yaml_results)
        
        # 2. Busca no GraphRAG (capacidades avançadas)
        if self.enable_graphrag:
            graph_results = self._search_graphrag_experiences(query, k)
            results.extend(graph_results)
        
        # 3. Remover duplicatas e ranquear
        unique_results = self._deduplicate_and_rank(results, query)
        
        return unique_results[:k]
    
    def _search_yaml_experiences(self, query: str) -> List[Dict]:
        """Busca compatível com sistema atual"""
        results = []
        
        try:
            # Buscar em cycle_history
            history = self._load_json(self.yaml_paths['history'])
            
            for agent_name, patterns in history.items():
                for pattern in patterns:
                    if query.lower() in pattern.lower():
                        results.append({
                            "source": "yaml",
                            "agent": agent_name,
                            "pattern": pattern,
                            "similarity": 0.5  # Score baixo para YAML
                        })
        except:
            pass
        
        return results
    
    def _search_graphrag_experiences(self, query: str, k: int) -> List[Dict]:
        """Busca avançada no GraphRAG"""
        results = []
        
        try:
            # Busca vetorial no ChromaDB
            query_embedding = self.encoder.encode(query).tolist()
            
            chroma_results = self.experiences_collection.query(
                query_embeddings=[query_embedding],
                n_results=k,
                include=['documents', 'metadatas', 'distances']
            )
            
            for i, (doc, metadata, distance) in enumerate(zip(
                chroma_results['documents'][0],
                chroma_results['metadatas'][0], 
                chroma_results['distances'][0]
            )):
                results.append({
                    "source": "graphrag",
                    "experience_id": metadata['experience_id'],
                    "task": metadata['task'],
                    "code": doc,
                    "quality": metadata['quality'],
                    "agent": metadata['agent'],
                    "similarity": 1.0 - distance  # Convert distance to similarity
                })
                
        except Exception as e:
            print(f"⚠️ Busca GraphRAG falhou: {e}")
        
        return results
    
    def _deduplicate_and_rank(self, results: List[Dict], query: str) -> List[Dict]:
        """Remove duplicatas e ranqueia por relevância"""
        # Implementação simples - pode ser melhorada
        seen = set()
        unique_results = []
        
        for result in results:
            key = result.get('experience_id', result.get('pattern', ''))
            if key not in seen:
                seen.add(key)
                unique_results.append(result)
        
        # Ranquear por similaridade
        return sorted(unique_results, key=lambda x: x.get('similarity', 0), reverse=True)
    
    # Métodos auxiliares
    def _load_yaml(self, path: Path) -> Dict:
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f) or {}
        except:
            return {}
    
    def _save_yaml(self, path: Path, data: Dict):
        with open(path, 'w', encoding='utf-8') as f:
            yaml.safe_dump(data, f, allow_unicode=True, sort_keys=False)
    
    def _load_json(self, path: Path) -> Dict:
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {}
    
    def _save_json(self, path: Path, data: Dict):
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def _extract_pattern_from_code(self, code: str, task: str) -> str:
        """Extrai padrão do código (compatível com sistema atual)"""
        if "login" in task.lower():
            return "Implementação funcional"
        elif "test" in task.lower():
            return "Cobertura de teste"
        elif "doc" in task.lower():
            return "Atualização documental"
        else:
            return "Execução padrão"
    
    def _extract_domain(self, task: str) -> str:
        """Extrai domínio da tarefa"""
        if "login" in task.lower() or "auth" in task.lower():
            return "authentication"
        elif "api" in task.lower():
            return "api_development"
        elif "database" in task.lower() or "db" in task.lower():
            return "database"
        else:
            return "general"
    
    def _update_avg_quality(self, agent_data: Dict, new_quality: float) -> float:
        """Atualiza média de qualidade do agente"""
        current_avg = agent_data.get('avg_quality_score', 0.0)
        total_exp = agent_data.get('total_experiences', 0)
        
        if total_exp == 0:
            return new_quality
        
        return (current_avg * total_exp + new_quality) / (total_exp + 1)
    
    def _calculate_consistency(self, agent_data: Dict, quality: float) -> str:
        """Calcula nível de consistência (compatível com sistema atual)"""
        if quality >= 8.0:
            return "Alta"
        elif quality >= 6.0:
            return "Moderada"
        else:
            return "Baixa"
    
    def close(self):
        """Fecha conexões"""
        if self.enable_graphrag and hasattr(self, 'neo4j'):
            self.neo4j.close()


# Exemplo de uso
if __name__ == "__main__":
    # Teste da integração
    memory = HybridMemoryStore(enable_graphrag=True)
    
    # Criar experiência de teste
    test_exp = CodingExperience(
        id="exp_test_001",
        task_description="criar função que soma dois números",
        code_generated="def soma(a, b):\n    return a + b",
        quality_score=8.5,
        execution_success=True,
        agent_name="CodeAgent",
        llm_model="qwen2:1.5b",
        timestamp=datetime.now(),
        context={"test": True},
        yaml_cycle=1
    )
    
    # Armazenar
    success = memory.store_experience(test_exp)
    print(f"Armazenamento: {'✅' if success else '❌'}")
    
    # Buscar
    similar = memory.retrieve_similar_experiences("função de soma", k=3)
    print(f"Encontradas {len(similar)} experiências similares")
    
    memory.close()