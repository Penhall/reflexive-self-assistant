"""
Agente responsável por gerar documentação a partir do código.
"""

import yaml
from pathlib import Path

# Fix para import de paths
try:
    from config.paths import IDENTITY_STATE
except ImportError:
    # Fallback para quando config.paths não está disponível
    PROJECT_ROOT = Path(__file__).parent.parent.parent
    IDENTITY_STATE = PROJECT_ROOT / "reflection" / "state" / "identity" / "identity_state.yaml"

class DocumentationAgent:
    def __init__(self):
        self.latest_output = ""
        self.adapted = False
        self.load_symbolic_profile()

    def load_symbolic_profile(self):
        try:
            identity_file = Path(IDENTITY_STATE)
            if identity_file.exists():
                with open(identity_file, "r", encoding="utf-8") as f:
                    profile = yaml.safe_load(f).get("DocumentationAgent", {})
                    if "looping" in str(profile.get("adaptive_hint", "")).lower():
                        self.adapted = True
        except FileNotFoundError:
            pass
        except Exception as e:
            print(f"Aviso: Erro ao carregar perfil simbólico: {e}")

    def create_docs(self, code):
        if self.adapted:
            print("⚙️ DocumentationAgent usando modo resumido por repetição simbólica")
            self.latest_output = f"# 📝 Resumo simbólico da função implementada: {code.split(':')[-1].strip()}"
        else:
            self.latest_output = f"# Documentação para: {code}"
        print(self.latest_output)
        return self.latest_output
