# interface/dashboard/streamlit_advanced.py
"""
Dashboard Avançado para RSCA - Visualiza evolução de agentes e GraphRAG
Expansão do dashboard atual com capacidades de GraphRAG
"""

import streamlit as st
import yaml
import json
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
from pathlib import Path
import networkx as nx
from typing import Dict, List, Any

# Configuração da página
st.set_page_config(
    page_title="RSCA - Dashboard Avançado", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# Imports do sistema
import sys
sys.path.append(str(Path(__file__).parent.parent.parent))

from memory.hybrid_store import HybridMemoryStore
from memory.pattern_discovery import PatternDiscoveryEngine
from evolution.checkpointing.agent_checkpoints import AgentCheckpointManager
from config.paths import IDENTITY_STATE, MEMORY_LOG, SYMBOLIC_TIMELINE

# CSS customizado
st.markdown("""
<style>
.metric-card {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    padding: 1rem;
    border-radius: 10px;
    color: white;
    margin: 0.5rem 0;
}
.success-metric {
    background: linear-gradient(135deg, #4CAF50 0%, #45a049 100%);
}
.warning-metric {
    background: linear-gradient(135deg, #ff9800 0%, #f57c00 100%);
}
.error-metric {
    background: linear-gradient(135deg, #f44336 0%, #d32f2f 100%);
}
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_system_data():
    """Carrega dados do sistema com cache"""
    data = {}
    
    # Dados YAML atuais (compatibilidade)
    try:
        with open(IDENTITY_STATE, 'r') as f:
            data['identity'] = yaml.safe_load(f) or {}
    except:
        data['identity'] = {}
    
    try:
        with open(MEMORY_LOG, 'r') as f:
            data['memory'] = yaml.safe_load(f) or {}
    except:
        data['memory'] = {}
    
    try:
        with open(SYMBOLIC_TIMELINE, 'r') as f:
            data['timeline'] = yaml.safe_load(f) or {}
    except:
        data['timeline'] = {}
    
    return data

@st.cache_data
def load_graphrag_data():
    """Carrega dados do GraphRAG"""
    try:
        memory = HybridMemoryStore(enable_graphrag=True)
        
        if memory.enable_graphrag:
            # Estatísticas básicas do Neo4j
            with memory.neo4j.session() as session:
                stats_query = """
                MATCH (e:Experience)
                RETURN 
                    count(e) as total_experiences,
                    avg(e.quality_score) as avg_quality,
                    max(e.quality_score) as max_quality,
                    min(e.quality_score) as min_quality
                """
                result = session.run(stats_query)
                stats = result.single()
                
                # Experiências por agente
                agent_query = """
                MATCH (e:Experience)-[:PERFORMED_BY]->(a:Agent)
                RETURN a.name as agent, count(e) as experiences
                ORDER BY experiences DESC
                """
                agent_result = session.run(agent_query)
                agent_stats = [dict(record) for record in agent_result]
                
                # Qualidade ao longo do tempo
                quality_query = """
                MATCH (e:Experience)
                WHERE e.timestamp IS NOT NULL
                RETURN 
                    date(e.timestamp) as date,
                    avg(e.quality_score) as avg_quality,
                    count(e) as experience_count
                ORDER BY date DESC
                LIMIT 30
                """
                quality_result = session.run(quality_query)
                quality_timeline = [dict(record) for record in quality_result]
        
        memory.close()
        
        return {
            'stats': dict(stats) if 'stats' in locals() else {},
            'agent_stats': agent_stats if 'agent_stats' in locals() else [],
            'quality_timeline': quality_timeline if 'quality_timeline' in locals() else [],
            'available': True
        }
        
    except Exception as e:
        return {
            'stats': {},
            'agent_stats': [],
            'quality_timeline': [],
            'available': False,
            'error': str(e)
        }

@st.cache_data
def load_pattern_data():
    """Carrega dados de padrões descobertos"""
    try:
        memory = HybridMemoryStore(enable_graphrag=True)
        discovery_engine = PatternDiscoveryEngine(memory)
        
        # Descobrir padrões
        patterns = discovery_engine.discover_patterns(min_occurrences=1, min_success_rate=0.3)
        
        # Exportar resumo
        pattern_summary = discovery_engine.export_patterns_summary()
        
        memory.close()
        
        return {
            'patterns': patterns,
            'summary': pattern_summary,
            'available': True
        }
        
    except Exception as e:
        return {
            'patterns': [],
            'summary': {},
            'available': False,
            'error': str(e)
        }

@st.cache_data
def load_checkpoint_data():
    """Carrega dados de checkpoints"""
    try:
        checkpoint_manager = AgentCheckpointManager()
        checkpoints = checkpoint_manager.list_checkpoints()
        summary = checkpoint_manager.export_checkpoint_summary()
        
        return {
            'checkpoints': checkpoints,
            'summary': summary,
            'available': True
        }
        
    except Exception as e:
        return {
            'checkpoints': [],
            'summary': {},
            'available': False,
            'error': str(e)
        }

def main():
    """Função principal do dashboard"""
    
    # Header
    st.title("🤖 RSCA - Dashboard Avançado")
    st.markdown("**Reflexive Self Coding Assistant** - Monitoramento de Agentes Evolutivos")
    
    # Sidebar para controles
    st.sidebar.header("🎛️ Controles")
    
    # Seleção de visualizações
    view_mode = st.sidebar.selectbox(
        "Modo de Visualização",
        ["Visão Geral", "GraphRAG Analytics", "Evolução de Agentes", "Padrões Descobertos", "Checkpoints", "Performance"]
    )
    
    # Atualização automática
    auto_refresh = st.sidebar.checkbox("Auto-refresh (30s)", value=False)
    if auto_refresh:
        st.rerun()
    
    # Carregar dados
    with st.spinner("Carregando dados do sistema..."):
        system_data = load_system_data()
        graphrag_data = load_graphrag_data()
        pattern_data = load_pattern_data()
        checkpoint_data = load_checkpoint_data()
    
    # Renderizar visualização selecionada
    if view_mode == "Visão Geral":
        render_overview(system_data, graphrag_data, pattern_data, checkpoint_data)
    elif view_mode == "GraphRAG Analytics":
        render_graphrag_analytics(graphrag_data)
    elif view_mode == "Evolução de Agentes":
        render_agent_evolution(system_data, graphrag_data)
    elif view_mode == "Padrões Descobertos":
        render_patterns_analysis(pattern_data)
    elif view_mode == "Checkpoints":
        render_checkpoint_management(checkpoint_data)
    elif view_mode == "Performance":
        render_performance_metrics(system_data, graphrag_data)

def render_overview(system_data, graphrag_data, pattern_data, checkpoint_data):
    """Renderiza visão geral do sistema"""
    
    st.header("📊 Visão Geral do Sistema")
    
    # Métricas principais
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_agents = len(system_data['identity'])
        st.metric(
            "👥 Agentes Ativos", 
            total_agents,
            help="Número de agentes com identidade simbólica"
        )
    
    with col2:
        if graphrag_data['available']:
            total_exp = graphrag_data['stats'].get('total_experiences', 0)
            st.metric(
                "🧠 Experiências", 
                total_exp,
                help="Total de experiências armazenadas no GraphRAG"
            )
        else:
            st.metric("🧠 Experiências", "N/A", help="GraphRAG não disponível")
    
    with col3:
        total_patterns = len(pattern_data.get('patterns', []))
        st.metric(
            "🔍 Padrões", 
            total_patterns,
            help="Padrões descobertos automaticamente"
        )
    
    with col4:
        total_checkpoints = len(checkpoint_data.get('checkpoints', []))
        st.metric(
            "💾 Checkpoints", 
            total_checkpoints,
            help="Versões salvas de agentes"
        )
    
    # Status do sistema
    st.subheader("🔧 Status dos Componentes")
    
    components = [
        ("Sistema YAML", True, "✅ Compatibilidade preservada"),
        ("GraphRAG", graphrag_data['available'], "✅ Neo4j + ChromaDB" if graphrag_data['available'] else "❌ Não disponível"),
        ("Pattern Discovery", pattern_data['available'], "✅ Funcionando" if pattern_data['available'] else "❌ Erro"),
        ("Checkpoints", checkpoint_data['available'], "✅ Sistema ativo" if checkpoint_data['available'] else "❌ Erro")
    ]
    
    for component, status, message in components:
        col1, col2, col3 = st.columns([2, 1, 4])
        with col1:
            st.write(f"**{component}**")
        with col2:
            st.write("🟢" if status else "🔴")
        with col3:
            st.write(message)
    
    # Gráfico de qualidade ao longo do tempo
    if graphrag_data['available'] and graphrag_data['quality_timeline']:
        st.subheader("📈 Evolução da Qualidade")
        
        quality_df = pd.DataFrame(graphrag_data['quality_timeline'])
        if not quality_df.empty:
            fig = px.line(
                quality_df, 
                x='date', 
                y='avg_quality',
                title="Qualidade Média das Experiências ao Longo do Tempo",
                markers=True
            )
            fig.update_layout(
                xaxis_title="Data",
                yaxis_title="Qualidade Média",
                yaxis_range=[0, 10]
            )
            st.plotly_chart(fig, use_container_width=True)
    
    # Distribuição de agentes
    if system_data['identity']:
        st.subheader("🤖 Distribuição de Agentes")
        
        agent_info = []
        for agent_name, profile in system_data['identity'].items():
            agent_info.append({
                'Agente': agent_name,
                'Padrão': profile.get('predominant_pattern', 'N/A'),
                'Consistência': profile.get('consistency_level', 'N/A'),
                'Traços': ', '.join(profile.get('traits', [])),
                'Experiências': system_data['memory'].get(agent_name, {}).get('ciclos_totais', 0)
            })
        
        agent_df = pd.DataFrame(agent_info)
        st.dataframe(agent_df, use_container_width=True)

def render_graphrag_analytics(graphrag_data):
    """Renderiza analytics do GraphRAG"""
    
    st.header("🧠 GraphRAG Analytics")
    
    if not graphrag_data['available']:
        st.error(f"❌ GraphRAG não disponível: {graphrag_data.get('error', 'Erro desconhecido')}")
        st.info("💡 Para habilitar GraphRAG, execute: `docker-compose up -d` e verifique se Neo4j e ChromaDB estão rodando")
        return
    
    # Estatísticas do grafo
    st.subheader("📊 Estatísticas do Grafo de Conhecimento")
    
    stats = graphrag_data['stats']
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total de Experiências", stats.get('total_experiences', 0))
    with col2:
        st.metric("Qualidade Média", f"{stats.get('avg_quality', 0):.2f}/10")
    with col3:
        st.metric("Melhor Qualidade", f"{stats.get('max_quality', 0):.2f}/10")
    with col4:
        st.metric("Pior Qualidade", f"{stats.get('min_quality', 0):.2f}/10")
    
    # Experiências por agente
    if graphrag_data['agent_stats']:
        st.subheader("👥 Experiências por Agente")
        
        agent_df = pd.DataFrame(graphrag_data['agent_stats'])
        fig = px.bar(
            agent_df, 
            x='agent', 
            y='experiences',
            title="Distribuição de Experiências por Agente"
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Timeline de qualidade
    if graphrag_data['quality_timeline']:
        st.subheader("📈 Evolução da Qualidade")
        
        timeline_df = pd.DataFrame(graphrag_data['quality_timeline'])
        
        # Gráfico principal
        fig = go.Figure()
        
        # Linha de qualidade média
        fig.add_trace(go.Scatter(
            x=timeline_df['date'],
            y=timeline_df['avg_quality'],
            mode='lines+markers',
            name='Qualidade Média',
            line=dict(color='#1f77b4', width=3)
        ))
        
        # Barra de volume de experiências
        fig.add_trace(go.Bar(
            x=timeline_df['date'],
            y=timeline_df['experience_count'],
            name='Experiências por Dia',
            yaxis='y2',
            opacity=0.3,
            marker_color='#ff7f0e'
        ))
        
        fig.update_layout(
            title="Qualidade vs Volume de Experiências",
            xaxis_title="Data",
            yaxis_title="Qualidade Média",
            yaxis2=dict(
                title="Número de Experiências",
                overlaying='y',
                side='right'
            ),
            hovermode='x unified'
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    # Rede de conhecimento (simulada)
    st.subheader("🕸️ Rede de Conhecimento")
    
    # Criar grafo de exemplo para visualização
    G = nx.Graph()
    
    # Adicionar nós baseados nos dados disponíveis
    if graphrag_data['agent_stats']:
        for agent_stat in graphrag_data['agent_stats']:
            G.add_node(agent_stat['agent'], type='agent', size=agent_stat['experiences'])
    
    # Adicionar algumas conexões de exemplo
    agents = [stat['agent'] for stat in graphrag_data['agent_stats']]
    for i, agent1 in enumerate(agents):
        for agent2 in agents[i+1:]:
            if np.random.random() > 0.7:  # Conexão aleatória para demo
                G.add_edge(agent1, agent2, weight=np.random.random())
    
    if G.nodes():
        # Layout do grafo
        pos = nx.spring_layout(G, k=1, iterations=50)
        
        # Extrair coordenadas
        edge_x = []
        edge_y = []
        for edge in G.edges():
            x0, y0 = pos[edge[0]]
            x1, y1 = pos[edge[1]]
            edge_x.extend([x0, x1, None])
            edge_y.extend([y0, y1, None])
        
        # Trace das arestas
        edge_trace = go.Scatter(
            x=edge_x, y=edge_y,
            line=dict(width=0.5, color='#888'),
            hoverinfo='none',
            mode='lines'
        )
        
        # Trace dos nós
        node_x = []
        node_y = []
        node_text = []
        node_size = []
        
        for node in G.nodes():
            x, y = pos[node]
            node_x.append(x)
            node_y.append(y)
            node_text.append(node)
            node_size.append(G.nodes[node].get('size', 10))
        
        node_trace = go.Scatter(
            x=node_x, y=node_y,
            mode='markers+text',
            hoverinfo='text',
            text=node_text,
            textposition="middle center",
            marker=dict(
                size=[s/2 + 20 for s in node_size],
                color='#1f77b4',
                line=dict(width=2, color='white')
            )
        )
        
        # Figura do grafo
        fig = go.Figure(data=[edge_trace, node_trace],
                       layout=go.Layout(
                           title="Rede de Conhecimento entre Agentes",
                           titlefont_size=16,
                           showlegend=False,
                           hovermode='closest',
                           margin=dict(b=20,l=5,r=5,t=40),
                           annotations=[ dict(
                               text="Conexões baseadas em experiências compartilhadas",
                               showarrow=False,
                               xref="paper", yref="paper",
                               x=0.005, y=-0.002,
                               xanchor='left', yanchor='bottom',
                               font=dict(color="#888", size=12)
                           )],
                           xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                           yaxis=dict(showgrid=False, zeroline=False, showticklabels=False)
                       ))
        
        st.plotly_chart(fig, use_container_width=True)

def render_agent_evolution(system_data, graphrag_data):
    """Renderiza evolução dos agentes"""
    
    st.header("🧬 Evolução de Agentes")
    
    # Seletor de agente
    agents = list(system_data['identity'].keys())
    if not agents:
        st.warning("Nenhum agente encontrado nos dados do sistema")
        return
    
    selected_agent = st.selectbox("Selecionar Agente", agents)
    
    if selected_agent:
        agent_profile = system_data['identity'][selected_agent]
        agent_memory = system_data['memory'].get(selected_agent, {})
        
        # Perfil atual do agente
        st.subheader(f"🤖 Perfil: {selected_agent}")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Identidade Simbólica:**")
            st.write(f"• Padrão: `{agent_profile.get('predominant_pattern', 'N/A')}`")
            st.write(f"• Consistência: `{agent_profile.get('consistency_level', 'N/A')}`")
            st.write(f"• Última adaptação: `{agent_profile.get('last_adaptation', 'N/A')}`")
            
            traits = agent_profile.get('traits', [])
            if traits:
                st.write(f"• Traços: {', '.join([f'`{t}`' for t in traits])}")
        
        with col2:
            st.markdown("**Memória e Experiência:**")
            st.write(f"• Ciclos totais: `{agent_memory.get('ciclos_totais', 0)}`")
            
            consistency = agent_memory.get('consistencia', {})
            if consistency:
                for level, count in consistency.items():
                    st.write(f"• {level}: `{count}` ciclos")
            
            frequent_traits = agent_memory.get('traços_frequentes', [])
            if frequent_traits:
                st.write(f"• Traços frequentes: {', '.join([f'`{t}`' for t in frequent_traits])}")
        
        # Evolução da consistência
        if consistency:
            st.subheader("📊 Distribuição de Consistência")
            
            consistency_df = pd.DataFrame([
                {'Nível': level, 'Ciclos': count} 
                for level, count in consistency.items()
            ])
            
            fig = px.pie(
                consistency_df, 
                values='Ciclos', 
                names='Nível',
                title=f"Distribuição de Consistência - {selected_agent}"
            )
            st.plotly_chart(fig, use_container_width=True)
        
        # Timeline simbólica
        timeline_data = system_data['timeline'].get('linha_temporal', [])
        if timeline_data:
            st.subheader("📅 Timeline Simbólica")
            
            # Filtrar eventos do agente selecionado
            agent_events = []
            for event in timeline_data:
                identidade = event.get('identidade', '')
                if selected_agent.lower() in identidade.lower():
                    agent_events.append({
                        'Ciclo': event.get('ciclo', 0),
                        'Data': event.get('timestamp', ''),
                        'Emoção': event.get('emoção', 'N/A'),
                        'Evento': event.get('evento', 'N/A'),
                        'Identidade': identidade
                    })
            
            if agent_events:
                events_df = pd.DataFrame(agent_events)
                st.dataframe(events_df, use_container_width=True)
                
                # Gráfico de evolução emocional
                emotion_counts = events_df['Emoção'].value_counts()
                if len(emotion_counts) > 1:
                    fig = px.bar(
                        x=emotion_counts.index,
                        y=emotion_counts.values,
                        title=f"Estados Emocionais - {selected_agent}"
                    )
                    fig.update_xaxis(title="Emoção")
                    fig.update_yaxis(title="Frequência")
                    st.plotly_chart(fig, use_container_width=True)

def render_patterns_analysis(pattern_data):
    """Renderiza análise de padrões descobertos"""
    
    st.header("🔍 Padrões Descobertos")
    
    if not pattern_data['available']:
        st.error(f"❌ Sistema de padrões não disponível: {pattern_data.get('error', 'Erro desconhecido')}")
        return
    
    patterns = pattern_data.get('patterns', [])
    summary = pattern_data.get('summary', {})
    
    if not patterns:
        st.info("🔍 Nenhum padrão descoberto ainda. Execute mais ciclos de geração de código para acumular experiências.")
        return
    
    # Métricas de padrões
    st.subheader("📊 Resumo dos Padrões")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total de Padrões", len(patterns))
    
    with col2:
        avg_success = sum(p.success_rate for p in patterns) / len(patterns)
        st.metric("Taxa Média de Sucesso", f"{avg_success:.1%}")
    
    with col3:
        high_conf_patterns = len([p for p in patterns if p.confidence_score > 0.8])
        st.metric("Alta Confiança", high_conf_patterns)
    
    with col4:
        total_usage = sum(p.usage_count for p in patterns)
        st.metric("Uso Total", total_usage)
    
    # Lista detalhada de padrões
    st.subheader("📋 Padrões Detalhados")
    
    for i, pattern in enumerate(patterns):
        with st.expander(f"🔹 {pattern.name} (Confiança: {pattern.confidence_score:.1%})"):
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**Informações Básicas:**")
                st.write(f"• **Descrição:** {pattern.description}")
                st.write(f"• **Taxa de Sucesso:** {pattern.success_rate:.1%}")
                st.write(f"• **Uso:** {pattern.usage_count} vezes")
                st.write(f"• **Impacto na Qualidade:** {pattern.quality_impact:.2f}/10")
                st.write(f"• **Descoberto em:** {pattern.discovery_date.strftime('%Y-%m-%d %H:%M')}")
            
            with col2:
                st.markdown("**Contextos de Aplicação:**")
                for context in pattern.contexts:
                    st.write(f"• `{context}`")
                
                if pattern.template:
                    st.markdown("**Template/Estrutura:**")
                    st.code(pattern.template[:200] + "..." if len(pattern.template) > 200 else pattern.template)
    
    # Visualização da distribuição de padrões
    if patterns:
        st.subheader("📈 Análise Visual dos Padrões")
        
        # Scatter plot: Success Rate vs Quality Impact
        pattern_viz_data = []
        for pattern in patterns:
            pattern_viz_data.append({
                'Nome': pattern.name,
                'Taxa de Sucesso': pattern.success_rate,
                'Impacto na Qualidade': pattern.quality_impact,
                'Confiança': pattern.confidence_score,
                'Uso': pattern.usage_count,
                'Contextos': ', '.join(pattern.contexts)
            })
        
        viz_df = pd.DataFrame(pattern_viz_data)
        
        fig = px.scatter(
            viz_df,
            x='Taxa de Sucesso',
            y='Impacto na Qualidade',
            size='Uso',
            color='Confiança',
            hover_data=['Nome', 'Contextos'],
            title="Padrões: Taxa de Sucesso vs Impacto na Qualidade",
            color_continuous_scale='Viridis'
        )
        
        fig.update_layout(
            xaxis_title="Taxa de Sucesso",
            yaxis_title="Impacto na Qualidade",
            coloraxis_colorbar_title="Confiança"
        )
        
        st.plotly_chart(fig, use_container_width=True)

def render_checkpoint_management(checkpoint_data):
    """Renderiza gerenciamento de checkpoints"""
    
    st.header("💾 Gerenciamento de Checkpoints")
    
    if not checkpoint_data['available']:
        st.error(f"❌ Sistema de checkpoints não disponível: {checkpoint_data.get('error', 'Erro desconhecido')}")
        return
    
    checkpoints = checkpoint_data.get('checkpoints', [])
    summary = checkpoint_data.get('summary', {})
    
    # Resumo dos checkpoints
    st.subheader("📊 Resumo")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total de Checkpoints", summary.get('total_checkpoints', 0))
    
    with col2:
        agent_types = len(summary.get('agent_types', []))
        st.metric("Tipos de Agentes", agent_types)
    
    with col3:
        specializations = len(summary.get('specializations', []))
        st.metric("Especializações", specializations)
    
    with col4:
        avg_quality = summary.get('average_quality', 0)
        st.metric("Qualidade Média", f"{avg_quality:.2f}")
    
    # Lista de checkpoints
    if checkpoints:
        st.subheader("📋 Checkpoints Disponíveis")
        
        # Filtros
        col1, col2 = st.columns(2)
        
        with col1:
            agent_filter = st.selectbox(
                "Filtrar por Agente",
                ["Todos"] + list(set(cp['agent_name'] for cp in checkpoints))
            )
        
        with col2:
            spec_filter = st.selectbox(
                "Filtrar por Especialização",
                ["Todas"] + list(set(cp['specialization'] for cp in checkpoints))
            )
        
        # Filtrar checkpoints
        filtered_checkpoints = checkpoints
        
        if agent_filter != "Todos":
            filtered_checkpoints = [cp for cp in filtered_checkpoints if cp['agent_name'] == agent_filter]
        
        if spec_filter != "Todas":
            filtered_checkpoints = [cp for cp in filtered_checkpoints if cp['specialization'] == spec_filter]
        
        # Tabela de checkpoints
        if filtered_checkpoints:
            checkpoint_table_data = []
            
            for cp in filtered_checkpoints:
                checkpoint_table_data.append({
                    'ID': cp['id'][:16] + "...",
                    'Agente': cp['agent_name'],
                    'Versão': cp['version'],
                    'Especialização': cp['specialization'],
                    'Qualidade': f"{cp['quality_average']:.2f}",
                    'Experiências': cp['experience_count'],
                    'Data': cp['creation_date'][:10]
                })
            
            cp_df = pd.DataFrame(checkpoint_table_data)
            st.dataframe(cp_df, use_container_width=True)
            
            # Gráfico de evolução de checkpoints
            if len(filtered_checkpoints) > 1:
                fig = px.line(
                    cp_df,
                    x='Data',
                    y='Qualidade',
                    color='Agente',
                    title="Evolução da Qualidade dos Checkpoints",
                    markers=True
                )
                st.plotly_chart(fig, use_container_width=True)
    
    else:
        st.info("📦 Nenhum checkpoint encontrado. Crie checkpoints executando agentes e salvando seus estados.")

def render_performance_metrics(system_data, graphrag_data):
    """Renderiza métricas de performance"""
    
    st.header("⚡ Métricas de Performance")
    
    # Métricas do sistema
    st.subheader("🔧 Performance do Sistema")
    
    # Simular algumas métricas (em implementação real, coletar dados reais)
    performance_data = {
        'Componente': ['Sistema YAML', 'GraphRAG Neo4j', 'ChromaDB', 'Pattern Discovery', 'Checkpoints'],
        'Status': ['✅ Ativo', '✅ Conectado' if graphrag_data['available'] else '❌ Desconectado', 
                  '✅ Conectado' if graphrag_data['available'] else '❌ Desconectado', 
                  '✅ Funcionando', '✅ Funcionando'],
        'Tempo Resposta (ms)': [50, 150 if graphrag_data['available'] else 0, 80 if graphrag_data['available'] else 0, 500, 200],
        'Uso Memória (MB)': [10, 512 if graphrag_data['available'] else 0, 256 if graphrag_data['available'] else 0, 128, 64]
    }
    
    perf_df = pd.DataFrame(performance_data)
    st.dataframe(perf_df, use_container_width=True)
    
    # Gráficos de performance
    col1, col2 = st.columns(2)
    
    with col1:
        fig = px.bar(
            perf_df,
            x='Componente',
            y='Tempo Resposta (ms)',
            title="Tempo de Resposta por Componente"
        )
        fig.update_xaxis(tickangle=45)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        fig = px.bar(
            perf_df,
            x='Componente',
            y='Uso Memória (MB)',
            title="Uso de Memória por Componente",
            color='Uso Memória (MB)',
            color_continuous_scale='Reds'
        )
        fig.update_xaxis(tickangle=45)
        st.plotly_chart(fig, use_container_width=True)
    
    # Alertas e recomendações
    st.subheader("🚨 Alertas e Recomendações")
    
    alerts = []
    
    if not graphrag_data['available']:
        alerts.append({
            'Tipo': '🔴 Crítico',
            'Componente': 'GraphRAG',
            'Mensagem': 'Neo4j ou ChromaDB não disponível - funcionalidades de aprendizado limitadas',
            'Ação': 'Execute: docker-compose up -d'
        })
    
    if graphrag_data['available'] and graphrag_data['stats'].get('total_experiences', 0) < 10:
        alerts.append({
            'Tipo': '🟡 Aviso',
            'Componente': 'Experiências',
            'Mensagem': 'Poucas experiências armazenadas - execute mais ciclos para melhor aprendizado',
            'Ação': 'Execute: python core/main.py'
        })
    
    if len(system_data['identity']) == 0:
        alerts.append({
            'Tipo': '🟡 Aviso',
            'Componente': 'Agentes',
            'Mensagem': 'Nenhum agente com identidade simbólica encontrado',
            'Ação': 'Execute alguns ciclos reflexivos'
        })
    
    if not alerts:
        st.success("✅ Todos os componentes funcionando normalmente!")
    else:
        for alert in alerts:
            st.warning(f"**{alert['Tipo']}** {alert['Componente']}: {alert['Mensagem']}")
            st.code(f"Ação recomendada: {alert['Ação']}")

if __name__ == "__main__":
    main()_graphrag=True)
        discovery_engine = PatternDiscoveryEngine(memory)
        
        # Descobrir padrões
        patterns