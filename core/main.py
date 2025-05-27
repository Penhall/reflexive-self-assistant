"""
Versão corrigida de core/main.py com imports e paths fixos
"""

import sys
from pathlib import Path

# 1. Configurar o path ANTES de qualquer import
sys.path.insert(0, str(Path(__file__).parent.parent))

# 2. Importar config.paths com tratamento de erro
try:
    import config.paths as paths
except ImportError as e:
    print(f"Erro crítico: Não foi possível importar config.paths - {e}")
    sys.exit(1)

import yaml
from time import sleep

# 3. Usar paths centralizados do config.paths
PROJECT_ROOT = Path(paths.PROJECT_ROOT)
REFLECTION_DIR = Path(paths.REFLECTION_DIR)

# Garantir que diretórios existem
def ensure_directories():
    """Cria todos os diretórios necessários"""
    required_dirs = [
        paths.IDENTITY_STATE.parent,
        paths.MEMORY_LOG.parent,
        paths.EMOTIONAL_STATE.parent,
        paths.SYMBOLIC_TIMELINE.parent,
        paths.SUPERVISOR_INSIGHT.parent,
        paths.LOGS_DIR,
        paths.DATA_DIR,
        paths.EXPORTS_DIR / "identities",
        paths.EXPORTS_DIR / "reports"
    ]
    
    for directory in required_dirs:
        directory.mkdir(parents=True, exist_ok=True)

# Executar setup
ensure_directories()

from core.agents.code_agent import CodeAgent
from core.agents.test_agent import TestAgent
from core.agents.doc_agent import DocumentationAgent
from core.agents.reflection_agent import ReflectionAgent

def handle_error(context: str, e: Exception):
    print(f"[Erro] {context}: {e}")

def load_dialogue_decision():
    if paths.DIALOGUE_DECISION.exists():
        with paths.DIALOGUE_DECISION.open("r", encoding="utf-8") as f:
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
    code_agent = CodeAgent(use_mock=True)
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
    except Exception as e:
        handle_error("avaliação simbólica", e)

    # Carregar e exibir perfis
    try:
        if paths.IDENTITY_STATE.exists():
            identity_state = yaml.safe_load(paths.IDENTITY_STATE.read_text(encoding="utf-8"))
            
            try:
                from memory.symbolic.symbolic_memory import SymbolicMemory
                memory = SymbolicMemory()
                memory.update_memory(identity_state)
            except ImportError:
                pass
            
            for agent_name in identity_state:
                print_agent_profile(agent_name, identity_state[agent_name])
        else:
            print("📝 Criando arquivo de identidade inicial...")
            initial_identity = {
                "CodeAgent": {
                    "predominant_pattern": "Execução padrão",
                    "last_adaptation": "2025-05-25 20:00:00",
                    "consistency_level": "Alta",
                    "traits": ["Consistente", "Objetivo"]
                },
                "TestAgent": {
                    "predominant_pattern": "Cobertura de teste",
                    "last_adaptation": "2025-05-25 20:00:00",
                    "consistency_level": "Alta",
                    "traits": ["Analítico", "Consistente"]
                },
                "DocumentationAgent": {
                    "predominant_pattern": "Atualização documental",
                    "last_adaptation": "2025-05-25 20:00:00",
                    "consistency_level": "Alta",
                    "traits": ["Consistente", "Explicativo"]
                }
            }
            
            with paths.IDENTITY_STATE.open("w", encoding="utf-8") as f:
                yaml.safe_dump(initial_identity, f, sort_keys=False, allow_unicode=True)
            
            print("✅ Arquivo de identidade criado!")
            
    except Exception as e:
        handle_error("carregamento de perfis", e)

    # Componentes reflexivos opcionais
    reflexive_components = [
        ("supervisor simbólico", "reflection.analysis.supervisor_agent", "SupervisorAgent"),
        ("otimização simbólica", "reflection.analysis.performance_evaluator", "SymbolicOptimizer"),
        ("diálogo simbólico", "reflection.symbolic.symbolic_dialogue", "SymbolicDialogue"),
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
            elif hasattr(component, 'generate_dialogue'):
                component.generate_dialogue()
                
        except Exception as e:
            handle_error(component_name, e)

    # Encerramento simbólico (último ciclo)
    if cycle_number == 11:
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
            sleep(1)
        except KeyboardInterrupt:
            print(f"\n⏹️ Execução interrompida pelo usuário no ciclo {cycle + 1}")
            break
        except Exception as e:
            print(f"❌ Erro no ciclo {cycle + 1}: {e}")
            continue
    
    print("\n🏁 Execução concluída!")

if __name__ == "__main__":
    run_project()
