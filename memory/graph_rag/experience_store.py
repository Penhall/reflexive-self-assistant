"""
Sistema GraphRAG para armazenar e recuperar experiências de codificação
"""

import json
import uuid
from datetime import datetime
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from neo4j import GraphDatabase
import hashlib

@dataclass
class CodingExperience:
    id: str
    task: str
    code: str
    quality_score: float
    success: bool
    timestamp: str
    agent_type: str
    execution_result: Optional[str] = None
    error: Optional[str] = None
    patterns: List[str] = None
    context: Dict[str, Any] = None

class ExperienceGraphRAG:
    """Sistema de memória experiencial baseado em grafo"""
    
    def __init__(self, neo4j_uri="bolt://localhost:7687", user="neo4j", password="abcd1234"):
        self.driver = GraphDatabase.driver(neo4j_uri, auth=(user, password))
        self._initialize_schema()
    
    def _initialize_schema(self):
        """Inicializa schema do grafo"""
        with self.driver.session() as session:
            # Constraints
            session.run("""
                CREATE CONSTRAINT experience_id IF NOT EXISTS
                FOR (e:Experience) REQUIRE e.id IS UNIQUE
            """)
            
            session.run("""
                CREATE CONSTRAINT pattern_name IF NOT EXISTS  
                FOR (p:Pattern) REQUIRE p.name IS UNIQUE
            """)
            
            # Indexes
            session.run("""
                CREATE INDEX experience_quality IF NOT EXISTS
                FOR (e:Experience) ON (e.quality_score)
            """)
            
            session.run("""
                CREATE INDEX experience_timestamp IF NOT EXISTS
                FOR (e:Experience) ON (e.timestamp)
            """)
    
    def store_experience(self, experience: CodingExperience) -> str:
        """Armazena uma experiência de codificação"""
        
        with self.driver.session() as session:
            # Criar nó de experiência
            query = """
                CREATE (e:Experience {
                    id: $id,
                    task: $task,
                    code: $code,
                    quality_score: $quality_score,
                    success: $success,
                    timestamp: $timestamp,
                    agent_type: $agent_type,
                    execution_result: $execution_result,
                    error: $error,
                    context: $context
                })
                RETURN e.id as id
            """
            
            result = session.run(query, 
                id=experience.id,
                task=experience.task,
                code=experience.code,
                quality_score=experience.quality_score,
                success=experience.success,
                timestamp=experience.timestamp,
                agent_type=experience.agent_type,
                execution_result=experience.execution_result,
                error=experience.error,
                context=json.dumps(experience.context or {})
            )
            
            experience_id = result.single()["id"]
            
            # Adicionar padrões descobertos
            if experience.patterns:
                for pattern in experience.patterns:
                    self._add_pattern_relation(session, experience_id, pattern)
            
            # Conectar experiências similares
            self._connect_similar_experiences(session, experience_id, experience.task)
            
            return experience_id
    
    def _add_pattern_relation(self, session, experience_id: str, pattern: str):
        """Adiciona relação com padrão"""
        query = """
            MERGE (p:Pattern {name: $pattern})
            WITH p
            MATCH (e:Experience {id: $experience_id})
            MERGE (e)-[:EXHIBITS]->(p)
            SET p.last_seen = $timestamp,
                p.frequency = coalesce(p.frequency, 0) + 1
        """
        
        session.run(query, 
            pattern=pattern,
            experience_id=experience_id,
            timestamp=datetime.now().isoformat()
        )
    
    def _connect_similar_experiences(self, session, experience_id: str, task: str):
        """Conecta experiências similares baseado na tarefa"""
        # Buscar experiências com tarefas similares
        query = """
            MATCH (e1:Experience {id: $experience_id})
            MATCH (e2:Experience) 
            WHERE e2.id <> $experience_id 
            AND (
                e2.task CONTAINS $task_words[0] OR
                e2.task CONTAINS $task_words[1] OR  
                e2.task CONTAINS $task_words[2]
            )
            WITH e1, e2, 
                 size([word IN $task_words WHERE e2.task CONTAINS word]) as similarity
            WHERE similarity >= 2
            MERGE (e1)-[:SIMILAR_TO {similarity: similarity}]->(e2)
        """
        
        # Extrair palavras-chave da tarefa
        task_words = [word.lower() for word in task.split() if len(word) > 3][:5]
        
        session.run(query, 
            experience_id=experience_id,
            task_words=task_words
        )
    
    def retrieve_similar_experiences(self, task: str, limit: int = 5, min_quality: float = 6.0) -> List[Dict]:
        """Recupera experiências similares para uma tarefa"""
        
        with self.driver.session() as session:
            query = """
                MATCH (e:Experience)
                WHERE e.quality_score >= $min_quality
                AND e.success = true
                AND (
                    e.task CONTAINS $task_words[0] OR
                    e.task CONTAINS $task_words[1] OR
                    e.task CONTAINS $task_words[2]
                )
                WITH e, 
                     size([word IN $task_words WHERE e.task CONTAINS word]) as relevance
                ORDER BY relevance DESC, e.quality_score DESC, e.timestamp DESC
                LIMIT $limit
                
                OPTIONAL MATCH (e)-[:EXHIBITS]->(p:Pattern)
                
                RETURN e.id as id,
                       e.task as task,
                       e.code as code,
                       e.quality_score as quality_score,
                       e.timestamp as timestamp,
                       e.agent_type as agent_type,
                       relevance,
                       collect(p.name) as patterns
            """
            
            task_words = [word.lower() for word in task.split() if len(word) > 3][:5]
            
            result = session.run(query,
                task_words=task_words,
                min_quality=min_quality,
                limit=limit
            )
            
            experiences = []
            for record in result:
                experiences.append({
                    "id": record["id"],
                    "task": record["task"],
                    "code": record["code"],
                    "quality_score": record["quality_score"],
                    "timestamp": record["timestamp"],
                    "agent_type": record["agent_type"],
                    "relevance": record["relevance"],
                    "patterns": record["patterns"]
                })
            
            return experiences
    
    def discover_patterns(self, min_frequency: int = 3) -> List[Dict]:
        """Descobre padrões emergentes nas experiências"""
        
        with self.driver.session() as session:
            query = """
                MATCH (p:Pattern)<-[:EXHIBITS]-(e:Experience)
                WHERE p.frequency >= $min_frequency
                WITH p, 
                     avg(e.quality_score) as avg_quality,
                     count(e) as experience_count,
                     collect(e.agent_type) as agent_types
                ORDER BY avg_quality DESC, experience_count DESC
                
                RETURN p.name as pattern,
                       p.frequency as frequency,
                       avg_quality,
                       experience_count,
                       agent_types
            """
            
            result = session.run(query, min_frequency=min_frequency)
            
            patterns = []
            for record in result:
                patterns.append({
                    "pattern": record["pattern"],
                    "frequency": record["frequency"],
                    "avg_quality": record["avg_quality"],
                    "experience_count": record["experience_count"],
                    "agent_types": list(set(record["agent_types"]))
                })
            
            return patterns
    
    def get_agent_performance(self, agent_type: str) -> Dict:
        """Analisa performance de um tipo de agente"""
        
        with self.driver.session() as session:
            query = """
                MATCH (e:Experience {agent_type: $agent_type})
                RETURN count(e) as total_experiences,
                       avg(e.quality_score) as avg_quality,
                       sum(case when e.success then 1 else 0 end) as successes,
                       count(case when e.success then 1 end) * 100.0 / count(e) as success_rate,
                       max(e.quality_score) as best_quality,
                       min(e.timestamp) as first_experience,
                       max(e.timestamp) as latest_experience
            """
            
            result = session.run(query, agent_type=agent_type)
            record = result.single()
            
            if record:
                return {
                    "agent_type": agent_type,
                    "total_experiences": record["total_experiences"],
                    "avg_quality": record["avg_quality"],
                    "success_rate": record["success_rate"],
                    "best_quality": record["best_quality"],
                    "first_experience": record["first_experience"],
                    "latest_experience": record["latest_experience"]
                }
            else:
                return {"agent_type": agent_type, "total_experiences": 0}
    
    def find_knowledge_gaps(self, task_categories: List[str]) -> List[Dict]:
        """Identifica lacunas de conhecimento"""
        
        gaps = []
        
        with self.driver.session() as session:
            for category in task_categories:
                query = """
                    MATCH (e:Experience)
                    WHERE e.task CONTAINS $category
                    RETURN count(e) as experience_count,
                           avg(e.quality_score) as avg_quality,
                           sum(case when e.success then 1 else 0 end) as successes
                """
                
                result = session.run(query, category=category)
                record = result.single()
                
                if record:
                    count = record["experience_count"]
                    avg_quality = record["avg_quality"] or 0
                    success_rate = (record["successes"] / count * 100) if count > 0 else 0
                    
                    # Considera gap se poucos exemplos ou baixa qualidade
                    if count < 5 or avg_quality < 7.0 or success_rate < 80:
                        gaps.append({
                            "category": category,
                            "experience_count": count,
                            "avg_quality": avg_quality,
                            "success_rate": success_rate,
                            "severity": self._calculate_gap_severity(count, avg_quality, success_rate)
                        })
        
        return sorted(gaps, key=lambda x: x["severity"], reverse=True)
    
    def _calculate_gap_severity(self, count: int, avg_quality: float, success_rate: float) -> float:
        """Calcula severidade da lacuna de conhecimento"""
        severity = 0.0
        
        # Penalizar por poucos exemplos
        if count < 3:
            severity += 5.0
        elif count < 10:
            severity += 2.0
        
        # Penalizar por baixa qualidade
        if avg_quality < 5.0:
            severity += 4.0
        elif avg_quality < 7.0:
            severity += 2.0
        
        # Penalizar por baixa taxa de sucesso
        if success_rate < 50:
            severity += 3.0
        elif success_rate < 80:
            severity += 1.0
        
        return severity
    
    def close(self):
        """Fecha conexão com banco"""
        self.driver.close()

# Função helper para criar experiências
def create_experience(task: str, code: str, quality_score: float, success: bool, 
                     agent_type: str, execution_result: str = None, error: str = None,
                     patterns: List[str] = None, context: Dict = None) -> CodingExperience:
    """Cria uma experiência de codificação"""
    
    return CodingExperience(
        id=str(uuid.uuid4()),
        task=task,
        code=code,
        quality_score=quality_score,
        success=success,
        timestamp=datetime.now().isoformat(),
        agent_type=agent_type,
        execution_result=execution_result,
        error=error,
        patterns=patterns or [],
        context=context or {}
    )