#!/usr/bin/env python3
"""
Instalação automática de modelos leves para RSCA
Instala apenas modelos otimizados para desenvolvimento
"""

import requests
import subprocess
import sys
import time
from typing import List, Dict, Tuple
from datetime import datetime
from dataclasses import dataclass

@dataclass
class ModelInfo:
    name: str
    size: str
    specialty: str
    priority: int  # 1=essencial, 2=recomendado, 3=opcional
    ram_usage: str
    description: str

class LightweightModelInstaller:
    def __init__(self):
        self.ollama_host = "http://localhost:11434"
        self.timeout = 300  # 5 minutos por modelo
        
        # Catálogo de modelos leves com informações detalhadas
        self.models_catalog = [
            ModelInfo(
                name="tinyllama:1.1b",
                size="~800MB",
                specialty="Testes rápidos e prototipagem",
                priority=1,  # Essencial
                ram_usage="~1GB",
                description="Ultra-leve, ideal para testes e desenvolvimento rápido"
            ),
            ModelInfo(
                name="codegemma:2b",
                size="~1.5GB", 
                specialty="Geração de código especializada",
                priority=1,  # Essencial
                ram_usage="~2GB",
                description="Otimizado para código Python, JavaScript, etc."
            ),
            ModelInfo(
                name="phi3:mini",
                size="~2GB",
                specialty="Uso geral equilibrado",
                priority=2,  # Recomendado
                ram_usage="~2.5GB", 
                description="Modelo da Microsoft, equilibrado para múltiplas tarefas"
            ),
            ModelInfo(
                name="llama3.2:1b",
                size="~1GB",
                specialty="Modelo compacto moderno",
                priority=2,  # Recomendado
                ram_usage="~1.5GB",
                description="Versão mais nova e eficiente da Meta"
            ),
            ModelInfo(
                name="qwen2:0.5b",
                size="~500MB",
                specialty="Ultra-compacto",
                priority=3,  # Opcional
                ram_usage="~800MB",
                description="Modelo ultra-leve da Alibaba para tarefas simples"
            ),
            ModelInfo(
                name="qwen2:1.5b",
                size="~1GB",
                specialty="Eficiência energética",
                priority=3,  # Opcional
                ram_usage="~1.5GB",
                description="Bom custo-benefício, eficiente em recursos"
            ),
            ModelInfo(
                name="gemma:2b",
                size="~1.5GB",
                specialty="Modelo do Google",
                priority=3,  # Opcional
                ram_usage="~2GB",
                description="Modelo aberto desenvolvido pelo Google"
            )
        ]
        
        self.stats = {
            "attempted": 0,
            "successful": 0,
            "failed": 0,
            "skipped": 0,
            "total_size": 0
        }
    
    def check_ollama_available(self) -> bool:
        """Verifica se Ollama está disponível"""
        print("🔍 Verificando conexão com Ollama...")
        
        try:
            response = requests.get(f"{self.ollama_host}/api/tags", timeout=10)
            if response.status_code == 200:
                print("✅ Ollama está funcionando!")
                return True
            else:
                print(f"❌ Ollama retornou status {response.status_code}")
                return False
        except requests.exceptions.RequestException as e:
            print(f"❌ Erro de conexão: {e}")
            print("\n💡 Para resolver:")
            print("   • Docker: docker-compose up -d")
            print("   • Local: ollama serve")
            print("   • Verificar se porta 11434 está livre")
            return False
    
    def list_installed_models(self) -> List[str]:
        """Lista modelos já instalados"""
        try:
            response = requests.get(f"{self.ollama_host}/api/tags", timeout=10)
            if response.status_code == 200:
                data = response.json()
                return [model.get("name") for model in data.get("models", [])]
            return []
        except:
            return []
    
    def install_model(self, model_info: ModelInfo) -> bool:
        """Instala um modelo específico"""
        print(f"\n📥 Instalando {model_info.name}...")
        print(f"   📊 Tamanho: {model_info.size}")
        print(f"   🎯 Especialidade: {model_info.specialty}")
        print(f"   🐏 RAM necessária: {model_info.ram_usage}")
        
        try:
            # Usar subprocess para instalação
            process = subprocess.Popen(
                ["ollama", "pull", model_info.name],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                universal_newlines=True
            )
            
            # Mostrar progresso em tempo real
            print("   ⏳ Baixando...", end="", flush=True)
            
            # Aguardar conclusão com timeout
            try:
                stdout, stderr = process.communicate(timeout=self.timeout)
                
                if process.returncode == 0:
                    print(" ✅ Sucesso!")
                    print(f"   💬 {model_info.description}")
                    return True
                else:
                    print(f" ❌ Falhou!")
                    print(f"   🔍 Erro: {stderr.strip()}")
                    return False
                    
            except subprocess.TimeoutExpired:
                process.kill()
                print(f" ⏰ Timeout após {self.timeout//60} minutos")
                return False
                
        except FileNotFoundError:
            print("   ❌ Comando 'ollama' não encontrado!")
            print("   💡 Certifique-se de que Ollama está instalado")
            return False
        except Exception as e:
            print(f"   ❌ Erro inesperado: {e}")
            return False
    
    def test_model(self, model_name: str) -> bool:
        """Testa se modelo foi instalado corretamente"""
        print(f"   🧪 Testando {model_name}...", end="", flush=True)
        
        try:
            test_payload = {
                "model": model_name,
                "prompt": "Hello, world!",
                "stream": False,
                "options": {"num_predict": 10}
            }
            
            response = requests.post(
                f"{self.ollama_host}/api/generate",
                json=test_payload,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                response_text = data.get("response", "").strip()
                if response_text:
                    print(" ✅ Funcionando!")
                    return True
                else:
                    print(" ⚠️ Resposta vazia")
                    return False
            else:
                print(f" ❌ HTTP {response.status_code}")
                return False
                
        except Exception as e:
            print(f" ❌ Erro: {e}")
            return False
    
    def show_installation_plan(self, models_to_install: List[ModelInfo]):
        """Mostra plano de instalação"""
        print("\n📋 PLANO DE INSTALAÇÃO")
        print("-" * 30)
        
        total_size_mb = 0
        by_priority = {1: [], 2: [], 3: []}
        
        for model in models_to_install:
            by_priority[model.priority].append(model)
            # Estimativa aproximada em MB
            size_str = model.size.replace("~", "").replace("GB", "000").replace("MB", "")
            try:
                total_size_mb += int(float(size_str))
            except:
                pass
        
        print(f"📊 Total de modelos: {len(models_to_install)}")
        print(f"💾 Espaço estimado: ~{total_size_mb//1000}GB")
        print(f"⏱️ Tempo estimado: {len(models_to_install) * 3-5} minutos")
        
        print(f"\n🎯 Por prioridade:")
        priorities = {1: "ESSENCIAIS", 2: "RECOMENDADOS", 3: "OPCIONAIS"}
        
        for priority in [1, 2, 3]:
            models = by_priority[priority]
            if models:
                print(f"\n   {priorities[priority]}:")
                for model in models:
                    print(f"   • {model.name} ({model.size}) - {model.specialty}")
    
    def install_by_priority(self, priority_filter: int = None):
        """Instala modelos filtrados por prioridade"""
        installed_models = self.list_installed_models()
        
        # Filtrar modelos
        models_to_install = []
        for model in self.models_catalog:
            if priority_filter and model.priority > priority_filter:
                continue
            if model.name not in installed_models:
                models_to_install.append(model)
            else:
                print(f"➖ {model.name} já está instalado")
                self.stats["skipped"] += 1
        
        if not models_to_install:
            print("✅ Todos os modelos selecionados já estão instalados!")
            return True
        
        # Mostrar plano
        self.show_installation_plan(models_to_install)
        
        # Confirmar instalação
        if not self.confirm_installation(models_to_install):
            print("⏹️ Instalação cancelada pelo usuário")
            return False
        
        # Executar instalações
        print(f"\n🚀 INICIANDO INSTALAÇÃO")
        print("=" * 30)
        
        success_count = 0
        for i, model in enumerate(models_to_install, 1):
            print(f"\n[{i}/{len(models_to_install)}] {model.name}")
            
            self.stats["attempted"] += 1
            
            if self.install_model(model):
                # Testar modelo após instalação
                if self.test_model(model.name):
                    success_count += 1
                    self.stats["successful"] += 1
                else:
                    print(f"   ⚠️ Instalado mas não passou no teste")
                    self.stats["failed"] += 1
            else:
                self.stats["failed"] += 1
                print(f"   💔 Falha na instalação de {model.name}")
        
        return success_count > 0
    
    def confirm_installation(self, models: List[ModelInfo]) -> bool:
        """Confirma instalação com usuário"""
        if len(sys.argv) > 1 and "--yes" in sys.argv:
            return True
        
        print(f"\n❓ Continuar com a instalação de {len(models)} modelos? (s/N): ", end="")
        try:
            response = input().strip().lower()
            return response in ['s', 'sim', 'y', 'yes']
        except KeyboardInterrupt:
            return False
    
    def show_final_summary(self):
        """Mostra resumo final da instalação"""
        print(f"\n" + "=" * 50)
        print("📋 RESUMO DA INSTALAÇÃO")
        print("=" * 50)
        
        print(f"🎯 Tentativas: {self.stats['attempted']}")
        print(f"✅ Sucessos: {self.stats['successful']}")
        print(f"❌ Falhas: {self.stats['failed']}")
        print(f"➖ Já instalados: {self.stats['skipped']}")
        
        success_rate = (
            self.stats['successful'] / self.stats['attempted'] * 100 
            if self.stats['attempted'] > 0 else 0
        )
        print(f"📊 Taxa de sucesso: {success_rate:.1f}%")
        
        if self.stats['successful'] > 0:
            print(f"\n🎉 {self.stats['successful']} modelos instalados com sucesso!")
            print("\n⚡ Próximos passos:")
            print("   1. Testar sistema: python scripts/tests/test_system.py")
            print("   2. Executar RSCA: python core/main.py")
        elif self.stats['failed'] > 0:
            print(f"\n⚠️ Algumas instalações falharam")
            print("💡 Possíveis soluções:")
            print("   • Verificar conexão com internet")
            print("   • Liberar mais espaço em disco") 
            print("   • Tentar novamente mais tarde")
        else:
            print(f"\n✅ Sistema já está otimizado!")
    
    def run_installation(self, mode: str = "recommended"):
        """Executa instalação baseada no modo"""
        print("📦 INSTALAÇÃO DE MODELOS LEVES - RSCA")
        print("=" * 45)
        print(f"🕒 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Verificar Ollama
        if not self.check_ollama_available():
            return False
        
        # Selecionar modelos baseado no modo
        if mode == "essential":
            priority_filter = 1
            print("🎯 Modo: ESSENCIAIS (apenas modelos críticos)")
        elif mode == "recommended":
            priority_filter = 2
            print("🎯 Modo: RECOMENDADOS (essenciais + recomendados)")
        elif mode == "all":
            priority_filter = None
            print("🎯 Modo: TODOS (todos os modelos leves)")
        else:
            print(f"❌ Modo inválido: {mode}")
            return False
        
        # Executar instalação
        success = self.install_by_priority(priority_filter)
        
        # Resumo final
        self.show_final_summary()
        
        return success

def main():
    if len(sys.argv) > 1 and "--help" in sys.argv:
        print("Instalação de modelos leves para RSCA")
        print("\nUso: python scripts/config/install_models.py [modo] [opções]")
        print("\nModos:")
        print("  essential     Instala apenas modelos essenciais (~2.5GB)")
        print("  recommended   Instala essenciais + recomendados (~5GB) [padrão]")
        print("  all          Instala todos os modelos leves (~8GB)")
        print("\nOpções:")
        print("  --yes        Confirma automaticamente (não pergunta)")
        print("  --help       Mostra esta ajuda")
        print("\nExemplos:")
        print("  python scripts/config/install_models.py essential")
        print("  python scripts/config/install_models.py recommended --yes")
        print("  python scripts/config/install_models.py all")
        sys.exit(0)
    
    # Determinar modo
    mode = "recommended"  # padrão
    if len(sys.argv) > 1:
        first_arg = sys.argv[1].lower()
        if first_arg in ["essential", "recommended", "all"]:
            mode = first_arg
    
    installer = LightweightModelInstaller()
    success = installer.run_installation(mode)
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()