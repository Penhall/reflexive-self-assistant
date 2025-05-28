#!/usr/bin/env python3
"""
Setup único e completo do RSCA com modelos leves
Substitui todos os outros scripts de setup
"""

import os
import subprocess
import sys
import time
import requests
from pathlib import Path

class RSCASetup:
    def __init__(self):
        self.project_root = Path(__file__).parent.parent.parent
        self.success_steps = []
        self.failed_steps = []
    
    def run_command(self, command, description, timeout=60):
        """Executa comando com feedback"""
        print(f"⏳ {description}...")
        
        try:
            result = subprocess.run(
                command, 
                shell=True, 
                capture_output=True, 
                text=True,
                timeout=timeout,
                cwd=self.project_root
            )
            
            if result.returncode == 0:
                print(f"✅ {description}")
                return True, result.stdout
            else:
                print(f"❌ {description} - Erro:")
                print(f"   {result.stderr[:200]}")
                return False, result.stderr
                
        except subprocess.TimeoutExpired:
            print(f"❌ {description} - Timeout após {timeout}s")
            return False, "Timeout"
        except Exception as e:
            print(f"❌ {description} - Exceção: {e}")
            return False, str(e)
    
    def step_1_check_docker(self):
        """Verifica Docker"""
        print("\n🐳 ETAPA 1: Verificando Docker")
        print("-" * 40)
        
        # Verificar se Docker está instalado
        success, output = self.run_command("docker --version", "Verificar Docker instalado")
        if not success:
            print("💡 Instale Docker: https://docs.docker.com/get-docker/")
            return False
        
        print(f"   {output.strip()}")
        
        # Verificar se Docker está rodando
        success, _ = self.run_command("docker ps", "Verificar Docker rodando")
        if not success:
            print("💡 Inicie Docker: sudo systemctl start docker")
            return False
        
        return True
    
    def step_2_setup_containers(self):
        """Configura containers"""
        print("\n🔧 ETAPA 2: Configurando Containers")
        print("-" * 40)
        
        # Verificar se docker-compose.yml existe
        compose_files = [
            self.project_root / "docker-compose.yml",
            self.project_root / "infrastructure" / "docker-compose.yml"
        ]
        
        compose_file = None
        for f in compose_files:
            if f.exists():
                compose_file = f
                break
        
        if not compose_file:
            print("❌ docker-compose.yml não encontrado!")
            self.create_docker_compose()
            compose_file = self.project_root / "docker-compose.yml"
        
        print(f"✅ Usando: {compose_file}")
        
        # Parar containers existentes
        self.run_command("docker-compose down", "Parar containers existentes")
        
        # Iniciar containers
        success, _ = self.run_command("docker-compose up -d", "Iniciar containers", timeout=120)
        if not success:
            return False
        
        # Aguardar Ollama
        print("⏳ Aguardando Ollama inicializar (45s)...")
        time.sleep(45)
        
        # Verificar se Ollama está respondendo
        for attempt in range(5):
            try:
                response = requests.get("http://localhost:11434/api/tags", timeout=10)
                if response.status_code == 200:
                    print("✅ Ollama está funcionando!")
                    return True
            except:
                pass
            
            if attempt < 4:
                print(f"   Tentativa {attempt + 1}/5 - aguardando...")
                time.sleep(10)
        
        print("❌ Ollama não está respondendo")
        return False
    
    def step_3_cleanup_models(self):
        """Remove modelos grandes"""
        print("\n🗑️ ETAPA 3: Removendo Modelos Grandes")
        print("-" * 40)
        
        large_models = [
            "llama3:8b", "llama3:15b", "llama3:70b",
            "codellama:7b", "codellama:13b", "codellama:34b", 
            "mistral:7b", "mixtral:8x7b"
        ]
        
        removed_count = 0
        for model in large_models:
            success, _ = self.run_command(f"ollama rm {model}", f"Remover {model}")
            if success:
                removed_count += 1
        
        print(f"🗑️ {removed_count} modelos grandes removidos")
        return True
    
    def step_4_install_lightweight(self):
        """Instala modelos leves"""
        print("\n📦 ETAPA 4: Instalando Modelos Leves")
        print("-" * 40)
        
        lightweight_models = [
            ("tinyllama:1.1b", "Modelo ultra-leve (~800MB)"),
            ("codegemma:2b", "Especializado em código (~1.5GB)"),
            ("phi3:mini", "Equilibrado (~2GB)")
        ]
        
        installed_count = 0
        for model, description in lightweight_models:
            print(f"\n📥 {model}: {description}")
            success, _ = self.run_command(f"ollama pull {model}", f"Instalar {model}", timeout=300)
            if success:
                installed_count += 1
                print(f"   ✅ {model} instalado!")
            else:
                print(f"   ⚠️ {model} falhou")
        
        print(f"\n📊 {installed_count}/{len(lightweight_models)} modelos instalados")
        return installed_count > 0
    
    def step_5_create_files(self):
        """Cria arquivos necessários"""
        print("\n📝 ETAPA 5: Criando Arquivos Necessários")
        print("-" * 40)
        
        # Criar diretórios
        dirs = [
            "core/llm", "core/agents", "config", "logs", 
            "data", "exports/identities", "exports/reports"
        ]
        
        for dir_path in dirs:
            (self.project_root / dir_path).mkdir(parents=True, exist_ok=True)
        
        # Criar __init__.py files
        init_files = [
            "core/__init__.py", "core/llm/__init__.py", "core/agents/__init__.py",
            "config/__init__.py", "scripts/__init__.py"
        ]
        
        for init_file in init_files:
            file_path = self.project_root / init_file
            if not file_path.exists():
                file_path.write_text("# Package init\n")
        
        # Criar ollama_client.py simplificado
        self.create_ollama_client()
        
        # Criar llm_manager.py
        self.create_llm_manager()
        
        print("✅ Arquivos necessários criados")
        return True
    
    def step_6_test_system(self):
        """Testa o sistema"""
        print("\n🧪 ETAPA 6: Testando Sistema")
        print("-" * 40)
        
        try:
            # Testar conexão Ollama
            response = requests.get("http://localhost:11434/api/tags", timeout=5)
            if response.status_code != 200:
                print("❌ Ollama não está respondendo")
                return False
            
            models = response.json().get("models", [])
            model_names = [m["name"] for m in models]
            
            print(f"✅ {len(model_names)} modelos disponíveis:")
            for model in model_names:
                print(f"   • {model}")
            
            # Teste básico de geração
            if model_names:
                print(f"\n🧪 Testando geração com {model_names[0]}...")
                
                test_payload = {
                    "model": model_names[0],
                    "prompt": "def hello(): return",
                    "stream": False
                }
                
                response = requests.post(
                    "http://localhost:11434/api/generate",
                    json=test_payload,
                    timeout=30
                )
                
                if response.status_code == 200:
                    result = response.json()
                    content = result.get("response", "").strip()
                    if content:
                        print("✅ Geração funcionando!")
                        print(f"   Resposta: {content[:50]}...")
                        return True
                    else:
                        print("⚠️ Resposta vazia")
                        return False
                else:
                    print(f"❌ Erro na geração: {response.status_code}")
                    return False
            else:
                print("⚠️ Nenhum modelo disponível para teste")
                return False
                
        except Exception as e:
            print(f"❌ Erro no teste: {e}")
            return False
    
    def create_docker_compose(self):
        """Cria docker-compose.yml básico"""
        compose_content = '''version: '3.8'

services:
  ollama:
    image: ollama/ollama:latest
    container_name: rsca-ollama
    ports:
      - "11434:11434"
    volumes:
      - ollama_data:/root/.ollama
    environment:
      - OLLAMA_HOST=0.0.0.0
    restart: unless-stopped

  chromadb:
    image: chromadb/chroma:latest
    container_name: rsca-chromadb
    ports:
      - "8000:8000"
    environment:
      - CHROMA_SERVER_HOST=0.0.0.0
      - CHROMA_SERVER_PORT=8000
    volumes:
      - chromadb_data:/chroma/chroma
    restart: unless-stopped

volumes:
  ollama_data:
  chromadb_data:
'''
        
        compose_path = self.project_root / "docker-compose.yml"
        compose_path.write_text(compose_content)
        print(f"✅ Criado: {compose_path}")
    
    def create_ollama_client(self):
        """Cria cliente Ollama simplificado"""
        client_code = '''"""
Cliente Ollama simplificado para modelos leves
"""

import requests
import time
from typing import Dict, List, Optional
from dataclasses import dataclass

@dataclass
class LLMResponse:
    content: str
    model: str = ""
    tokens_used: int = 0
    generation_time: float = 0.0
    success: bool = True
    error: Optional[str] = None

class OllamaClient:
    def __init__(self, host: str = "http://localhost:11434"):
        self.host = host
        self.timeout = 60
        
        self.task_models = {
            "codigo": "codegemma:2b",
            "testes": "tinyllama:1.1b",
            "documentacao": "phi3:mini",
            "geral": "tinyllama:1.1b"
        }
    
    def is_available(self) -> bool:
        try:
            response = requests.get(f"{self.host}/api/tags", timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def list_models(self) -> List[str]:
        try:
            response = requests.get(f"{self.host}/api/tags", timeout=10)
            if response.status_code == 200:
                data = response.json()
                return [model["name"] for model in data.get("models", [])]
        except:
            pass
        return []
    
    def get_best_model_for_task(self, task_type: str = "geral") -> str:
        available = self.list_models()
        preferred = self.task_models.get(task_type.lower(), "tinyllama:1.1b")
        
        if preferred in available:
            return preferred
            
        for fallback in ["tinyllama:1.1b", "codegemma:2b", "phi3:mini"]:
            if fallback in available:
                return fallback
                
        return available[0] if available else "tinyllama:1.1b"
    
    def generate(self, model: str, prompt: str, **kwargs) -> LLMResponse:
        start_time = time.time()
        
        payload = {
            "model": model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": kwargs.get("temperature", 0.2),
                "top_p": kwargs.get("top_p", 0.9),
                "num_predict": kwargs.get("num_predict", 1024)
            }
        }
        
        try:
            response = requests.post(
                f"{self.host}/api/generate",
                json=payload,
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                data = response.json()
                return LLMResponse(
                    content=data.get("response", "").strip(),
                    model=model,
                    tokens_used=data.get("eval_count", 0),
                    generation_time=time.time() - start_time,
                    success=True
                )
            else:
                error_msg = f"HTTP {response.status_code}"
                
        except Exception as e:
            error_msg = str(e)
        
        return LLMResponse(
            content="",
            model=model,
            generation_time=time.time() - start_time,
            success=False,
            error=error_msg
        )
    
    def generate_code(self, task: str, context: Optional[Dict] = None) -> LLMResponse:
        model = self.get_best_model_for_task("codigo")
        
        prompt = f"""Você é um assistente de programação Python.

Tarefa: {task}

Instruções:
- Escreva código Python funcional
- Use nomes descritivos
- Inclua docstring simples
- Mantenha conciso

Código:"""
        
        return self.generate(model, prompt)

ollama_client = OllamaClient()
'''
        
        client_path = self.project_root / "core/llm/ollama_client.py"
        client_path.write_text(client_code)
        print(f"✅ Criado: {client_path}")
    
    def create_llm_manager(self):
        """Cria LLM manager"""
        manager_code = '''"""
LLM Manager simplificado
"""

from typing import Dict, Optional
from .ollama_client import ollama_client, LLMResponse

class LightweightLLMManager:
    def __init__(self):
        self.client = ollama_client
    
    def generate_code(self, task: str, context: Optional[Dict] = None) -> LLMResponse:
        return self.client.generate_code(task, context)
    
    def is_ready(self) -> bool:
        return self.client.is_available() and len(self.client.list_models()) > 0
    
    def get_system_info(self) -> Dict:
        return {
            "ollama_available": self.client.is_available(),
            "models_available": self.client.list_models(),
            "recommended_models": self.client.task_models
        }

llm_manager = LightweightLLMManager()
'''
        
        manager_path = self.project_root / "core/llm/llm_manager.py"
        manager_path.write_text(manager_code)
        print(f"✅ Criado: {manager_path}")
    
    def run_setup(self):
        """Executa setup completo"""
        print("🚀 SETUP COMPLETO DO RSCA - MODELOS LEVES")
        print("=" * 60)
        print(f"🕒 {time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        steps = [
            ("Docker", self.step_1_check_docker),
            ("Containers", self.step_2_setup_containers),
            ("Limpeza", self.step_3_cleanup_models),
            ("Modelos Leves", self.step_4_install_lightweight),
            ("Arquivos", self.step_5_create_files),
            ("Teste", self.step_6_test_system)
        ]
        
        for step_name, step_function in steps:
            try:
                success = step_function()
                if success:
                    self.success_steps.append(step_name)
                    print(f"✅ {step_name} - SUCESSO")
                else:
                    self.failed_steps.append(step_name)
                    print(f"❌ {step_name} - FALHOU")
                    
                    # Parar em falhas críticas
                    if step_name in ["Docker", "Containers"]:
                        print(f"\n🛑 Falha crítica em {step_name} - parando setup")
                        break
                        
            except KeyboardInterrupt:
                print(f"\n⏹️ Setup cancelado pelo usuário")
                return False
            except Exception as e:
                print(f"❌ {step_name} - ERRO: {e}")
                self.failed_steps.append(step_name)
        
        # Resumo final
        self.print_summary()
        return len(self.failed_steps) == 0
    
    def print_summary(self):
        """Mostra resumo final"""
        print("\n" + "=" * 60)
        print("🎯 RESUMO DO SETUP")
        print("=" * 60)
        
        total = len(self.success_steps) + len(self.failed_steps)
        success_rate = (len(self.success_steps) / total * 100) if total > 0 else 0
        
        print(f"📊 Etapas concluídas: {len(self.success_steps)}/{total}")
        print(f"🏆 Taxa de sucesso: {success_rate:.1f}%")
        
        if self.success_steps:
            print(f"\n✅ SUCESSOS:")
            for step in self.success_steps:
                print(f"   • {step}")
        
        if self.failed_steps:
            print(f"\n❌ FALHAS:")
            for step in self.failed_steps:
                print(f"   • {step}")
        
        # Próximos passos
        if success_rate >= 80:
            print(f"\n🎉 SETUP CONCLUÍDO COM SUCESSO!")
            print(f"🚀 Próximos passos:")
            print("   1. Testar: python scripts/tests/test_system.py")
            print("   2. Executar: python core/main.py")
            print("   3. Dashboard: streamlit run interface/dashboard/streamlit_app.py")
        elif success_rate >= 50:
            print(f"\n⚠️ Setup parcialmente concluído")
            print("🔧 Corrija as falhas e execute novamente")
        else:
            print(f"\n❌ Setup falhou")
            print("🆘 Verifique logs e tente novamente")

def main():
    if len(sys.argv) > 1 and sys.argv[1] == "--help":
        print("Setup completo do RSCA com modelos leves")
        print("\nUso: python scripts/config/setup_system.py")
        print("\nEste script:")
        print("  • Verifica Docker")
        print("  • Configura containers") 
        print("  • Remove modelos grandes")
        print("  • Instala modelos leves")
        print("  • Cria arquivos necessários")
        print("  • Testa funcionamento")
        sys.exit(0)
    
    setup = RSCASetup()
    success = setup.run_setup()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
