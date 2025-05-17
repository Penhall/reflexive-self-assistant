"""
Agente responsável por gerar código com base em instruções.
"""

class CodeAgent:
    def __init__(self):
        self.latest_output = ""

    def execute_task(self, instruction):
        self.latest_output = f"# Código gerado para: {instruction}"
        print(self.latest_output)