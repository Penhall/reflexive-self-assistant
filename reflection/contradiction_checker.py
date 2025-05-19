import yaml
from datetime import datetime

FILES = {
    "impact": "reflection/symbolic_impact_log.yaml",
    "governance": "reflection/symbolic_governance.yaml",
    "timeline": "reflection/symbolic_timeline.yaml",
    "output": "reflection/symbolic_contradictions.yaml"
}

class ContradictionChecker:
    def __init__(self):
        self.impact = self.load(FILES["impact"]).get("impacto_simbólico", {})
        self.gov = self.load(FILES["governance"], multiple=True)
        self.timeline = self.load(FILES["timeline"]).get("linha_temporal", [])
        self.alertas = []

    def load(self, path, multiple=False):
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f) or {}
                return [data] if multiple and isinstance(data, dict) else data
        except:
            return {}

    def detect_contradictions(self):
        for entry in self.gov if isinstance(self.gov, list) else [self.gov]:
            proposta = entry.get("governança_simbolica", {}).get("proposta", "").lower()
            decisao = entry.get("governança_simbolica", {}).get("decisão", "").lower()
            ciclo = entry.get("governança_simbolica", {}).get("ciclo", 0)
            for padrao, score in self.impact.items():
                if padrao in proposta and "rejeitada" in decisao and score > 0:
                    self.alertas.append({
                        "ciclo": ciclo,
                        "padrão": padrao,
                        "impacto": score,
                        "proposta": proposta,
                        "decisão": decisao,
                        "tipo": "Contradição",
                        "mensagem": f"Padrão '{padrao}' tem impacto positivo (+{score}) mas foi rejeitado."
                    })

        self.save_results()

    def save_results(self):
        resultado = {
            "contradições_simbólicas": self.alertas,
            "última_varredura": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        with open(FILES["output"], "w", encoding="utf-8") as f:
            yaml.safe_dump(resultado, f, allow_unicode=True)
        self.print_alerts()

    def print_alerts(self):
        if not self.alertas:
            print("\n✅ Nenhuma contradição simbólica detectada.")
        else:
            print("\n⚠️ [CONTRADIÇÕES SIMBÓLICAS DETECTADAS]")
            for alerta in self.alertas:
                print(f"🔸 Ciclo {alerta['ciclo']}: {alerta['mensagem']}")