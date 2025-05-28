#!/usr/bin/env python3
"""
Teste rápido do sistema RSCA para desenvolvimento
Foca apenas nos componentes essenciais - execução em <30s
"""

import sys
import time
import requests
from pathlib import Path
from datetime import datetime

# Adicionar path do projeto
sys.path.append(str(Path(__file__).parent.parent.parent))

class QuickTest:
    def __init__(self):
        self.start_time = time.time()
        self.tests_run = 0
        self.tests_passed = 0
        
    def test_ollama_basic(self):
        """Teste básico do Ollama (5s timeout)"""
        print("🔗 Ollama...", end=" ", flush=True)
        
        try:
            response = requests.get("http://localhost:11434/api/tags", timeout=5)
            if response.status_code == 200:
                models = response.json().get("models", [])
                print(f"✅ ({len(models)} modelos)")
                return True
            else:
                print(f"❌ HTTP {response.status_code}")
                return False
        except:
            print("❌ Não disponível")
            return False
    
    def test_imports(self):
        """Teste de imports críticos"""
        print("📦 Imports...", end=" ", flush=True)
        
        try:
            # Imports essenciais
            from config.paths import PROJECT_ROOT, ensure_directories
            from core.llm.ollama_client import ollama_client
            
            print("✅")
            return True
        except ImportError as e:
            print(f"❌ {e}")
            return False
        except Exception as e:
            print(f"❌ {e}")
            return False
    
    def test_directories(self):
        """Teste de estrutura de diretórios"""
        print("📁 Diretórios...", end=" ", flush=True)
        
        try:
            from config.paths import ensure_directories
            ensure_directories()
            print("✅")
            return True
        except Exception as e:
            print(f"❌ {e}")
            return False
    
    def test_agents_basic(self):
        """Teste básico dos agentes"""
        print("🤖 Agentes...", end=" ", flush=True)
        
        try:
            from core.agents.code_agent import CodeAgent
            
            # Teste básico com LLM real
            agent = CodeAgent()
            result = agent.execute_task("crie uma função que retorna 'Hello World'")
            
            if result.success:
                print("✅")
                return True
            else:
                print(f"⚠️ {result.error}")
                return False
                
        except ImportError as e:
            print(f"❌ Import: {e}")
            return False
        except Exception as e:
            print(f"❌ {e}")
            return False
    
    def test_llm_manager(self):
        """Teste do LLM Manager"""
        print("🧠 LLM Manager...", end=" ", flush=True)
        
        try:
            from core.llm.ollama_client import llm_manager
            
            # Verificar se está configurado
            status = llm_manager.get_system_status()
            
            if status and "ready" in status:
                print("✅")
                return True
            else:
                print("⚠️ Não configurado")
                return False
                
        except ImportError as e:
            print(f"❌ Import: {e}")
            return False
        except Exception as e:
            print(f"❌ {e}")
            return False
    
    def test_generation_quick(self):
        """Teste rápido de geração (apenas se Ollama disponível)"""
        print("⚡ Geração...", end=" ", flush=True)
        
        try:
            # Verificar se Ollama está disponível primeiro
            response = requests.get("http://localhost:11434/api/tags", timeout=3)
            if response.status_code != 200:
                print("➖ Ollama indisponível")
                return True  # Não é falha crítica
            
            models = response.json().get("models", [])
            if not models:
                print("➖ Sem modelos")
                return True  # Não é falha crítica
            
            # Teste rápido com modelo mais leve
            model = models[0]["name"]
            
            test_payload = {
                "model": model,
                "prompt": "def hello():",
                "stream": False,
                "options": {"num_predict": 20}  # Muito pouco para ser rápido
            }
            
            response = requests.post(
                "http://localhost:11434/api/generate",
                json=test_payload,
                timeout=10  # Timeout baixo
            )
            
            if response.status_code == 200:
                data = response.json()
                content = data.get("response", "").strip()
                if content:
                    print("✅")
                    return True
                else:
                    print("⚠️ Resposta vazia")
                    return False
            else:
                print(f"❌ HTTP {response.status_code}")
                return False
                
        except requests.exceptions.Timeout:
            print("⏰ Timeout")
            return False
        except Exception as e:
            print(f"❌ {e}")
            return False
    
    def test_memory_basic(self):
        """Teste básico do sistema de memória"""
        print("💾 Memória...", end=" ", flush=True)
        
        try:
            from config.paths import IDENTITY_STATE, LOGS_DIR
            
            # Verificar se paths estão funcionando
            identity_dir = IDENTITY_STATE.parent
            if identity_dir.exists() or LOGS_DIR.exists():
                print("✅")
                return True
            else:
                print("❌ Diretórios não criados")
                return False
                
        except Exception as e:
            print(f"❌ {e}")
            return False
    
    def run_quick_tests(self):
        """Executa todos os testes rápidos"""
        print("⚡ TESTE RÁPIDO - RSCA")
        print("=" * 25)
        print(f"🕒 {datetime.now().strftime('%H:%M:%S')}")
        print()
        
        # Lista de testes (nome, função, crítico)
        tests = [
            ("Imports", self.test_imports, True),
            ("Diretórios", self.test_directories, True),
            ("Ollama", self.test_ollama_basic, False),
            ("Agentes", self.test_agents_basic, True),
            ("LLM Manager", self.test_llm_manager, True),
            ("Memória", self.test_memory_basic, True),
            ("Geração", self.test_generation_quick, False)
        ]
        
        critical_failures = []
        
        for test_name, test_func, is_critical in tests:
            self.tests_run += 1
            
            try:
                if test_func():
                    self.tests_passed += 1
                else:
                    if is_critical:
                        critical_failures.append(test_name)
            except Exception as e:
                print(f"💥 {test_name}: ERRO - {e}")
                if is_critical:
                    critical_failures.append(test_name)
        
        # Resultado final
        execution_time = time.time() - self.start_time
        success_rate = (self.tests_passed / self.tests_run * 100) if self.tests_run > 0 else 0
        
        print()
        print("-" * 25)
        print(f"⏱️  {execution_time:.1f}s")
        print(f"📊 {self.tests_passed}/{self.tests_run} ({success_rate:.0f}%)")
        
        # Status final
        if critical_failures:
            print(f"🚨 FALHAS CRÍTICAS: {', '.join(critical_failures)}")
            print("💡 Execute: python scripts/fixes/fix_imports.py")
            return False
        elif success_rate >= 80:
            print("✅ SISTEMA OK")
            if success_rate < 100:
                print("💡 Algumas funcionalidades opcionais indisponíveis")
            return True
        else:
            print("⚠️ PROBLEMAS DETECTADOS")
            print("💡 Execute teste completo: python scripts/tests/test_system.py")
            return False

