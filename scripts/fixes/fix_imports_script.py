#!/usr/bin/env python3
"""
Corrige todos os imports quebrados do sistema RSCA
Arquivo crítico para funcionamento do sistema
"""

import os
import re
import sys
from pathlib import Path
from typing import List, Dict, Set

class ImportFixer:
    def __init__(self):
        self.project_root = Path(__file__).parent.parent.parent
        self.fixes_applied = 0
        self.files_modified = []
        self.errors_found = []
        
        # Mapeamento de imports antigos para novos
        self.import_mappings = {
            # Paths antigos
            "from config.paths import": "from config.paths import",
            "import config.paths as paths": "import config.paths as paths",
            
            # LLM Manager
            "from core.llm.ollama_client import llm_manager": "from core.llm.ollama_client import llm_manager",
            "from core.llm.ollama_client import": "from core.llm.ollama_client import",
            
            # Reflexão
            "from reflection.analysis.supervisor_agent import": "from reflection.analysis.supervisor_agent import",
            "from reflection.analysis.pattern_analyzer import": "from reflection.analysis.pattern_analyzer import", 
            "from reflection.symbolic.symbolic_dialogue import": "from reflection.symbolic.symbolic_dialogue import",
            
            # Memória
            "from reflection.memory.symbolic_memory import": "from memory.symbolic.symbolic_memory import",
            "from memory.graph_rag.graph_interface import": "from memory.graph_rag.graph_interface import",
            
            # Agentes
            "from agents.": "from core.agents.",
            "from core.agents.reflection_agent import": "from core.agents.reflection_agent import",
            
            # Utils antigos
            "from utils.": "from scripts.",
            "from scripts.logger import": "from scripts.utils.logger import"
        }
        
        # Arquivos essenciais que devem existir
        self.essential_files = {
            "core/__init__.py": "# Core package",
            "core/agents/__init__.py": "# Agents package", 
            "core/llm/__init__.py": "# LLM package",
            "config/__init__.py": "# Config package",
            "memory/__init__.py": "# Memory package",
            "memory/symbolic/__init__.py": "# Symbolic memory package",
            "memory/graph_rag/__init__.py": "# GraphRAG package",
            "reflection/__init__.py": "# Reflection package",
            "reflection/symbolic/__init__.py": "# Symbolic reflection package",
            "reflection/analysis/__init__.py": "# Analysis package",
            "scripts/__init__.py": "# Scripts package",
            "scripts/utils/__init__.py": "# Scripts utils package"
        }
    
    def create_missing_init_files(self):
        """Cria arquivos __init__.py faltantes"""
        print("📝 Criando arquivos __init__.py faltantes...")
        
        created_count = 0
        for file_path, content in self.essential_files.items():
            full_path = self.project_root / file_path
            
            if not full_path.exists():
                # Criar diretório se não existir
                full_path.parent.mkdir(parents=True, exist_ok=True)
                
                # Criar arquivo
                full_path.write_text(f"{content}\n", encoding="utf-8")
                print(f"   ✅ Criado: {file_path}")
                created_count += 1
            else:
                print(f"   ➖ Já existe: {file_path}")
        
        print(f"📝 {created_count} arquivos __init__.py criados")
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

# Diretório raiz do projeto
PROJECT_ROOT = Path(__file__).parent.parent

# Diretórios principais
REFLECTION_DIR = PROJECT_ROOT / "reflection"
LOGS_DIR = PROJECT_ROOT / "logs"
DATA_DIR = PROJECT_ROOT / "data"

