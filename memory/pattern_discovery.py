# memory/pattern_discovery.py
"""
Sistema de Descoberta de Padrões - Identifica padrões emergentes nas experiências
Integra com sistema simbólico atual para manter compatibilidade

CORREÇÕES APLICADAS:
- Garantir criação do campo 'symbolic_traits' 
- Mapeamento robusto de padrões para traits simbólicos
- Integração simbólica mais completa
"""

import yaml
import json
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from collections import Counter, defaultdict
from sklearn.cluster import DBSCAN
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from memory.hybrid_store import HybridMemoryStore
from config.paths import SYMBOLIC_TIMELINE, MEMORY_LOG, IDENTITY_STATE

@dataclass
class DiscoveredPattern:
    """Padrão descoberto pelo sistema"""
    id: str
    name: str
    description: str
    template: str
    success_rate: float
    usage_count: int
    contexts: List[str]
    quality_impact: float
    discovery_date: datetime
    related_experiences: List[str]
    confidence_score: float


class PatternDiscoveryEngine:
    """
    Engine para descoberta automática de padrões de codificação
    """
    
    def __init__(self, memory_store: HybridMemoryStore):
        self.memory = memory_store
        self.vectorizer = TfidfVectorizer(
            max_features=1000,
            stop_words='english',
            ngram_range=(1, 3)
        )
        self.discovered_patterns = []
        self.pattern_evolution = {}
        
    def discover_patterns(self, min_occurrences: int = 3, 
                         min_success_rate: float = 0.7) -> List[DiscoveredPattern]:
        """
        Descobre padrões emergentes nas experiências armazenadas
        """
        print("🔍 Iniciando descoberta de padrões...")
        
        # 1. Coletar experiências recentes
        experiences = self._collect_recent_experiences()
        if len(experiences) < min_occurrences:
            print(f"⚠️ Poucas experiências ({len(experiences)}) para descobrir padrões")
            return []
        
        # 2. Análise de clustering por similaridade
        code_clusters = self._cluster_by_code_similarity(experiences)
        
        # 3. Análise de padrões por domínio/tarefa  
        task_patterns = self._analyze_task_patterns(experiences)
        
        # 4. Análise de qualidade vs abordagem
        quality_patterns = self._analyze_quality_patterns(experiences)
        
        # 5. Combinar e validar padrões
        all_patterns = code_clusters + task_patterns + quality_patterns
        validated_patterns = self._validate_patterns(all_patterns, min_occurrences, min_success_rate)
        
        # 6. Atualizar padrões conhecidos
        self._update_pattern_evolution(validated_patterns)
        
        # 7. Integrar com sistema simbólico atual - CORRIGIDO
        self._integrate_with_symbolic_system(validated_patterns)
        
        self.discovered_patterns = validated_patterns
        print(f"✅ {len(validated_patterns)} padrões descobertos")
        
        return validated_patterns
    
    def _collect_recent_experiences(self, days_ago: int = 30) -> List[Dict]:
        """Coleta experiências recentes do GraphRAG e sistema YAML"""
        experiences = []
        
        try:
            # Experiências do GraphRAG
            if self.memory.enable_graphrag:
                with self.memory.neo4j.session() as session:
                    result = session.run("""
                        MATCH (e:Experience)-[:GENERATED_CODE]->(c:Code)
                        WHERE e.timestamp > datetime() - duration('P30D')
                        RETURN e, c
                        ORDER BY e.timestamp DESC
                        LIMIT 100
                    """)
                    
                    for record in result:
                        exp = record['e']
                        code = record['c']
                        experiences.append({
                            'id': exp['id'],
                            'task': exp['task_description'],
                            'code': code['content'],
                            'quality': exp['quality_score'], 
                            'success': exp['execution_success'],
                            'agent': exp['agent_name'],
                            'timestamp': exp['timestamp'],
                            'source': 'graphrag'
                        })
            
            # Experiências do sistema YAML atual (compatibilidade)
            yaml_experiences = self._extract_yaml_experiences()
            experiences.extend(yaml_experiences)
            
        except Exception as e:
            print(f"⚠️ Erro ao coletar experiências: {e}")
            # Fallback para sistema YAML apenas
            experiences = self._extract_yaml_experiences()
        
        return experiences
    
    def _extract_yaml_experiences(self) -> List[Dict]:
        """Extrai experiências do sistema YAML atual para compatibilidade"""
        experiences = []
        
        try:
            # Carregar dados YAML atuais
            with open(MEMORY_LOG, 'r', encoding='utf-8') as f:
                memory_data = yaml.safe_load(f) or {}
            
            with open(SYMBOLIC_TIMELINE, 'r', encoding='utf-8') as f:
                timeline_data = yaml.safe_load(f) or {}
            
            # Converter dados YAML em formato compatível
            timeline_entries = timeline_data.get('linha_temporal', [])
            
            for entry in timeline_entries[-20:]:  # Últimas 20 entradas
                # Simular experiência baseada nos dados simbólicos
                experiences.append({
                    'id': f"yaml_{entry.get('ciclo', 0)}",
                    'task': entry.get('evento', 'Tarefa desconhecida'),
                    'code': f"# Código simbólico do ciclo {entry.get('ciclo', 0)}",
                    'quality': 7.0,  # Assumir qualidade média
                    'success': True,
                    'agent': 'CodeAgent',
                    'timestamp': entry.get('timestamp', datetime.now().isoformat()),
                    'source': 'yaml_symbolic'
                })
                
        except Exception as e:
            print(f"⚠️ Erro ao extrair experiências YAML: {e}")
        
        return experiences
    
    def _cluster_by_code_similarity(self, experiences: List[Dict]) -> List[DiscoveredPattern]:
        """Agrupa experiências por similaridade de código"""
        patterns = []
        
        try:
            # Extrair códigos válidos
            codes = [exp['code'] for exp in experiences if exp.get('code') and len(exp['code'].strip()) > 20]
            
            if len(codes) < 3:
                return patterns
            
            # Vetorizar códigos
            code_vectors = self.vectorizer.fit_transform(codes)
            
            # Clustering DBSCAN
            clustering = DBSCAN(eps=0.3, min_samples=2, metric='cosine')
            clusters = clustering.fit_predict(code_vectors.toarray())
            
            # Processar cada cluster
            cluster_groups = defaultdict(list)
            for i, cluster_id in enumerate(clusters):
                if cluster_id != -1:  # Ignorar outliers
                    cluster_groups[cluster_id].append(i)
            
            for cluster_id, indices in cluster_groups.items():
                if len(indices) >= 2:  # Mínimo 2 experiências similares
                    cluster_experiences = [experiences[codes.index(experiences[i]['code'])] for i in indices]
                    pattern = self._extract_code_pattern(cluster_experiences, f"code_cluster_{cluster_id}")
                    if pattern:
                        patterns.append(pattern)
                        
        except Exception as e:
            print(f"⚠️ Erro no clustering de código: {e}")
        
        return patterns
    
    def _extract_code_pattern(self, similar_experiences: List[Dict], pattern_id: str) -> Optional[DiscoveredPattern]:
        """Extrai padrão comum de experiências similares"""
        try:
            # Calcular métricas do padrão
            success_rate = sum(1 for exp in similar_experiences if exp.get('success', False)) / len(similar_experiences)
            avg_quality = sum(exp.get('quality', 0) for exp in similar_experiences) / len(similar_experiences)
            
            # Extrair características comuns
            codes = [exp.get('code', '') for exp in similar_experiences]
            tasks = [exp.get('task', '') for exp in similar_experiences]
            
            # Identificar template comum
            template = self._find_common_code_structure(codes)
            
            # Identificar contextos
            contexts = list(set([self._extract_context(task) for task in tasks]))
            
            # Gerar descrição
            description = self._generate_pattern_description(template, contexts, similar_experiences)
            
            return DiscoveredPattern(
                id=pattern_id,
                name=f"Padrão de {contexts[0] if contexts else 'Código'}",
                description=description,
                template=template,
                success_rate=success_rate,
                usage_count=len(similar_experiences),
                contexts=contexts,
                quality_impact=avg_quality,
                discovery_date=datetime.now(),
                related_experiences=[exp.get('id', '') for exp in similar_experiences],
                confidence_score=min(success_rate + (len(similar_experiences) / 10), 1.0)
            )
            
        except Exception as e:
            print(f"⚠️ Erro ao extrair padrão: {e}")
            return None
    
    def _find_common_code_structure(self, codes: List[str]) -> str:
        """Encontra estrutura comum entre códigos"""
        if not codes:
            return ""
        
        # Análise simples de estruturas comuns
        common_patterns = []
        
        # Verificar padrões de função
        if all('def ' in code for code in codes):
            common_patterns.append("def {function_name}({parameters}):")
        
        # Verificar padrões de validação
        if any(pattern in ' '.join(codes).lower() for pattern in ['if not', 'raise', 'assert']):
            common_patterns.append("    # Validação de entrada")
        
        # Verificar padrões de retorno
        if all('return' in code for code in codes):
            common_patterns.append("    return {result}")
        
        # Verificar padrões de erro
        if any('try:' in code for code in codes):
            common_patterns.append("    # Tratamento de erro")
        
        template = '\n'.join(common_patterns) if common_patterns else codes[0][:100] + "..."
        return template
    
    def _analyze_task_patterns(self, experiences: List[Dict]) -> List[DiscoveredPattern]:
        """Analisa padrões por tipo de tarefa"""
        patterns = []
        
        try:
            # Agrupar por domínio de tarefa
            task_groups = defaultdict(list)
            
            for exp in experiences:
                domain = self._extract_context(exp.get('task', ''))
                task_groups[domain].append(exp)
            
            # Analisar cada grupo
            for domain, group_experiences in task_groups.items():
                if len(group_experiences) >= 3:  # Mínimo 3 experiências por domínio
                    pattern = self._create_task_pattern(domain, group_experiences)
                    if pattern:
                        patterns.append(pattern)
                        
        except Exception as e:
            print(f"⚠️ Erro na análise de padrões de tarefa: {e}")
        
        return patterns
    
    def _create_task_pattern(self, domain: str, experiences: List[Dict]) -> Optional[DiscoveredPattern]:
        """Cria padrão baseado em domínio de tarefa"""
        try:
            # Calcular métricas
            success_rate = sum(1 for exp in experiences if exp.get('success', False)) / len(experiences)
            avg_quality = sum(exp.get('quality', 0) for exp in experiences) / len(experiences)
            
            # Identificar abordagens bem-sucedidas
            successful_approaches = [
                exp for exp in experiences 
                if exp.get('success', False) and exp.get('quality', 0) >= 7.0
            ]
            
            if not successful_approaches:
                return None
            
            # Extrair template de abordagem
            best_approach = max(successful_approaches, key=lambda x: x.get('quality', 0))
            template = best_approach.get('code', '')[:200] + "..." if len(best_approach.get('code', '')) > 200 else best_approach.get('code', '')
            
            # Gerar descrição
            description = f"Padrão para tarefas de {domain}: abordagem bem-sucedida em {len(successful_approaches)}/{len(experiences)} casos"
            
            return DiscoveredPattern(
                id=f"task_pattern_{domain}",
                name=f"Padrão {domain.title()}",
                description=description,
                template=template,
                success_rate=success_rate,
                usage_count=len(experiences),
                contexts=[domain],
                quality_impact=avg_quality,
                discovery_date=datetime.now(),
                related_experiences=[exp.get('id', '') for exp in experiences],
                confidence_score=min(success_rate * (len(successful_approaches) / len(experiences)), 1.0)
            )
            
        except Exception as e:
            print(f"⚠️ Erro ao criar padrão de tarefa: {e}")
            return None
    
    def _analyze_quality_patterns(self, experiences: List[Dict]) -> List[DiscoveredPattern]:
        """Analisa padrões que levam a alta qualidade"""
        patterns = []
        
        try:
            # Dividir em alta e baixa qualidade
            high_quality = [exp for exp in experiences if exp.get('quality', 0) >= 8.0]
            low_quality = [exp for exp in experiences if exp.get('quality', 0) < 6.0]
            
            if len(high_quality) < 3:
                return patterns
            
            # Analisar características de alta qualidade
            hq_codes = [exp.get('code', '') for exp in high_quality]
            lq_codes = [exp.get('code', '') for exp in low_quality]
            
            # Encontrar elementos que aparecem mais em alta qualidade
            quality_indicators = self._find_quality_indicators(hq_codes, lq_codes)
            
            if quality_indicators:
                pattern = DiscoveredPattern(
                    id="quality_pattern_high",
                    name="Padrão de Alta Qualidade",
                    description=f"Elementos que aumentam qualidade: {', '.join(quality_indicators)}",
                    template=f"# Incluir: {', '.join(quality_indicators)}",
                    success_rate=1.0,
                    usage_count=len(high_quality),
                    contexts=["quality_improvement"],
                    quality_impact=sum(exp.get('quality', 0) for exp in high_quality) / len(high_quality),
                    discovery_date=datetime.now(),
                    related_experiences=[exp.get('id', '') for exp in high_quality],
                    confidence_score=len(high_quality) / len(experiences)
                )
                patterns.append(pattern)
                
        except Exception as e:
            print(f"⚠️ Erro na análise de padrões de qualidade: {e}")
        
        return patterns
    
    def _find_quality_indicators(self, high_quality_codes: List[str], low_quality_codes: List[str]) -> List[str]:
        """Encontra elementos que indicam alta qualidade"""
        indicators = []
        
        # Elementos a verificar
        quality_elements = [
            ('docstrings', ['"""', "'''"]),
            ('error_handling', ['try:', 'except:', 'raise']),
            ('validation', ['if not', 'assert', 'validate']),
            ('comments', ['#']),
            ('type_hints', [': str', ': int', ': float', ': bool', '->'])
        ]
        
        hq_text = ' '.join(high_quality_codes).lower()
        lq_text = ' '.join(low_quality_codes).lower() if low_quality_codes else ''
        
        for element_name, keywords in quality_elements:
            hq_count = sum(hq_text.count(keyword) for keyword in keywords)
            lq_count = sum(lq_text.count(keyword) for keyword in keywords) if lq_text else 0
            
            # Se aparece mais em alta qualidade
            if hq_count > lq_count * 1.5:  # 50% mais frequente
                indicators.append(element_name)
        
        return indicators
    
    def _validate_patterns(self, patterns: List[DiscoveredPattern], 
                          min_occurrences: int, min_success_rate: float) -> List[DiscoveredPattern]:
        """Valida e filtra padrões descobertos"""
        validated = []
        
        for pattern in patterns:
            if (pattern.usage_count >= min_occurrences and 
                pattern.success_rate >= min_success_rate and
                pattern.confidence_score >= 0.5):
                validated.append(pattern)
        
        # Ordenar por confiança
        validated.sort(key=lambda p: p.confidence_score, reverse=True)
        
        return validated
    
    def _update_pattern_evolution(self, new_patterns: List[DiscoveredPattern]):
        """Atualiza evolução dos padrões ao longo do tempo"""
        timestamp = datetime.now().isoformat()
        
        for pattern in new_patterns:
            if pattern.id not in self.pattern_evolution:
                self.pattern_evolution[pattern.id] = []
            
            self.pattern_evolution[pattern.id].append({
                'timestamp': timestamp,
                'usage_count': pattern.usage_count,
                'success_rate': pattern.success_rate,
                'quality_impact': pattern.quality_impact,
                'confidence_score': pattern.confidence_score
            })
    
    def _integrate_with_symbolic_system(self, patterns: List[DiscoveredPattern]):
        """
        CORRIGIDO: Integra padrões descobertos com sistema simbólico atual
        Garante criação de symbolic_traits e mapeamento robusto
        """
        try:
            # Carregar estado simbólico atual
            with open(IDENTITY_STATE, 'r', encoding='utf-8') as f:
                identity_data = yaml.safe_load(f) or {}
            
            # CORREÇÃO: Adicionar insights de padrões aos agentes
            for agent_name in identity_data.keys():
                if agent_name not in identity_data:
                    continue
                
                agent_data = identity_data[agent_name]
                
                # CORREÇÃO: Garantir que symbolic_traits existe SEMPRE
                if 'symbolic_traits' not in agent_data:
                    agent_data['symbolic_traits'] = []
                
                # Adicionar padrões relevantes
                relevant_patterns = [
                    p for p in patterns 
                    if p.success_rate > 0.8 and p.confidence_score > 0.7
                ]
                
                if relevant_patterns:
                    if 'discovered_patterns' not in agent_data:
                        agent_data['discovered_patterns'] = []
                    
                    for pattern in relevant_patterns[:3]:  # Top 3 padrões
                        agent_data['discovered_patterns'].append({
                            'name': pattern.name,
                            'success_rate': pattern.success_rate,
                            'contexts': pattern.contexts,
                            'discovery_date': pattern.discovery_date.isoformat()
                        })
                    
                    # CORREÇÃO: Mapeamento robusto de padrões para traits simbólicos
                    new_traits = self._map_patterns_to_traits(relevant_patterns)
                    
                    # Adicionar novos traits únicos
                    existing_traits = set(agent_data.get('traits', []))
                    existing_symbolic_traits = set(agent_data.get('symbolic_traits', []))
                    
                    for trait in new_traits:
                        # Adicionar a traits normais se não existir
                        if trait not in existing_traits:
                            if 'traits' not in agent_data:
                                agent_data['traits'] = []
                            agent_data['traits'].append(trait)
                            existing_traits.add(trait)
                        
                        # Adicionar a symbolic_traits se não existir
                        if trait not in existing_symbolic_traits:
                            agent_data['symbolic_traits'].append(trait)
                            existing_symbolic_traits.add(trait)
            
            # Salvar estado atualizado
            with open(IDENTITY_STATE, 'w', encoding='utf-8') as f:
                yaml.safe_dump(identity_data, f, allow_unicode=True, sort_keys=False)
            
            print(f"🔗 {len(patterns)} padrões integrados ao sistema simbólico")
            
        except Exception as e:
            print(f"⚠️ Erro na integração simbólica: {e}")
    
    def _map_patterns_to_traits(self, patterns: List[DiscoveredPattern]) -> List[str]:
        """
        NOVO: Mapeia padrões descobertos para traits simbólicos
        """
        traits = []
        
        for pattern in patterns:
            pattern_name_lower = pattern.name.lower()
            pattern_desc_lower = pattern.description.lower()
            contexts = [ctx.lower() for ctx in pattern.contexts]
            
            # Mapeamento baseado no nome do padrão
            if 'qualidade' in pattern_name_lower or 'quality' in pattern_name_lower:
                traits.append('Qualidade-Orientado')
            
            if 'validação' in pattern_name_lower or 'validation' in pattern_name_lower:
                traits.append('Validador')
            
            if 'segurança' in pattern_name_lower or 'security' in pattern_name_lower:
                traits.append('Segurança-Consciente')
            
            if 'performance' in pattern_name_lower or 'otimização' in pattern_name_lower:
                traits.append('Performance-Otimizado')
            
            # Mapeamento baseado no contexto
            if 'authentication' in contexts:
                traits.append('Especialista-Auth')
            
            if 'api_development' in contexts:
                traits.append('API-Developer')
            
            if 'database' in contexts:
                traits.append('Data-Handler')
            
            if 'testing' in contexts:
                traits.append('Test-Driven')
            
            # Mapeamento baseado na descrição
            if 'error' in pattern_desc_lower or 'exception' in pattern_desc_lower:
                traits.append('Error-Handler')
            
            if 'docstring' in pattern_desc_lower or 'documentation' in pattern_desc_lower:
                traits.append('Documentador')
            
            # Mapeamento baseado na taxa de sucesso
            if pattern.success_rate >= 0.95:
                traits.append('Altamente-Confiável')
            elif pattern.success_rate >= 0.85:
                traits.append('Confiável')
            
            # Mapeamento baseado no impacto na qualidade
            if pattern.quality_impact >= 9.0:
                traits.append('Excellence-Seeker')
            elif pattern.quality_impact >= 8.0:
                traits.append('Quality-Focused')
        
        # Remover duplicatas e retornar
        return list(set(traits))
    
    def _extract_context(self, task: str) -> str:
        """Extrai contexto/domínio da tarefa"""
        task_lower = task.lower()
        
        if any(word in task_lower for word in ['login', 'auth', 'password', 'user']):
            return 'authentication'
        elif any(word in task_lower for word in ['api', 'endpoint', 'rest', 'http']):
            return 'api_development'
        elif any(word in task_lower for word in ['database', 'db', 'sql', 'query']):
            return 'database'
        elif any(word in task_lower for word in ['test', 'verify', 'check']):
            return 'testing'
        elif any(word in task_lower for word in ['file', 'read', 'write', 'csv']):
            return 'file_processing'
        elif any(word in task_lower for word in ['soma', 'calc', 'math', 'number']):
            return 'mathematical'
        else:
            return 'general'
    
    def _generate_pattern_description(self, template: str, contexts: List[str], 
                                    experiences: List[Dict]) -> str:
        """Gera descrição humana do padrão"""
        context_str = ', '.join(contexts) if contexts else 'geral'
        success_count = sum(1 for exp in experiences if exp.get('success', False))
        
        return f"Padrão comum para {context_str}: usado em {len(experiences)} casos, {success_count} sucessos"
    
    def get_pattern_recommendations(self, current_task: str) -> List[Dict[str, Any]]:
        """Retorna recomendações de padrões para tarefa atual"""
        if not self.discovered_patterns:
            return []
        
        task_context = self._extract_context(current_task)
        recommendations = []
        
        for pattern in self.discovered_patterns:
            if (task_context in pattern.contexts or 
                'general' in pattern.contexts or
                pattern.success_rate > 0.9):
                
                relevance_score = self._calculate_relevance(pattern, current_task, task_context)
                
                recommendations.append({
                    'pattern': pattern,
                    'relevance_score': relevance_score,
                    'recommendation': self._generate_recommendation_text(pattern, current_task)
                })
        
        # Ordenar por relevância
        recommendations.sort(key=lambda x: x['relevance_score'], reverse=True)
        
        return recommendations[:5]  # Top 5 recomendações
    
    def _calculate_relevance(self, pattern: DiscoveredPattern, task: str, context: str) -> float:
        """Calcula relevância do padrão para a tarefa"""
        score = 0.0
        
        # Contexto matching
        if context in pattern.contexts:
            score += 0.4
        
        # Success rate
        score += pattern.success_rate * 0.3
        
        # Quality impact
        score += (pattern.quality_impact / 10.0) * 0.2
        
        # Confidence
        score += pattern.confidence_score * 0.1
        
        return min(score, 1.0)
    
    def _generate_recommendation_text(self, pattern: DiscoveredPattern, task: str) -> str:
        """Gera texto de recomendação para o padrão"""
        return f"Considere usar o padrão '{pattern.name}' (taxa de sucesso: {pattern.success_rate:.1%}, qualidade média: {pattern.quality_impact:.1f})"
    
    def export_patterns_summary(self) -> Dict[str, Any]:
        """Exporta resumo dos padrões para dashboard"""
        return {
            'total_patterns': len(self.discovered_patterns),
            'patterns': [
                {
                    'id': p.id,
                    'name': p.name,
                    'description': p.description,
                    'success_rate': p.success_rate,
                    'usage_count': p.usage_count,
                    'quality_impact': p.quality_impact,
                    'contexts': p.contexts,
                    'confidence_score': p.confidence_score,
                    'discovery_date': p.discovery_date.isoformat()
                }
                for p in self.discovered_patterns
            ],
            'pattern_evolution': self.pattern_evolution,
            'summary_stats': {
                'avg_success_rate': sum(p.success_rate for p in self.discovered_patterns) / len(self.discovered_patterns) if self.discovered_patterns else 0,
                'total_experiences_analyzed': sum(p.usage_count for p in self.discovered_patterns),
                'high_confidence_patterns': len([p for p in self.discovered_patterns if p.confidence_score > 0.8])
            }
        }


