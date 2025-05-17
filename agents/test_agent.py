"""
Agente responsável por gerar testes com base no código fornecido.
"""

class TestAgent:
    def __init__(self):
        self.latest_output = ""

    def generate_tests(self, code):
        self.latest_output = f"# Testes gerados para o código: {code}"
        print(self.latest_output)