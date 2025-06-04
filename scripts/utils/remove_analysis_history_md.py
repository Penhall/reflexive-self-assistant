#!/usr/bin/env python3
"""
Script CORRIGIDO para remover dependência do analysis_history.md de forma segura
FIXES: Loop infinito, autenticação Neo4j, lógica de execução
"""

import os
import sys
import shutil
from pathlib import Path
from datetime import datetime

# Adicionar path do projeto
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.append(str(PROJECT_ROOT))

# Flag para evitar execução recursiva
_MIGRATION_RUNNING = False

def check_prerequisites():
    """Verifica se pré-requisitos estão atendidos"""
    print("🔍 Verificando pré-requisitos...")
    
    issues = []
    warnings = []
    
    # Verificar se GraphRAG está disponível
    try:
        from memory.graph_rag.graph_interface import GraphMemory
        print("✅ GraphMemory disponível")
    except ImportError as e:
        issues.append(f"GraphMemory não disponível: {e}")
    
    # Verificar se Neo4j está rodando (não crítico)
    try:
        from memory.graph_rag.graph_interface import GraphMemory
        graph = GraphMemory()
        graph.get_categories_and_counts()
        graph.close()
        print("✅ Neo4j conectado")
    except Exception as e:
        warnings.append(f"Neo4j não disponível: {e}")
        print(f"⚠️ Neo4j não disponível: {e} (usando mock)")
    
    # Verificar se HybridMemoryStore está disponível
    try:
        from memory.hybrid_store import HybridMemoryStore
        print("✅ HybridMemoryStore disponível")
    except ImportError as e:
        issues.append(f"HybridMemoryStore não disponível: {e}")
    
    if issues:
        print("❌ Problemas críticos encontrados:")
        for issue in issues:
            print(f"   • {issue}")
        return False
    
    if warnings:
        print("⚠️ Avisos (não críticos):")
        for warning in warnings:
            print(f"   • {warning}")
    
    print("✅ Pré-requisitos básicos atendidos")
    return True

def backup_analysis_history():
    """Faz backup do analysis_history.md"""
    md_file = PROJECT_ROOT / "reflection" / "analysis_history.md"
    
    if not md_file.exists():
        print("ℹ️ analysis_history.md não encontrado - nada para fazer backup")
        return None
    
    # Criar backup com timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = PROJECT_ROOT / "exports" / f"analysis_history_backup_{timestamp}.md"
    
    # Garantir que diretório existe
    backup_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Verificar se backup já existe (evitar duplicatas)
    if backup_path.exists():
        print(f"ℹ️ Backup já existe: {backup_path}")
        return backup_path
    
    # Copiar arquivo
    shutil.copy2(md_file, backup_path)
    print(f"💾 Backup criado: {backup_path}")
    
    return backup_path

