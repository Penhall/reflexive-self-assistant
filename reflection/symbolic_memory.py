import yaml
from datetime import datetime
from collections import Counter

MEMORY_LOG_PATH = "reflection/memory_log.yaml"

class SymbolicMemory:
    def __init__(self):
        self.memory = self.load_memory()

    def load_memory(self):
        try:
            with open(MEMORY_LOG_PATH, "r", encoding="utf-8") as f:
                return yaml.safe_load(f) or {}
        except FileNotFoundError:
            return {}

    def save_memory(self):
        with open(MEMORY_LOG_PATH, "w", encoding="utf-8") as f:
            yaml.safe_dump(self.memory, f, sort_keys=False, allow_unicode=True)

    def update_memory(self, identity_state):
        for agent, profile in identity_state.items():
            if agent not in self.memory:
                self.memory[agent] = {
                    "ciclos_totais": 0,
                    "consistencia": {"Alta": 0, "Moderada": 0, "Baixa": 0},
                    "traços_frequentes": [],
                    "marcos": []
                }

            self.memory[agent]["ciclos_totais"] += 1
            consist = profile.get("consistency_level", "Desconhecido")
            if consist in self.memory[agent]["consistencia"]:
                self.memory[agent]["consistencia"][consist] += 1

            traços = profile.get("traits", [])
            self.memory[agent]["traços_frequentes"].extend(traços)

            hint = profile.get("adaptive_hint", "")
            if "anomalia" in hint.lower():
                self.memory[agent]["marcos"].append(f"{self.timestamp()}: Anomalia detectada")
            elif "loop" in hint.lower():
                self.memory[agent]["marcos"].append(f"{self.timestamp()}: Loop identificado")

        self.sintetizar_tracos()
        self.save_memory()

    def sintetizar_tracos(self):
        for agent in self.memory:
            freq = Counter(self.memory[agent]["traços_frequentes"])
            self.memory[agent]["traços_frequentes"] = [
                t for t, _ in freq.most_common(3)
            ]

    def timestamp(self):
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")