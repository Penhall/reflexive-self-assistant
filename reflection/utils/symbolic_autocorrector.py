import yaml
from datetime import datetime

FILES = {
    "impact": "reflection/symbolic_impact_log.yaml",
    "contradictions": "reflection/symbolic_contradictions.yaml",
    "correction_log": "reflection/symbolic_correction_log.yaml"
}

class SymbolicAutocorrector:
    def __init__(self):
        self.impact = self.load(FILES["impact"]).get("impacto_simbólico", {})
        self.contradições = self.load(FILES["contradictions"]).get("contradições_simbólicas", [])
        self.correções = []

    def load(self, path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                return yaml.safe_load(f) or {}
        except:
            return {}

    def apply_corrections(self):
        for item in self.contradições:
            padrao = item.get("padrão")
            ciclo = item.get("ciclo")
            if padrao in self.impact and self.impact[padrao] > 0:
                old_val = self.impact[padrao]
                self.impact[padrao] -= 1
                self.correções.append({
                    "ciclo": ciclo,
                    "padrão": padrao,
                    "de": old_val,
                    "para": self.impact[padrao],
                    "justificativa": f"Contradição detectada no ciclo {ciclo}"
                })

        self.save_corrections()

    def save_corrections(self):
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        # Atualiza log de impacto
        with open(FILES["impact"], "w", encoding="utf-8") as f:
            yaml.safe_dump({
                "impacto_simbólico": self.impact,
                "última_atualização": now
            }, f, allow_unicode=True)

        # Salva histórico de correções
        with open(FILES["correction_log"], "w", encoding="utf-8") as f:
            yaml.safe_dump({
                "ajustes_simbólicos": self.correções,
                "última_execução": now
            }, f, allow_unicode=True)

        self.print_summary()

    def print_summary(self):
        if not self.correções:
            print("\n✅ Nenhum ajuste simbólico necessário.")
        else:
            print("\n♻️ [AUTOCORREÇÃO SIMBÓLICA]")
            for c in self.correções:
                print(f"🔻 {c['padrão']}: impacto ajustado de {c['de']} → {c['para']} (ciclo {c['ciclo']})")