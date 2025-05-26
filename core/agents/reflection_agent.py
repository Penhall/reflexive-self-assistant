"""
Agente reflexivo que analisa padrões e atualiza a identidade simbólica do sistema.
"""

import os
from datetime import datetime
from memory.graph_rag.graph_interface import GraphMemory, MockGraphMemory
from neo4j import exceptions


class ReflectionAgent:
    def __init__(self):
        try:
            self.graph = GraphMemory()
            # Testa a conexão
            self.graph.get_categories_and_counts()
            self.using_mock = False
        except (exceptions.ServiceUnavailable, exceptions.AuthError) as e:
            from memory.graph_rag.graph_interface import MockGraphMemory
            self.graph = MockGraphMemory()
            self.using_mock = True
            print(f"⚠️ Neo4j não disponível ({str(e)}) - usando implementação em memória")
            
        self.log_path = os.path.join("reflection", "analysis_history.md")

    def reflect_on_tasks(self, agents):
        print("🔁 Iniciando reflexão simbólica sobre os agentes...\n")

        log_lines = []
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_lines.append(f"### Ciclo de Reflexão — {timestamp}\n")

        for agent in agents:
            reaction = agent.latest_output
            pattern = self.identify_pattern(reaction)
            category = self.categorize_pattern(pattern)
            agent_name = agent.__class__.__name__

            print(f"🧠 {agent_name} → padrão: '{pattern}' (categoria: {category})")
            self.graph.register_pattern(reaction, pattern, category, agent_name)

            log_lines.append(f"- **{agent_name}** → Padrão: _{pattern}_ (Categoria: _{category}_)")
        
        log_lines.append("\n")

        self.append_to_log(log_lines)
        print("✅ Reflexão simbólica registrada com sucesso.\n")

    def identify_pattern(self, text):
        text = text.lower()
        if "erro" in text or "falha" in text:
            return "Comportamento anômalo"
        elif "documentação" in text:
            return "Atualização documental"
        elif "testes" in text:
            return "Cobertura de teste"
        elif "login" in text:
            return "Implementação funcional"
        else:
            return "Execução padrão"

    def categorize_pattern(self, pattern):
        mapping = {
            "Comportamento anômalo": "Falha",
            "Atualização documental": "Documentação",
            "Cobertura de teste": "Testes",
            "Implementação funcional": "Funcionalidade",
            "Execução padrão": "Operação"
        }
        return mapping.get(pattern, "Outro")

    def append_to_log(self, lines):
        with open(self.log_path, "a", encoding="utf-8") as log_file:
            log_file.write("\n".join(lines) + "\n")

    def close(self):
        self.graph.close()