import streamlit as st
import yaml
import json
import pandas as pd
from datetime import datetime
from pathlib import Path
import sys

# Configurar paths
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent # Corrigido para apontar para a raiz do projeto
sys.path.append(str(PROJECT_ROOT))

# Configuração da página
st.set_page_config(
    page_title="RSCA - Dashboard Simples", 
    layout="wide",
    initial_sidebar_state="expanded"
)

def load_identity():
    """Carrega dados de identidade"""
    try:
        identity_file = PROJECT_ROOT / "reflection" / "state" / "identity" / "identity_state.yaml"
        with open(identity_file, "r", encoding="utf-8") as f:
            return yaml.safe_load(f) or {}
    except Exception as e:
        st.error(f"Erro ao carregar identidade: {e}")
        return {}

def load_history():
    """Carrega histórico"""
    try:
        history_file = PROJECT_ROOT / "reflection" / "state" / "temporal" / "cycle_history.json"
        with open(history_file, "r", encoding="utf-8") as f:
            return json.load(f) or {}
    except Exception as e:
        st.warning(f"Histórico não disponível: {e}")
        return {}

def main():
    """Dashboard principal"""
    st.title("🤖 RSCA - Dashboard Simplificado")
    st.markdown("**Reflexive Self Coding Assistant** - Monitoramento Pós-Migração")
    
    # Status da migração
    st.header("📊 Status da Migração")
    
    # Verificar se analysis_history.md foi removido
    analysis_md = PROJECT_ROOT / "reflection" / "analysis_history.md"
    md_removed = not analysis_md.exists()
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            "analysis_history.md", 
            "✅ Removido" if md_removed else "❌ Ainda existe",
            "Migração bem-sucedida" if md_removed else "Necessita atenção"
        )
    
    with col2:
        # Verificar GraphRAG
        try:
            from memory.graph_rag.graph_interface import GraphMemory
            graph = GraphMemory()
            graph.close()
            graphrag_status = "✅ Funcionando"
        except:
            graphrag_status = "⚠️ Mock Mode"
        
        st.metric("GraphRAG", graphrag_status)
    
    with col3:
        # Verificar ReflectionAgent
        try:
            from core.agents.reflection_agent import ReflectionAgent
            agent = ReflectionAgent()
            agent_status = "❌ MD Ativo" if agent.enable_md_logging else "✅ GraphRAG Only"
            agent.close()
        except Exception as e:
            agent_status = f"❌ Erro: {str(e)[:20]}"
        
        st.metric("ReflectionAgent", agent_status)
    
    # Dados dos agentes
    st.header("🧠 Estado dos Agentes")
    
    identity_data = load_identity()
    history_data = load_history()
    
    if identity_data:
        for agent_name, profile in identity_data.items():
            with st.expander(f"🤖 {agent_name}"):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write(f"**Padrão:** {profile.get('predominant_pattern', 'N/A')}")
                    st.write(f"**Consistência:** {profile.get('consistency_level', 'N/A')}")
                    st.write(f"**Última adaptação:** {profile.get('last_adaptation', 'N/A')}")
                
                with col2:
                    traits = profile.get('traits', [])
                    if traits:
                        st.write(f"**Traços:** {', '.join(traits)}")
                    
                    # Mostrar experiências se disponível
                    total_exp = profile.get('total_experiences', 0)
                    if total_exp > 0:
                        st.write(f"**Experiências:** {total_exp}")
                        
                        avg_quality = profile.get('avg_quality_score', 0)
                        st.write(f"**Qualidade média:** {avg_quality:.2f}")
    
    # Histórico de padrões
    st.header("📈 Histórico de Padrões")
    
    if history_data:
        for agent_name, patterns in history_data.items():
            if patterns:
                st.subheader(f"📊 {agent_name}")
                
                # Criar DataFrame para visualização
                pattern_counts = {}
                for pattern in patterns:
                    pattern_counts[pattern] = pattern_counts.get(pattern, 0) + 1
                
                if pattern_counts:
                    df = pd.DataFrame(list(pattern_counts.items()), 
                                    columns=['Padrão', 'Frequência'])
                    st.bar_chart(df.set_index('Padrão'))
    
    # Informações de sistema
    st.header("🔧 Informações do Sistema")
    
    system_info = {
        "Python": sys.version.split()[0],
        "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "Projeto": str(PROJECT_ROOT),
    }
    
    for key, value in system_info.items():
        st.write(f"**{key}:** {value}")
    
    # Logs recentes
    st.header("📝 Status dos Logs")
    
    log_files = [
        ("System Log", PROJECT_ROOT / "logs" / "system.log"),
        ("Identity State", PROJECT_ROOT / "reflection" / "state" / "identity" / "identity_state.yaml"),
        ("Cycle History", PROJECT_ROOT / "reflection" / "state" / "temporal" / "cycle_history.json")
    ]
    
    for log_name, log_path in log_files:
        if log_path.exists():
            size = log_path.stat().st_size
            st.write(f"✅ **{log_name}:** {size} bytes")
        else:
            st.write(f"❌ **{log_name}:** Não encontrado")
    
    # Instruções
    st.header("💡 Próximos Passos")
    
    st.markdown("""
    ### ✅ Migração Concluída com Sucesso!
    
    O sistema está funcionando sem `analysis_history.md`:
    
    1. **Execute ciclos:** `python core/main.py`
    2. **Monitore este dashboard** para acompanhar evolução
    3. **Configure Neo4j** se quiser GraphRAG completo: `python scripts/setup_neo4j.py`
    4. **Limpe backups antigos** após algumas semanas
    
    ### 🔧 Comandos Úteis:
    ```bash
    # Testar sistema
    python scripts/test_neo4j.py
    
    # Executar ciclos
    python core/main.py
    
    # Configurar Neo4j
    python scripts/setup_neo4j.py
    ```
    """)

if __name__ == "__main__":
    main()
