import yaml
from collections import defaultdict
from datetime import datetime

FILES = {
    "timeline": "reflection/symbolic_timeline.yaml",
    "emotion": str(EMOTIONAL_STATE),
    "governance": "reflection/symbolic_governance.yaml",
    "output": "reflection/symbolic_impact_log.yaml"
}

class SymbolicOptimizer:
    def __init__(self):
        self.timeline = self.load(FILES["timeline"])
        self.governance = self.load(FILES["governance"])
        self.impacto = defaultdict(int)

    def load(self, path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                return yaml.safe_load(f) or {}
        except:
            return {}

    def evaluate(self):
        eventos = self.timeline.get("linha_temporal", [])
        for e in eventos:
            identidade = e.get("identidade", "")
            emocao = e.get("emoção", "")
            proposta = e.get("evento", "")

            emocao_lower = emocao.lower() if emocao and isinstance(emocao, str) else ""
            proposta_lower = proposta.lower() if proposta and isinstance(proposta, str) else ""

            if identidade and isinstance(identidade, str):
                for parte in identidade.split(","):
                    parte = parte.strip().split(":")[-1].strip().lower()
                    score = self.score_emocao(emocao_lower)
                    self.impacto[parte] += score

            if "disruptivo" in proposta_lower:
                self.impacto["padrão disruptivo"] += self.score_emocao(emocao_lower)
            elif "estabilidade" in proposta_lower:
                self.impacto["estabilidade"] += self.score_emocao(emocao_lower)

        self.save_log()

    def score_emocao(self, e):
        if not e or not isinstance(e, str):
            return 0
        return {
            "confiante": 1,
            "curioso": 1,
            "cauteloso": 0,
            "neutro": 0,
            "estagnado": -1,
            "frustrado": -1
        }.get(e.lower(), 0)

    def save_log(self):
        output = {
            "impacto_simbólico": dict(self.impacto),
            "última_atualização": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        with open(FILES["output"], "w", encoding="utf-8") as f:
            yaml.safe_dump(output, f, allow_unicode=True)

        self.print_result(output)

    def print_result(self, dados):
        print("\n📊 [OTIMIZAÇÃO SIMBÓLICA]")
        for k, v in dados["impacto_simbólico"].items():
            print(f"🔹 {k}: {v:+}")
        print(f"🕓 Atualizado em: {dados['última_atualização']}")