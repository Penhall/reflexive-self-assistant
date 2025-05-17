"""
Agente responsável por gerar testes com base no código fornecido.
"""

import yaml

class TestAgent:
    def __init__(self):
        self.latest_output = ""
        self.adapted = False
        self.load_symbolic_profile()

    def load_symbolic_profile(self):
        try:
            with open("reflection/identity_state.yaml", "r", encoding="utf-8") as f:
                profile = yaml.safe_load(f).get("TestAgent", {})
                if "fallback" in str(profile.get("adaptive_hint", "")).lower():
                    self.adapted = True
        except FileNotFoundError:
            pass

    def generate_tests(self, code):
        if self.adapted:
            print("⚙️ TestAgent entrou em modo adaptativo por sugestão simbólica")
            self.latest_output = "# ⚠️ Teste básico gerado automaticamente por fallback simbólico"
        else:
            self.latest_output = f"# Testes gerados para o código: {code}"
        print(self.latest_output)