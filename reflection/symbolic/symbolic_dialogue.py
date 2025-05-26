import yaml
from datetime import datetime

FILES = {
    "identity": str(IDENTITY_STATE),
    "proposta": "reflection/creative_regeneration.yaml",
    "output": str(SYMBOLIC_DIALOGUE)
}

class SymbolicDialogue:
    def __init__(self):
        self.identity = self.load(FILES["identity"])
        self.proposta = self.load(FILES["proposta"]).get("regeneração_criativa", {})
        self.retorno = {}

    def load(self, path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                return yaml.safe_load(f) or {}
        except:
            return {}

    def generate_dialogue(self):
        proposta = self.proposta.get("proposta", "").lower()
        ciclo = self.proposta.get("ciclo", 0)

        for agente, dados in self.identity.items():
            padrao = dados.get("predominant_pattern", "").lower()
            consistencia = dados.get("consistency_level", "").lower()

            if padrao in proposta and consistencia == "alta":
                resposta = "Apoio. Padrão alinhado e historicamente consistente comigo."
            elif consistencia == "baixa" and padrao in proposta:
                resposta = "Rejeito. Histórico de inconsistência com esse padrão."
            elif "variação" in proposta and "teste" in agente.lower():
                resposta = "Alerta. Pode impactar previsibilidade de testes."
            elif "documentação" in agente.lower() and consistencia in ["alta", "média"]:
                resposta = "Neutro. Posso adaptar minha estrutura a qualquer padrão."
            else:
                resposta = "Neutro. Sem impacto direto na minha coerência simbólica."

            self.retorno[agente] = resposta

        self.save_dialogue(ciclo)

    def save_dialogue(self, ciclo):
        resultado = {
            "diálogo_simbólico": self.retorno,
            "ciclo": ciclo,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        with open(FILES["output"], "w", encoding="utf-8") as f:
            yaml.safe_dump(resultado, f, allow_unicode=True)
        self.print_dialogue()

    def print_dialogue(self):
        print("\n🗣️ [DIÁLOGO SIMBÓLICO ENTRE AGENTES]")
        for agente, fala in self.retorno.items():
            icone = {
                "code": "🤖", "test": "🧪", "doc": "📄"
            }.get(agente.lower().split("agent")[0], "🔹")
            print(f"{icone} {agente}: {fala}")