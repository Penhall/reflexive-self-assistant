import yaml
from datetime import datetime

FILES = {
    "regeneration": "reflection/creative_regeneration.yaml",
    "identity": "reflection/identity_state.yaml",
    "output": "reflection/symbolic_governance.yaml"
}

class SymbolicGovernance:
    def __init__(self):
        self.regen = self.load(FILES["regeneration"])
        self.identity = self.load(FILES["identity"])

    def load(self, path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                return yaml.safe_load(f) or {}
        except:
            return {}

    def deliberate(self):
        proposta = self.regen.get("regeneração_criativa", {}).get("proposta", "")
        ciclo = self.regen.get("regeneração_criativa", {}).get("ciclo", 0)

        votos = {}
        count_yes = 0
        count_no = 0

        for agente, perfil in self.identity.items():
            padrao = perfil.get("predominant_pattern", "").lower()
            consistencia = perfil.get("consistency_level", "").lower()
            if padrao in proposta.lower() and consistencia in ["alta", "média"]:
                votos[agente] = "Sim"
                count_yes += 1
            elif "disruptivo" in proposta.lower() and consistencia == "baixa":
                votos[agente] = "Sim - oportunidade de evolução"
                count_yes += 1
            else:
                votos[agente] = "Não - risco de desalinhamento"
                count_no += 1

        if count_yes > count_no:
            decisao = "Aprovada"
            justificativa = "Maioria dos agentes apoiou a proposta."
        elif count_yes == count_no:
            decisao = "Aprovada com ressalvas (empate)"
            justificativa = "Decisão empatada — supervisor assume aprovação cautelosa."
        else:
            decisao = "Rejeitada"
            justificativa = "A maioria dos agentes considerou a proposta desalinhada."

        resultado = {
            "governança_simbolica": {
                "ciclo": ciclo,
                "proposta": proposta,
                "votos": votos,
                "decisão": decisao,
                "justificativa": justificativa,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
        }

        with open(FILES["output"], "w", encoding="utf-8") as f:
            yaml.safe_dump(resultado, f, allow_unicode=True)

        self.print_summary(resultado["governança_simbolica"])
        return decisao.lower().startswith("aprovada")

    def print_summary(self, resultado):
        print("\n⚖️ [GOVERNANÇA SIMBÓLICA]")
        print(f"📅 Ciclo {resultado['ciclo']} | 🕓 {resultado['timestamp']}")
        print(f"📜 Proposta: {resultado['proposta']}")
        print(f"📊 Votos: {resultado['votos']}")
        print(f"✅ Decisão: {resultado['decisão']}")
        print(f"🧠 Justificativa: {resultado['justificativa']}")