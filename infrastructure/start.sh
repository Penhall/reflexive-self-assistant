#!/bin/bash
# Script de inicialização para container RSCA

echo "🚀 Iniciando Reflexive Self Coding Assistant..."

# Aguardar serviços dependentes
echo "⏳ Aguardando Neo4j..."
while ! nc -z neo4j 7687; do
  sleep 1
done

echo "⏳ Aguardando ChromaDB..."
while ! nc -z chromadb 8000; do
  sleep 1
done

echo "⏳ Aguardando Ollama..."
while ! nc -z ollama 11434; do
  sleep 1
done

echo "✅ Todos os serviços estão disponíveis!"

# Configurar diretórios
python -c "from config.paths import ensure_directories; ensure_directories()"

# Iniciar aplicação
if [ "$1" = "dashboard" ]; then
    echo "🖥️ Iniciando Dashboard..."
    streamlit run interface/dashboard/streamlit_app.py --server.port=8501 --server.address=0.0.0.0
elif [ "$1" = "api" ]; then
    echo "🌐 Iniciando API..."
    python interface/api/rest_api.py
else
    echo "🔄 Iniciando modo padrão (ciclos reflexivos)..."
    python core/main.py
fi