"""
Paths centralizados para todos os arquivos do sistema.
"""

from pathlib import Path
from config.settings import PROJECT_ROOT

# Diretórios base
REFLECTION_DIR = PROJECT_ROOT / "reflection"
MEMORY_DIR = PROJECT_ROOT / "memory" 
CORE_DIR = PROJECT_ROOT / "core"
INTERFACE_DIR = PROJECT_ROOT / "interface"
LOGS_DIR = PROJECT_ROOT / "logs"

# Estados de identidade
IDENTITY_STATE = REFLECTION_DIR / "state" / "identity" / "identity_state.yaml"
MEMORY_LOG = REFLECTION_DIR / "state" / "identity" / "memory_log.yaml"
SYMBOLIC_LEGACY = REFLECTION_DIR / "state" / "identity" / "symbolic_legacy.yaml"

# Estados emocionais
EMOTIONAL_STATE = REFLECTION_DIR / "state" / "emotional" / "emotional_state.yaml"
SELF_NARRATIVE = REFLECTION_DIR / "state" / "emotional" / "self_narrative.yaml"
CREATIVE_REGENERATION = REFLECTION_DIR / "state" / "emotional" / "creative_regeneration.yaml"

# Estados temporais
SYMBOLIC_TIMELINE = REFLECTION_DIR / "state" / "temporal" / "symbolic_timeline.yaml"
CYCLE_HISTORY = REFLECTION_DIR / "state" / "temporal" / "cycle_history.json"
COUNTERFACTUAL_REFLECTION = REFLECTION_DIR / "state" / "temporal" / "counterfactual_reflection.yaml"

# Estados de governança
SUPERVISOR_INSIGHT = REFLECTION_DIR / "state" / "governance" / "supervisor_insight.yaml"
SYMBOLIC_GOVERNANCE = REFLECTION_DIR / "state" / "governance" / "symbolic_governance.yaml"
SYMBOLIC_AGENDA = REFLECTION_DIR / "state" / "governance" / "symbolic_agenda.yaml"

# Diálogos e comunicação
SYMBOLIC_DIALOGUE = REFLECTION_DIR / "symbolic" / "symbolic_dialogue.yaml"
DIALOGUE_DECISION = REFLECTION_DIR / "symbolic" / "dialogue_decision.yaml"

# Análise e otimização
SYMBOLIC_CONTRADICTIONS = REFLECTION_DIR / "analysis" / "symbolic_contradictions.yaml"
SYMBOLIC_CORRECTION_LOG = REFLECTION_DIR / "analysis" / "symbolic_correction_log.yaml"
SYMBOLIC_IMPACT_LOG = REFLECTION_DIR / "analysis" / "symbolic_impact_log.yaml"
SYMBOLIC_EXPLANATION = REFLECTION_DIR / "analysis" / "symbolic_explanation.yaml"

# Simulação
SCENARIOS = REFLECTION_DIR / "simulation" / "scenarios.yaml"
SIMULATED_DECISION = REFLECTION_DIR / "simulation" / "simulated_decision.yaml"

# Logs e histórico
ANALYSIS_HISTORY = REFLECTION_DIR / "analysis_history.md"
CYCLE_LOG = LOGS_DIR / "cycle_log.txt"
ALERTS_LOG = LOGS_DIR / "alerts.log"

# Dados e armazenamento
DATA_DIR = PROJECT_ROOT / "data"
CHECKPOINTS_DIR = DATA_DIR / "checkpoints"
EXPERIENCES_DIR = DATA_DIR / "experiences"
EXPORTS_DIR = PROJECT_ROOT / "exports"

# Interface
DASHBOARD_DIR = INTERFACE_DIR / "dashboard"
CLI_DIR = INTERFACE_DIR / "cli"

def ensure_directories():
    """Garante que todos os diretórios necessários existem"""
    directories = [
        REFLECTION_DIR / "state" / "identity",
        REFLECTION_DIR / "state" / "emotional", 
        REFLECTION_DIR / "state" / "temporal",
        REFLECTION_DIR / "state" / "governance",
        REFLECTION_DIR / "symbolic",
        REFLECTION_DIR / "analysis",
        REFLECTION_DIR / "simulation",
        LOGS_DIR,
        DATA_DIR,
        CHECKPOINTS_DIR,
        EXPERIENCES_DIR,
        EXPORTS_DIR / "identities",
        EXPORTS_DIR / "reports"
    ]
    
    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)

# Executar ao importar
ensure_directories()