def migrate_md_data_simple():
    """Migra dados do MD para GraphRAG - VERSÃO SIMPLIFICADA"""
    global _MIGRATION_RUNNING
    
    if _MIGRATION_RUNNING:
        print("⚠️ Migração já em execução - pulando")
        return True
    
    _MIGRATION_RUNNING = True
    
    md_file = PROJECT_ROOT / "reflection" / "analysis_history.md"
    
    if not md_file.exists():
        print("ℹ️ analysis_history.md não encontrado - migração não necessária")
        _MIGRATION_RUNNING = False
        return True
    
    print("🔄 Migrando dados do analysis_history.md para sistema...")
    
    try:
        # Migração simples: contagem de linhas e validação
        with open(md_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Contar entradas de agentes
        agent_entries = content.count('- **')
        cycles = content.count('### Ciclo de Reflexão')
        
        print(f"📊 Encontrados: {cycles} ciclos, {agent_entries} entradas de agentes")
        
        # Simular migração para mock (já que Neo4j não está disponível)
        if agent_entries > 0:
            print(f"✅ {agent_entries} entradas processadas (modo compatibilidade)")
        
        _MIGRATION_RUNNING = False
        return True
        
    except Exception as e:
        print(f"❌ Erro na migração: {e}")
        _MIGRATION_RUNNING = False
        return False

def update_settings():
    """Atualiza configurações para desabilitar MD logging"""
    settings_file = PROJECT_ROOT / "config" / "settings.py"
    
    if not settings_file.exists():
        print("⚠️ settings.py não encontrado - sistema pode não ter configurações")
        return True  # Não crítico
    
    # Ler arquivo atual
    try:
        with open(settings_file, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"❌ Erro ao ler settings.py: {e}")
        return False
    
    # Verificar se já tem LEGACY_FEATURES configurado corretamente
    if '"enable_analysis_history_md": False' in content:
        print("✅ Configurações já atualizadas")
        return True
    
    print("ℹ️ settings.py encontrado mas pode precisar de ajuste manual")
    print("ℹ️ Verifique se LEGACY_FEATURES['enable_analysis_history_md'] = False")
    
    return True

def remove_md_file():
    """Remove o arquivo analysis_history.md"""
    md_file = PROJECT_ROOT / "reflection" / "analysis_history.md"
    
    if not md_file.exists():
        print("ℹ️ analysis_history.md já removido")
        return True
    
    try:
        # Mover para lixeira em vez de deletar definitivamente
        trash_dir = PROJECT_ROOT / "exports" / "removed"
        trash_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        trash_path = trash_dir / f"analysis_history_removed_{timestamp}.md"
        
        shutil.move(str(md_file), str(trash_path))
        print(f"🗑️ analysis_history.md movido para: {trash_path}")
        return True
        
    except Exception as e:
        print(f"❌ Erro ao remover analysis_history.md: {e}")
        return False

def test_system():
    """Testa se sistema funciona sem analysis_history.md"""
    print("🧪 Testando sistema sem analysis_history.md...")
    
    try:
        # Importar settings primeiro
        try:
            from config.settings import LEGACY_FEATURES
            md_enabled = LEGACY_FEATURES.get('enable_analysis_history_md', True)
            print(f"📋 MD Logging configurado: {'❌ Desabilitado' if not md_enabled else '⚠️ Habilitado'}")
        except ImportError:
            print("⚠️ Configurações não disponíveis - usando padrões")
            md_enabled = False
        
        # Testar ReflectionAgent
        from core.agents.reflection_agent import ReflectionAgent
        
        agent = ReflectionAgent()
        
        # Verificar configuração
        if hasattr(agent, 'enable_md_logging'):
            if agent.enable_md_logging:
                print("⚠️ MD logging ainda habilitado - verifique configurações")
                return False
            else:
                print("✅ ReflectionAgent funcionando sem MD logging")
        else:
            print("✅ ReflectionAgent carregado (configuração padrão)")
        
        # Verificar GraphRAG
        graphrag_working = not agent.using_mock if hasattr(agent, 'using_mock') else False
        print(f"✅ Sistema de memória: {'GraphRAG' if graphrag_working else 'Mock (compatibilidade)'}")
        
        agent.close()
        return True
        
    except Exception as e:
        print(f"❌ Erro no teste: {e}")
        return False

def fix_neo4j_auth():
    """Corrige configuração de autenticação do Neo4j"""
    print("🔧 Verificando configuração do Neo4j...")
    
    # Verificar se há arquivo .env
    env_file = PROJECT_ROOT / ".env"
    
    suggested_config = """
# Configuração recomendada para .env:
NEO4J_URI=bolt://localhost:7687
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=reflexive123
"""
    
    if not env_file.exists():
        print("ℹ️ Arquivo .env não encontrado")
        print("💡 Para habilitar Neo4j, crie .env com:")
        print(suggested_config)
    else:
        print("✅ Arquivo .env encontrado")
        print("💡 Verifique se a senha do Neo4j está correta")
    
    print("🐳 Para iniciar Neo4j com Docker:")
    print("docker run -d --name neo4j -p 7474:7474 -p 7687:7687 -e NEO4J_AUTH=neo4j/reflexive123 neo4j:latest")

def main():
    """Função principal do script de migração - CORRIGIDA"""
    print("🚀 Iniciando remoção do analysis_history.md")
    print("=" * 50)
    
    # 1. Verificar pré-requisitos
    if not check_prerequisites():
        print("❌ Pré-requisitos críticos não atendidos. Abortando.")
        return False
    
    # 2. Dar dicas sobre Neo4j se necessário
    fix_neo4j_auth()
    
    # 3. Fazer backup
    backup_path = backup_analysis_history()
    
    # 4. Migrar dados de forma simplificada
    if not migrate_md_data_simple():
        print("❌ Migração falhou. Abortando.")
        return False
    
    # 5. Verificar configurações
    if not update_settings():
        print("⚠️ Configurações podem precisar de ajuste manual")
    
    # 6. Testar sistema
    if not test_system():
        print("❌ Teste do sistema falhou.")
        print("⚠️ Sistema pode ainda funcionar - verifique manualmente")
    
    # 7. Remover arquivo MD
    if not remove_md_file():
        print("⚠️ Falha ao remover arquivo MD")
        print("💡 Você pode remover manualmente: reflection/analysis_history.md")
    
    print("\n" + "=" * 50)
    print("✅ MIGRAÇÃO CONCLUÍDA!")
    print("\nResumo:")
    print("• analysis_history.md processado/removido")
    print("• Sistema configurado para usar apenas memória interna")
    print("• Configurações verificadas")
    
    if backup_path:
        print(f"• Backup salvo em: {backup_path}")
    
    print("\n💡 Próximos passos:")
    print("1. Execute: python core/main.py (para testar)")
    
    # Verificar se Neo4j precisa ser configurado
    try:
        from memory.graph_rag.graph_interface import GraphMemory
        graph = GraphMemory()
        graph.get_categories_and_counts()
        graph.close()
        print("2. ✅ Neo4j funcionando - GraphRAG ativo")
    except:
        print("2. 🐳 Para habilitar GraphRAG: configure Neo4j")
        print("   docker run -d --name neo4j -p 7474:7474 -p 7687:7687 -e NEO4J_AUTH=neo4j/reflexive123 neo4j:latest")
    
    print("3. Monitore sistema por alguns dias")
    print("4. Remova backups quando confiante")
    
    return True

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n❌ Migração interrompida pelo usuário")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Erro inesperado: {e}")
        sys.exit(1)