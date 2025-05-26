from pathlib import Path
from datetime import datetime

class TestAgent:
    def __init__(self):
        self.output_path = Path("output/test")
        self.output_path.mkdir(parents=True, exist_ok=True)

    def generate_tests(self, code: str, function_name="funcao"):
        test_code = f"""def test_{function_name}():
    # Substitua abaixo pelo comportamento esperado
    resultado = {function_name}(2, 3)
    assert resultado == 5
"""
        filename = f"test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.py"
        file_path = self.output_path / filename
        file_path.write_text(test_code.strip(), encoding="utf-8")
        print(f"✅ Teste salvo em: {file_path}")
        return test_code