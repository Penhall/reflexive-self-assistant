"""
Módulo principal de execução do sistema multiagente reflexivo com ciclos automáticos.
Versão atualizada para nova estrutura de diretórios.
"""

import sys
from pathlib import Path
import yaml
from time import sleep

# Adicionar diretório raiz ao path
sys.path.append(str(Path(__file__).parent.parent))

from config.paths import (
    IDENTITY_STATE,
    SYMBOLIC_LEGACY,
    MEMORY_LOG,
    DIALOGUE_DECISION
)

from core.agents.code_agent import CodeAgent
from core.agents.test_agent import TestAgent
from core.agents.doc_agent import DocumentationAgent
from core.agents.reflection_agent import ReflectionAgent


def handle_error(context: str, e: Exception):
    print(f"[Erro] {context}: {e}")


def load_dialogue_decision():
    decision_file = Path(DIALOGUE_DECISION)
    if decision_file.exists():
        with decision_file.open("r", encoding="utf-8") as f:
            try:
                return yaml.safe_load(f).get("decisão_dialogada", {}).get("resultado", "Mantida")
            except Exception:
                return "Mantida"
    return "Mantida"


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

    # Inicializar agentes
    code_agent = CodeAgent()
    test_agent = TestAgent()
    doc_agent = DocumentationAgent()
    reflector = ReflectionAgent()

    # Executar tarefas
    code_agent.execute_task("Implementar função de login")
    test_agent.generate_tests(code_agent.latest_output)
    doc_agent.create_docs(code_agent.latest_output)

    # Reflexão
    reflector.reflect_on_tasks([code_agent, test_agent, doc_agent])
    reflector.close()

    # Avaliação simbólica
    try:
        from reflection.analysis.pattern_analyzer import SymbolicEvaluator
        evaluator = SymbolicEvaluator()
        evaluator.update_symbolic_identity([code_agent, test_agent, doc_agent])
    except ImportError as e:
        handle_error("avaliação simbólica", e)

    # Carregar e exibir perfis
    try:
        state_path = Path(IDENTITY_STATE)
        if state_path.exists():
            identity_state = yaml.safe_load(state_path.read_text(encoding="utf-8"))
            
            # Atualizar memória simbólica
            try:
                from memory.symbolic.symbolic_memory import SymbolicMemory
                memory = SymbolicMemory()
                memory.update_memory(identity_state)
            except ImportError:
                pass  # Memória simbólica opcional
            
            for agent_name in identity_state:
                print_agent_profile(agent_name, identity_state[agent_name])
    except Exception as e:
        handle_error("carregamento de perfis", e)

    # Componentes reflexivos opcionais
    reflexive_components = [
        ("supervisor simbólico", "reflection.analysis.supervisor_agent", "SupervisorAgent"),
        ("otimização simbólica", "reflection.analysis.performance_evaluator", "SymbolicOptimizer"),
        ("autocorreção simbólica", "reflection.analysis.contradiction_checker", "SymbolicAutocorrector"),
        ("verificação de contradições", "reflection.analysis.contradiction_checker", "ContradictionChecker"),
        ("diálogo simbólico", "reflection.symbolic.symbolic_dialogue", "SymbolicDialogue"),
        ("decisão dialogada", "reflection.symbolic.dialogue_based_filter", "DialogueBasedFilter"),
    ]

    for component_name, module_path, class_name in reflexive_components:
        try:
            module = __import__(module_path, fromlist=[class_name])
            component_class = getattr(module, class_name)
            component = component_class()
            
            if hasattr(component, 'evaluate_global_state'):
                component.evaluate_global_state()
            elif hasattr(component, 'evaluate'):
                component.evaluate()
            elif hasattr(component, 'apply_corrections'):
                component.apply_corrections()
            elif hasattr(component, 'detect_contradictions'):
                component.detect_contradictions()
            elif hasattr(component, 'generate_dialogue'):
                component.generate_dialogue()
            elif hasattr(component, 'decide'):
                component.decide()
                
        except Exception as e:
            handle_error(component_name, e)

    # Encerramento simbólico (último ciclo)
    if cycle_number == 11:  # 12º ciclo (0-indexed)
        try:
            from reflection.symbolic.closure import SymbolicClosure
            closure = SymbolicClosure()
            closure.summarize(cycles_completed=cycle_number+1)
        except Exception as e:
            handle_error("encerramento simbólico", e)


def run_project():
    """Executa o projeto completo com 12 ciclos"""
    print("🚀 Iniciando Reflexive Self Coding Assistant")
    print("📊 Configuração: 12 ciclos reflexivos")
    
    for cycle in range(12):
        try:
            run_cycle(cycle)
            sleep(1)  # Pequena pausa entre ciclos
        except KeyboardInterrupt:
            print(f"\n⏹️ Execução interrompida pelo usuário no ciclo {cycle + 1}")
            break
        except Exception as e:
            print(f"❌ Erro no ciclo {cycle + 1}: {e}")
            continue
    
    print("\n🏁 Execução concluída!")


if __name__ == "__main__":
    run_project()