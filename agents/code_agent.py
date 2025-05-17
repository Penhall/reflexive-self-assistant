"""
Agente responsável por gerar código com base em instruções.
"""

import yaml

class CodeAgent:
    def __init__(self):
        self.latest_output = ""
        self.adapted = False
        self.load_symbolic_profile()

    def load_symbolic_profile(self):
        try:
            with open("reflection/identity_state.yaml", "r", encoding="utf-8") as f:
                profile = yaml.safe_load(f).get("CodeAgent", {})
                if "funcional" in str(profile.get("predominant_pattern", "")).lower():
                    self.adapted = True
        except FileNotFoundError:
            pass

    def execute_task(self, instruction):
        if self.adapted:
            print("⚙️ CodeAgent gerando código funcional simplificado")
            self.latest_output = f"# Código direto para: {instruction} → return True"
        else:
            self.latest_output = f"# Código gerado para: {instruction}"
        print(self.latest_output)