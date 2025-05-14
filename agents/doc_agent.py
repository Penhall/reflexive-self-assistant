"""
Agente responsável por gerar documentação técnica.
"""

class DocumentationAgent:
    def __init__(self):
        self.latest_output = ""

    def create_docs(self, code):
        self.latest_output = f"# Documentação para: {code}"
        print(self.latest_output)