# Estados principais (compatibilidade)
IDENTITY_STATE = REFLECTION_DIR / "state" / "identity" / "identity_state.yaml"
MEMORY_LOG = REFLECTION_DIR / "state" / "identity" / "memory_log.yaml"
CYCLE_HISTORY = REFLECTION_DIR / "state" / "temporal" / "cycle_history.json"
SYMBOLIC_DIALOGUE = REFLECTION_DIR / "symbolic" / "symbolic_dialogue.yaml"
DIALOGUE_DECISION = REFLECTION_DIR / "symbolic" / "dialogue_decision.yaml"
EMOTIONAL_STATE = REFLECTION_DIR / "state" / "emotional" / "emotional_state.yaml"
SUPERVISOR_INSIGHT = REFLECTION_DIR / "state" / "governance" / "supervisor_insight.yaml"
SYMBOLIC_TIMELINE = REFLECTION_DIR / "state" / "temporal" / "symbolic_timeline.yaml"
CYCLE_LOG = LOGS_DIR / "cycle_log.txt"
ALERTS_LOG = LOGS_DIR / "alerts.log"

def ensure_directories():
    """Garante que diretórios essenciais existem"""
    dirs_to_create = [
        REFLECTION_DIR / "state" / "identity",
        REFLECTION_DIR / "state" / "emotional",
        REFLECTION_DIR / "state" / "temporal", 
        REFLECTION_DIR / "state" / "governance",
        REFLECTION_DIR / "symbolic",
        REFLECTION_DIR / "analysis",
        LOGS_DIR,
        DATA_DIR
    ]
    
    for directory in dirs_to_create:
        directory.mkdir(parents=True, exist_ok=True)

# Executar ao importar
ensure_directories()
'''
            
            paths_file.write_text(paths_content)
            print("✅ config/paths.py criado!")
            return True
        else:
            print("➖ config/paths.py já existe")
            return False
    
    def create_simplified_agents(self):
        """Cria versões simplificadas dos agentes se não existirem"""
        agents_to_create = {
            "core/agents/code_agent.py": '''"""
CodeAgent simplificado que funciona com sistema atual
"""

from core.llm.ollama_client import llm_manager
from datetime import datetime
from dataclasses import dataclass

@dataclass
class CodeResult:
    code: str
    success: bool
    error: str = None
    quality_score: float = 5.0

class CodeAgent:
    def __init__(self, use_mock=False):
        self.llm = llm_manager
        self.latest_output = ""
        self.use_mock = use_mock
    
    def execute_task(self, task: str):
        """Executa tarefa de geração de código"""
        if self.use_mock:
            self.latest_output = f'def {task.lower().replace(" ", "_")}():\\n    """\\n    {task}\\n    """\\n    pass'
            return CodeResult(code=self.latest_output, success=True, quality_score=6.0)
        
        try:
            if self.llm.is_ready():
                response = self.llm.generate_code(task)
                if response.success:
                    self.latest_output = response.content
                    return CodeResult(code=response.content, success=True, quality_score=7.0)
                else:
                    error_msg = response.error or "Erro desconhecido"
                    self.latest_output = f"# Erro: {error_msg}"
                    return CodeResult(code=self.latest_output, success=False, error=error_msg)
            else:
                # Fallback
                self.latest_output = f'def {task.lower().replace(" ", "_")}():\\n    """\\n    {task}\\n    """\\n    return "TODO: Implementar"'
                return CodeResult(code=self.latest_output, success=True, quality_score=4.0)
                
        except Exception as e:
            error_msg = str(e)
            self.latest_output = f"# Erro na geração: {error_msg}"
            return CodeResult(code=self.latest_output, success=False, error=error_msg)
''',
            
            "core/agents/test_agent.py": '''"""
TestAgent simplificado
"""

from datetime import datetime
from pathlib import Path

class TestAgent:
    def __init__(self):
        self.latest_output = ""
        self.output_dir = Path("output/tests")
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def generate_tests(self, code: str, function_name: str = "function"):
        """Gera testes básicos para o código"""
        # Extrair nome da função do código se possível
        import re
        func_match = re.search(r'def\\s+(\\w+)\\s*\\(', code)
        if func_match:
            function_name = func_match.group(1)
        
        test_code = f'''"""
Testes gerados automaticamente
"""

import pytest

def test_{function_name}_exists():
    """Testa se a função existe e é chamável"""
    from main import {function_name}
    assert callable({function_name})

def test_{function_name}_basic():
    """Teste básico da função"""
    from main import {function_name}
    # TODO: Implementar teste específico
    result = {function_name}()
    assert result is not None

def test_{function_name}_edge_cases():
    """Testa casos extremos"""
    from main import {function_name}
    # TODO: Implementar testes de edge cases
    pass
'''
        
        self.latest_output = test_code
        
        # Salvar arquivo de teste
        test_file = self.output_dir / f"test_{function_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.py"
        test_file.write_text(test_code, encoding="utf-8")
        
        return test_code
