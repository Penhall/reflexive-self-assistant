import yaml
from datetime import datetime

INSIGHT_PATH = "reflection/supervisor_insight.yaml"
MEMORY_PATH = "reflection/memory_log.yaml"
AGENDA_PATH = "reflection/symbolic_agenda.yaml"

class StrategyPlanner:
    def __init__(self):
        self.insight = self.load_yaml(INSIGHT_PATH)
        self.memory = self.load_yaml(MEMORY_PATH)

    def load_yaml(self, path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                return yaml.safe_load(f) or {}
        except FileNotFoundError:
            return {}

    def generate_agenda(self):
        recommendation = self.insight.get("insight_global", {}).get("recomendação", "")
        agenda = {"next_cycle": {}}

        if "variação" in recommendation.lower():
            agenda["next_cycle"] = {
                "CodeAgent": "Implementar versão alternativa da função atual",
                "TestAgent": "Ampliar cobertura com novos cenários",
                "DocumentationAgent": "Gerar documentação com exemplos"
            }
        elif "falhas" in recommendation.lower():
            agenda["next_cycle"] = {
                "CodeAgent": "Refatorar função para robustez",
                "TestAgent": "Executar fallback simbólico por anomalias",
                "DocumentationAgent": "Gerar resumo simbólico mínimo"
            }
        else:
            agenda["next_cycle"] = {
                "CodeAgent": "Implementar função de login",
                "TestAgent": "Gerar testes padrão",
                "DocumentationAgent": "Documentar conforme padrão"
            }

        agenda["timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(AGENDA_PATH, "w", encoding="utf-8") as f:
            yaml.safe_dump(agenda, f, sort_keys=False, allow_unicode=True)