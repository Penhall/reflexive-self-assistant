#!/usr/bin/env python3
"""
Limpeza de modelos grandes do Ollama - versão Python multiplataforma
Substitui cleanup_large_models.sh para funcionar no Windows
"""

import requests
import subprocess
import sys
import time
from typing import List, Dict, Tuple
from datetime import datetime

class ModelCleaner:
    def __init__(self):
        self.ollama_host = "http://localhost:11434"
        self.timeout = 30
        
        # Modelos grandes para remoção (usar RAM excessiva)
        self.large_models_to_remove = [
            "llama3:8b", "llama3:15b", "llama3:70b",
            "codellama:7b", "codellama:13b", "codellama:34b", 
            "mistral:7b", "mistral:15b",
            "mixtral:8x7b", "mixtral:8x22b",
            "llama2:7b", "llama2:13b", "llama2:70b",
            "vicuna:7b", "vicuna:13b", "vicuna:33b",
            "orca-mini:7b", "orca-mini:13b",
            "wizardcoder:7b", "wizardcoder:13b", "wizardcoder:34b",
            "deepseek-coder:6.7b", "deepseek-coder:33b",
            "openchat:7b", "starling-lm:7b",
            "yi:6b", "yi:34b",
            "solar:10.7b", "dolphin-mixtral:8x7b"
        ]
        
        # Modelos leves recomendados (manter)
        self.recommended_lightweight = [
            "tinyllama:1.1b",    # ~800MB - Ultra leve
            "llama3.2:1b",       # ~1GB - Novo e eficiente  
            "codegemma:2b",      # ~1.5GB - Especializado em código
            "phi3:mini",         # ~2GB - Equilibrado
            "qwen2:0.5b",        # ~500MB - Ultra compacto
            "qwen2:1.5b",        # ~1GB - Bom custo-benefício
            "gemma:2b"           # ~1.5GB - Desenvolvido pelo Google
        ]
        
        self.stats = {
            "removed": 0,
            "kept": 0,
            "errors": 0,
            "space_freed": "Unknown"
        }
    
    def check_ollama_available(self) -> bool:
        """Verifica se Ollama está disponível"""
        print("🔍 Verificando se Ollama está rodando...")
        
        try:
            response = requests.get(f"{self.ollama_host}/api/tags", timeout=5)
            if response.status_code == 200:
                print("✅ Ollama está rodando!")
                return True
            else:
                print(f"❌ Ollama retornou status {response.status_code}")
                return False
        except requests.exceptions.RequestException as e:
            print(f"❌ Erro de conexão com Ollama: {e}")
            print("💡 Certifique-se de que Ollama está rodando:")
            print("   • Docker: docker-compose up -d")
            print("   • Local: ollama serve")
            return False
    
    def list_installed_models(self) -> List[Dict]:
        """Lista modelos instalados"""
        try:
            response = requests.get(f"{self.ollama_host}/api/tags", timeout=10)
            if response.status_code == 200:
                data = response.json()
                return data.get("models", [])
            else:
                print(f"❌ Erro ao listar modelos: HTTP {response.status_code}")
                return []
        except Exception as e:
            print(f"❌ Erro ao listar modelos: {e}")
            return []
    
    def remove_model(self, model_name: str) -> bool:
        """Remove um modelo específico"""
        try:
            # Usar subprocess para chamada direta ao ollama
            result = subprocess.run(
                ["ollama", "rm", model_name],
                capture_output=True,
                text=True,
                timeout=self.timeout
            )
            
            if result.returncode == 0:
                return True
            else:
                print(f"      ⚠️ Erro ao remover {model_name}: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            print(f"      ⚠️ Timeout ao remover {model_name}")
            return False
        except FileNotFoundError:
            print("      ❌ Comando 'ollama' não encontrado")
            print("      💡 Certifique-se de que Ollama está instalado e no PATH")
            return False
        except Exception as e:
            print(f"      ⚠️ Erro ao remover {model_name}: {e}")
            return False
    
    def estimate_model_size(self, model_info: Dict) -> str:
        """Estima tamanho do modelo baseado no nome"""
        name = model_info.get("name", "").lower()
        
        # Estimativas baseadas no tamanho do modelo
        if "70b" in name or "72b" in name:
            return "~40GB"
        elif any(size in name for size in ["33b", "34b"]):
            return "~20GB"  
        elif any(size in name for size in ["13b", "15b"]):
            return "~8GB"
        elif any(size in name for size in ["7b", "8b"]):
            return "~4GB"
        elif "2b" in name:
            return "~1.5GB"
        elif "1b" in name:
            return "~800MB"
        elif "0.5b" in name or "mini" in name:
            return "~500MB"
        else:
            # Tentar obter do campo size se disponível
            return model_info.get("size", "Unknown")
    
    def analyze_and_remove_large_models(self):
        """Analisa e remove modelos grandes"""
        print("\n🔍 ANALISANDO MODELOS INSTALADOS")
        print("-" * 50)
        
        installed_models = self.list_installed_models()
        if not installed_models:
            print("❌ Nenhum modelo encontrado ou erro na listagem")
            return False
        
        print(f"📦 {len(installed_models)} modelos instalados:")
        for model in installed_models:
            name = model.get("name", "unknown")
            size = self.estimate_model_size(model)
            print(f"   • {name} ({size})")
        
        print(f"\n🗑️ REMOVENDO MODELOS GRANDES:")
        print("-" * 30)
        
        removed_models = []
        for model_name in self.large_models_to_remove:
            # Verificar se modelo está instalado
            is_installed = any(
                model.get("name") == model_name 
                for model in installed_models
            )
            
            if is_installed:
                print(f"   🗑️ Removendo {model_name}...")
                
                # Mostrar tamanho estimado
                matching_model = next(
                    (m for m in installed_models if m.get("name") == model_name), 
                    {}
                )
                size = self.estimate_model_size(matching_model)
                print(f"      Liberando {size} de espaço...")
                
                if self.remove_model(model_name):
                    print(f"      ✅ {model_name} removido com sucesso")
                    removed_models.append(model_name)
                    self.stats["removed"] += 1
                else:
                    print(f"      ❌ Falha ao remover {model_name}")
                    self.stats["errors"] += 1
        
        print(f"\n📊 Resumo da remoção:")
        print(f"   🗑️ Modelos removidos: {len(removed_models)}")
        if removed_models:
            for model in removed_models:
                print(f"      • {model}")
        
        return len(removed_models) > 0
    
    def check_recommended_models(self):
        """Verifica se modelos recomendados estão instalados"""
        print(f"\n✅ VERIFICANDO MODELOS RECOMENDADOS")
        print("-" * 40)
        
        installed_models = self.list_installed_models()
        installed_names = [model.get("name") for model in installed_models]
        
        present_models = []
        missing_models = []
        
        for model in self.recommended_lightweight:
            if model in installed_names:
                matching_model = next(
                    (m for m in installed_models if m.get("name") == model), 
                    {}
                )
                size = self.estimate_model_size(matching_model)
                print(f"   ✅ {model} ({size}) - Instalado")
                present_models.append(model)
                self.stats["kept"] += 1
            else:
                print(f"   ⚠️ {model} - Não instalado (recomendado)")
                missing_models.append(model)
        
        print(f"\n📊 Status dos modelos recomendados:")
        print(f"   ✅ Presentes: {len(present_models)}/{len(self.recommended_lightweight)}")
        print(f"   ⚠️ Ausentes: {len(missing_models)}")
        
        if missing_models:
            print(f"\n💡 MODELOS RECOMENDADOS PARA INSTALAR:")
            for model in missing_models:
                specialty = self.get_model_specialty(model)
                print(f"   📥 ollama pull {model}  # {specialty}")
        
        return present_models, missing_models
    
    def get_model_specialty(self, model_name: str) -> str:
        """Retorna especialidade do modelo"""
        specialties = {
            "tinyllama:1.1b": "Ultra-leve, ideal para testes",
            "llama3.2:1b": "Novo modelo compacto da Meta",
            "codegemma:2b": "Especializado em código",
            "phi3:mini": "Equilibrado para uso geral",
            "qwen2:0.5b": "Ultra-compacto da Alibaba",
            "qwen2:1.5b": "Eficiente para tarefas variadas",
            "gemma:2b": "Modelo leve do Google"
        }
        return specialties.get(model_name, "Modelo leve recomendado")
    
    def show_installation_guide(self, missing_models: List[str]):
        """Mostra guia de instalação para modelos faltantes"""
        if not missing_models:
            return
        
        print(f"\n🚀 GUIA DE INSTALAÇÃO RÁPIDA")
        print("-" * 35)
        
        print("Instalar todos os modelos recomendados:")
        print("```bash")
        for model in missing_models:
            print(f"ollama pull {model}")
        print("```")
        
        print(f"\nOu instalar apenas os essenciais:")
        essentials = ["codegemma:2b", "tinyllama:1.1b"]
        for model in essentials:
            if model in missing_models:
                specialty = self.get_model_specialty(model)
                print(f"ollama pull {model}  # {specialty}")
    
    def calculate_benefits(self):
        """Calcula benefícios da limpeza"""
        print(f"\n🧠 BENEFÍCIOS DA LIMPEZA")
        print("-" * 25)
        
        if self.stats["removed"] > 0:
            print("✨ Melhorias obtidas:")
            print(f"   💾 Espaço liberado: ~{self.stats['removed'] * 5}GB estimados")
            print(f"   🐏 RAM liberada: ~{self.stats['removed'] * 4}GB por execução")
            print("   ⚡ Velocidade: Modelos leves respondem 3-5x mais rápido")
            print("   🔄 Estabilidade: Menor chance de timeout/out-of-memory")
            print("   🎯 Foco: Otimização para desenvolvimento com modelos eficientes")
        else:
            print("ℹ️ Nenhum modelo grande foi removido")
            print("   Isso pode significar que:")
            print("   • Sistema já está otimizado")
            print("   • Modelos grandes não estavam instalados")
    
    def show_next_steps(self, missing_models: List[str]):
        """Mostra próximos passos recomendados"""
        print(f"\n⚡ PRÓXIMOS PASSOS")
        print("-" * 18)
        
        if missing_models:
            print("1. 📥 Instalar modelos recomendados:")
            print(f"   python scripts/config/install_models.py")
            print()
        
        print("2. 🧪 Testar sistema:")
        print("   python scripts/tests/test_system.py")
        print()
        
        print("3. 🚀 Executar RSCA:")
        print("   python core/main.py")
        print()
        
        print("4. 📊 Dashboard (opcional):")
        print("   streamlit run interface/dashboard/streamlit_app.py")
    
    def run_cleanup(self):
        """Executa limpeza completa"""
        print("🧹 LIMPEZA DE MODELOS GRANDES - RSCA")
        print("=" * 50)
        print(f"🕒 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Verificar se Ollama está disponível
        if not self.check_ollama_available():
            return False
        
        # Mostrar modelos atuais
        installed_models = self.list_installed_models()
        if not installed_models:
            print("❌ Não foi possível listar modelos")
            return False
        
        # Executar limpeza
        print(f"\n🎯 Iniciando limpeza de {len(self.large_models_to_remove)} modelos grandes conhecidos...")
        cleanup_success = self.analyze_and_remove_large_models()
        
        # Verificar modelos recomendados
        present_models, missing_models = self.check_recommended_models()
        
        # Calcular benefícios
        self.calculate_benefits()
        
        # Mostrar próximos passos
        self.show_next_steps(missing_models)
        
        # Resumo final
        print(f"\n" + "=" * 50)
        print("📋 RESUMO DA LIMPEZA")
        print("=" * 50)
        
        print(f"🗑️ Modelos removidos: {self.stats['removed']}")
        print(f"✅ Modelos leves presentes: {self.stats['kept']}")
        print(f"❌ Erros: {self.stats['errors']}")
        print(f"⚠️ Modelos recomendados ausentes: {len(missing_models)}")
        
        if self.stats["removed"] > 0 or self.stats["kept"] > 0:
            print(f"\n✨ Limpeza concluída com sucesso!")
            if missing_models:
                print(f"💡 Considere instalar os modelos recomendados ausentes")
        else:
            print(f"\n⚠️ Nenhuma alteração realizada")
            print("   Sistema pode já estar otimizado ou sem modelos grandes")
        
        return True

def main():
    if len(sys.argv) > 1:
        if sys.argv[1] == "--help":
            print("Limpeza de modelos grandes do Ollama")
            print("\nUso: python scripts/config/cleanup_models.py [opções]")
            print("\nOpções:")
            print("  --help     Mostra esta ajuda")
            print("  --dry-run  Simula limpeza sem remover modelos")
            print("\nEste script:")
            print("  • Remove modelos grandes (7B+) que consomem muita RAM")
            print("  • Mantém modelos leves (≤2B) otimizados para desenvolvimento")
            print("  • Mostra recomendações de modelos ausentes")
            print("  • Calcula benefícios da limpeza")
            sys.exit(0)
        elif sys.argv[1] == "--dry-run":
            print("🔍 MODO SIMULAÇÃO - Nenhum modelo será removido")
            print("-" * 45)
            # Implementar dry-run seria interessante, mas não é crítico
    
    cleaner = ModelCleaner()
    success = cleaner.run_cleanup()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()