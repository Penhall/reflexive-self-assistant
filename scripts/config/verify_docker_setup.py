#!/usr/bin/env python3
"""
Script para verificar se o setup Docker + Ollama + Modelos está funcionando
"""

import requests
import json
import time
import subprocess
from datetime import datetime

class DockerSetupVerifier:
    def __init__(self):
        self.ollama_host = "http://localhost:11434"
        self.neo4j_host = "http://localhost:7474"
        self.chromadb_host = "http://localhost:8000"
        
    def check_containers(self):
        """Verifica se containers estão rodando"""
        print("🐳 Verificando containers Docker...")
        
        try:
            result = subprocess.run(['docker', 'ps'], capture_output=True, text=True)
            containers = result.stdout
            
            expected_containers = [
                "rsca-ollama",
                "rsca-neo4j", 
                "rsca-chromadb"
            ]
            
            status = {}
            for container in expected_containers:
                if container in containers:
                    print(f"✅ {container} - Rodando")
                    status[container] = True
                else:
                    print(f"❌ {container} - Não encontrado")
                    status[container] = False
            
            # Verificar container de setup
            if "rsca-ollama-setup" in containers:
                print("🔄 rsca-ollama-setup - Ainda instalando modelos...")
            elif "rsca-ollama-setup" in result.stdout:
                print("✅ rsca-ollama-setup - Instalação de modelos concluída")
            
            return status
            
        except Exception as e:
            print(f"❌ Erro ao verificar containers: {e}")
            return {}
    
    def check_ollama_api(self):
        """Verifica se API do Ollama está respondendo"""
        print(f"\n🤖 Verificando Ollama API ({self.ollama_host})...")
        
        try:
            # Verificar se Ollama está respondendo
            response = requests.get(f"{self.ollama_host}/api/tags", timeout=10)
            
            if response.status_code == 200:
                print("✅ Ollama API está respondendo!")
                
                # Listar modelos instalados
                models_data = response.json()
                models = [model["name"] for model in models_data.get("models", [])]
                
                print(f"📦 Modelos instalados: {len(models)}")
                for model in models:
                    print(f"   • {model}")
                
                # Verificar modelos esperados
                expected_models = ["llama3:8b", "codellama:7b", "codellama:13b"]
                missing_models = [m for m in expected_models if m not in models]
                
                if missing_models:
                    print(f"⚠️ Modelos faltando: {missing_models}")
                    print("💡 Aguarde a instalação automática ou execute:")
                    for model in missing_models:
                        print(f"   docker exec rsca-ollama ollama pull {model}")
                else:
                    print("✅ Todos os modelos esperados estão instalados!")
                
                return True, models
            else:
                print(f"❌ Ollama API retornou status: {response.status_code}")
                return False, []
                
        except requests.exceptions.ConnectionError:
            print("❌ Não foi possível conectar ao Ollama")
            print("💡 Verifique se o container rsca-ollama está rodando")
            return False, []
        except Exception as e:
            print(f"❌ Erro ao verificar Ollama: {e}")
            return False, []
    
    def test_model_generation(self, model="llama3:8b"):
        """Testa geração de texto com um modelo"""
        print(f"\n🧪 Testando geração com {model}...")
        
        try:
            payload = {
                "model": model,
                "prompt": "Responda apenas: 'Funcionando!'",
                "stream": False
            }
            
            response = requests.post(
                f"{self.ollama_host}/api/generate",
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                generated_text = data.get("response", "").strip()
                
                print(f"✅ {model} respondeu: '{generated_text}'")
                return True, generated_text
            else:
                print(f"❌ Erro na geração: {response.status_code}")
                return False, ""
                
        except Exception as e:
            print(f"❌ Erro ao testar modelo: {e}")
            return False, ""
    
    def check_neo4j(self):
        """Verifica conexão com Neo4j"""
        print(f"\n🗃️ Verificando Neo4j ({self.neo4j_host})...")
        
        try:
            response = requests.get(self.neo4j_host, timeout=10)
            if response.status_code == 200:
                print("✅ Neo4j está acessível!")
                return True
            else:
                print(f"⚠️ Neo4j retornou status: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Erro ao conectar Neo4j: {e}")
            return False
    
    def check_chromadb(self):
        """Verifica conexão com ChromaDB"""
        print(f"\n🔍 Verificando ChromaDB ({self.chromadb_host})...")
        
        try:
            response = requests.get(f"{self.chromadb_host}/api/v1/heartbeat", timeout=10)
            if response.status_code == 200:
                print("✅ ChromaDB está acessível!")
                return True
            else:
                print(f"⚠️ ChromaDB retornou status: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Erro ao conectar ChromaDB: {e}")
            return False
    
    def test_integration(self):
        """Testa integração completa"""
        print(f"\n🔗 Testando integração completa...")
        
        try:
            # Importar e testar LLM client
            import sys
            from pathlib import Path
            sys.path.append(str(Path(__file__).parent.parent))
            
            from core.llm.ollama_client import OllamaClient
            
            client = OllamaClient()
            
            if client.is_available():
                print("✅ Cliente Ollama conectado!")
                
                # Testar geração
                response = client.generate("llama3:8b", "def hello():")
                if response.success:
                    print("✅ Geração via cliente funcionando!")
                    print(f"📝 Resposta: {response.content[:100]}...")
                else:
                    print(f"❌ Erro na geração: {response.error}")
                
                return True
            else:
                print("❌ Cliente Ollama não conseguiu conectar")
                return False
                
        except ImportError as e:
            print(f"⚠️ Módulo não encontrado: {e}")
            print("💡 Implemente primeiro: core/llm/ollama_client.py")
            return False
        except Exception as e:
            print(f"❌ Erro na integração: {e}")
            return False
    
    def generate_report(self):
        """Gera relatório completo do setup"""
        print("\n" + "="*60)
        print("📋 RELATÓRIO COMPLETO DO SETUP")
        print("="*60)
        
        # Verificar tudo
        containers_status = self.check_containers()
        ollama_ok, models = self.check_ollama_api()
        neo4j_ok = self.check_neo4j()
        chromadb_ok = self.check_chromadb()
        
        # Testar modelos se disponíveis
        model_tests = {}
        if ollama_ok and models:
            for model in ["llama3:8b", "codellama:7b"]:
                if model in models:
                    success, response = self.test_model_generation(model)
                    model_tests[model] = success
        
        # Testar integração
        integration_ok = self.test_integration()
        
        # Resumo final
        print(f"\n🎯 RESUMO FINAL")
        print("-" * 30)
        
        total_checks = 0
        passed_checks = 0
        
        # Containers
        for container, status in containers_status.items():
            total_checks += 1
            if status:
                passed_checks += 1
        
        # Serviços
        services = [
            ("Ollama API", ollama_ok),
            ("Neo4j", neo4j_ok), 
            ("ChromaDB", chromadb_ok),
            ("Integração", integration_ok)
        ]
        
        for service, status in services:
            total_checks += 1
            if status:
                passed_checks += 1
            print(f"{'✅' if status else '❌'} {service}")
        
        # Modelos
        if model_tests:
            for model, status in model_tests.items():
                total_checks += 1
                if status:
                    passed_checks += 1
                print(f"{'✅' if status else '❌'} {model}")
        
        # Score final
        score = (passed_checks / total_checks) * 100 if total_checks > 0 else 0
        print(f"\n📊 Score: {passed_checks}/{total_checks} ({score:.1f}%)")
        
        if score >= 80:
            print("🎉 Setup está funcionando bem!")
            print("🚀 Próximo passo: python scripts/test_llm_integration.py")
        elif score >= 60:
            print("⚠️ Setup parcialmente funcional")
            print("🔧 Verifique os itens com ❌ acima")
        else:
            print("❌ Setup precisa de correções")
            print("🆘 Verifique logs do Docker: docker-compose logs")
        
        return score

def main():
    print("🔍 VERIFICAÇÃO DO SETUP DOCKER + OLLAMA")
    print("="*50)
    print(f"🕒 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    verifier = DockerSetupVerifier()
    score = verifier.generate_report()
    
    print(f"\n📋 Verificação concluída com score: {score:.1f}%")

if __name__ == "__main__":
    main()