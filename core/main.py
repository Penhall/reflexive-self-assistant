"""
Módulo principal de execução do sistema multiagente reflexivo com ciclos automáticos.
"""

import sys
from pathlib import Path
import yaml
from time import sleep

sys.path.append(str(Path(__file__).parent.parent))

from agents.code_agent import CodeAgent
from agents.test_agent import TestAgent
from agents.doc_agent import DocumentationAgent
from agents.reflection_agent import ReflectionAgent
from reflection.reflection_agent_update_patch import SymbolicEvaluator


def print_agent_profile(agent_name, profile):
    print(f"\n🧠 {agent_name}")
    print(f"   → Padrão predominante: {profile.get('predominant_pattern')}")
    print(f"   → Consistência: {profile.get('consistency_level')}")
    print(f"   → Última adaptação: {profile.get('last_adaptation')}")
    print(f"   → Traços simbólicos: {', '.join(profile.get('traits', [])) or 'Nenhum'}")


def run_cycle(cycle_number):
    print(f"\n==============================")
    print(f"🔁 Iniciando Ciclo Reflexivo {cycle_number + 1}")
    print(f"==============================")

    code_agent = CodeAgent()
    test_agent = TestAgent()
    doc_agent = DocumentationAgent()
    reflector = ReflectionAgent()

    # Execução das tarefas
    code_agent.execute_task("Implementar função de login")
    test_agent.generate_tests(code_agent.latest_output)
    doc_agent.create_docs(code_agent.latest_output)

    # Reflexão simbólica
    reflector.reflect_on_tasks([code_agent, test_agent, doc_agent])
    reflector.close()

    # Evolução simbólica
    evaluator = SymbolicEvaluator()
    evaluator.update_symbolic_identity([code_agent, test_agent, doc_agent])

    # Carregar estado simbólico
    state_path = Path("reflection/identity_state.yaml")
    if state_path.exists():
        identity_state = yaml.safe_load(state_path.read_text(encoding="utf-8"))
        for agent_name in identity_state:
            print_agent_profile(agent_name, identity_state[agent_name])


def run_project():
    for cycle in range(3):
        run_cycle(cycle)
        sleep(1)


if __name__ == "__main__":
    run_project()