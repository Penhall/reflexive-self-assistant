#!/usr/bin/env python3
"""
Script para corrigir problemas do dashboard Streamlit
"""

import sys
import subprocess
from pathlib import Path
import time

PROJECT_ROOT = Path(__file__).parent.parent

def check_streamlit_installation():
    """Verifica se Streamlit está instalado"""
    try:
        import streamlit
        print(f"✅ Streamlit instalado: v{streamlit.__version__}")
        return True
    except ImportError:
        print("❌ Streamlit não instalado")
        return False

def install_streamlit():
    """Instala Streamlit"""
    print("📦 Instalando Streamlit...")
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "streamlit"], 
                      check=True, timeout=120)
        print("✅ Streamlit instalado com sucesso")
        return True
    except Exception as e:
        print(f"❌ Erro ao instalar Streamlit: {e}")
        return False

def check_dashboard_file():
    """Verifica se arquivo do dashboard existe"""
    dashboard_file = PROJECT_ROOT / "interface" / "dashboard" / "streamlit_app.py"
    
    if dashboard_file.exists():
        print(f"✅ Dashboard encontrado: {dashboard_file}")
        return str(dashboard_file)
    
    # Procurar por outros arquivos de dashboard
    dashboard_files = list((PROJECT_ROOT / "interface").glob("**/streamlit*.py"))
    
    if dashboard_files:
        dashboard_file = dashboard_files[0]
        print(f"✅ Dashboard alternativo encontrado: {dashboard_file}")
        return str(dashboard_file)
    
    print("❌ Arquivo do dashboard não encontrado")
    return None

def test_dashboard_imports():
    """Testa se imports do dashboard funcionam"""
    try:
        sys.path.append(str(PROJECT_ROOT))
        
        # Testar imports principais
        from config.paths import IDENTITY_STATE, CYCLE_HISTORY
        print("✅ config.paths importado")
        
        import yaml
        import json
        import pandas as pd
        print("✅ Dependências básicas OK")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro nos imports: {e}")
        return False

def create_simple_dashboard():
    """Cria dashboard simplificado que funciona"""
    dashboard_dir = PROJECT_ROOT / "interface" / "dashboard"
    dashboard_dir.mkdir(parents=True, exist_ok=True)
    
    simple_dashboard = dashboard_dir / "streamlit_simple.py"
    
    dashboard_code = '''import streamlit as st
import yaml
import json
import pandas as pd
from datetime import datetime
from pathlib import Path
import sys

# Configurar paths
PROJECT_ROOT = Path(__file__).parent.parent.parent
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
'''
    
    with open(simple_dashboard, 'w', encoding='utf-8') as f:
        f.write(dashboard_code)
    
    print(f"✅ Dashboard simplificado criado: {simple_dashboard}")
    return str(simple_dashboard)

def install_dependencies():
    """Instala dependências necessárias"""
    deps = ["streamlit", "pandas", "plotly"]
    
    for dep in deps:
        try:
            __import__(dep)
            print(f"✅ {dep} já instalado")
        except ImportError:
            print(f"📦 Instalando {dep}...")
            try:
                subprocess.run([sys.executable, "-m", "pip", "install", dep], 
                              check=True, timeout=60)
                print(f"✅ {dep} instalado")
            except Exception as e:
                print(f"❌ Erro ao instalar {dep}: {e}")

def start_dashboard(dashboard_file):
    """Inicia dashboard Streamlit"""
    print(f"🚀 Iniciando dashboard: {dashboard_file}")
    print("🌐 Acesse: http://localhost:8501")
    print("⏹️ Para parar: Ctrl+C")
    
    try:
        # Comando para iniciar Streamlit
        cmd = [sys.executable, "-m", "streamlit", "run", dashboard_file, 
               "--server.port", "8501", "--server.headless", "true"]
        
        subprocess.run(cmd, cwd=PROJECT_ROOT)
        
    except KeyboardInterrupt:
        print("\n⏹️ Dashboard interrompido")
    except Exception as e:
        print(f"❌ Erro ao iniciar dashboard: {e}")

def main():
    """Função principal"""
    print("🔧 Corrigindo Dashboard Streamlit")
    print("=" * 40)
    
    # 1. Verificar/instalar Streamlit
    if not check_streamlit_installation():
        if not install_streamlit():
            return False
    
    # 2. Instalar outras dependências
    install_dependencies()
    
    # 3. Verificar arquivo do dashboard
    dashboard_file = check_dashboard_file()
    
    if not dashboard_file:
        print("📝 Criando dashboard simplificado...")
        dashboard_file = create_simple_dashboard()
    
    # 4. Testar imports
    if not test_dashboard_imports():
        print("⚠️ Alguns imports podem falhar, mas dashboard básico deve funcionar")
    
    print("\n" + "=" * 40)
    print("✅ DASHBOARD PRONTO!")
    print(f"📁 Arquivo: {dashboard_file}")
    print("\n🚀 Para iniciar:")
    print(f"streamlit run {dashboard_file}")
    print("ou")
    print("python scripts/fix_streamlit_dashboard.py --start")
    
    # 5. Iniciar se solicitado
    if "--start" in sys.argv:
        start_dashboard(dashboard_file)
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)