#!/usr/bin/env python3
"""
Script para corrigir imports quebrados após reestruturação
"""

import os
import re
from pathlib import Path

def fix_file_imports(file_path):
    """Corrige imports em um arquivo específico"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Mapeamentos de correções comuns
        fixes = [
            # Imports quebrados
            (r'from config\.paths import \([\s\S]*?\)', 'from config.paths import *'),
            
            # Variáveis não definidas (adiciona no início do arquivo se necessário)
            (r'IDENTITY_STATE(?!\s*=)', 'config.paths.IDENTITY_STATE'),
            (r'MEMORY_LOG(?!\s*=)', 'config.paths.MEMORY_LOG'),
            (r'SUPERVISOR_INSIGHT(?!\s*=)', 'config.paths.SUPERVISOR_INSIGHT'),
            (r'EMOTIONAL_STATE(?!\s*=)', 'config.paths.EMOTIONAL_STATE'),
            (r'CYCLE_HISTORY(?!\s*=)', 'config.paths.CYCLE_HISTORY'),
            (r'SYMBOLIC_DIALOGUE(?!\s*=)', 'config.paths.SYMBOLIC_DIALOGUE'),
            
            # Imports de paths usando str()
            (r'str\(IDENTITY_STATE\)', 'str(config.paths.IDENTITY_STATE)'),
            (r'str\(MEMORY_LOG\)', 'str(config.paths.MEMORY_LOG)'),
            (r'str\(CYCLE_HISTORY\)', 'str(config.paths.CYCLE_HISTORY)'),
        ]
        
        # Aplicar correções
        for pattern, replacement in fixes:
            content = re.sub(pattern, replacement, content)
        
        # Se o arquivo usa paths mas não importa config.paths, adicionar import
        if 'config.paths.' in content and 'import config.paths' not in content:
            # Encontrar local para inserir import
            import_section = []
            lines = content.split('\n')
            insert_pos = 0
            
            for i, line in enumerate(lines):
                if line.startswith('import ') or line.startswith('from '):
                    insert_pos = i + 1
                elif line.strip() == '' and insert_pos > 0:
                    break
            
            lines.insert(insert_pos, 'import config.paths')
            content = '\n'.join(lines)
        
        # Salvar apenas se houve mudanças
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
            
    except Exception as e:
        print(f"Erro ao processar {file_path}: {e}")
        return False
    
    return False

def main():
    print("🔧 Corrigindo imports quebrados...")
    
    # Encontrar todos os arquivos Python
    root_dir = Path('.')
    python_files = list(root_dir.rglob('*.py'))
    
    fixed_count = 0
    
    # Arquivos prioritários para corrigir
    priority_files = [
        'core/main.py',
        'core/agents/code_agent.py',
        'core/agents/doc_agent.py', 
        'reflection/analysis/supervisor_agent.py',
        'reflection/analysis/meta_coordinator.py',
        'reflection/symbolic/symbolic_dialogue.py',
        'interface/dashboard/streamlit_app.py'
    ]
    
    # Corrigir arquivos prioritários primeiro
    for file_path in priority_files:
        if Path(file_path).exists():
            if fix_file_imports(file_path):
                print(f"✅ Corrigido: {file_path}")
                fixed_count += 1
    
    # Corrigir outros arquivos Python
    for file_path in python_files:
        # Pular arquivos já processados
        if str(file_path) in priority_files:
            continue
            
        # Pular arquivos de configuração e scripts
        if 'config' in str(file_path) or 'scripts' in str(file_path):
            continue
        
        if fix_file_imports(file_path):
            print(f"✅ Corrigido: {file_path}")
            fixed_count += 1
    
    print(f"\n🎉 Correção concluída! {fixed_count} arquivos corrigidos.")
    
    # Criar arquivo temporário com imports manuais para arquivos críticos
    create_manual_fixes()

def create_manual_fixes():
    """Cria fixes manuais para arquivos críticos"""
    
    # Fix para doc_agent.py
    doc_agent_fix = '''
# Fix temporário para doc_agent.py
try:
    from config.paths import IDENTITY_STATE
except ImportError:
    from pathlib import Path
    IDENTITY_STATE = Path("reflection/state/identity/identity_state.yaml")
'''
    
    # Aplicar fix se necessário
    doc_agent_path = Path('core/agents/doc_agent.py')
    if doc_agent_path.exists():
        with open(doc_agent_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if 'IDENTITY_STATE' in content and 'import config.paths' not in content:
            # Inserir fix no início do arquivo
            lines = content.split('\n')
            insert_pos = 0
            
            # Encontrar posição após docstring
            for i, line in enumerate(lines):
                if line.strip().startswith('"""') or line.strip().startswith("'''"):
                    # Pular docstring
                    quote_type = '"""' if '"""' in line else "'''"
                    if line.count(quote_type) == 2:
                        insert_pos = i + 1
                    else:
                        for j in range(i + 1, len(lines)):
                            if quote_type in lines[j]:
                                insert_pos = j + 1
                                break
                    break
            
            lines.insert(insert_pos, doc_agent_fix.strip())
            
            with open(doc_agent_path, 'w', encoding='utf-8') as f:
                f.write('\n'.join(lines))
            
            print("✅ Fix manual aplicado em doc_agent.py")

if __name__ == "__main__":
    main()
