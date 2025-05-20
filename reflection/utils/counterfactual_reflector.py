import yaml
from datetime import datetime

FILES = {
    "governance": "reflection/symbolic_governance.yaml",
    "regeneration": "reflection/creative_regeneration.yaml",
    "identity": "reflection/identity_state.yaml",
    "output": "reflection/counterfactual_reflection.yaml"
}

class CounterfactualReflector:
    def __init__(self):
        self.gov = self.load(FILES["governance"])
        self.regen = self.load(FILES["regeneration"])
        self.identity = self.load(FILES["identity"])

    def load(self, path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                return yaml.safe_load(f) or {}
        except:
            return {}

    def reflect(self):
        decisao = self.gov.get("governança_simbolica", {}).get("decisão", "").lower()
        proposta = self.regen.get("regeneração_criativa", {}).get("proposta", "")
        ciclo = self.gov.get("governança_simbolica", {}).get("ciclo", 0)

        if not proposta or "rejeitada" not in decisao:
            return  # Nada a refletir contrafactualmente

        padroes = [v.get("predominant_pattern", "").lower() for v in self.identity.values()]
        diversidade = len(set(padroes))

        if "disruptivo" in proposta.lower() and diversidade < 2:
            impacto = "Poderia ter promovido diversidade simbólica significativa."
            emocao = "Curioso"
            sugestao = "Revisitar proposta futuramente com consistência maior."
        elif "reforçar" in proposta.lower():
            impacto = "Teria estabilizado padrões frágeis."
            emocao = "Confiante"
            sugestao = "Avaliar necessidade caso instabilidade persista."
        else:
            impacto = "Impacto incerto — proposta simbólica neutra."
            emocao = "Neutro"
            sugestao = "Monitorar relevância em ciclos futuros."

        resultado = {
            "reflexao_contrafactual": {
                "ciclo": ciclo,
                "proposta_ignorada": proposta,
                "impacto_simulado": impacto,
                "emoção_simulada": emocao,
                "sugestão_futura": sugestao,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
        }

        with open(FILES["output"], "w", encoding="utf-8") as f:
            yaml.safe_dump(resultado, f, allow_unicode=True)

        self.print_summary(resultado["reflexao_contrafactual"])

    def print_summary(self, dados):
        print("\n🔍 [REFLEXÃO CONTRAFACTUAL]")
        print(f"📅 Ciclo: {dados['ciclo']} | 🕓 {dados['timestamp']}")
        print(f"🚫 Proposta ignorada: {dados['proposta_ignorada']}")
        print(f"🔁 Impacto simulado: {dados['impacto_simulado']}")
        print(f"🎭 Emoção simulada: {dados['emoção_simulada']}")
        print(f"🧭 Sugestão futura: {dados['sugestão_futura']}")