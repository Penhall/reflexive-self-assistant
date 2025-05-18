import yaml
from datetime import datetime
from collections import Counter

IDENTITY_STATE = "reflection/identity_state.yaml"
MEMORY_LOG = "reflection/memory_log.yaml"
INSIGHT_OUTPUT = "reflection/supervisor_insight.yaml"

class SupervisorAgent:
    def __init__(self):
        self.identity = self.load_yaml(IDENTITY_STATE)
        self.memory = self.load_yaml(MEMORY_LOG)
        self.insight = {}

    def load_yaml(self, path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                return yaml.safe_load(f) or {}
        except FileNotFoundError:
            return {}

    def evaluate_global_state(self):
        ciclo = max([v.get("ciclos_totais", 0) for v in self.memory.values()], default=0)
        consistencias = [v.get("consistency_level", "Desconhecido") for v in self.identity.values()]
        predominant_patterns = [v.get("predominant_pattern", "") for v in self.identity.values()]
        hints = [v.get("adaptive_hint", "") for v in self.identity.values()]

        insight = {
            "ciclo": ciclo,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "diagnóstico": None,
            "recomendação": None
        }

        if all("Baixa" == c for c in consistencias):
            insight["diagnóstico"] = "Todos os agentes estão com consistência simbólica baixa"
            insight["recomendação"] = "Reavaliar prompts ou lógica base"
        elif hints.count("⚠️ Sugerido fallback por 2 anomalias consecutivas") >= 2:
            insight["diagnóstico"] = "Falhas recorrentes em múltiplos agentes"
            insight["recomendação"] = "Verificar entrada de tarefas ou estado do código base"
        elif Counter(predominant_patterns).most_common(1)[0][1] == len(predominant_patterns):
            pattern = predominant_patterns[0]
            insight["diagnóstico"] = f"Uniformidade simbólica: todos os agentes estão no padrão '{pattern}'"
            insight["recomendação"] = f"Introduzir variação estratégica nos prompts"
        else:
            insight["diagnóstico"] = "Nenhuma anomalia crítica detectada"
            insight["recomendação"] = "Continuar ciclos normalmente"

        self.insight = {"insight_global": insight}
        self.save_insight()
        self.print_insight()

    def save_insight(self):
        with open(INSIGHT_OUTPUT, "w", encoding="utf-8") as f:
            yaml.safe_dump(self.insight, f, sort_keys=False, allow_unicode=True)

    def print_insight(self):
        print("\n📡 [SUPERVISOR] INSIGHT GLOBAL:")
        print(f"   Ciclo: {self.insight['insight_global']['ciclo']}")
        print(f"   Diagnóstico: {self.insight['insight_global']['diagnóstico']}")
        print(f"   Recomendações: {self.insight['insight_global']['recomendação']}")