# Scheduler para execução automática (mantido inalterado)
import threading
import time

class PatternDiscoveryScheduler:
    """Scheduler para executar descoberta de padrões automaticamente"""
    
    def __init__(self, discovery_engine: PatternDiscoveryEngine, 
                 interval_hours: int = 24):
        self.engine = discovery_engine
        self.interval_hours = interval_hours
        self.running = False
        self.thread = None
    
    def start(self):
        """Inicia execução automática"""
        if not self.running:
            self.running = True
            self.thread = threading.Thread(target=self._run_discovery_loop)
            self.thread.daemon = True
            self.thread.start()
            print(f"🔄 Pattern Discovery agendado a cada {self.interval_hours}h")
    
    def stop(self):
        """Para execução automática"""
        self.running = False
        if self.thread:
            self.thread.join()
        print("⏹️ Pattern Discovery interrompido")
    
    def _run_discovery_loop(self):
        """Loop principal de descoberta"""
        while self.running:
            try:
                print("🕐 Executando descoberta automática de padrões...")
                patterns = self.engine.discover_patterns()
                print(f"✅ Descoberta concluída: {len(patterns)} padrões")
                
            except Exception as e:
                print(f"❌ Erro na descoberta automática: {e}")
            
            # Aguardar próxima execução
            time.sleep(self.interval_hours * 3600)


