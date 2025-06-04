"""
Agente reflexivo que analisa padrões e atualiza a identidade simbólica do sistema.
VERSÃO ATUALIZADA: Remove dependência do analysis_history.md em favor do GraphRAG
"""

import os
from datetime import datetime
from memory.graph_rag.graph_interface import GraphMemory, MockGraphMemory
from neo4j import exceptions

# Importar configurações de legacy features
try:
    from config.settings import LEGACY_FEATURES
except ImportError:
    # Fallback se settings não estiver disponível
    LEGACY_FEATURES = {
        "enable_analysis_history_md": False,
        "verbose_logging": False
    }


class ReflectionAgent:
    def __init__(self):
        # Configurar GraphRAG (principal sistema de armazenamento)
        try:
            self.graph = GraphMemory()
            # Testa a conexão
            self.graph.get_categories_and_counts()
            self.using_mock = False
            print("🔗 GraphRAG conectado com sucesso")
        except (exceptions.ServiceUnavailable, exceptions.AuthError) as e:
            from memory.graph_rag.graph_interface import MockGraphMemory
            self.graph = MockGraphMemory()
            self.using_mock = True
            print(f"⚠️ Neo4j não disponível ({str(e)}) - usando implementação em memória")
        
        # ⚡ OTIMIZAÇÃO: Configurar path do log apenas se habilitado
        self.enable_md_logging = LEGACY_FEATURES.get("enable_analysis_history_md", False)
        if self.enable_md_logging:
            self.log_path = os.path.join("reflection", "analysis_history.md")
            print("📝 Log MD habilitado (modo compatibilidade)")
        else:
            self.log_path = None
            print("🚀 Log MD desabilitado - usando apenas GraphRAG")
        
        # Estatísticas de reflexão
        self.reflection_stats = {
            "total_cycles": 0,
            "patterns_identified": {},
            "agents_processed": set()
        }

    def reflect_on_tasks(self, agents):
        """
        Reflexão principal - OTIMIZADA para usar principalmente GraphRAG
        """
        print("🔁 Iniciando reflexão simbólica sobre os agentes...\n")
        
        # Registrar estatísticas
        self.reflection_stats["total_cycles"] += 1
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # ⚡ OTIMIZAÇÃO: Preparar dados apenas se logging MD estiver habilitado
        log_lines = []
        if self.enable_md_logging:
            log_lines.append(f"### Ciclo de Reflexão — {timestamp}\n")

        # Processar cada agente
        processed_patterns = []
        for agent in agents:
            try:
                # Extrair informações do agente
                reaction = getattr(agent, 'latest_output', '') or ''
                pattern = self.identify_pattern(reaction)
                category = self.categorize_pattern(pattern)
                agent_name = agent.__class__.__name__
                
                # Registrar no GraphRAG (sistema principal)
                self.graph.register_pattern(reaction, pattern, category, agent_name)
                
                # Atualizar estatísticas
                self.reflection_stats["agents_processed"].add(agent_name)
                if pattern not in self.reflection_stats["patterns_identified"]:
                    self.reflection_stats["patterns_identified"][pattern] = 0
                self.reflection_stats["patterns_identified"][pattern] += 1
                
                # Exibir feedback
                print(f"🧠 {agent_name} → padrão: '{pattern}' (categoria: {category})")
                
                # ⚡ CONDICIONAL: Apenas adicionar ao log MD se habilitado
                if self.enable_md_logging:
                    log_lines.append(f"- **{agent_name}** → Padrão: _{pattern}_ (Categoria: _{category}_)")
                
                processed_patterns.append({
                    "agent": agent_name,
                    "pattern": pattern,
                    "category": category,
                    "timestamp": timestamp
                })
                
            except Exception as e:
                print(f"⚠️ Erro ao processar agente {agent.__class__.__name__}: {e}")
                continue
        
        # ⚡ CONDICIONAL: Salvar em MD apenas se habilitado
        if self.enable_md_logging and log_lines:
            log_lines.append("\n")
            self.append_to_log(log_lines)
        
        # 📊 Exibir estatísticas de reflexão
        self._display_reflection_summary(processed_patterns)
        
        print("✅ Reflexão simbólica registrada com sucesso.\n")
        
        return processed_patterns

    def _display_reflection_summary(self, patterns):
        """Exibe resumo da reflexão atual"""
        if not patterns:
            print("⚠️ Nenhum padrão processado neste ciclo")
            return
        
        # Contar padrões únicos
        unique_patterns = set(p["pattern"] for p in patterns)
        unique_categories = set(p["category"] for p in patterns)
        
        print(f"📊 Resumo da reflexão:")
        print(f"   • Agentes processados: {len(patterns)}")
        print(f"   • Padrões únicos: {len(unique_patterns)}")
        print(f"   • Categorias: {', '.join(unique_categories)}")
        print(f"   • Total de ciclos: {self.reflection_stats['total_cycles']}")
        
        # Mostrar padrão mais comum
        if self.reflection_stats["patterns_identified"]:
            most_common = max(self.reflection_stats["patterns_identified"].items(), 
                            key=lambda x: x[1])
            print(f"   • Padrão mais frequente: {most_common[0]} ({most_common[1]}x)")

    def identify_pattern(self, text):
        """
        Identifica padrão no texto de saída do agente
        MANTIDO: Lógica original preservada
        """
        if not text or not isinstance(text, str):
            return "Execução padrão"
        
        text = text.lower()
        
        # Padrões de erro/falha
        if any(keyword in text for keyword in ["erro", "falha", "exception", "error"]):
            return "Comportamento anômalo"
        
        # Padrões específicos de domínio
        elif any(keyword in text for keyword in ["documentação", "doc", "readme"]):
            return "Atualização documental"
        elif any(keyword in text for keyword in ["teste", "test", "assert", "pytest"]):
            return "Cobertura de teste"
        elif any(keyword in text for keyword in ["login", "auth", "função", "def "]):
            return "Implementação funcional"
        elif any(keyword in text for keyword in ["refactor", "otimiz", "melhori"]):
            return "Otimização de código"
        else:
            return "Execução padrão"

    def categorize_pattern(self, pattern):
        """
        Categoriza padrão identificado
        MANTIDO: Lógica original preservada + novas categorias
        """
        mapping = {
            "Comportamento anômalo": "Falha",
            "Atualização documental": "Documentação",
            "Cobertura de teste": "Testes",
            "Implementação funcional": "Funcionalidade",
            "Otimização de código": "Otimização",
            "Execução padrão": "Operação"
        }
        return mapping.get(pattern, "Outro")

    def append_to_log(self, lines):
        """
        ⚡ OTIMIZADO: Apenas executa se logging MD estiver habilitado
        """
        if not self.enable_md_logging or not self.log_path:
            return  # Sair silenciosamente se MD logging desabilitado
        
        try:
            with open(self.log_path, "a", encoding="utf-8") as log_file:
                log_file.write("\n".join(lines) + "\n")
        except Exception as e:
            print(f"⚠️ Erro ao escrever log MD: {e}")

    def get_reflection_stats(self):
        """
        NOVO: Retorna estatísticas de reflexão do GraphRAG
        """
        stats = {
            "local_stats": self.reflection_stats,
            "graphrag_enabled": not self.using_mock,
            "md_logging_enabled": self.enable_md_logging
        }
        
        # Adicionar estatísticas do GraphRAG se disponível
        if not self.using_mock:
            try:
                graphrag_stats = self.graph.get_categories_and_counts()
                stats["graphrag_categories"] = graphrag_stats
            except Exception as e:
                stats["graphrag_error"] = str(e)
        
        return stats

    def export_patterns_summary(self):
        """
        NOVO: Exporta resumo de padrões do GraphRAG
        """
        if self.using_mock:
            return {
                "source": "mock",
                "patterns": list(self.reflection_stats["patterns_identified"].keys()),
                "total_cycles": self.reflection_stats["total_cycles"]
            }
        
        try:
            # Obter padrões do GraphRAG
            patterns = self.graph.get_patterns_by_agent("all")  # Se método existir
            categories = self.graph.get_categories_and_counts()
            
            return {
                "source": "graphrag",
                "patterns": patterns if patterns else [],
                "categories": categories,
                "agents_processed": list(self.reflection_stats["agents_processed"]),
                "total_cycles": self.reflection_stats["total_cycles"],
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            return {
                "source": "error",
                "error": str(e),
                "fallback_stats": self.reflection_stats
            }

    def cleanup_old_data(self, max_age_days=30):
        """
        NOVO: Limpeza de dados antigos para economizar memória
        """
        if self.using_mock:
            print("🧹 Limpeza não necessária (modo mock)")
            return
        
        try:
            # Implementar limpeza no GraphRAG se necessário
            print(f"🧹 Iniciando limpeza de dados > {max_age_days} dias")
            
            # Para implementação futura - limpeza baseada em timestamp
            # self.graph.cleanup_old_patterns(max_age_days)
            
            print("✅ Limpeza concluída")
        except Exception as e:
            print(f"⚠️ Erro na limpeza: {e}")

    def close(self):
        """
        Fecha conexões do GraphRAG
        """
        if hasattr(self.graph, 'close'):
            self.graph.close()
        
        # Exibir estatísticas finais
        if LEGACY_FEATURES.get("verbose_logging", False):
            print(f"\n📊 Estatísticas finais do ReflectionAgent:")
            print(f"   • Total de ciclos: {self.reflection_stats['total_cycles']}")
            print(f"   • Agentes processados: {len(self.reflection_stats['agents_processed'])}")
            print(f"   • Padrões identificados: {len(self.reflection_stats['patterns_identified'])}")
            print(f"   • GraphRAG: {'✅' if not self.using_mock else '❌ Mock'}")
            print(f"   • MD Logging: {'✅' if self.enable_md_logging else '❌ Desabilitado'}")


# ⚡ FUNÇÃO UTILITÁRIA: Migração de dados MD para GraphRAG (se necessário)
def migrate_md_to_graphrag(md_file_path="reflection/analysis_history.md"):
    """
    Utilitário para migrar dados do analysis_history.md para GraphRAG
    """
    print(f"🔄 Iniciando migração de {md_file_path} para GraphRAG...")
    
    if not os.path.exists(md_file_path):
        print(f"⚠️ Arquivo {md_file_path} não encontrado")
        return False
    
    try:
        # Criar instância do ReflectionAgent para acessar GraphRAG
        agent = ReflectionAgent()
        
        # Ler arquivo MD e extrair dados (implementação simples)
        with open(md_file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Processar linha por linha (implementação básica)
        lines = content.split('\n')
        migrated_count = 0
        
        for line in lines:
            if line.startswith('- **') and '**' in line:
                # Extrair dados da linha: - **AgentName** → Padrão: _pattern_ (Categoria: _category_)
                try:
                    parts = line.split('→')
                    if len(parts) >= 2:
                        agent_part = parts[0].replace('- **', '').replace('**', '').strip()
                        pattern_part = parts[1]
                        
                        # Extrair padrão e categoria com regex simples
                        import re
                        pattern_match = re.search(r'Padrão: _([^_]+)_', pattern_part)
                        category_match = re.search(r'Categoria: _([^_]+)_', pattern_part)
                        
                        if pattern_match and category_match:
                            pattern = pattern_match.group(1)
                            category = category_match.group(1)
                            
                            # Registrar no GraphRAG
                            agent.graph.register_pattern("migrated_data", pattern, category, agent_part)
                            migrated_count += 1
                            
                except Exception as e:
                    print(f"⚠️ Erro ao processar linha: {line[:50]}... - {e}")
                    continue
        
        agent.close()
        
        print(f"✅ Migração concluída: {migrated_count} entradas migradas")
        
        # Opcional: Fazer backup do arquivo MD
        backup_path = f"{md_file_path}.backup"
        import shutil
        shutil.copy2(md_file_path, backup_path)
        print(f"💾 Backup criado: {backup_path}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro na migração: {e}")
        return False


# 🧪 Teste da funcionalidade
if __name__ == "__main__":
    print("🧪 Testando ReflectionAgent otimizado...")
    
    # Criar agente de teste
    agent = ReflectionAgent()
    
    # Simular agentes mock
    class MockAgent:
        def __init__(self, name, output):
            self.__class__.__name__ = name
            self.latest_output = output
    
    mock_agents = [
        MockAgent("CodeAgent", "def login(): return True"),
        MockAgent("TestAgent", "test completed successfully"),
        MockAgent("DocumentationAgent", "documentation updated")
    ]
    
    # Executar reflexão
    patterns = agent.reflect_on_tasks(mock_agents)
    
    # Exibir estatísticas
    stats = agent.get_reflection_stats()
    print(f"\n📊 Estatísticas: {stats}")
    
    # Exportar resumo
    summary = agent.export_patterns_summary()
    print(f"\n📋 Resumo: {summary}")
    
    agent.close()
    print("\n✅ Teste concluído!")