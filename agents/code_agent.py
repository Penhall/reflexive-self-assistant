"""
Agente responsável por gerar código com base nas instruções recebidas.
"""

class CodeAgent:
    def __init__(self):
        self.latest_output = ""

    def execute_task(self, instruction):
        # Simulação de geração de código
        self.latest_output = f"# Código gerado para: {instruction}"
        print(self.latest_output)