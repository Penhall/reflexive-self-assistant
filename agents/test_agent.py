"""
Agente responsável por gerar testes automatizados.
"""

class TestAgent:
    def __init__(self):
        self.latest_output = ""

    def generate_tests(self, code):
        self.latest_output = f"# Testes gerados para o código: {code}"
        print(self.latest_output)