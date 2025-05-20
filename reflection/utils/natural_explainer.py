import yaml
from datetime import datetime

FILES = {
    "identity": "reflection/identity_state.yaml",
    "emotion": "reflection/emotional_state.yaml",
    "insight": "reflection/supervisor_insight.yaml",
    "timeline": "reflection/symbolic_timeline.yaml",
    "output": "reflection/symbolic_explanation.yaml"
}

class NaturalExplainer:
    def __init__(self):
        self.identity = self.load(FILES["identity"])
        self.emotion = self.load(FILES["emotion"])
        self.insight = self.load(FILES["insight"])
        self.timeline = self.load(FILES["timeline"])

    def load(self, path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                return yaml.safe_load(f) or {}
        except:
            return {}

    def generate_explanation(self):
        ciclo = self.emotion.get("emotional_state", {}).get("ciclo", 0)
        emotion = self.emotion.get("emotional_state", {}).get("status", "neutro")
        reason = self.emotion.get("emotional_state", {}).get("razão", "")
        suggestion = self.emotion.get("emotional_state", {}).get("sugestão", "")

        patterns = [v.get("predominant_pattern", "N/D") for v in self.identity.values()]
        consistencies = [v.get("consistency_level", "-") for v in self.identity.values()]
        insight = self.insight.get("insight_global", {}).get("diagnóstico", "Sem diagnóstico")

        texto = (
            f"No ciclo {ciclo}, os agentes apresentaram padrões predominantes como "
            f"{', '.join(set(patterns))}, com níveis de consistência simbólica "
            f"{', '.join(set(consistencies))}. "
            f"O supervisor diagnosticou: {insight.lower()}. "
            f"O sistema se percebeu em um estado emocional "{emotion}", motivado por: {reason.lower()}. "
            f"Como resposta, a sugestão simbólica foi: {suggestion.lower()}."
        )

        resultado = {
            "explicação_natural": {
                "ciclo": ciclo,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "texto": texto
            }
        }

        with open(FILES["output"], "w", encoding="utf-8") as f:
            yaml.safe_dump(resultado, f, allow_unicode=True)

        print("\n📝 [EXPLICAÇÃO NATURAL SIMBÓLICA]")
        print(texto)