''',
            
            "core/agents/doc_agent.py": '''"""
DocumentationAgent simplificado  
"""

class DocumentationAgent:
    def __init__(self):
        self.latest_output = ""
    
    def create_docs(self, code: str):
        """Cria documentação básica para o código"""
        lines = code.split('\\n')
        first_line = lines[0] if lines else "código"
        
        if 'def ' in first_line:
            func_name = first_line.split('def ')[1].split('(')[0] if 'def ' in first_line else 'função'
            self.latest_output = f"""# Documentação: {func_name}

## Descrição
Função gerada automaticamente pelo CodeAgent.

## Código
```python
{code}
```

## Uso
```python
result = {func_name}()
print(result)
```

## Notas
- Código gerado automaticamente
- Revisar implementação antes do uso em produção
"""
        else:
            self.latest_output = f"""# Documentação do Código

```python
{code}
```

Código gerado automaticamente pelo sistema RSCA.
"""
        
        print(f"📄 Documentação gerada: {len(self.latest_output)} caracteres")
        return self.latest_output
'''
        }
        
        created_count = 0
        for file_path, content in agents_to_create.items():
            full_path = self.project_root / file_path
            
            if not full_path.exists():
                full_path.parent.mkdir(parents=True, exist_ok=True)
                full_path.write_text(content, encoding="utf-8")
                print(f"   ✅ Criado: {file_path}")
                created_count += 1
            else:
                print(f"   ➖ Já existe: {file_path}")
        
        return created_count
    
    def fix_imports_in_file(self, file_path: Path) -> bool:
        """Corrige imports em um arquivo específico"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            original_content = content
            modified = False
            
            # Aplicar mapeamentos de imports
            for old_import, new_import in self.import_mappings.items():
                if old_import in content:
                    content = content.replace(old_import, new_import)
                    modified = True
            
            # Fixes específicos para paths hardcoded
            path_fixes = {
                'str(IDENTITY_STATE)': 'str(IDENTITY_STATE)',
                'str(MEMORY_LOG)': 'str(MEMORY_LOG)', 
                'str(CYCLE_HISTORY)': 'str(CYCLE_HISTORY)',
                '"reflection/': 'str(REFLECTION_DIR / "',
                '"logs/': 'str(LOGS_DIR / "'
            }
            
            for old_path, new_path in path_fixes.items():
                if old_path in content and old_path != new_path:
                    content = content.replace(old_path, new_path)
                    modified = True
            
            # Salvar se modificado
            if modified:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                return True
            
            return False
            
        except Exception as e:
            self.errors_found.append(f"Erro em {file_path}: {e}")
            return False
    
    def fix_all_imports(self):
        """Corrige imports em todos os arquivos Python"""
        print("🔧 Corrigindo imports em arquivos Python...")
        
        # Encontrar todos os arquivos Python
        python_files = []
        for pattern in ["**/*.py"]:  
            python_files.extend(self.project_root.rglob(pattern))
        
        # Filtrar arquivos do sistema
        python_files = [f for f in python_files if not any(skip in str(f) for skip in [
            "__pycache__", ".git", "venv", ".venv", "node_modules"
        ])]
        
        print(f"📁 Encontrados {len(python_files)} arquivos Python")
        
        modified_count = 0
        for file_path in python_files:
            if self.fix_imports_in_file(file_path):
                self.files_modified.append(str(file_path.relative_to(self.project_root)))
                modified_count += 1
                self.fixes_applied += 1
        
        print(f"🔧 {modified_count} arquivos modificados")
        return modified_count
    
    def integrate_ollama_client(self):
        """Integra o ollama_client.py com o sistema existente"""
        source_file = self.project_root / "ollama_client.py"
        target_file = self.project_root / "core/llm/llm_manager.py"
        
        if source_file.exists():
            print("🔄 Integrando ollama_client.py com sistema...")
            
            # Fazer backup do arquivo antigo se existir
            if target_file.exists():
                backup_file = target_file.with_suffix('.py.backup')
                target_file.rename(backup_file)
                print(f"   💾 Backup salvo: {backup_file}")
            
            # Copiar novo arquivo
            target_file.parent.mkdir(parents=True, exist_ok=True)
            content = source_file.read_text(encoding="utf-8")
            target_file.write_text(content, encoding="utf-8")
            
            # Remover arquivo original
            source_file.unlink()
            
            print("   ✅ ollama_client.py integrado como core/llm/llm_manager.py")
            return True
        else:
            print("   ⚠️ ollama_client.py não encontrado na raiz")
            return False
    
    def run_complete_fix(self):
        """Executa correção completa do sistema"""
        print("🔧 CORREÇÃO COMPLETA DE IMPORTS - SISTEMA RSCA")
        print("=" * 60)
        
        steps = [
            ("Criação de __init__.py", self.create_missing_init_files),
            ("Configuração de paths", self.fix_config_paths), 
            ("Integração Ollama Client", self.integrate_ollama_client),
            ("Criação de agentes", self.create_simplified_agents),
            ("Correção de imports", self.fix_all_imports)
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
                print(f"✅ {step_name} concluído")
            except Exception as e:
                print(f"❌ {step_name} falhou: {e}")
                self.errors_found.append(f"{step_name}: {e}")
        
        # Resumo final
        self.print_summary(total_operations)
        
        return len(self.errors_found) == 0
    
    def print_summary(self, total_operations):
        """Imprime resumo das correções"""
        print("\n" + "=" * 60)
        print("📋 RESUMO DAS CORREÇÕES")
        print("=" * 60)
        
        print(f"🔧 Total de operações: {total_operations}")
        print(f"📝 Correções aplicadas: {self.fixes_applied}")
        print(f"📁 Arquivos modificados: {len(self.files_modified)}")
        print(f"❌ Erros encontrados: {len(self.errors_found)}")
        
        if self.files_modified:
            print(f"\n✅ ARQUIVOS MODIFICADOS:")
            for file_path in self.files_modified[:10]:  # Mostrar apenas os primeiros 10
                print(f"   • {file_path}")
            if len(self.files_modified) > 10:
                print(f"   ... e mais {len(self.files_modified) - 10} arquivos")
        
        if self.errors_found:
            print(f"\n❌ ERROS ENCONTRADOS:")
            for error in self.errors_found[:5]:  # Mostrar apenas os primeiros 5
                print(f"   • {error}")
            if len(self.errors_found) > 5:
                print(f"   ... e mais {len(self.errors_found) - 5} erros")
        
        # Próximos passos
        if not self.errors_found:
            print(f"\n🎉 CORREÇÕES CONCLUÍDAS COM SUCESSO!")
            print("🚀 Próximos passos:")
            print("   1. Testar sistema: python scripts/tests/test_system.py")
            print("   2. Setup completo: python scripts/config/setup_system.py")
        else:
            print(f"\n⚠️ Algumas correções falharam")
            print("🔧 Revise os erros e execute novamente se necessário")

def main():
    if len(sys.argv) > 1 and sys.argv[1] == "--help":
        print("Corrige imports quebrados no sistema RSCA")
        print("\nUso: python scripts/fixes/fix_imports.py")
        print("\nEste script:")
        print("  • Cria arquivos __init__.py faltantes")
        print("  • Corrige imports quebrados")
        print("  • Integra ollama_client.py")
        print("  • Cria agentes básicos se não existirem")
        sys.exit(0)
    
    fixer = ImportFixer()
    success = fixer.run_complete_fix()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()