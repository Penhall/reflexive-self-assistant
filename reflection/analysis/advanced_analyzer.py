"""
Sistema de Reflexão Simbólica Avançada com GraphRAG
"""

import yaml
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from memory.graph_rag.experience_store import ExperienceGraphRAG

@dataclass
class ReflectionInsight:
    type: str  # "pattern", "improvement", "anomaly", "opportunity"
    description: str
    evidence: List[str]
    confidence: float
    recommendations: List[str]
    timestamp: str

class AdvancedSymbolicAnalyzer:
    """Analisador simbólico que usa GraphRAG para insights profundos"""
    
    def __init__(self):
        self.graph_rag = ExperienceGraphRAG()
        self.insights_history = []
        
    def deep_analyze_agent_evolution(self, agent_name: str) -> List[ReflectionInsight]:
        """Análise profunda da evolução de um agente"""
        
        insights = []
        
        # 1. Análise de performance temporal
        performance_insight = self._analyze_performance_trends(agent_name)
        if performance_insight:
            insights.append(performance_insight)
        
        # 2. Análise de padrões emergentes
        pattern_insights = self._discover_behavioral_patterns(agent_name)
        insights.extend(pattern_insights)
        
        # 3. Identificação de lacunas
        gap_insights = self._identify_knowledge_gaps(agent_name)
        insights.extend(gap_insights)
        
        # 4. Oportunidades de especialização
        specialization_insight = self._identify_specialization_opportunities(agent_name)
        if specialization_insight:
            insights.append(specialization_insight)
        
        return insights
    
    def _analyze_performance_trends(self, agent_name: str) -> Optional[ReflectionInsight]:
        """Analisa tendências de performance ao longo do tempo"""
        
        performance_data = self.graph_rag.get_agent_performance(agent_name)
        
        if performance_data["total_experiences"] < 5:
            return None
        
        # Analisar experiências recentes vs antigas
        with self.graph_rag.driver.session() as session:
            query = """
                MATCH (e:Experience {agent_type: $agent_name})
                WITH e ORDER BY e.timestamp
                WITH collect(e) as experiences
                WITH experiences[..size(experiences)/2] as old_half,
                     experiences[size(experiences)/2..] as new_half
                
                UNWIND old_half as old_exp
                WITH avg(old_exp.quality_score) as old_avg, new_half
                
                UNWIND new_half as new_exp  
                WITH old_avg, avg(new_exp.quality_score) as new_avg
                
                RETURN old_avg, new_avg, new_avg - old_avg as improvement
            """
            
            result = session.run(query, agent_name=agent_name)
            record = result.single()
            
            if record:
                improvement = record["improvement"]
                confidence = min(abs(improvement) * 10, 0.95)
                
                if improvement > 0.5:
                    return ReflectionInsight(
                        type="improvement",
                        description=f"{agent_name} mostra evolução positiva significativa",
                        evidence=[
                            f"Qualidade antiga: {record['old_avg']:.2f}",
                            f"Qualidade recente: {record['new_avg']:.2f}",
                            f"Melhoria: +{improvement:.2f} pontos"
                        ],
                        confidence=confidence,
                        recommendations=[
                            "Continuar estratégias atuais",
                            "Documentar padrões que levaram à melhoria",
                            "Aplicar aprendizados a outros agentes"
                        ],
                        timestamp=datetime.now().isoformat()
                    )
                elif improvement < -0.5:
                    return ReflectionInsight(
                        type="anomaly",
                        description=f"{agent_name} mostra degradação de performance",
                        evidence=[
                            f"Qualidade antiga: {record['old_avg']:.2f}",
                            f"Qualidade recente: {record['new_avg']:.2f}",
                            f"Declínio: {improvement:.2f} pontos"
                        ],
                        confidence=confidence,
                        recommendations=[
                            "Investigar causas da degradação",
                            "Revisar mudanças recentes nos prompts",
                            "Considerar reset para checkpoint anterior"
                        ],
                        timestamp=datetime.now().isoformat()
                    )
        
        return None
    
    def _discover_behavioral_patterns(self, agent_name: str) -> List[ReflectionInsight]:
        """Descobre padrões comportamentais emergentes"""
        
        insights = []
        patterns = self.graph_rag.discover_patterns(min_frequency=3)
        
        # Filtrar padrões do agente específico
        agent_patterns = []
        with self.graph_rag.driver.session() as session:
            for pattern in patterns:
                query = """
                    MATCH (p:Pattern {name: $pattern_name})<-[:EXHIBITS]-(e:Experience {agent_type: $agent_name})
                    RETURN count(e) as occurrences
                """
                result = session.run(query, pattern_name=pattern["pattern"], agent_name=agent_name)
                record = result.single()
                
                if record and record["occurrences"] > 0:
                    pattern["agent_occurrences"] = record["occurrences"]
                    agent_patterns.append(pattern)
        
        # Identificar padrões dominantes
        if agent_patterns:
            dominant_pattern = max(agent_patterns, key=lambda x: x["avg_quality"])
            
            insights.append(ReflectionInsight(
                type="pattern",
                description=f"Padrão dominante identificado: {dominant_pattern['pattern']}",
                evidence=[
                    f"Frequência: {dominant_pattern['frequency']} experiências",
                    f"Qualidade média: {dominant_pattern['avg_quality']:.2f}",
                    f"Ocorrências no agente: {dominant_pattern['agent_occurrences']}"
                ],
                confidence=min(dominant_pattern["frequency"] / 10, 0.9),
                recommendations=[
                    f"Reforçar uso do padrão '{dominant_pattern['pattern']}'",
                    "Documentar como template para reutilização",
                    "Ensinar padrão a outros agentes similares"
                ],
                timestamp=datetime.now().isoformat()
            ))
        
        return insights
    
    def _identify_knowledge_gaps(self, agent_name: str) -> List[ReflectionInsight]:
        """Identifica lacunas de conhecimento específicas do agente"""
        
        insights = []
        
        # Categorias comuns de tarefas de código
        task_categories = [
            "validação", "autenticação", "banco de dados", "API", 
            "algoritmo", "estrutura de dados", "teste", "logging",
            "cache", "performance", "segurança", "concorrência"
        ]
        
        gaps = []
        with self.graph_rag.driver.session() as session:
            for category in task_categories:
                query = """
                    MATCH (e:Experience {agent_type: $agent_name})
                    WHERE toLower(e.task) CONTAINS $category
                    RETURN count(e) as count,
                           avg(e.quality_score) as avg_quality,
                           sum(case when e.success then 1 else 0 end) * 100.0 / count(e) as success_rate
                """
                
                result = session.run(query, agent_name=agent_name, category=category)
                record = result.single()
                
                if record:
                    count = record["count"] or 0
                    avg_quality = record["avg_quality"] or 0
                    success_rate = record["success_rate"] or 0
                    
                    # Identificar lacunas significativas
                    if count < 2 or avg_quality < 6.0 or success_rate < 70:
                        gaps.append({
                            "category": category,
                            "count": count,
                            "avg_quality": avg_quality,
                            "success_rate": success_rate
                        })
        
        if gaps:
            # Priorizar lacunas mais críticas
            critical_gaps = sorted(gaps, key=lambda x: x["count"] + x["avg_quality"] / 10)[:3]
            
            for gap in critical_gaps:
                insights.append(ReflectionInsight(
                    type="opportunity",
                    description=f"Lacuna de conhecimento identificada: {gap['category']}",
                    evidence=[
                        f"Experiências: {gap['count']}",
                        f"Qualidade média: {gap['avg_quality']:.2f}",
                        f"Taxa de sucesso: {gap['success_rate']:.1f}%"
                    ],
                    confidence=0.8,
                    recommendations=[
                        f"Criar tarefas de treinamento específicas para '{gap['category']}'",
                        f"Estudar padrões bem-sucedidos de outros agentes nesta área",
                        f"Implementar templates específicos para '{gap['category']}'"
                    ],
                    timestamp=datetime.now().isoformat()
                ))
        
        return insights
    
    def _identify_specialization_opportunities(self, agent_name: str) -> Optional[ReflectionInsight]:
        """Identifica oportunidades de especialização"""
        
        performance_data = self.graph_rag.get_agent_performance(agent_name)
        
        if performance_data["total_experiences"] < 10:
            return None
        
        # Analisar distribuição de qualidade por categoria
        specialization_scores = {}
        
        with self.graph_rag.driver.session() as session:
            # Categorias para análise
            categories = ["API", "algoritmo", "validação", "banco de dados", "interface"]
            
            for category in categories:
                query = """
                    MATCH (e:Experience {agent_type: $agent_name})
                    WHERE toLower(e.task) CONTAINS $category
                    AND e.success = true
                    RETURN avg(e.quality_score) as avg_quality,
                           count(e) as count
                """
                
                result = session.run(query, agent_name=agent_name, category=category)
                record = result.single()
                
                if record and record["count"] >= 3:
                    quality = record["avg_quality"]
                    count = record["count"]
                    
                    # Score baseado em qualidade e experiência
                    specialization_scores[category] = quality * (1 + count / 20)
        
        if specialization_scores:
            best_category = max(specialization_scores, key=specialization_scores.get)
            best_score = specialization_scores[best_category]
            
            if best_score > 8.0:  # Alta qualidade consistente
                return ReflectionInsight(
                    type="opportunity",
                    description=f"Oportunidade de especialização identificada: {best_category}",
                    evidence=[
                        f"Score de especialização: {best_score:.2f}",
                        f"Categoria com melhor performance: {best_category}",
                        f"Performance superior a outras categorias"
                    ],
                    confidence=0.85,
                    recommendations=[
                        f"Focar treinamento em tarefas de '{best_category}'",
                        f"Criar checkpoint especializado para '{best_category}'",
                        f"Desenvolver templates específicos desta área",
                        f"Compartilhar expertise de '{best_category}' com outros agentes"
                    ],
                    timestamp=datetime.now().isoformat()
                )
        
        return None
    
    def generate_evolution_strategy(self, agent_name: str) -> Dict[str, Any]:
        """Gera estratégia de evolução baseada nos insights"""
        
        insights = self.deep_analyze_agent_evolution(agent_name)
        
        strategy = {
            "agent_name": agent_name,
            "timestamp": datetime.now().isoformat(),
            "insights_analyzed": len(insights),
            "priorities": [],
            "training_focus": [],
            "checkpointing_recommendations": [],
            "collaboration_opportunities": []
        }
        
        # Processar insights por tipo
        for insight in insights:
            if insight.type == "improvement":
                strategy["priorities"].append({
                    "action": "maintain_momentum",
                    "description": "Continuar estratégias que levaram à melhoria",
                    "confidence": insight.confidence
                })
                
            elif insight.type == "anomaly":
                strategy["priorities"].insert(0, {  # Alta prioridade
                    "action": "investigate_degradation",
                    "description": insight.description,
                    "confidence": insight.confidence
                })
                
            elif insight.type == "opportunity":
                if "especialização" in insight.description:
                    strategy["checkpointing_recommendations"].append({
                        "type": "specialization_checkpoint",
                        "description": insight.description,
                        "recommendations": insight.recommendations
                    })
                else:  # Lacuna de conhecimento
                    strategy["training_focus"].append({
                        "area": insight.description.split(": ")[1],
                        "priority": "high" if insight.confidence > 0.7 else "medium",
                        "recommendations": insight.recommendations
                    })
                    
            elif insight.type == "pattern":
                strategy["collaboration_opportunities"].append({
                    "type": "pattern_sharing",
                    "pattern": insight.description,
                    "confidence": insight.confidence
                })
        
        return strategy
    
    def cross_agent_analysis(self, agents: List[str]) -> Dict[str, Any]:
        """Análise comparativa entre múltiplos agentes"""
        
        analysis = {
            "timestamp": datetime.now().isoformat(),
            "agents_analyzed": agents,
            "performance_comparison": {},
            "knowledge_transfer_opportunities": [],
            "collaboration_patterns": [],
            "system_level_insights": []
        }
        
        # Comparar performance entre agentes
        for agent in agents:
            perf = self.graph_rag.get_agent_performance(agent)
            analysis["performance_comparison"][agent] = {
                "avg_quality": perf.get("avg_quality", 0),
                "success_rate": perf.get("success_rate", 0),
                "total_experiences": perf.get("total_experiences", 0)
            }
        
        # Identificar oportunidades de transferência de conhecimento
        with self.graph_rag.driver.session() as session:
            # Encontrar padrões que um agente domina mas outros não
            for source_agent in agents:
                for target_agent in agents:
                    if source_agent != target_agent:
                        query = """
                            // Padrões que source_agent domina (qualidade alta)
                            MATCH (source:Experience {agent_type: $source_agent})-[:EXHIBITS]->(p:Pattern)
                            WHERE source.quality_score >= 8.0
                            WITH p, avg(source.quality_score) as source_quality, count(source) as source_count
                            WHERE source_count >= 3
                            
                            // Mesmo padrão em target_agent (qualidade baixa ou poucos exemplos)
                            OPTIONAL MATCH (target:Experience {agent_type: $target_agent})-[:EXHIBITS]->(p)
                            WITH p, source_quality, source_count, 
                                 avg(target.quality_score) as target_quality, 
                                 count(target) as target_count
                            
                            WHERE target_count < 2 OR target_quality < 6.0
                            
                            RETURN p.name as pattern,
                                   source_quality,
                                   source_count,
                                   coalesce(target_quality, 0) as target_quality,
                                   coalesce(target_count, 0) as target_count
                            ORDER BY source_quality DESC, source_count DESC
                            LIMIT 3
                        """
                        
                        result = session.run(query, 
                            source_agent=source_agent, 
                            target_agent=target_agent
                        )
                        
                        for record in result:
                            analysis["knowledge_transfer_opportunities"].append({
                                "from_agent": source_agent,
                                "to_agent": target_agent,
                                "pattern": record["pattern"],
                                "source_quality": record["source_quality"],
                                "target_quality": record["target_quality"],
                                "potential_improvement": record["source_quality"] - record["target_quality"]
                            })
        
        # Insights do nível do sistema
        total_experiences = sum(perf["total_experiences"] for perf in analysis["performance_comparison"].values())
        avg_system_quality = sum(perf["avg_quality"] * perf["total_experiences"] 
                               for perf in analysis["performance_comparison"].values()) / total_experiences
        
        analysis["system_level_insights"].append({
            "metric": "system_quality",
            "value": avg_system_quality,
            "description": f"Qualidade média do sistema: {avg_system_quality:.2f}",
            "benchmark": "target: >7.5"
        })
        
        # Identificar agente com melhor performance
        best_agent = max(analysis["performance_comparison"].items(), 
                        key=lambda x: x[1]["avg_quality"])
        
        analysis["system_level_insights"].append({
            "metric": "top_performer",
            "value": best_agent[0],
            "description": f"Agente com melhor performance: {best_agent[0]} ({best_agent[1]['avg_quality']:.2f})",
            "recommendation": f"Usar padrões de {best_agent[0]} como referência"
        })
        
        return analysis
    
    def save_insights(self, insights: List[ReflectionInsight], filename: str = None):
        """Salva insights em arquivo YAML"""
        
        if not filename:
            filename = f"reflection/analysis/insights_{datetime.now().strftime('%Y%m%d_%H%M%S')}.yaml"
        
        insights_data = {
            "reflection_insights": [
                {
                    "type": insight.type,
                    "description": insight.description,
                    "evidence": insight.evidence,
                    "confidence": insight.confidence,
                    "recommendations": insight.recommendations,
                    "timestamp": insight.timestamp
                }
                for insight in insights
            ],
            "analysis_timestamp": datetime.now().isoformat(),
            "total_insights": len(insights)
        }
        
        with open(filename, "w", encoding="utf-8") as f:
            yaml.safe_dump(insights_data, f, sort_keys=False, allow_unicode=True)
        
        print(f"💾 Insights salvos em: {filename}")
    
    def close(self):
        """Fecha conexões"""
        self.graph_rag.close()

