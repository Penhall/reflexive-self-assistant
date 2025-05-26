"""
Agente responsável por gerar documentação a partir do código.
"""

import yaml

class DocumentationAgent:
    def __init__(self):
        self.latest_output = ""
        self.adapted = False
        self.load_symbolic_profile()

    def load_symbolic_profile(self):
        try:
            with open(str(IDENTITY_STATE), "r", encoding="utf-8") as f:
                profile = yaml.safe_load(f).get("DocumentationAgent", {})
                if "looping" in str(profile.get("adaptive_hint", "")).lower():
                    self.adapted = True
        except FileNotFoundError:
            pass

    def create_docs(self, code):
        if self.adapted:
            print("⚙️ DocumentationAgent usando modo resumido por repetição simbólica")
            self.latest_output = f"# 📝 Resumo simbólico da função implementada: {code.split(':')[-1].strip()}"
        else:
            self.latest_output = f"# Documentação para: {code}"
        print(self.latest_output)