# Exemplo de uso (mantido inalterado)
if __name__ == "__main__":
    # Inicializar sistema
    memory_store = HybridMemoryStore(enable_graphrag=True)
    discovery_engine = PatternDiscoveryEngine(memory_store)
    
    # Descobrir padrões
    patterns = discovery_engine.discover_patterns()
    
    print(f"\n📊 RESUMO DOS PADRÕES DESCOBERTOS:")
    print(f"Total: {len(patterns)}")
    
    for pattern in patterns:
        print(f"\n🔹 {pattern.name}")
        print(f"   Descrição: {pattern.description}")
        print(f"   Taxa de sucesso: {pattern.success_rate:.1%}")
        print(f"   Impacto na qualidade: {pattern.quality_impact:.1f}")
        print(f"   Confiança: {pattern.confidence_score:.1%}")
    
    # Testar recomendações
    print(f"\n💡 RECOMENDAÇÕES PARA 'criar função de login':")
    recommendations = discovery_engine.get_pattern_recommendations("criar função de login")
    
    for rec in recommendations:
        print(f"   • {rec['recommendation']} (Relevância: {rec['relevance_score']:.1%})")
    
    # Exportar resumo
    summary = discovery_engine.export_patterns_summary()
    print(f"\n📈 ESTATÍSTICAS:")
    print(f"   Padrões de alta confiança: {summary['summary_stats']['high_confidence_patterns']}")
    print(f"   Taxa média de sucesso: {summary['summary_stats']['avg_success_rate']:.1%}")
    
    memory_store.close()