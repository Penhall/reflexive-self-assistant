"""
Módulo de integração com Neo4j para representar e consultar a memória simbólica em grafo.
Inclui implementação mock para quando o Neo4j não está disponível.
"""

from neo4j import GraphDatabase, exceptions
import os
from dotenv import load_dotenv
from typing import List, Dict, Optional

load_dotenv()

NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER = os.getenv("NEO4J_USERNAME", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "password")


class MockGraphMemory:
    """Implementação em memória para quando o Neo4j não está disponível"""
    
    def __init__(self):
        self.patterns = []
        self.categories = []
        self.agents = []
        self.relations = []
    
    def close(self):
        pass
    
    def register_pattern(self, reaction: str, pattern: str, category: str, agent_name: str) -> None:
        """Registra um padrão na memória"""
        self.patterns.append({"reaction": reaction, "pattern": pattern})
        self.categories.append(category)
        self.agents.append(agent_name)
        self.relations.append({
            "reaction": reaction,
            "pattern": pattern,
            "category": category,
            "agent": agent_name
        })
    
    def get_patterns_by_agent(self, agent_name: str) -> List[str]:
        """Obtém padrões por agente"""
        return [r["pattern"] for r in self.relations if r["agent"] == agent_name]
    
    def get_categories_and_counts(self) -> List[Dict[str, int]]:
        """Obtém categorias e contagens"""
        from collections import Counter
        counts = Counter(self.categories)
        return [{"category": k, "count": v} for k, v in counts.items()]


class GraphMemory:
    def __init__(self):
        self.driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))

    def close(self):
        self.driver.close()

    def register_pattern(self, reaction, pattern, category, agent_name):
        query = (
            "MERGE (r:Reaction {text: $reaction}) "
            "MERGE (p:Pattern {description: $pattern}) "
            "MERGE (c:Category {name: $category}) "
            "MERGE (a:Agent {name: $agent_name}) "
            "MERGE (r)-[:EXHIBITS]->(p) "
            "MERGE (p)-[:BELONGS_TO]->(c) "
            "MERGE (p)-[:OBSERVED_IN]->(a)"
        )
        with self.driver.session() as session:
            session.run(query, reaction=reaction, pattern=pattern, category=category, agent_name=agent_name)

    def get_patterns_by_agent(self, agent_name):
        query = (
            "MATCH (a:Agent {name: $agent_name})<-[:OBSERVED_IN]-(p:Pattern) "
            "RETURN p.description AS pattern"
        )
        with self.driver.session() as session:
            result = session.run(query, agent_name=agent_name)
            return [record["pattern"] for record in result]

    def get_categories_and_counts(self):
        query = (
            "MATCH (p:Pattern)-[:BELONGS_TO]->(c:Category) "
            "RETURN c.name AS category, count(p) AS count "
            "ORDER BY count DESC"
        )
        with self.driver.session() as session:
            return [{"category": record["category"], "count": record["count"]} for record in session.run(query)]