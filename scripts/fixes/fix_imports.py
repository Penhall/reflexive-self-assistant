#!/usr/bin/env python3
"""
Corrige imports quebrados do sistema RSCA - Versão corrigida
"""

import os
import re
import sys
from pathlib import Path

class ImportFixer:
    def __init__(self):
        self.project_root = Path(__file__).parent.parent.parent
        self.fixes_applied = 0
        self.files_modified = []
        self.errors_found = []
        
        # Mapeamento de imports problemáticos
        self.import_mappings = {
            "from config.paths import": "from config.paths import",
            "import config.paths as paths": "import config.paths as paths",
            "from core.llm.ollama_client import llm_manager": "from core.llm.ollama_client import llm_manager",
            "from core.llm.ollama_client import": "from core.llm.ollama_client import",
        }
        
        # Arquivos essenciais que devem existir
        self.essential_files = {
            "core/__init__.py": "# Core package",
            "core/agents/__init__.py": "# Agents package", 
            "core/llm/__init__.py": "# LLM package",
            "config/__init__.py": "# Config package",
        }
    
    def create_missing_init_files(self):
        """Cria arquivos __init__.py faltantes"""
        print("📝 Criando arquivos __init__.py faltantes...")
        
        created_count = 0
        for file_path, content in self.essential_files.items():
            full_path = self.project_root / file_path
            
            if not full_path.exists():
                full_path.parent.mkdir(parents=True, exist_ok=True)
                full_path.write_text(f"{content}\n", encoding="utf-8")
                print(f"   ✅ Criado: {file_path}")
                created_count += 1
            else:
                print(f"   ➖ Já existe: {file_path}")
        
        return created_count
    
    def fix_config_paths(self):
        """Cria config/paths.py básico se não existir"""
        paths_file = self.project_root / "config/paths.py"
        
        if not paths_file.exists():
            print("📁 Criando config/paths.py básico...")
            
            paths_content = '''"""
Paths básicos para funcionamento do sistema
"""

from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
REFLECTION_DIR = PROJECT_ROOT / "reflection"
LOGS_DIR = PROJECT_ROOT / "logs"

# Estados principais
IDENTITY_STATE = REFLECTION_DIR / "state" / "identity" / "identity_state.yaml"
MEMORY_LOG = REFLECTION_DIR / "state" / "identity" / "memory_log.yaml"
CYCLE_HISTORY = REFLECTION_DIR / "state" / "temporal" / "cycle_history.json"

def ensure_directories():
    """Garante que diretórios essenciais existem"""
    dirs = [
        REFLECTION_DIR / "state" / "identity",
        REFLECTION_DIR / "state" / "temporal", 
        LOGS_DIR
    ]
    
    for directory in dirs:
        directory.mkdir(parents=True, exist_ok=True)

ensure_directories()
'''
            
            paths_file.write_text(paths_content)
            print("✅ config/paths.py criado!")
            return True
        else:
            print("➖ config/paths.py já existe")
            return False
    
    def create_basic_code_agent(self):
        """Cria CodeAgent básico se não existir"""
        code_agent_file = self.project_root / "core/agents/code_agent.py"
        
        if not code_agent_file.exists():
            print("🤖 Criando CodeAgent básico...")
            
            code_agent_content = '''"""
CodeAgent básico para funcionamento
"""

class CodeAgent:
    def __init__(self, use_mock=False):
        self.latest_output = ""
        self.use_mock = use_mock
    
    def execute_task(self, task: str):
        """Executa tarefa básica"""
        self.latest_output = f'def {task.lower().replace(" ", "_")}():\\n    """\\n    {task}\\n    """\\n    return "TODO"'
        
        # Simular resultado
        class Result:
            def __init__(self, code, success=True):
                self.code = code
                self.success = success
                self.quality_score = 5.0
        
        return Result(self.latest_output)
'''
            
            code_agent_file.parent.mkdir(parents=True, exist_ok=True)
            code_agent_file.write_text(code_agent_content)
            print("✅ CodeAgent básico criado!")
            return True
        else:
            print("➖ CodeAgent já existe")
            return False
    
    def integrate_ollama_client(self):
        """Move ollama_client.py para local correto"""
        source_file = self.project_root / "ollama_client.py"
        target_file = self.project_root / "core/llm/llm_manager.py"
        
        if source_file.exists():
            print("🔄 Movendo ollama_client.py...")
            
            # Backup se existir
            if target_file.exists():
                backup = target_file.with_suffix('.py.backup')
                target_file.rename(backup)
                print(f"   💾 Backup: {backup}")
            
            # Mover arquivo
            target_file.parent.mkdir(parents=True, exist_ok=True)
            content = source_file.read_text(encoding="utf-8")
            target_file.write_text(content, encoding="utf-8")
            source_file.unlink()
            
            print("   ✅ Integrado como core/llm/llm_manager.py")
            return True
        else:
            print("   ➖ ollama_client.py não encontrado")
            return False
    
    def fix_imports_in_file(self, file_path: Path) -> bool:
        """Corrige imports em arquivo específico"""
        try:
            content = file_path.read_text(encoding='utf-8')
            original_content = content
            
            # Aplicar correções
            for old_import, new_import in self.import_mappings.items():
                if old_import in content:
                    content = content.replace(old_import, new_import)
            
            # Salvar se modificado
            if content != original_content:
                file_path.write_text(content, encoding='utf-8')
                return True
            
            return False
            
        except Exception as e:
            self.errors_found.append(f"Erro em {file_path}: {e}")
            return False
    
    def fix_all_imports(self):
        """Corrige imports em todos arquivos Python"""
        print("🔧 Corrigindo imports...")
        
        python_files = list(self.project_root.rglob("*.py"))
        python_files = [f for f in python_files if not any(skip in str(f) for skip in [
            "__pycache__", ".git", "venv", ".venv"
        ])]
        
        modified_count = 0
        for file_path in python_files:
            if self.fix_imports_in_file(file_path):
                self.files_modified.append(str(file_path.relative_to(self.project_root)))
                modified_count += 1
        
        print(f"🔧 {modified_count} arquivos modificados")
        return modified_count
    
    def run_complete_fix(self):
        """Executa correção completa"""
        print("🔧 CORREÇÃO DE IMPORTS - RSCA")
        print("=" * 40)
        
        steps = [
            ("Init files", self.create_missing_init_files),
            ("Config paths", self.fix_config_paths), 
            ("Ollama client", self.integrate_ollama_client),
            ("Code agent", self.create_basic_code_agent),
            ("Fix imports", self.fix_all_imports)
        ]
        
        total_operations = 0
        
        for step_name, step_function in steps:
            print(f"\n🔄 {step_name}...")
            try:
                result = step_function()
                if isinstance(result, int):
                    total_operations += result
                elif result:
                    total_operations += 1
                print(f"✅ {step_name} OK")
            except Exception as e:
                print(f"❌ {step_name} falhou: {e}")
                self.errors_found.append(f"{step_name}: {e}")
        
        # Resumo
        print(f"\n📊 RESUMO:")
        print(f"🔧 Operações: {total_operations}")
        print(f"📁 Arquivos modificados: {len(self.files_modified)}")
        print(f"❌ Erros: {len(self.errors_found)}")
        
        if not self.errors_found:
            print(f"\n✅ CORREÇÕES CONCLUÍDAS!")
            print("🚀 Próximo: python scripts/tests/test_quick.py")
        else:
            print(f"\n⚠️ Alguns erros encontrados")
            for error in self.errors_found[:3]:
                print(f"   • {error}")
        
        return len(self.errors_found) == 0

def main():
    fixer = ImportFixer()
    success = fixer.run_complete_fix()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()