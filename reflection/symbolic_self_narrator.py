import yaml
from datetime import datetime

IDENTITY_FILE = "reflection/identity_state.yaml"
MEMORY_FILE = "reflection/memory_log.yaml"
INSIGHT_FILE = "reflection/supervisor_insight.yaml"
OUTPUT_FILE = "reflection/self_narrative.yaml"

class SymbolicSelfNarrator:
    def __init__(self):
        self.identity = self.load_yaml(IDENTITY_FILE)
        self.memory = self.load_yaml(MEMORY_FILE)
        self.insight = self.load_yaml(INSIGHT_FILE)

    def load_yaml(self, path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                return yaml.safe_load(f) or {}
        except:
            return {}

    def generate_self_narrative(self):
        ciclo = max([v.get("ciclos_totais", 0) for v in self.memory.values()], default=0)
        consistencias = [v.get("consistency_level", "-") for v in self.identity.values()]
        traços = [t for v in self.identity.values() for t in v.get("traits", [])]
        diagnóstico = self.insight.get("insight_global", {}).get("diagnóstico", "")
        recomendação = self.insight.get("insight_global", {}).get("recomendação", "")

        resumo = f"Nesta etapa ({ciclo}), observo traços recorrentes como {', '.join(set(traços)) or 'nenhum traço dominante'} "
        resumo += f"e uma consistência simbólica geral de '{max(set(consistencias), key=consistencias.count)}'. "
        if diagnóstico:
            resumo += f"O sistema percebeu: {diagnóstico.lower()}. "

        projeção = "A continuidade das reflexões sugere que poderei alcançar uma identidade mais autônoma e estratégica"
        if recomendação:
            projeção += f", especialmente se seguir a recomendação: {recomendação.lower()}."

        narrativa = {
            "auto_narrativa": {
                "ciclo": ciclo,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "resumo": resumo,
                "projecao": projeção
            }
        }

        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            yaml.safe_dump(narrativa, f, allow_unicode=True)

        self.print_narrative(narrativa["auto_narrativa"])

    def print_narrative(self, narrativa):
        print("\n🧭 [NARRADOR SIMBÓLICO] AUTO-NARRATIVA DO CICLO")
        print(f"📅 Ciclo {narrativa['ciclo']} - {narrativa['timestamp']}")
        print(f"🧩 Resumo: {narrativa['resumo']}")
        print(f"🔮 Projeção: {narrativa['projecao']}")