class MetaLearningOrchestrator:
    """Orquestrador de meta-aprendizado para o sistema completo"""
    
    def __init__(self):
        self.analyzer = AdvancedSymbolicAnalyzer()
        
    def run_system_evolution_cycle(self, agents: List[str]) -> Dict[str, Any]:
        """Executa um ciclo completo de evolução do sistema"""
        
        print("🧠 Iniciando ciclo de evolução simbólica...")
        
        evolution_report = {
            "timestamp": datetime.now().isoformat(),
            "cycle_type": "system_evolution",
            "agents_analyzed": agents,
            "individual_strategies": {},
            "cross_agent_analysis": {},
            "system_recommendations": []
        }
        
        # 1. Análise individual de cada agente
        for agent in agents:
            print(f"🔍 Analisando {agent}...")
            strategy = self.analyzer.generate_evolution_strategy(agent)
            evolution_report["individual_strategies"][agent] = strategy
        
        # 2. Análise cruzada entre agentes
        print("🔗 Analisando interações entre agentes...")
        cross_analysis = self.analyzer.cross_agent_analysis(agents)
        evolution_report["cross_agent_analysis"] = cross_analysis
        
        # 3. Recomendações do sistema
        evolution_report["system_recommendations"] = self._generate_system_recommendations(
            evolution_report["individual_strategies"],
            cross_analysis
        )
        
        # 4. Salvar relatório
        report_filename = f"reflection/analysis/evolution_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.yaml"
        with open(report_filename, "w", encoding="utf-8") as f:
            yaml.safe_dump(evolution_report, f, sort_keys=False, allow_unicode=True)
        
        print(f"📋 Relatório de evolução salvo em: {report_filename}")
        
        return evolution_report
    
    def _generate_system_recommendations(self, individual_strategies: Dict, cross_analysis: Dict) -> List[Dict]:
        """Gera recomendações do nível do sistema"""
        
        recommendations = []
        
        # Analisar prioridades comuns
        all_priorities = []
        for strategy in individual_strategies.values():
            all_priorities.extend([p["action"] for p in strategy["priorities"]])
        
        if all_priorities.count("investigate_degradation") > 1:
            recommendations.append({
                "type": "system_alert",
                "priority": "high", 
                "description": "Múltiplos agentes mostram degradação de performance",
                "action": "Investigar causas sistêmicas (mudanças de LLM, ambiente, etc.)"
            })
        
        # Oportunidades de transferência de conhecimento
        if cross_analysis["knowledge_transfer_opportunities"]:
            high_impact_transfers = [
                t for t in cross_analysis["knowledge_transfer_opportunities"] 
                if t["potential_improvement"] > 2.0
            ]
            
            if high_impact_transfers:
                recommendations.append({
                    "type": "knowledge_transfer",
                    "priority": "medium",
                    "description": f"{len(high_impact_transfers)} oportunidades de transferência de alto impacto",
                    "action": "Implementar sistema de sharing de padrões entre agentes"
                })
        
        # Performance do sistema
        system_quality = cross_analysis["system_level_insights"][0]["value"]
        if system_quality < 7.0:
            recommendations.append({
                "type": "system_improvement",
                "priority": "high",
                "description": f"Qualidade do sistema abaixo do alvo (atual: {system_quality:.2f}, alvo: >7.5)",
                "action": "Revisar prompts base e estratégias de treinamento"
            })
        
        return recommendations
    
    def close(self):
        """Fecha conexões"""
        self.analyzer.close()