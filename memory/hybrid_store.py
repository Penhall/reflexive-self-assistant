"""
Sistema de Memória GraphRAG - Versão simplificada sem YAML legado
Utiliza exclusivamente Neo4j + ChromaDB para persistência
"""

import json
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from pathlib import Path

from neo4j import GraphDatabase
import chromadb
from sentence_transformers import SentenceTransformer

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

class GraphRAGMemoryStore:
    """
    Armazena experiências apenas em GraphRAG (Neo4j + ChromaDB)
    """
    
    def __init__(self):
        self._setup_graphrag()
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
            print(f"⚠️ Falha ao conectar GraphRAG: {e}")
            raise RuntimeError("GraphRAG initialization failed")

    def store_experience(self, experience: CodingExperience) -> bool:
        """
        Armazena experiência no GraphRAG
        """
        try:
            # 1. Gerar embedding
            text_to_embed = f"{experience.task_description} {experience.code_generated}"
            embedding = self.encoder.encode(text_to_embed).tolist()
            
            # 2. Armazenar em ChromaDB
            self.experiences_collection.add(
                documents=[experience.code_generated],
                embeddings=[embedding],
                metadatas=[{
                    "experience_id": experience.id,
                    "task": experience.task_description,
                    "quality": experience.quality_score,
                    "agent": experience.agent_name,
                    "timestamp": experience.timestamp.isoformat()
                }],
                ids=[experience.id]
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
                        exp.llm_model = $llm_model
                    
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
                    exp_id=experience.id,
                    task=experience.task_description,
                    quality=experience.quality_score,
                    success=experience.execution_success,
                    timestamp=experience.timestamp.isoformat(),
                    agent=experience.agent_name,
                    llm_model=experience.llm_model,
                    task_id=f"task_{hash(experience.task_description)}",
                    domain=self._extract_domain(experience.task_description),
                    code_hash=f"code_{hash(experience.code_generated)}",
                    code=experience.code_generated,
                    syntax_valid=experience.execution_success,
                    avg_quality=experience.quality_score
                )
            
            return True
            
        except Exception as e:
            print(f"❌ Erro ao salvar experiência: {e}")
            return False
    
    def retrieve_similar_experiences(self, query: str, k: int = 5) -> List[Dict]:
        """
        Busca experiências similares usando GraphRAG
        """
        try:
            query_embedding = self.encoder.encode(query).tolist()
            
            results = self.experiences_collection.query(
                query_embeddings=[query_embedding],
                n_results=k,
                include=['documents', 'metadatas', 'distances']
            )
            
            formatted_results = []
            for doc, metadata, distance in zip(
                results['documents'][0],
                results['metadatas'][0], 
                results['distances'][0]
            ):
                formatted_results.append({
                    "experience_id": metadata['experience_id'],
                    "task": metadata.get('task', ''),
                    "code": doc,
                    "quality": metadata.get('quality', 0),
                    "agent": metadata.get('agent', ''),
                    "similarity": 1.0 - distance
                })
            
            return formatted_results
            
        except Exception as e:
            print(f"⚠️ Busca falhou: {e}")
            return []

    def _extract_domain(self, task: str) -> str:
        """Extrai domínio da tarefa"""
        task_lower = task.lower()
        if "login" in task_lower or "auth" in task_lower:
            return "authentication"
        elif "api" in task_lower:
            return "api_development"
        elif "database" in task_lower or "db" in task_lower:
            return "database"
        else:
            return "general"

    def close(self):
        """Fecha conexões"""
        if hasattr(self, 'neo4j'):
            self.neo4j.close()

# Exemplo de uso atualizado
if __name__ == "__main__":
    try:
        memory = GraphRAGMemoryStore()
        
        test_exp = CodingExperience(
            id="exp_test_001",
            task_description="criar função que soma dois números",
            code_generated="def soma(a, b):\n    return a + b",
            quality_score=8.5,
            execution_success=True,
            agent_name="CodeAgent",
            llm_model="qwen2:1.5b",
            timestamp=datetime.now(),
            context={"test": True}
        )
        
        success = memory.store_experience(test_exp)
        print(f"Armazenamento: {'✅' if success else '❌'}")
        
        similar = memory.retrieve_similar_experiences("função de soma")
        print(f"Encontradas {len(similar)} experiências similares")
        
    except Exception as e:
        print(f"Erro: {e}")
    finally:
        if 'memory' in locals():
            memory.close()
