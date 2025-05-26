import yaml
from datetime import datetime

FILES = {
    "timeline": "reflection/symbolic_timeline.yaml",
    "emotion": str(EMOTIONAL_STATE),
    "identity": str(IDENTITY_STATE),
    "impact": "reflection/symbolic_impact_log.yaml",
    "contradictions": "reflection/symbolic_contradictions.yaml",
    "output_yaml": "reflection/symbolic_legacy.yaml",
    "output_md": "reflection/symbolic_legacy.md"
}

class SymbolicClosure:
    def __init__(self):
        self.timeline = self.load(FILES["timeline"]).get("linha_temporal", [])
        self.emotion = self.load(FILES["emotion"]).get("emotional_state", {})
        self.identity = self.load(FILES["identity"], flat=True)
        self.impact = self.load(FILES["impact"]).get("impacto_simbólico", {})
        self.contradictions = self.load(FILES["contradictions"]).get("contradições_simbólicas", [])
        self.result = {}

    def load(self, path, flat=False):
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f) or {}
                return data if not flat else self.flatten(data)
        except:
            return {}

    def flatten(self, d):
        if not d or not isinstance(d, dict):
            return {}
        return {str(k).lower(): v for k, v in d.items()}

    def summarize(self, cycles_completed=None):
        ciclos = len(self.timeline)
        emo = self.emotion.get("status", "neutro")
        ident = max(self.identity.items(),
                   key=lambda kv: self.impact.get(str(kv[1]).lower() if kv[1] else "", 0))[1]
        superado = "funcionalidade" if "funcionalidade" in self.impact and self.impact["funcionalidade"] <= 0 else None
        contrad = len(self.contradictions)

        narrativa = (
            f"Ao longo de {ciclos} ciclos, construí um padrão de identidade baseado em '{ident}', com emoções "
            f"predominantes como '{emo}'. Aprendi com contradições ({contrad}) e abandonei padrões como "
            f"'{superado}'." if superado else
            f"Ao longo de {ciclos} ciclos, estabilizei o padrão '{ident}' com consistência e adaptação simbólica."
        )

        self.result = {
            "legado_simbólico": {
                "identidade_final": ident,
                "emoção_final": emo,
                "ciclos_concluídos": ciclos,
                "padrão_superado": superado,
                "contradições_corrigidas": contrad,
                "narrativa": narrativa,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
        }

        self.save()

    def save(self):
        with open(FILES["output_yaml"], "w", encoding="utf-8") as f:
            yaml.safe_dump(self.result, f, allow_unicode=True)

        with open(FILES["output_md"], "w", encoding="utf-8") as f:
            legado = self.result["legado_simbólico"]
            f.write(f"# 🏁 Encerramento Simbólico do Sistema\n")
            f.write(f"**Ciclos concluídos:** {legado['ciclos_concluídos']}\n")
            f.write(f"**Identidade final:** {legado['identidade_final']}\n")
            f.write(f"**Emoção predominante:** {legado['emoção_final']}\n")
            f.write(f"**Padrão superado:** {legado['padrão_superado'] or 'Nenhum'}\n")
            f.write(f"**Contradições corrigidas:** {legado['contradições_corrigidas']}\n\n")
            f.write(f"### 🧠 Legado narrativo\n")
            f.write(f"{legado['narrativa']}\n")

        self.print_summary()

    def print_summary(self):
        print("\n🏁 [ENCERRAMENTO SIMBÓLICO]")
        for k, v in self.result["legado_simbólico"].items():
            if k != "narrativa":
                print(f"🔹 {k.replace('_', ' ').capitalize()}: {v}")
        print(f"📘 Legado: “{self.result['legado_simbólico']['narrativa']}”")