class DevQuickCheck:
    """Versão ainda mais rápida para desenvolvimento contínuo"""
    
    def __init__(self):
        self.start_time = time.time()
    
    def check_essentials(self):
        """Verifica apenas o essencial em <10s"""
        print("⚡ Quick Check...", end=" ")
        
        try:
            # Import crítico
            from config.paths import PROJECT_ROOT
            from core.agents.code_agent import CodeAgent
            
            # Teste básico de agente
            agent = CodeAgent(timeout=3)  # Timeout reduzido para teste rápido
            result = agent.execute_task("test")
            
            # Ollama (sem timeout longo)
            try:
                response = requests.get("http://localhost:11434/api/tags", timeout=2)
                ollama_ok = response.status_code == 200
            except:
                ollama_ok = False
            
            execution_time = time.time() - self.start_time
            
            if result.success:
                status = "✅" if ollama_ok else "⚠️"
                print(f"{status} ({execution_time:.1f}s)")
                return True
            else:
                print(f"❌ ({execution_time:.1f}s)")
                return False
                
        except Exception as e:
            execution_time = time.time() - self.start_time
            print(f"💥 ({execution_time:.1f}s) - {e}")
            return False

def main():
    if len(sys.argv) > 1:
        if sys.argv[1] == "--help":
            print("Teste rápido do sistema RSCA para desenvolvimento")
            print("\nUso: python scripts/tests/test_quick.py [opção]")
            print("\nOpções:")
            print("  --help        Mostra esta ajuda")
            print("  --dev         Modo ultra-rápido (<10s)")
            print("  --full        Modo completo (~30s) [padrão]")
            print("\nEste script:")
            print("  • Verifica componentes essenciais rapidamente")
            print("  • Ideal para desenvolvimento contínuo")
            print("  • Detecta problemas críticos sem demora")
            print("\nPara teste completo use: python scripts/tests/test_system.py")
            sys.exit(0)
        elif sys.argv[1] == "--dev":
            # Modo ultra-rápido
            checker = DevQuickCheck()
            success = checker.check_essentials()
            sys.exit(0 if success else 1)
    
    # Modo padrão (completo mas rápido)
    tester = QuickTest()
    success = tester.run_quick_tests()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
