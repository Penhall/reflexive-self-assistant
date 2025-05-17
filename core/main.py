"""
Módulo principal de execução do sistema multiagente reflexivo.
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))


from agents.code_agent import CodeAgent
from agents.test_agent import TestAgent
from agents.doc_agent import DocumentationAgent
from agents.reflection_agent import ReflectionAgent

def run_project():
    """
    Orquestra os agentes e inicia o ciclo de reflexão.
    """
    code_agent = CodeAgent()
    test_agent = TestAgent()
    doc_agent = DocumentationAgent()
    reflector = ReflectionAgent()

    # Exemplo simples de execução
    code_agent.execute_task("Implementar função de login")
    test_agent.generate_tests(code_agent.latest_output)
    doc_agent.create_docs(code_agent.latest_output)
    reflector.reflect_on_tasks([code_agent, test_agent, doc_agent])

if __name__ == "__main__":
    run_project()