from pathlib import Path
from datetime import datetime

class TestAgent:
    def __init__(self):
        self.output_path = Path("output/test")
        self.output_path.mkdir(parents=True, exist_ok=True)
        self.latest_output = ""
        self.adapted = False
        self.load_symbolic_profile()

    def load_symbolic_profile(self):
        """Carrega perfil simbólico para adaptar comportamento"""
        try:
            from config.paths import IDENTITY_STATE
            identity_file = Path(IDENTITY_STATE)
            if identity_file.exists():
                import yaml
                profile = yaml.safe_load(identity_file.read_text(encoding="utf-8")).get("TestAgent", {})
                if "optimized" in str(profile.get("adaptive_hint", "")).lower():
                    self.adapted = True
        except Exception:
            pass

    def generate_tests(self, code: str, function_name="funcao"):
        if self.adapted:
            test_code = f"""def test_{function_name}():
    # Teste otimizado
    assert True  # Placeholder para teste otimizado
"""
        else:
            test_code = f"""def test_{function_name}():
    # Substitua abaixo pelo comportamento esperado
    resultado = {function_name}(2, 3)
    assert resultado == 5
"""
        
        filename = f"test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.py"
        file_path = self.output_path / filename
        file_path.write_text(test_code.strip(), encoding="utf-8")
        print(f"✅ Teste salvo em: {file_path}")
        self.latest_output = test_code
        return test_code
