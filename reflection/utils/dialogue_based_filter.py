import yaml
from datetime import datetime

FILES = {
    "dialogue": "reflection/symbolic_dialogue.yaml",
    "proposta": "reflection/creative_regeneration.yaml",
    "output": "reflection/dialogue_decision.yaml"
}

class DialogueBasedFilter:
    def __init__(self):
        self.dialogue = self.load(FILES["dialogue"]).get("diálogo_simbólico", {})
        self.meta = self.load(FILES["dialogue"])
        self.proposta = self.load(FILES["proposta"]).get("regeneração_criativa", {})
        self.resultado = {}

    def load(self, path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                return yaml.safe_load(f) or {}
        except:
            return {}

    def decide(self):
        apoio = sum(1 for v in self.dialogue.values() if "apoio" in v.lower())
        rejeicao = sum(1 for v in self.dialogue.values() if "rejeito" in v.lower())
        alerta = sum(1 for v in self.dialogue.values() if "alerta" in v.lower())
        ciclo = self.meta.get("ciclo", self.proposta.get("ciclo", 0))

        if rejeicao > apoio:
            decisao = "Vetada"
            just = f"Maioria dos agentes rejeitaram a proposta ({rejeicao} rejeições, {apoio} apoios)."
        elif apoio > rejeicao:
            decisao = "Reforçada"
            just = f"Maioria dos agentes apoiaram a proposta ({apoio} apoios, {rejeicao} rejeições)."
        else:
            decisao = "Mantida"
            just = f"Sem maioria clara. Proposta mantida com {apoio} apoios e {rejeicao} rejeições."

        self.resultado = {
            "decisão_dialogada": {
                "resultado": decisao,
                "justificativa": just,
                "ciclo": ciclo,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
        }

        with open(FILES["output"], "w", encoding="utf-8") as f:
            yaml.safe_dump(self.resultado, f, allow_unicode=True)

        self.print_decision()

    def print_decision(self):
        decisao = self.resultado.get("decisão_dialogada", {})
        print("\n🔄 [DECISÃO SIMBÓLICA BASEADA EM DIÁLOGO]")
        print(f"🟢 Resultado: {decisao['resultado']}")
        print(f"📄 Justificativa: {decisao['justificativa']}")