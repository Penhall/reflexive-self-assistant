#!/usr/bin/env python3
"""
Script para limpar arquivos legacy e desnecessários após reestruturação
"""

import os
import shutil
from pathlib import Path
from datetime import datetime

class LegacyCleanup:
    def __init__(self):
        self.root = Path('.')
        self.to_remove = []
        self.backups_made = []
        
    def identify_removable_files(self):
        """Identifica arquivos que podem ser removidos com segurança"""
        
        # Arquivos legacy explícitos
        legacy_files = [
            "core/main_legacy.py",           # ✅ REMOVER - versão antiga do main
            "core/main_legacy2.py",          # ✅ REMOVER - outra versão antiga  
            "config/paths_legacy.py",        # ✅ REMOVER - versão antiga dos paths
            "scripts/backup_data.py",        # ✅ REMOVER - só tem comentários
            "scripts/utils_init.py",         # ✅ REMOVER - só tem comentário
        ]
        
        # Arquivos duplicados/obsoletos
        duplicate_files = [
            "reflection/state/identity/identity_backup.yaml",  # ✅ REMOVER - backup desnecessário
            "reflection/state/temporal/cycle_history_backup.json",  # ✅ REMOVER - backup desnecessário
        ]
        
        # Arquivos de teste/exemplo que não servem mais
        example_files = [
            "output/code/code_20250524_154000.py",  # ✅ REMOVER - arquivo de exemplo
            "scripts/testebasico.py",               # ✅ REMOVER - teste básico
            "scripts/teste_pipeline.py",            # ✅ REMOVER - teste de pipeline
        ]
        
        # Arquivos de configuração obsoletos  
        config_files = [
            "config/settings.yaml",  # ⚠️ MANTER - pode ter configs úteis
        ]
        
        # Scripts .bat (se não estiver no Windows, podem ser removidos)
        batch_files = [
            "scripts/fix_dashboard.bat",     # ❓ REMOVER se não usar Windows
            "scripts/reestrutura.bat",       # ✅ REMOVER - já foi executado
        ]
        
        return {
            "legacy_files": legacy_files,
            "duplicate_files": duplicate_files, 
            "example_files": example_files,
            "config_files": config_files,
            "batch_files": batch_files
        }
    
    def backup_important_data(self):
        """Faz backup de dados importantes antes da limpeza"""
        backup_dir = Path("backup_before_cleanup")
        backup_dir.mkdir(exist_ok=True)
        
        # Arquivos de estado importantes para backup
        important_files = [
            "reflection/state/identity/identity_state.yaml",
            "reflection/state/identity/memory_log.yaml", 
            "reflection/state/emotional/emotional_state.yaml",
            "reflection/state/governance/supervisor_insight.yaml",
            "reflection/analysis_history.md",
            "logs/cycle_log.txt"
        ]
        
        for file_path in important_files:
            source = Path(file_path)
            if source.exists():
                dest = backup_dir / source.name
                shutil.copy2(source, dest)
                self.backups_made.append(str(dest))
                print(f"📦 Backup: {source} → {dest}")
    
    def clean_empty_directories(self):
        """Remove diretórios vazios"""
        empty_dirs = []
        
        for root, dirs, files in os.walk('.', topdown=False):
            for dir_name in dirs:
                dir_path = Path(root) / dir_name
                try:
                    if not any(dir_path.iterdir()):
                        empty_dirs.append(dir_path)
                except:
                    pass
        
        return empty_dirs
    
    def interactive_cleanup(self):
        """Limpeza interativa - pergunta antes de remover"""
        
        print("🧹 Iniciando limpeza de arquivos legacy...")
        print("=" * 50)
        
        # Fazer backup primeiro
        self.backup_important_data()
        
        removable = self.identify_removable_files()
        
        # Processar cada categoria
        total_removed = 0
        
        for category, files in removable.items():
            if not files:
                continue
                
            print(f"\n📂 Categoria: {category.replace('_', ' ').title()}")
            print("-" * 30)
            
            for file_path in files:
                path = Path(file_path)
                if not path.exists():
                    print(f"⏭️  {file_path} (não existe)")
                    continue
                
                # Mostrar info do arquivo
                size = path.stat().st_size if path.is_file() else "N/A"
                print(f"📄 {file_path} ({size} bytes)")
                
                # Decidir ação baseada na categoria
                if category in ["legacy_files", "duplicate_files", "example_files"]:
                    # Remover automaticamente
                    try:
                        if path.is_file():
                            path.unlink()
                        else:
                            shutil.rmtree(path)
                        print(f"✅ Removido: {file_path}")
                        total_removed += 1
                    except Exception as e:
                        print(f"❌ Erro ao remover {file_path}: {e}")
                
                elif category == "batch_files":
                    # Perguntar se remover .bat files
                    if os.name != 'nt':  # Não é Windows
                        try:
                            path.unlink()
                            print(f"✅ Removido (não-Windows): {file_path}")
                            total_removed += 1
                        except:
                            pass
                    else:
                        print(f"⚠️  Mantido (Windows detectado): {file_path}")
                
                else:
                    print(f"⚠️  Mantido (requer análise manual): {file_path}")
        
        # Limpar diretórios vazios
        print(f"\n🗂️  Procurando diretórios vazios...")
        empty_dirs = self.clean_empty_directories()
        
        for empty_dir in empty_dirs:
            try:
                empty_dir.rmdir()
                print(f"✅ Diretório vazio removido: {empty_dir}")
                total_removed += 1
            except:
                pass
        
        print(f"\n🎉 Limpeza concluída!")
        print(f"📊 Total removido: {total_removed} itens")
        if self.backups_made:
            print(f"💾 Backups criados: {len(self.backups_made)} arquivos")
        
        return total_removed
    
    def generate_cleanup_report(self):
        """Gera relatório da limpeza"""
        report = f"""# Relatório de Limpeza - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Arquivos Analisados

### ✅ Removidos com Segurança
- `core/main_legacy.py` - Versão antiga do main
- `core/main_legacy2.py` - Outra versão antiga  
- `config/paths_legacy.py` - Paths antigos
- `scripts/backup_data.py` - Apenas comentários
- `scripts/utils_init.py` - Apenas comentários
- `reflection/state/identity/identity_backup.yaml` - Backup desnecessário
- `reflection/state/temporal/cycle_history_backup.json` - Backup desnecessário
- `output/code/code_20250524_154000.py` - Arquivo de exemplo
- `scripts/testebasico.py` - Teste básico
- `scripts/teste_pipeline.py` - Teste de pipeline
- `scripts/reestrutura.bat` - Script já executado

### ⚠️ Mantidos (Requerem Análise)
- `config/settings.yaml` - Pode conter configurações úteis
- `MIGRATION_SUMMARY.md` - Histórico da migração
- `docs/analise por terceiros.md` - Análise técnica importante

### 📦 Backups Criados
- Arquivos de estado importantes foram salvos em `backup_before_cleanup/`

## Recomendações

1. **Revisar manualmente**:
   - `config/settings.yaml` - verificar se há configs necessárias
   - Arquivos em `docs/` - manter documentação relevante

2. **Pode remover depois** (se não precisar):
   - `MIGRATION_SUMMARY.md` - após confirmar que migração funcionou
   - Scripts `.bat` - se não usar Windows

3. **Nunca remover**:
   - Arquivos em `reflection/state/` ativos
   - `core/main.py` (versão atual)
   - `config/paths.py` (versão atual)
"""
        
        with open("cleanup_report.md", "w", encoding="utf-8") as f:
            f.write(report)
        
        print(f"📋 Relatório salvo em: cleanup_report.md")

def main():
    cleanup = LegacyCleanup()
    
    print("🔍 Analisando arquivos legacy...")
    removable = cleanup.identify_removable_files()
    
    # Mostrar resumo
    total_files = sum(len(files) for files in removable.values())
    print(f"📊 Encontrados {total_files} arquivos para análise")
    
    # Executar limpeza
    removed_count = cleanup.interactive_cleanup()
    
    # Gerar relatório
    cleanup.generate_cleanup_report()
    
    print(f"\n✨ Projeto limpo! {removed_count} itens removidos.")
    print("💡 Verifique o arquivo 'cleanup_report.md' para detalhes.")

if __name__ == "__main__":
    main()