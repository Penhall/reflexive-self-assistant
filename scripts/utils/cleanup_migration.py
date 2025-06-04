#!/usr/bin/env python3
"""
Script de limpeza para corrigir problemas da migração anterior
Remove duplicatas e organiza backups
"""

import os
import sys
from pathlib import Path
import shutil
from datetime import datetime

PROJECT_ROOT = Path(__file__).parent.parent

def cleanup_duplicate_backups():
    """Remove backups duplicados mantendo apenas o mais recente"""
    exports_dir = PROJECT_ROOT / "exports"
    
    if not exports_dir.exists():
        print("ℹ️ Diretório exports não encontrado")
        return
    
    # Buscar backups
    backup_files = list(exports_dir.glob("analysis_history_backup_*.md"))
    
    if not backup_files:
        print("ℹ️ Nenhum backup encontrado")
        return
    
    print(f"🧹 Encontrados {len(backup_files)} backups")
    
    # Manter apenas o mais recente
    if len(backup_files) > 1:
        backup_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
        latest_backup = backup_files[0]
        
        print(f"✅ Mantendo backup mais recente: {latest_backup.name}")
        
        # Remover outros backups
        for backup in backup_files[1:]:
            try:
                backup.unlink()
                print(f"🗑️ Removido: {backup.name}")
            except Exception as e:
                print(f"⚠️ Erro ao remover {backup.name}: {e}")

def check_analysis_history_status():
    """Verifica status do analysis_history.md"""
    md_file = PROJECT_ROOT / "reflection" / "analysis_history.md"
    
    if md_file.exists():
        print(f"📄 analysis_history.md ainda existe ({md_file.stat().st_size} bytes)")
        return True
    else:
        print("✅ analysis_history.md removido com sucesso")
        return False

def verify_settings():
    """Verifica se settings está configurado corretamente"""
    settings_file = PROJECT_ROOT / "config" / "settings.py"
    
    if not settings_file.exists():
        print("⚠️ settings.py não encontrado")
        return False
    
    try:
        with open(settings_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if '"enable_analysis_history_md": False' in content:
            print("✅ settings.py configurado corretamente")
            return True
        else:
            print("⚠️ settings.py pode precisar de ajuste")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao verificar settings: {e}")
        return False

def test_reflection_agent():
    """Testa se ReflectionAgent funciona sem MD"""
    try:
        sys.path.append(str(PROJECT_ROOT))
        from core.agents.reflection_agent import ReflectionAgent
        
        agent = ReflectionAgent()
        
        md_logging = getattr(agent, 'enable_md_logging', True)
        
        if md_logging:
            print("⚠️ ReflectionAgent ainda tentando usar MD logging")
            return False
        else:
            print("✅ ReflectionAgent funcionando sem MD logging")
            agent.close()
            return True
            
    except Exception as e:
        print(f"❌ Erro ao testar ReflectionAgent: {e}")
        return False

def create_neo4j_instructions():
    """Cria arquivo com instruções para configurar Neo4j"""
    instructions_file = PROJECT_ROOT / "NEO4J_SETUP.md"
    
    instructions = """# 🐳 Configuração do Neo4j para RSCA

## Problema Atual
O sistema está usando MockGraphMemory devido a erro de autenticação:
`Neo.ClientError.Security.Unauthorized`

## Solução

### 1. Iniciar Neo4j com Docker
```bash
docker run -d --name rsca-neo4j \\
  -p 7474:7474 -p 7687:7687 \\
  -e NEO4J_AUTH=neo4j/reflexive123 \\
  neo4j:latest
```

### 2. Aguardar inicialização
```bash
# Aguardar ~30 segundos
sleep 30

# Verificar se está rodando
docker logs rsca-neo4j
```

### 3. Testar conexão
```bash
python -c "
from memory.graph_rag.graph_interface import GraphMemory
try:
    graph = GraphMemory()
    graph.get_categories_and_counts()
    print('✅ Neo4j conectado!')
    graph.close()
except Exception as e:
    print(f'❌ Erro: {e}')
"
```

### 4. Configurar .env (opcional)
```bash
# .env
NEO4J_URI=bolt://localhost:7687
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=reflexive123
```

## Interface Web
- URL: http://localhost:7474
- Usuário: neo4j
- Senha: reflexive123

## Troubleshooting

### Porta já em uso
```bash
docker stop rsca-neo4j
docker rm rsca-neo4j
# Repetir comando de inicialização
```

### Verificar se Docker está rodando
```bash
docker --version
docker ps
```
"""
    
    with open(instructions_file, 'w', encoding='utf-8') as f:
        f.write(instructions)
    
    print(f"📋 Instruções Neo4j criadas: {instructions_file}")

def main():
    """Função principal de limpeza"""
    print("🧹 Iniciando limpeza pós-migração")
    print("=" * 40)
    
    # 1. Limpar backups duplicados
    cleanup_duplicate_backups()
    
    # 2. Verificar status do analysis_history.md
    md_exists = check_analysis_history_status()
    
    # 3. Verificar configurações
    settings_ok = verify_settings()
    
    # 4. Testar ReflectionAgent
    agent_ok = test_reflection_agent()
    
    # 5. Criar instruções Neo4j
    create_neo4j_instructions()
    
    print("\n" + "=" * 40)
    print("📊 RESUMO DA LIMPEZA:")
    print(f"• analysis_history.md removido: {'✅' if not md_exists else '❌'}")
    print(f"• Configurações OK: {'✅' if settings_ok else '⚠️'}")
    print(f"• ReflectionAgent funcionando: {'✅' if agent_ok else '⚠️'}")
    print(f"• Backups organizados: ✅")
    print(f"• Instruções Neo4j criadas: ✅")
    
    print("\n🎯 PRÓXIMOS PASSOS:")
    
    if md_exists:
        print("1. Remover manualmente: reflection/analysis_history.md")
    
    if not settings_ok:
        print("2. Editar config/settings.py:")
        print("   LEGACY_FEATURES = {'enable_analysis_history_md': False}")
    
    if not agent_ok:
        print("3. Verificar imports do ReflectionAgent")
    
    print("4. Configurar Neo4j (ver NEO4J_SETUP.md)")
    print("5. Testar: python core/main.py")
    
    # Determinar se migração foi bem-sucedida
    success = not md_exists and agent_ok
    
    if success:
        print("\n✅ LIMPEZA CONCLUÍDA COM SUCESSO!")
        print("O sistema está funcionando sem analysis_history.md")
    else:
        print("\n⚠️ LIMPEZA PARCIAL - verifique itens acima")
    
    return success

if __name__ == "__main__":
    main()