"""
Módulo principal de execução do sistema multiagente reflexivo com ciclos automáticos.
"""

import sys
from pathlib import Path
import yaml
from time import sleep

sys.path.append(str(Path(__file__).parent.parent))

from core.agents.code_agent import CodeAgent
from core.agents.test_agent import TestAgent
from core.agents.doc_agent import DocumentationAgent
from core.agents.reflection_agent import ReflectionAgent
from reflection.reflection_agent_update_patch import SymbolicEvaluator
from memory.symbolic_memory import SymbolicMemory


def handle_error(context: str, e: Exception):
    print(f"[Erro] {context}: {e}")


def load_dialogue_decision():
    from paths import DIALOGUE_DECISION
    if DIALOGUE_DECISION.exists():
        try:
            data = yaml.safe_load(DIALOGUE_DECISION.read_text(encoding="utf-8"))
            return data.get("decisão_dialogada", {}).get("resultado", "Mantida")
        except Exception:
            return "Mantida"
    return "Mantida"


def print_agent_profile(agent_name, profile):
    print(f"\n🤮 {agent_name}")
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

    code_agent.execute_task("Implementar função de login")
    test_agent.generate_tests(code_agent.latest_output)
    doc_agent.create_docs(code_agent.latest_output)

    reflector.reflect_on_tasks([code_agent, test_agent, doc_agent])
    reflector.close()

    evaluator = SymbolicEvaluator()
    evaluator.update_symbolic_identity([code_agent, test_agent, doc_agent])

    try:
        state_path = Path("memory/identity_state.yaml")
        if state_path.exists():
            identity_state = yaml.safe_load(state_path.read_text(encoding="utf-8"))
            memory = SymbolicMemory()
            memory.update_memory(identity_state)
            for agent_name in identity_state:
                print_agent_profile(agent_name, identity_state[agent_name])
    except Exception as e:
        handle_error("memória simbólica", e)

    try:
        from supervision.supervisor_agent import SupervisorAgent
        SupervisorAgent().evaluate_global_state()
    except Exception as e:
        handle_error("supervisor simbólico", e)

    try:
        from optimization.symbolic_optimizer import SymbolicOptimizer
        SymbolicOptimizer().evaluate()
    except Exception as e:
        handle_error("otimização simbólica", e)

    try:
        from correction.symbolic_autocorrector import SymbolicAutocorrector
        SymbolicAutocorrector().apply_corrections()
    except Exception as e:
        handle_error("autocorreção simbólica", e)

    try:
        from contradiction.contradiction_checker import ContradictionChecker
        ContradictionChecker().detect_contradictions()
    except Exception as e:
        handle_error("verificação de contradições simbólicas", e)

    try:
        from dialogue.symbolic_dialogue import SymbolicDialogue
        SymbolicDialogue().generate_dialogue()
    except Exception as e:
        handle_error("diálogo simbólico entre agentes", e)

    try:
        from dialogue.dialogue_based_filter import DialogueBasedFilter
        DialogueBasedFilter().decide()
        decision = load_dialogue_decision()
        if decision == "Vetada":
            print("🚫 Proposta vetada pelos agentes. Ciclo encerrado sem execução criativa.")
            return
    except Exception as e:
        handle_error("decisão simbólica dialogada", e)

    try:
        from closure.symbolic_closure import SymbolicClosure
        if cycle_number == 11:
            closure = SymbolicClosure()
            closure.summarize()  # <-- corrigido aqui
    except Exception as e:
        handle_error("encerramento simbólico", e)


def run_project():
    for cycle in range(12):
        run_cycle(cycle)
        sleep(1)


if __name__ == "__main__":
    run_project()
