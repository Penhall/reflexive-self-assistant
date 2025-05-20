import yaml
from datetime import datetime
import random

FILES = {
    "impact": "reflection/symbolic_impact_log.yaml",
    "emotion": "reflection/emotional_state.yaml",
    "output": "reflection/creative_regeneration.yaml"
}

class CreativeRegenerator:
    def __init__(self):
        self.impact = self.load(FILES["impact"]).get("impacto_simbólico", {})
        self.emotion = self.load(FILES["emotion"]).get("emotional_state", {})

    def load(self, path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                return yaml.safe_load(f) or {}
        except:
            return {}

    def propose_creative_action(self):
        ciclo = self.emotion.get("ciclo", 0)
        estado = self.emotion.get("status", "neutro").lower()

        proposta, motivacao = self.select_pattern_based_on_impact(estado)

        resultado = {
            "regeneração_criativa": {
                "ciclo": ciclo,
                "proposta": proposta,
                "motivação": motivacao,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
        }

        with open(FILES["output"], "w", encoding="utf-8") as f:
            yaml.safe_dump(resultado, f, allow_unicode=True)

        self.print_regeneration(resultado["regeneração_criativa"])

    def select_pattern_based_on_impact(self, estado):
        positivos = [k for k, v in self.impact.items() if v > 0]
        negativos = [k for k, v in self.impact.items() if v < 0]
        neutros = [k for k, v in self.impact.items() if v == 0]

        if estado == "confiante":
            if positivos:
                escolhido = max(positivos, key=lambda k: self.impact[k])
                return f"Reforçar padrão '{escolhido}'", "Alta confiança e impacto positivo anterior"
        elif estado == "frustrado":
            escolha = [k for k in self.impact if k not in negativos]
            if escolha:
                return f"Evitar padrão negativo. Usar '{random.choice(escolha)}'", "Frustração com padrão anterior"
        elif estado == "curioso":
            candidatos = positivos or neutros or list(self.impact.keys())
            if candidatos:
                return f"Explorar padrão '{random.choice(candidatos)}'", "Curiosidade com padrões simbólicos variados"
        elif estado == "estagnado":
            novos = [k for k in ["variação", "integração", "combinação"] if k not in self.impact]
            if novos:
                return f"Experimentar padrão inédito: '{random.choice(novos)}'", "Estagnação sugere tentativa ousada"

        return "Executar padrão simbólico alternativo ao atual", "Estado simbólico neutro ou sem dados anteriores"

    def print_regeneration(self, data):
        print("\n✨ [REGENERAÇÃO CRIATIVA ESTRATÉGICA]")
        print(f"📅 Ciclo: {data['ciclo']} | 🕓 {data['timestamp']}")
        print(f"🧠 Proposta: {data['proposta']}")
        print(f"🎯 Motivação: {data['motivação']}")