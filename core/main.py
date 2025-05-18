"""
Módulo principal de execução do sistema multiagente reflexivo com ciclos automáticos e reorganização simbólica.
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
from reflection.symbolic_memory import SymbolicMemory
from reflection.supervisor_agent import SupervisorAgent
from reflection.strategy_planner import StrategyPlanner


def print_agent_profile(agent_name, profile):
    print(f"\n🧐 {agent_name}")
    print(f"   → Padrão predominante: {profile.get('predominant_pattern')}")
    print(f"   → Consistência: {profile.get('consistency_level')}")
    print(f"   → Última adaptação: {profile.get('last_adaptation')}")
    print(f"   → Traços simbólicos: {', '.join(profile.get('traits', [])) or 'Nenhum'}")


def run_cycle(cycle_number):
    print(f"\n==============================")
    print(f"🔁 Iniciando Ciclo Reflexivo {cycle_number + 1}")
    print(f"==============================")

    # Ler agenda simbólica (ou usar padrão)
    try:
        agenda = yaml.safe_load(Path("reflection/symbolic_agenda.yaml").read_text(encoding="utf-8"))
        tasks = agenda.get("next_cycle", {})
    except Exception:
        tasks = {}

    code_agent = CodeAgent()
    test_agent = TestAgent()
    doc_agent = DocumentationAgent()
    reflector = ReflectionAgent()

    # Execução das tarefas com base na agenda simbólica
    code_task = tasks.get("CodeAgent", "Implementar função de login")
    test_task = tasks.get("TestAgent", "Gerar testes padrão")
    doc_task = tasks.get("DocumentationAgent", "Documentar conforme padrão")

    code_agent.execute_task(code_task)
    test_agent.generate_tests(code_agent.latest_output)
    doc_agent.create_docs(code_agent.latest_output)

    # Reflexão simbólica
    reflector.reflect_on_tasks([code_agent, test_agent, doc_agent])
    reflector.close()

    # Evolução simbólica
    evaluator = SymbolicEvaluator()
    evaluator.update_symbolic_identity([code_agent, test_agent, doc_agent])

    # Atualização de memória simbólica
    try:
        state_path = Path("reflection/identity_state.yaml")
        if state_path.exists():
            identity_state = yaml.safe_load(state_path.read_text(encoding="utf-8"))
            memory = SymbolicMemory()
            memory.update_memory(identity_state)
            for agent_name in identity_state:
                print_agent_profile(agent_name, identity_state[agent_name])
    except Exception as e:
        print(f"Erro ao atualizar memória simbólica: {e}")

    # Supervisão simbólica global
    try:
        supervisor = SupervisorAgent()
        supervisor.evaluate_global_state()
    except Exception as e:
        print(f"Erro na supervisão simbólica global: {e}")

    # Reorganização simbólica
    try:
        planner = StrategyPlanner()
        planner.generate_agenda()
    except Exception as e:
        print(f"Erro ao gerar nova agenda simbólica: {e}")


def run_project():
    for cycle in range(3):
        run_cycle(cycle)
        sleep(1)


if __name__ == "__main__":
    run_project()