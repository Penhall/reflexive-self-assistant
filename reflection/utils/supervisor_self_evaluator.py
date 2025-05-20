import yaml
from datetime import datetime
from collections import Counter

INSIGHT_FILE = "reflection/supervisor_insight.yaml"
OUTPUT_FILE = "reflection/supervisor_self_reflection.yaml"

class SupervisorSelfEvaluator:
    def __init__(self):
        self.insight_data = self.load_yaml(INSIGHT_FILE)
        self.history = []

    def load_yaml(self, path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                return yaml.safe_load(f) or {}
        except FileNotFoundError:
            return {}

    def self_reflect(self):
        insight = self.insight_data.get("insight_global", {})
        if not insight:
            return

        self.history.append(insight.get("diagnóstico", "indefinido"))

        reflection = {
            "ciclo": insight.get("ciclo"),
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "diagnóstico_atual": insight.get("diagnóstico"),
            "frequência_diagnósticos": dict(Counter(self.history)),
            "revisão": None
        }

        if self.history.count(insight.get("diagnóstico")) >= 2:
            reflection["revisão"] = f"O diagnóstico '{insight.get('diagnóstico')}' apareceu várias vezes. Pode indicar falha estratégica."

        elif "nenhuma anomalia" in insight.get("diagnóstico", "").lower():
            reflection["revisão"] = "Padrão estável detectado. Reflexão supervisionada parece estar funcionando bem."

        else:
            reflection["revisão"] = "Diagnóstico novo registrado. Acompanhar se haverá repetição."

        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            yaml.safe_dump({"reflexão_supervisor": reflection}, f, allow_unicode=True)

        self.print_reflection(reflection)

    def print_reflection(self, data):
        print("\n📘 [AUTOAVALIAÇÃO DO SUPERVISOR]")
        print(f"📅 Ciclo: {data['ciclo']} | {data['timestamp']}")
        print(f"📌 Diagnóstico atual: {data['diagnóstico_atual']}")
        print(f"📈 Frequência: {data['frequência_diagnósticos']}")
        print(f"🧠 Revisão simbólica: {data['revisão']}")