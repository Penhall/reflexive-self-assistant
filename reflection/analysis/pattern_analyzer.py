"""
Extensão para o ReflectionAgent: evolução simbólica com base em padrões recorrentes.
"""

import json
import yaml
from datetime import datetime
from memory.graph_rag.graph_interface import GraphMemory
import config.paths

config.paths.CYCLE_HISTORY_PATH = str(config.paths.CYCLE_HISTORY)
config.paths.IDENTITY_STATE_PATH = str(config.paths.IDENTITY_STATE)
MAX_HISTORY = 5

class SymbolicEvaluator:
    def __init__(self):
        self.graph = GraphMemory()

    def update_symbolic_identity(self, agents):
        history = self.load_history()
        identity = self.load_identity()

        for agent in agents:
            agent_name = agent.__class__.__name__
            current_pattern = self.get_latest_pattern(agent_name)

            if not current_pattern:
                continue

            # Atualiza histórico
            history[agent_name].append(current_pattern)
            if len(history[agent_name]) > MAX_HISTORY:
                history[agent_name] = history[agent_name][-MAX_HISTORY:]

            # Avaliação simbólica
            predominant = max(set(history[agent_name]), key=history[agent_name].count) if history[agent_name] else "Padrão inicial"
            freq = history[agent_name].count(predominant) if history[agent_name] else 1

            identity[agent_name]["predominant_pattern"] = predominant
            identity[agent_name]["last_adaptation"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            identity[agent_name]["consistency_level"] = "Alta" if freq >= 4 else "Moderada" if freq >= 2 else "Baixa"

            # Traços simbólicos baseados em padrões e comportamentos
            traits = []
            if predominant and isinstance(predominant, str):
                predominant_lower = predominant.lower()
                
                # Traits baseados em padrões explícitos
                if any(word in predominant_lower for word in ["teste", "verific", "valid"]):
                    traits.append("Analítico")
                if any(word in predominant_lower for word in ["document", "explic", "descr"]):
                    traits.append("Explicativo")
                if any(word in predominant_lower for word in ["funcional", "exec", "implement"]):
                    traits.append("Objetivo")
                if "reflex" in predominant_lower or "adapt" in predominant_lower:
                    traits.append("Adaptável")
                
                # Traits baseados em consistência
                if identity[agent_name]["consistency_level"] == "Alta":
                    traits.append("Consistente")
                elif identity[agent_name]["consistency_level"] == "Baixa":
                    traits.append("Variável")
                
                # Garante pelo menos um trait básico
                if not traits:
                    traits.append("Operacional")

            identity[agent_name]["traits"] = sorted(list(set(traits)))  # Remove duplicados

        self.save_history(history)
        self.save_identity(identity)
        self.graph.close()

    def get_latest_pattern(self, agent_name):
        patterns = self.graph.get_patterns_by_agent(agent_name)
        if not patterns:
            return f"Padrão inicial {agent_name}"
        return patterns[-1] if patterns else f"Padrão inicial {agent_name}"

    def load_history(self):
        try:
            with open(config.paths.CYCLE_HISTORY_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            return { "CodeAgent": [], "TestAgent": [], "DocumentationAgent": [] }

    def save_history(self, history):
        with open(config.paths.CYCLE_HISTORY_PATH, "w", encoding="utf-8") as f:
            json.dump(history, f, indent=2)

    def load_identity(self):
        try:
            with open(config.paths.IDENTITY_STATE_PATH, "r", encoding="utf-8") as f:
                identity = yaml.safe_load(f)
                if not identity:
                    identity = {}
                
                # Garante estrutura básica para cada agente
                for agent_name in ["CodeAgent", "TestAgent", "DocumentationAgent"]:
                    if agent_name not in identity:
                        identity[agent_name] = {
                            "predominant_pattern": "",
                            "last_adaptation": "",
                            "consistency_level": "Baixa",
                            "traits": []
                        }
                return identity
        except FileNotFoundError:
            return {
                "CodeAgent": {
                    "predominant_pattern": "",
                    "last_adaptation": "",
                    "consistency_level": "Baixa",
                    "traits": []
                },
                "TestAgent": {
                    "predominant_pattern": "",
                    "last_adaptation": "",
                    "consistency_level": "Baixa",
                    "traits": []
                },
                "DocumentationAgent": {
                    "predominant_pattern": "",
                    "last_adaptation": "",
                    "consistency_level": "Baixa",
                    "traits": []
                }
            }

    def save_identity(self, identity):
        with open(config.paths.IDENTITY_STATE_PATH, "w", encoding="utf-8") as f:
            yaml.safe_dump(identity, f, sort_keys=False, allow_unicode=True)