#!/bin/bash
# cleanup_large_models.sh
# Remove modelos grandes desnecessários e otimiza o sistema

echo "🧹 LIMPEZA DE MODELOS GRANDES"
echo "============================================"

# Verificar se Ollama está rodando
if ! curl -s http://localhost:11434/api/tags >/dev/null 2>&1; then
    echo "❌ Ollama não está rodando!"
    echo "💡 Execute: docker-compose up -d"
    exit 1
fi

echo "✅ Ollama está rodando"

# Listar modelos atuais
echo ""
echo "📦 MODELOS ATUALMENTE INSTALADOS:"
ollama list

# Identificar modelos grandes para remoção
LARGE_MODELS_TO_REMOVE=(
    "llama3:8b"
    "llama3:15b" 
    "llama3:70b"
    "codellama:7b"
    "codellama:13b"
    "codellama:34b"
    "mistral:7b"
    "mixtral:8x7b"
    "llama2:7b"
    "llama2:13b"
    "llama2:70b"
    "vicuna:7b"
    "vicuna:13b"
    "orca-mini:7b"
    "orca-mini:13b"
    "wizardcoder:7b"
    "wizardcoder:13b"
)

# Modelos leves que devemos manter
KEEP_MODELS=(
    "tinyllama:1.1b"
    "llama3.2:1b"
    "codegemma:2b"
    "phi3:mini"
    "qwen2:0.5b"
    "qwen2:1.5b"
)

echo ""
echo "🔍 ANALISANDO MODELOS PARA REMOÇÃO..."

# Obter lista de modelos instalados
INSTALLED_MODELS=$(ollama list | tail -n +2 | awk '{print $1}')

removed_count=0
kept_count=0
total_size_freed=0

echo ""
echo "🗑️ REMOVENDO MODELOS GRANDES:"

for model in "${LARGE_MODELS_TO_REMOVE[@]}"; do
    if echo "$INSTALLED_MODELS" | grep -q "^$model$"; then
        echo "   🗑️ Removendo $model..."
        
        # Obter tamanho antes de remover (aproximado)
        model_info=$(ollama list | grep "^$model")
        if [[ $model_info == *"GB"* ]]; then
            size=$(echo "$model_info" | grep -o '[0-9.]*GB' | head -1)
            echo "      Liberando ~$size"
        fi
        
        if ollama rm "$model" 2>/dev/null; then
            echo "      ✅ $model removido"
            ((removed_count++))
        else
            echo "      ⚠️ Erro ao remover $model"
        fi
    fi
done

echo ""
echo "✅ MODELOS MANTIDOS (leves e eficientes):"

# Verificar modelos que devemos manter
for model in "${KEEP_MODELS[@]}"; do
    if echo "$INSTALLED_MODELS" | grep -q "^$model$"; then
        echo "   ✅ $model (mantido)"
        ((kept_count++))
    else
        echo "   ⚠️ $model (não instalado - recomendado)"
    fi
done

echo ""
echo "============================================"
echo "📊 RESUMO DA LIMPEZA:"
echo "============================================"
echo "🗑️ Modelos removidos: $removed_count"
echo "✅ Modelos mantidos: $kept_count"

# Status após limpeza
echo ""
echo "📦 MODELOS APÓS LIMPEZA:"
ollama list

# Verificar espaço em disco
echo ""
echo "💾 USO DE ESPAÇO:"
if command -v du >/dev/null 2>&1; then
    ollama_size=$(du -sh ~/.ollama 2>/dev/null || echo "Não foi possível calcular")
    echo "   Diretório Ollama: $ollama_size"
fi

# Recomendações
echo ""
echo "💡 RECOMENDAÇÕES PÓS-LIMPEZA:"

# Verificar se temos modelos leves suficientes
current_models=$(ollama list | tail -n +2 | awk '{print $1}')
has_tinyllama=$(echo "$current_models" | grep -q "tinyllama:1.1b" && echo "yes" || echo "no")
has_codegemma=$(echo "$current_models" | grep -q "codegemma:2b" && echo "yes" || echo "no")
has_phi3=$(echo "$current_models" | grep -q "phi3:mini" && echo "yes" || echo "no")

if [[ "$has_tinyllama" == "no" ]] || [[ "$has_codegemma" == "no" ]]; then
    echo ""
    echo "⚠️ MODELOS RECOMENDADOS AUSENTES:"
    
    if [[ "$has_tinyllama" == "no" ]]; then
        echo "   📥 Instalar TinyLlama: ollama pull tinyllama:1.1b"
    fi
    
    if [[ "$has_codegemma" == "no" ]]; then
        echo "   📥 Instalar CodeGemma: ollama pull codegemma:2b"
    fi
    
    if [[ "$has_phi3" == "no" ]]; then
        echo "   📥 Instalar Phi3: ollama pull phi3:mini"
    fi
    
    echo ""
    echo "🚀 INSTALAR TODOS DE UMA VEZ:"
    echo "   bash scripts/setup_lightweight_models.sh"
else
    echo "✅ Você tem os modelos essenciais instalados!"
fi

echo ""
echo "⚡ PRÓXIMOS PASSOS:"
echo "   1. Testar sistema: python test_lightweight_models.py"
echo "   2. Demo completo: python demo_lightweight_rsca.py"
echo "   3. Executar RSCA: python core/main.py"

# Verificar RAM liberada
echo ""
echo "🧠 BENEFÍCIOS DA LIMPEZA:"
echo "   • RAM liberada: Cada modelo 7B+ libera ~4-8GB"
echo "   • Velocidade: Modelos leves respondem 3-5x mais rápido"
echo "   • Desenvolvimento: Foco em modelos otimizados para código"
echo "   • Estabilidade: Menos chance de timeout/out-of-memory"

echo ""
echo "✨ Limpeza concluída! Sistema otimizado para desenvolvimento."