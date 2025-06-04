import streamlit as st
import yaml
import json
from datetime import datetime
from collections import Counter
import pandas as pd
from pathlib import Path
import sys

# Adicionar diretório raiz ao path do Python
sys.path.append(str(Path(__file__).parent.parent.parent.parent)) # Corrigido para apontar para a raiz do projeto

from config.paths import IDENTITY_STATE, CYCLE_HISTORY

st.set_page_config(page_title="Reflexive Self Dashboard", layout="wide")

def load_identity():
    try:
        with open(str(IDENTITY_STATE), "r", encoding="utf-8") as f:
            return yaml.safe_load(f)
    except:
        return {}

def load_history():
    try:
        with open(str(CYCLE_HISTORY), "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {}

identity = load_identity()
history = load_history()

st.title("🤖 Painel de Identidade Simbólica dos Agentes")
st.sidebar.header("🔄 Atualização e Filtros")

if st.sidebar.button("Recarregar dados"):
    st.experimental_rerun()

filter_consistency = st.sidebar.selectbox("Filtrar por consistência", ["Todos", "Alta", "Moderada", "Baixa"])

# Estatísticas agregadas
st.subheader("📊 Estatísticas Simbólicas Gerais")
consistency_counts = Counter([v.get("consistency_level", "Desconhecido") for v in identity.values()])
most_common_traits = Counter(t for v in identity.values() for t in v.get("traits", []))

st.markdown(f"- Agentes com consistência alta: **{consistency_counts.get('Alta', 0)}**")
st.markdown(f"- Traço simbólico mais comum: **{most_common_traits.most_common(1)[0][0] if most_common_traits else '-'}**")

# Tabela de visão geral
st.markdown("### 🧾 Visão Geral dos Agentes")
table_data = []
for name, data in identity.items():
    table_data.append({
        "Agente": name,
        "Padrão": data.get("predominant_pattern", "-"),
        "Consistência": data.get("consistency_level", "-"),
        "Traços": ", ".join(data.get("traits", [])),
        "Recomendação": data.get("adaptive_hint", "-")
    })

df = pd.DataFrame(table_data)
if filter_consistency != "Todos":
    df = df[df["Consistência"] == filter_consistency]
st.dataframe(df)

# Detalhamento por agente
for agent_name, profile in identity.items():
    if filter_consistency != "Todos" and profile.get("consistency_level") != filter_consistency:
        continue

    col1, col2 = st.columns([2, 1])

    with col1:
        st.subheader(f"🧠 {agent_name}")
        st.markdown(f"""
        - **Padrão predominante:** `{profile.get("predominant_pattern", "-")}`
        - **Consistência:** `{profile.get("consistency_level", "-")}`
        - **Última adaptação:** `{profile.get("last_adaptation", "-")}`
        - **Traços simbólicos:** {", ".join(profile.get("traits", [])) or "-"}
        """)

        hint = profile.get("adaptive_hint")
        if hint:
            if "⚠️" in hint:
                st.error(hint)
            elif "ℹ️" in hint:
                st.info(hint)
            else:
                st.warning(hint)
        else:
            st.success("Nenhuma recomendação adaptativa no momento.")

    with col2:
        st.markdown("### 📈 Histórico de Padrões")
        last_patterns = history.get(agent_name, [])[-5:]
        for i, pattern in enumerate(reversed(last_patterns), 1):
            st.markdown(f"{i}. `{pattern}`")

    st.markdown("---")

# Exportar como relatório (HTML simples)
if st.sidebar.button("📤 Exportar relatório HTML"):
    export_path = Path("logs/symbolic_dashboard_export.html")
    with open(export_path, "w", encoding="utf-8") as f:
        f.write(df.to_html(index=False))
    st.sidebar.success(f"Relatório salvo em {export_path}")

st.caption("Última atualização: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

#  Gerar relatório completo
if st.sidebar.button("📄 Gerar Relatório Completo"):
    st.system("python generate_report.py")
    
def exibir_legado_simbólico():
    legacy_path = Path("reflection/symbolic_legacy.yaml")
    if not legacy_path.exists():
        st.warning("⚠️ Nenhum legado simbólico encontrado ainda.")
        return

    with legacy_path.open("r", encoding="utf-8") as f:
        legado = yaml.safe_load(f).get("legado_simbólico", {})

    st.markdown("## 🏁 Encerramento Simbólico do Sistema")

    st.write(f"**🧠 Identidade final:** {legado.get('identidade_final', '---')}")
    st.write(f"**🎭 Emoção final:** {legado.get('emoção_final', '---')}")
    st.write(f"**🔁 Ciclos concluídos:** {legado.get('ciclos_concluídos', '---')}")
    st.write(f"**🧩 Padrão superado:** {legado.get('padrão_superado') or 'Nenhum'}")
    st.write(f"**⚖️ Contradições corrigidas:** {legado.get('contradições_corrigidas', 0)}")

    st.markdown("### 📘 Legado Narrativo")
    st.info(legado.get("narrativa", "Nenhuma narrativa disponível."))

# Chamar a função no app principal
if st.sidebar.checkbox("🧾 Ver Legado Simbólico"):
    exibir_legado_simbólico()
