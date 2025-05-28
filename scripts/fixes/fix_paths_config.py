#!/usr/bin/env python3
"""
Script para corrigir paths e criar configuração centralizada após reestruturação.
"""

import os
import re
import shutil
from pathlib import Path
from datetime import datetime

class PathMigrator:
    def __init__(self):
        self.root_path = Path.cwd()
        self.migration_log = []
        self.new_paths = self._define_new_paths()
        
    def _define_new_paths(self):
        """Define todos os novos paths do sistema"""
        return {
            # Estados de identidade
            "IDENTITY_STATE": "reflection/state/identity/identity_state.yaml",
            "MEMORY_LOG": "reflection/state/identity/memory_log.yaml",
            "SYMBOLIC_LEGACY": "reflection/state/identity/symbolic_legacy.yaml",
            
            # Estados emocionais
            "EMOTIONAL_STATE": "reflection/state/emotional/emotional_state.yaml",
            "SELF_NARRATIVE": "reflection/state/emotional/self_narrative.yaml",
            "CREATIVE_REGENERATION": "reflection/state/emotional/creative_regeneration.yaml",
            
            # Estados temporais
            "SYMBOLIC_TIMELINE": "reflection/state/temporal/symbolic_timeline.yaml",
            "CYCLE_HISTORY": "reflection/state/temporal/cycle_history.json",
            "COUNTERFACTUAL_REFLECTION": "reflection/state/temporal/counterfactual_reflection.yaml",
            
            # Estados de governança
            "SUPERVISOR_INSIGHT": "reflection/state/governance/supervisor_insight.yaml",
            "SYMBOLIC_GOVERNANCE": "reflection/state/governance/symbolic_governance.yaml",
            "SYMBOLIC_AGENDA": "reflection/state/governance/symbolic_agenda.yaml",
            
            # Diálogos e comunicação
            "SYMBOLIC_DIALOGUE": "reflection/symbolic/symbolic_dialogue.yaml",
            "DIALOGUE_DECISION": "reflection/symbolic/dialogue_decision.yaml",
            
            # Análise e otimização
            "SYMBOLIC_CONTRADICTIONS": "reflection/analysis/symbolic_contradictions.yaml",
            "SYMBOLIC_CORRECTION_LOG": "reflection/analysis/symbolic_correction_log.yaml",
            "SYMBOLIC_IMPACT_LOG": "reflection/analysis/symbolic_impact_log.yaml",
            "SYMBOLIC_EXPLANATION": "reflection/analysis/symbolic_explanation.yaml",
            
            # Simulação
            "SCENARIOS": "reflection/simulation/scenarios.yaml",
            "SIMULATED_DECISION": "reflection/simulation/simulated_decision.yaml",
            
            # Logs e histórico
            "ANALYSIS_HISTORY": "reflection/analysis_history.md",
            "CYCLE_LOG": str(CYCLE_LOG),
            "ALERTS_LOG": str(ALERTS_LOG)
        }
    
    def create_config_files(self):
        """Cria os arquivos de configuração centralizados"""
        print("📝 Criando arquivos de configuração...")
        
        # Criar config/settings.py
        self._create_settings_py()
        
        # Criar config/paths.py
        self._create_paths_py()
        
        # Criar config/model_configs/
        self._create_model_configs()
        
        # Criar config/environment/
        self._create_environment_config()
        
        print("✅ Arquivos de configuração criados!")
    
    def _create_settings_py(self):
        """Cria o arquivo de configurações principal"""
        settings_content = '''"""
Configurações centralizadas do Reflexive Self Coding Assistant.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

# Diretório raiz do projeto
PROJECT_ROOT = Path(__file__).parent.parent

# Configurações de LLM
LLM_CONFIG = {
    "ollama": {
        "host": os.getenv("OLLAMA_HOST", "http://localhost:11434"),
        "models": {
            "code": os.getenv("CODE_MODEL", "codellama:7b"),
            "general": os.getenv("GENERAL_MODEL", "llama3:8b"),
            "analysis": os.getenv("ANALYSIS_MODEL", "codellama:13b")
        }
    }
}

# Configurações de banco de dados
DATABASE_CONFIG = {
    "neo4j": {
        "uri": os.getenv("NEO4J_URI", "bolt://localhost:7687"),
        "username": os.getenv("NEO4J_USERNAME", "neo4j"),
        "password": os.getenv("NEO4J_PASSWORD", "password")
    },
    "chromadb": {
        "path": PROJECT_ROOT / "data" / "chromadb",
        "collection_name": "coding_experiences"
    }
}

# Configurações de reflexão
REFLECTION_CONFIG = {
    "cycle_frequency": int(os.getenv("CYCLE_FREQUENCY", "5")),  # minutos
    "max_history": int(os.getenv("MAX_HISTORY", "100")),
    "pattern_threshold": float(os.getenv("PATTERN_THRESHOLD", "0.7")),
    "consistency_levels": {
        "high_threshold": 4,
        "medium_threshold": 2
    }
}

# Configurações de logging
LOGGING_CONFIG = {
    "level": os.getenv("LOG_LEVEL", "INFO"),
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    "file_path": PROJECT_ROOT / "logs" / "system.log"
}

# Configurações de performance
PERFORMANCE_CONFIG = {
    "max_concurrent_agents": int(os.getenv("MAX_CONCURRENT_AGENTS", "3")),
    "timeout_seconds": int(os.getenv("TIMEOUT_SECONDS", "30")),
    "retry_attempts": int(os.getenv("RETRY_ATTEMPTS", "3"))
}
'''
        
        config_dir = self.root_path / "config"
        config_dir.mkdir(exist_ok=True)
        
        with open(config_dir / "settings.py", "w", encoding="utf-8") as f:
            f.write(settings_content)
    
    def _create_paths_py(self):
        """Cria o arquivo de paths centralizados"""
        paths_content = '''"""
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
'''
        
        with open(self.root_path / "config" / "paths.py", "w", encoding="utf-8") as f:
            f.write(paths_content)
    
    def _create_model_configs(self):
        """Cria configurações específicas de modelos"""
        model_configs_dir = self.root_path / "config" / "model_configs"
        model_configs_dir.mkdir(exist_ok=True)
        
        # Configuração do CodeLlama
        codellama_config = '''# Configuração para CodeLlama
MODEL_NAME = "codellama:7b" 
CONTEXT_LENGTH = 4096
TEMPERATURE = 0.1
TOP_P = 0.9
SYSTEM_PROMPT = """You are a specialized code generation assistant. 
Generate clean, functional, and well-documented code based on the given requirements.
Focus on best practices, error handling, and code maintainability."""

PROMPT_TEMPLATES = {
    "code_generation": """
Task: {task}

Context from similar experiences:
{context}

Generate Python code that:
1. Implements the requested functionality
2. Includes proper error handling
3. Follows Python best practices
4. Is well-documented with docstrings

Code:
""",
    
    "code_improvement": """
Current code:
{current_code}

Issues found:
{issues}

Improve the code addressing the issues while maintaining functionality:
""",
    
    "code_documentation": """
Code to document:
{code}

Generate comprehensive documentation including:
1. Function/class docstrings
2. Inline comments for complex logic
3. Usage examples
4. Parameter descriptions

Documentation:
"""
}
'''
        
        with open(model_configs_dir / "codellama.py", "w", encoding="utf-8") as f:
            f.write(codellama_config)
    
    def _create_environment_config(self):
        """Cria arquivo de exemplo de variáveis de ambiente"""
        env_dir = self.root_path / "config" / "environment"
        env_dir.mkdir(exist_ok=True)
        
        env_example = '''# Configurações de LLM
OLLAMA_HOST=http://localhost:11434
CODE_MODEL=codellama:7b
GENERAL_MODEL=llama3:8b
ANALYSIS_MODEL=codellama:13b

# Configurações de Banco de Dados
NEO4J_URI=bolt://localhost:7687
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=your_password_here

# Configurações de Sistema
LOG_LEVEL=INFO
CYCLE_FREQUENCY=5
MAX_HISTORY=100
PATTERN_THRESHOLD=0.7
MAX_CONCURRENT_AGENTS=3
TIMEOUT_SECONDS=30
RETRY_ATTEMPTS=3

# Configurações de Development
DEBUG=false
MOCK_LLMS=false
MOCK_DATABASE=false
'''
        
        with open(env_dir / ".env.example", "w", encoding="utf-8") as f:
            f.write(env_example)
    
    def update_imports_in_files(self):
        """Atualiza imports em todos os arquivos Python"""
        print("🔄 Atualizando imports nos arquivos Python...")
        
        # Mapeamento de imports antigos para novos
        import_mappings = {
            "from config.paths import": "from config.paths import",
            "from memory.symbolic.symbolic_memory import": "from memory.symbolic.symbolic_memory import",
            "from memory.graph_rag.graph_interface import": "from memory.graph_rag.graph_interface import",
            "from core.agents.": "from core.agents.",
            "from reflection.analysis.": "from reflection.analysis.",
            "from reflection.analysis.": "from reflection.analysis.",
            "from reflection.symbolic.": "from reflection.symbolic."
        }
        
        # Encontrar todos os arquivos Python
        python_files = list(self.root_path.rglob("*.py"))
        updated_files = []
        
        for file_path in python_files:
            if self._update_file_imports(file_path, import_mappings):
                updated_files.append(file_path)
        
        print(f"✅ {len(updated_files)} arquivos atualizados!")
        return updated_files
    
    def _update_file_imports(self, file_path, mappings):
        """Atualiza imports em um arquivo específico"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            original_content = content
            
            # Aplicar mapeamentos
            for old_import, new_import in mappings.items():
                content = re.sub(rf'{re.escape(old_import)}([.\w]*)', f'{new_import}\\1', content)
            
            # Atualizar paths hardcoded
            content = self._update_hardcoded_paths(content)
            
            if content != original_content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                return True
            
        except Exception as e:
            print(f"⚠️ Erro ao atualizar {file_path}: {e}")
        
        return False
    
    def _update_hardcoded_paths(self, content):
        """Atualiza paths hardcoded no conteúdo"""
        path_replacements = {
            'str(IDENTITY_STATE)': 'str(IDENTITY_STATE)',
            'str(MEMORY_LOG)': 'str(MEMORY_LOG)',
            'str(CYCLE_HISTORY)': 'str(CYCLE_HISTORY)',
            'str(SYMBOLIC_DIALOGUE)': 'str(SYMBOLIC_DIALOGUE)',
            'str(SUPERVISOR_INSIGHT)': 'str(SUPERVISOR_INSIGHT)',
            'str(EMOTIONAL_STATE)': 'str(EMOTIONAL_STATE)',
            'str(CYCLE_LOG)': 'str(CYCLE_LOG)',
            'str(ALERTS_LOG)': 'str(ALERTS_LOG)'
        }
        
        for old_path, new_path in path_replacements.items():
            content = content.replace(old_path, new_path)
        
        return content
    
    def create_migration_summary(self):
        """Cria um resumo da migração"""
        summary_path = self.root_path / "MIGRATION_SUMMARY.md"
        
        summary_content = f'''# Resumo da Migração - {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

## Estrutura Antiga → Nova

### Diretórios Principais
- `agents/` → `core/agents/`
- `utils/` → `memory/graph_rag/` e `scripts/`
- `config/` → `config/` (reestruturado)
- `reflection/` → `reflection/` (reorganizado)
- `dashboard/` → `interface/dashboard/`
- `tests/` → `tests/` (reorganizado)

### Estados YAML Organizados
- **Identidade**: `reflection/state/identity/`
- **Emocional**: `reflection/state/emotional/`
- **Temporal**: `reflection/state/temporal/`
- **Governança**: `reflection/state/governance/`

### Novos Componentes
- `memory/` - Sistema de memória GraphRAG
- `evolution/` - Sistema de evolução de agentes
- `interface/` - Interfaces de usuário
- `infrastructure/` - Docker e configurações

## Arquivos de Configuração Criados
- `config/settings.py` - Configurações centralizadas
- `config/paths.py` - Paths organizados
- `config/model_configs/` - Configurações de modelos
- `config/environment/.env.example` - Variáveis de ambiente

## Próximos Passos
1. Verificar se todos os imports foram atualizados
2. Testar execução básica do sistema
3. Implementar componentes faltantes (LLM, GraphRAG)
4. Executar testes de integração

## Rollback
Para reverter as mudanças:
```bash
git checkout .  # Se usando Git
# ou restaurar backup manual
```
'''
        
        with open(summary_path, "w", encoding="utf-8") as f:
            f.write(summary_content)
        
        print(f"📋 Resumo da migração salvo em: {summary_path}")
    
    def run_migration(self):
        """Executa todo o processo de migração"""
        print("🚀 Iniciando migração de paths e configuração...")
        print("=" * 60)
        
        try:
            # 1. Criar arquivos de configuração
            self.create_config_files()
            
            # 2. Atualizar imports
            self.update_imports_in_files()
            
            # 3. Criar resumo
            self.create_migration_summary()
            
            print("\n" + "=" * 60)
            print("✅ Migração concluída com sucesso!")
            print("\n📋 Resumo:")
            print("  → Configurações centralizadas criadas")
            print("  → Imports atualizados automaticamente")
            print("  → Paths organizados e centralizados")
            print("  → Estrutura preparada para próximas fases")
            
            print("\n⚠️  Próximos passos recomendados:")
            print("  1. Testar execução: python core/main.py")
            print("  2. Verificar dashboard: streamlit run interface/dashboard/streamlit_app.py")  
            print("  3. Revisar MIGRATION_SUMMARY.md para detalhes")
            
        except Exception as e:
            print(f"❌ Erro durante migração: {e}")
            raise

if __name__ == "__main__":
    migrator = PathMigrator()
    migrator.run_migration()