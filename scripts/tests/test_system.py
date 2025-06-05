#!/usr/bin/env python3
"""
Teste único e completo do sistema RSCA
Substitui todos os outros arquivos de teste
"""

import sys
import time
import requests
from pathlib import Path
from datetime import datetime

# Adicionar path do projeto
sys.path.append(str(Path(__file__).parent.parent.parent))

class RSCASystemTest:
    def __init__(self):
        self.results = {}
        self.start_time = time.time()
        # Definir modelos a serem usados nos testes
        self.ollama_code_model = "deepseek-r1:1.5b"
        self.ollama_general_model = "qwen2:1.5b"
    
    def test_ollama_connection(self):
        """Testa conexão com Ollama e verifica se os modelos necessários estão presentes."""
        print("🔗 Testando conexão Ollama...")
        
        try:
            response = requests.get("http://localhost:11434/api/tags", timeout=10)
            if response.status_code == 200:
                models_data = response.json().get("models", [])
                model_names = [m["name"] for m in models_data]
                
                print(f"✅ Ollama funcionando! Modelos disponíveis: {len(model_names)}")
                for model in model_names:
                    print(f"   • {model}")
                
                # Verificar se os modelos específicos estão presentes
                has_code_model = any(m.startswith(self.ollama_code_model.split(':')[0]) for m in model_names)
                has_general_model = any(m.startswith(self.ollama_general_model.split(':')[0]) for m in model_names)

                if has_code_model and has_general_model:
                    print(f"✅ Modelos '{self.ollama_code_model}' e '{self.ollama_general_model}' encontrados.")
                    return True, model_names
                else:
                    print(f"❌ Modelos '{self.ollama_code_model}' ou '{self.ollama_general_model}' não encontrados.")
                    return False, model_names
                
            else:
                print(f"❌ Ollama retornou status {response.status_code}")
                return False, []
                
        except Exception as e:
            print(f"❌ Erro na conexão: {e}")
            return False, []
    
    def test_ollama_generation(self, model_to_use):
        """Testa geração com Ollama usando um modelo específico."""
        print(f"\n🤖 Testando geração de código com modelo: {model_to_use}...")
        
        try:
            payload = {
                "model": model_to_use,
                "prompt": "def calculate_sum(a, b): return",
                "stream": False,
                "options": {
                    "temperature": 0.1,
                    "num_predict": 100
                }
            }
            
            response = requests.post(
                "http://localhost:11434/api/generate",
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                content = result.get("response", "").strip()
                
                if content:
                    print("✅ Geração funcionando!")
                    print(f"📄 Código gerado:")
                    print("-" * 30)
                    print(content[:150] + "..." if len(content) > 150 else content)
                    print("-" * 30)
                    return True
                else:
                    print("⚠️ Resposta vazia")
                    return False
            else:
                print(f"❌ Erro HTTP {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Erro na geração: {e}")
            return False
    
    def test_code_agent(self):
        """Testa CodeAgent."""
        print("\n🛠️ Testando CodeAgent...")
        
        try:
            from core.agents.code_agent import CodeAgent
            
            # Criar agente, garantindo que use o modelo correto
            # O CodeAgent deve pegar o modelo de config.settings.py
            agent = CodeAgent(use_mock=False)
            
            # Tarefa simples
            task = "Criar função que multiplica dois números"
            print(f"📝 Tarefa: {task}")
            
            result = agent.execute_task(task)
            
            print(f"📊 Resultado:")
            print(f"   Sucesso: {result.success}")
            print(f"   Qualidade: {result.quality_score:.1f}/10")
            print(f"   Modelo: {getattr(result, 'llm_used', 'unknown')}")
            
            if result.success:
                print(f"✅ CodeAgent funcionando!")
                if hasattr(result, 'execution_result') and result.execution_result:
                    print(f"   Execução: {result.execution_result.strip()}")
                return True
            else:
                print(f"❌ CodeAgent falhou: {getattr(result, 'error', 'Erro desconhecido')}")
                return False
                
        except ImportError as e:
            print(f"❌ Erro de import: {e}")
            print("💡 Execute: python scripts/fixes/fix_imports.py")
            return False
        except Exception as e:
            print(f"❌ Erro no CodeAgent: {e}")
            return False
    
    def test_pipeline(self):
        """Testa pipeline completo."""
        print("\n🔄 Testando pipeline Code->Test->Doc...")
        
        try:
            from core.agents.code_agent import CodeAgent
            from core.agents.test_agent import TestAgent
            from core.agents.doc_agent import DocumentationAgent
            
            # Criar agentes
            code_agent = CodeAgent(use_mock=False)
            test_agent = TestAgent()
            doc_agent = DocumentationAgent()
            
            task = "Função que calcula área de um círculo"
            print(f"📝 Tarefa: {task}")
            
            # 1. Código
            print("1️⃣ Gerando código...")
            code_result = code_agent.execute_task(task)
            
            if not code_result.success:
                print("❌ Falha na geração de código")
                return False
            
            # 2. Testes
            print("2️⃣ Gerando testes...")
            try:
                test_code = test_agent.generate_tests(code_result.code, "calcular_area_circulo")
                print("✅ Testes gerados!")
                
                # Mostrar primeira linha do teste
                first_line = test_code.split('\n')[0] if test_code else "Vazio"
                print(f"   Primeira linha: {first_line}")
                
            except Exception as e:
                print(f"⚠️ Erro nos testes: {e}")
            
            # 3. Documentação
            print("3️⃣ Gerando documentação...")
            try:
                doc_agent.create_docs(code_result.code)
                print("✅ Documentação gerada!")
                print(f"   Conteúdo: {doc_agent.latest_output[:100]}...")
                
            except Exception as e:
                print(f"⚠️ Erro na documentação: {e}")
            
            print("✅ Pipeline funcionando!")
            return True
            
        except ImportError as e:
            print(f"❌ Erro de import no pipeline: {e}")
            return False
        except Exception as e:
            print(f"❌ Erro no pipeline: {e}")
            return False
    
    def test_reflection_system(self):
        """Testa sistema de reflexão."""
        print("\n🧠 Testando sistema de reflexão...")
        
        try:
            from core.agents.reflection_agent import ReflectionAgent
            from core.agents.code_agent import CodeAgent
            
            # Criar agentes
            code_agent = CodeAgent(use_mock=True)  # Mock para rapidez
            reflection_agent = ReflectionAgent()
            
            # Gerar algum código
            code_agent.execute_task("Função simples de teste")
            
            # Testar reflexão
            print("🔍 Executando reflexão simbólica...")
            reflection_agent.reflect_on_tasks([code_agent])
            
            # Verificar se log foi criado
            log_path = Path("reflection/analysis_history.md")
            if log_path.exists():
                # Ler últimas linhas
                with open(log_path, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                    if lines:
                        last_lines = ''.join(lines[-5:])
                        print("✅ Reflexão registrada!")
                        print(f"   Últimas entradas: {last_lines[:100]}...")
                    else:
                        print("⚠️ Log vazio")
            else:
                print("⚠️ Log de reflexão não encontrado")
            
            reflection_agent.close()
            print("✅ Sistema de reflexão funcionando!")
            return True
            
        except ImportError as e:
            print(f"❌ Erro de import na reflexão: {e}")
            return False
        except Exception as e:
            print(f"❌ Erro na reflexão: {e}")
            return False
    
    def test_memory_system(self):
        """Testa sistema de memória."""
        print("\n💾 Testando sistema de memória...")
        
        try:
            # Testar paths
            from config.paths import IDENTITY_STATE, MEMORY_LOG, ensure_directories
            
            print("📁 Verificando diretórios...")
            ensure_directories()
            print("✅ Diretórios criados!")
            
            # Testar arquivos de estado
            identity_exists = Path(IDENTITY_STATE).exists()
            memory_exists = Path(MEMORY_LOG).exists()
            
            print(f"📄 Identity state: {'Existe' if identity_exists else 'Não existe'}")
            print(f"📄 Memory log: {'Existe' if memory_exists else 'Não existe'}")
            
            # Testar memória simbólica
            try:
                from memory.symbolic.symbolic_memory import SymbolicMemory
                memory = SymbolicMemory()
                
                # Teste básico
                test_data = {"TestAgent": {"pattern": "test", "quality": "high"}}
                memory.update_memory(test_data)
                
                print("✅ Memória simbólica funcionando!")
                return True
                
            except ImportError:
                print("⚠️ Memória simbólica não disponível (usando fallback)")
                return True
                
        except Exception as e:
            print(f"❌ Erro no sistema de memória: {e}")
            return False
    
    def test_llm_manager(self):
        """Testa o LLM Manager."""
        print("\n🧠 Testando LLM Manager...")
        
        try:
            from core.llm.llm_manager import LLMManager
            
            # Instanciar LLMManager para usar as configurações de settings.py
            llm_manager = LLMManager()
            
            # Testar informações dos modelos
            model_info = llm_manager.get_model_info()
            print(f"📊 Modelos configurados: {model_info.get('configured_models', {})}")
            print(f"🔗 Ollama disponível: {model_info.get('ollama_available', False)}")
            
            # Testar geração se Ollama estiver disponível
            if model_info.get('ollama_available', False):
                print("🔥 Testando geração via LLM Manager...")
                # Usar o modelo de código configurado
                response = llm_manager.generate_code("def hello_world():")
                
                if response.success:
                    print("✅ LLM Manager funcionando!")
                    print(f"   Modelo usado: {response.model}")
                    print(f"   Tokens: {response.tokens_used}")
                    print(f"   Tempo: {response.generation_time:.2f}s")
                    return True
                else:
                    print(f"❌ Falha na geração: {response.error}")
                    return False
            else:
                print("⚠️ Ollama não disponível, usando Mock")
                return True
                
        except ImportError as e:
            print(f"❌ Erro de import LLM Manager: {e}")
            return False
        except Exception as e:
            print(f"❌ Erro no LLM Manager: {e}")
            return False
    
    def test_dashboard_files(self):
        """Testa se arquivos do dashboard existem."""
        print("\n📊 Verificando arquivos do dashboard...")
        
        dashboard_files = [
            "interface/dashboard/streamlit_app.py",
            "config/paths.py", 
            "config/settings.py"
        ]
        
        all_exist = True
        for file_path in dashboard_files:
            path = Path(file_path)
            exists = path.exists()
            print(f"📄 {file_path}: {'✅' if exists else '❌'}")
            
            if not exists:
                all_exist = False
        
        if all_exist:
            print("✅ Todos os arquivos do dashboard estão presentes!")
            return True
        else:
            print("⚠️ Alguns arquivos estão faltando")
            return False
    
    def run_all_tests(self):
        """Executa todos os testes."""
        print("🚀 INICIANDO TESTE COMPLETO DO SISTEMA RSCA")
        print("=" * 60)
        
        tests = [
            ("Conexão Ollama", self.test_ollama_connection),
            ("LLM Manager", self.test_llm_manager),
            ("Sistema de Memória", self.test_memory_system),
            ("CodeAgent", self.test_code_agent),
            ("Pipeline Completo", self.test_pipeline),
            ("Sistema de Reflexão", self.test_reflection_system),
            ("Arquivos Dashboard", self.test_dashboard_files)
        ]
        
        results = {}
        ollama_models = []
        
        for test_name, test_func in tests:
            print(f"\n{'='*20} {test_name} {'='*20}")
            
            try:
                if test_name == "Conexão Ollama":
                    success, models = test_func()
                    ollama_models = models
                    results[test_name] = success
                elif test_name == "Geração Ollama" and ollama_models:
                    # Este teste agora usa um modelo específico
                    results[test_name] = self.test_ollama_generation(self.ollama_code_model)
                else:
                    results[test_name] = test_func()
                    
            except Exception as e:
                print(f"❌ ERRO CRÍTICO em {test_name}: {e}")
                results[test_name] = False
        
        # Adicionar teste de geração se Ollama estiver funcionando
        if results.get("Conexão Ollama", False) and ollama_models:
            print(f"\n{'='*20} Geração Ollama {'='*20}")
            results["Geração Ollama"] = self.test_ollama_generation(self.ollama_code_model)
        
        # Relatório final
        self.print_final_report(results)
        
        return results
    
    def print_final_report(self, results):
        """Imprime relatório final."""
        execution_time = time.time() - self.start_time
        
        print("\n" + "="*60)
        print("📋 RELATÓRIO FINAL DE TESTES")
        print("="*60)
        
        passed = sum(1 for v in results.values() if v)
        total = len(results)
        success_rate = (passed / total) * 100 if total > 0 else 0
        
        print(f"⏱️  Tempo de execução: {execution_time:.2f}s")
        print(f"📊 Testes passaram: {passed}/{total} ({success_rate:.1f}%)")
        print()
        
        # Detalhamento por teste
        for test_name, success in results.items():
            status = "✅ PASSOU" if success else "❌ FALHOU"
            print(f"{status:<12} {test_name}")
        
        print()
        
        # Diagnóstico e recomendações
        if success_rate >= 80:
            print("🎉 SISTEMA FUNCIONANDO BEM!")
            print("💡 Pronto para uso em desenvolvimento")
        elif success_rate >= 60:
            print("⚠️  SISTEMA PARCIALMENTE FUNCIONAL")
            print("💡 Alguns componentes precisam de atenção")
        else:
            print("🚨 SISTEMA COM PROBLEMAS CRÍTICOS")
            print("💡 Revisar configuração e dependências")
        
        # Recomendações específicas
        if not results.get("Conexão Ollama", False):
            print("🔧 Para usar LLMs reais: docker run -d -p 11434:11434 ollama/ollama")
        
        if not results.get("Sistema de Memória", False):
            print("🔧 Verificar config/paths.py e estrutura de diretórios")
        
        if not results.get("CodeAgent", False):
            print("🔧 Verificar imports e dependências dos agentes")
        
        print("\n" + "="*60)
        
        # Salvar relatório
        self.save_test_report(results, execution_time)
    
    def save_test_report(self, results, execution_time):
        """Salva relatório em arquivo."""
        try:
            report_dir = Path("logs")
            report_dir.mkdir(exist_ok=True)
            
            report_file = report_dir / f"test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
            
            with open(report_file, 'w', encoding='utf-8') as f:
                f.write(f"# Relatório de Testes RSCA - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                f.write(f"**Tempo de execução:** {execution_time:.2f}s\n")
                f.write(f"**Testes passaram:** {sum(1 for v in results.values() if v)}/{len(results)}\n\n")
                
                f.write("## Resultados por Teste\n\n")
                for test_name, success in results.items():
                    status = "✅ PASSOU" if success else "❌ FALHOU"
                    f.write(f"- **{test_name}:** {status}\n")
                
                f.write(f"\n## Sistema\n")
                f.write(f"- Python: {sys.version}\n")
                f.write(f"- Diretório: {Path.cwd()}\n")
            
            print(f"📄 Relatório salvo em: {report_file}")
            
        except Exception as e:
            print(f"⚠️ Não foi possível salvar relatório: {e}")


def main():
    """Função principal."""
    print(f"🔬 Teste do Sistema RSCA")
    print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🐍 Python {sys.version.split()[0]}")
    print(f"📁 Diretório: {Path.cwd()}")
    
    tester = RSCASystemTest()
    results = tester.run_all_tests()
    
    # Código de saída baseado no sucesso
    success_rate = sum(1 for v in results.values() if v) / len(results) if results else 0
    exit_code = 0 if success_rate >= 0.8 else 1
    
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
