"""
Extensão para o ReflectionAgent: evolução simbólica com base em padrões recorrentes.
"""

import json
import yaml
from datetime import datetime
from utils.graph_interface import GraphMemory

CYCLE_HISTORY_PATH = "reflection/cycle_history.json"
IDENTITY_STATE_PATH = "reflection/identity_state.yaml"
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
            predominant = max(set(history[agent_name]), key=history[agent_name].count)
            freq = history[agent_name].count(predominant)

            identity[agent_name]["predominant_pattern"] = predominant
            identity[agent_name]["last_adaptation"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            identity[agent_name]["consistency_level"] = "Alta" if freq >= 4 else "Moderada" if freq >= 2 else "Baixa"

            # Traços simbólicos simplificados
            traits = []
            if "teste" in predominant.lower():
                traits.append("Analítico")
            if "document" in predominant.lower():
                traits.append("Explicativo")
            if "funcional" in predominant.lower():
                traits.append("Objetivo")

            identity[agent_name]["traits"] = traits

        self.save_history(history)
        self.save_identity(identity)
        self.graph.close()

    def get_latest_pattern(self, agent_name):
        patterns = self.graph.get_patterns_by_agent(agent_name)
        return patterns[-1] if patterns else None

    def load_history(self):
        try:
            with open(CYCLE_HISTORY_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            return { "CodeAgent": [], "TestAgent": [], "DocumentationAgent": [] }

    def save_history(self, history):
        with open(CYCLE_HISTORY_PATH, "w", encoding="utf-8") as f:
            json.dump(history, f, indent=2)

    def load_identity(self):
        try:
            with open(IDENTITY_STATE_PATH, "r", encoding="utf-8") as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            return {}

    def save_identity(self, identity):
        with open(IDENTITY_STATE_PATH, "w", encoding="utf-8") as f:
            yaml.safe_dump(identity, f, sort_keys=False, allow_unicode=True)