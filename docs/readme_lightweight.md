# 🚀 RSCA com Modelos Leves - Guia Rápido

## 🎯 Objetivo

Configurar o **Reflexive Self Coding Assistant** para funcionar com modelos LLM leves (1B-2B parâmetros) que rodam eficientemente em máquinas de desenvolvimento com RAM limitada.

## ⚡ Setup Rápido (5 minutos)

### 1. **Setup Automático**
```bash
# Setup completo em um comando
python quick_setup_lightweight.py
```

### 2. **Setup Manual** (se automático falhar)

#### Passo 1: Docker
```bash
# Iniciar containers
docker-compose up -d

# Aguardar Ollama inicializar (30-60s)
docker-compose logs ollama
```

#### Passo 2: Instalar Modelos
```bash
# Modelo ultra-leve para testes
ollama pull tinyllama:1.1b

# Modelo especializado em código  
ollama pull codegemma:2b

# Modelo equilibrado
ollama pull phi3:mini
```

#### Passo 3: Testar Sistema
```bash
python test_lightweight_models.py
```

## 📦 Modelos Recomendados

| Modelo | Tamanho | RAM | Velocidade | Especialidade |
|--------|---------|-----|------------|---------------|
| **TinyLlama 1.1B** | ~800MB | ~1GB | ⚡ Muito rápido | Testes rápidos |
| **CodeGemma 2B** | ~1.5GB | ~2GB | 🔄 Médio | 💻 **Código** |
| **Phi3 Mini** | ~2GB | ~2.5GB | 🔄 Médio | 📚 Equilibrado |
| **Llama 3.2 1B** | ~1GB | ~1.5GB | ⚡ Rápido | Tarefas simples |

### 🎯 Modelo Recomendado por Tarefa

```python
# Configuração automática no sistema
TASK_MODELS = {
    "codigo": "codegemma:2b",      # Melhor para programação
    "testes": "tinyllama:1.1b",    # Rápido para testes
    "documentacao": "phi3:mini",   # Equilibrado para texto
    "analise": "phi3:mini"         # Análise geral
}
```

## 🧪 Testando o Sistema

### Teste Completo
```bash
python test_lightweight_models.py
```

### Teste Rápido
```bash
# Verificar modelos instalados
ollama list

# Teste manual
curl http://localhost:11434/api/tags
```

### Exemplo de Uso
```python
from core.agents.code_agent import CodeAgent

# Criar agente com modelos leves
agent = CodeAgent(use_mock=False)

# Gerar código (usa automaticamente CodeGemma 2B)
result = agent.execute_task("Criar função que calcula fibonacci")

print(f"Sucesso: {result.success}")
print(f"Qualidade: {result.quality_score}/10")
print(f"Código:\n{result.code}")
```

## 🔄 Executando o Sistema Completo

### Modo Desenvolvimento
```bash
# Execução única
python core/main.py

# Dashboard visual
streamlit run interface/dashboard/streamlit_app.py

# Ciclos automáticos
python scripts/scheduler.py
```

### Monitoramento
```bash
# Status dos containers
docker-compose ps

# Logs do Ollama
docker-compose logs -f ollama

# Uso de recursos
docker stats
```

## ⚙️ Configurações Avançadas

### Otimização por RAM Disponível

#### 🟢 **2-4GB RAM Disponível**
```python
# Use apenas TinyLlama
PREFERRED_MODEL = "tinyllama:1.1b"
MAX_CONCURRENT_MODELS = 1
```

#### 🟡 **4-6GB RAM Disponível** 
```python
# CodeGemma para código, TinyLlama para testes
MODELS = {
    "code": "codegemma:2b",
    "other": "tinyllama:1.1b"
}
```

#### 🟢 **6GB+ RAM Disponível**
```python
# Configuração completa recomendada
MODELS = {
    "code": "codegemma:2b",
    "docs": "phi3:mini", 
    "tests": "tinyllama:1.1b"
}
```

### Ajustes de Performance

```python
# config/lightweight_config.py
OLLAMA_CONFIG = {
    "timeout": 60,          # Timeout mais longo para modelos leves
    "retry_attempts": 2,    # Tentativas em caso de falha
    "temperature": 0.1,     # Menos criatividade, mais precisão
    "max_tokens": 1024,     # Respostas mais concisas
}
```

## 🔧 Solução de Problemas

### ❌ **Ollama não conecta**
```bash
# Verificar se container está rodando
docker-compose ps

# Reiniciar se necessário
docker-compose restart ollama

# Verificar logs
docker-compose logs ollama
```

### ❌ **Modelo não encontrado**
```bash
# Listar modelos instalados
ollama list

# Instalar modelo específico
ollama pull codegemma:2b

# Verificar se modelo funciona
ollama run codegemma:2b "def hello(): return"
```

### ❌ **Erro de RAM/Timeout**
```bash
# Verificar uso de RAM
free -h

# Matar processos que consomem RAM
docker stats
docker-compose down

# Usar apenas o modelo mais leve
ollama run tinyllama:1.1b
```

### ❌ **Código gerado com baixa qualidade**
```python
# Ajustar configurações do modelo
GENERATION_CONFIG = {
    "temperature": 0.05,    # Mais determinístico
    "top_p": 0.85,         # Menos aleatoriedade
    "repeat_penalty": 1.2  # Evitar repetições
}
```

### ❌ **Sistema lento**
```bash
# Usar modelo mais rápido
export PREFERRED_MODEL="tinyllama:1.1b"

# Reduzir tamanho das respostas
export MAX_TOKENS=512

# Verificar se há outros processos pesados
htop
```

## 📊 Métricas de Performance

### Benchmarks Esperados

| Modelo | Tempo Médio | Qualidade | RAM Peak | Recomendação |
|--------|-------------|-----------|----------|--------------|
| TinyLlama 1.1B | ~3-5s | 6/10 | ~1GB | ✅ Desenvolvimento rápido |
| CodeGemma 2B | ~8-12s | 8/10 | ~2GB | ✅ **Melhor equilíbrio** |
| Phi3 Mini | ~10-15s | 7.5/10 | ~2.5GB | ✅ Tarefas mistas |

### Qualidade do Código Esperada

```
✅ Sintaxe correta: >95%
✅ Funcionalidade básica: >85%
✅ Boas práticas: >70%
✅ Documentação: >60%
⚠️ Otimização avançada: ~40%
⚠️ Arquiteturas complexas: ~30%
```

## 🎯 Casos de Uso Ideais

### ✅ **Funciona Muito Bem**
- Funções simples e utilitárias
- Scripts de automação
- Testes unitários básicos
- Documentação de código
- Prototipagem rápida
- Refatoração simples

### ⚠️ **Funciona com Limitações**
- APIs REST complexas
- Algoritmos avançados
- Design patterns elaborados
- Otimizações de performance
- Arquiteturas de sistema

### ❌ **Não Recomendado**
- Sistemas distribuídos complexos
- Machine Learning/IA avançada
- Otimizações de baixo nível
- Arquiteturas enterprise
- Código crítico de produção sem revisão

## 🔮 Roadmap e Próximos Passos

### Fase Atual: Modelos Leves Funcionais
- [x] Setup de modelos 1B-2B
- [x] Integração com CodeAgent
- [x] Testes automatizados
- [x] Dashboard básico

### Próxima Fase: GraphRAG + Especialização
- [ ] Implementar GraphRAG para experiências
- [ ] Sistema de checkpoints de agentes
- [ ] Especialização automática por domínio
- [ ] Transfer learning entre projetos

### Fase Futura: Ecosystem de Agentes
- [ ] Repositório de agentes especializados
- [ ] Agentes colaborativos
- [ ] Otimização automática de performance
- [ ] Integração com IDEs

## 💡 Dicas de Produtividade

### Para Desenvolvimento Diário
```bash
# Alias úteis para .bashrc
alias rsca-start="docker-compose up -d && sleep 30"
alias rsca-test="python test_lightweight_models.py"
alias rsca-run="python core/main.py"
alias rsca-dash="streamlit run interface/dashboard/streamlit_app.py"
alias rsca-status="docker-compose ps && ollama list"
```

### Workflow Recomendado
1. **Manhã**: `rsca-start` para inicializar
2. **Desenvolvimento**: Use CodeGemma 2B para código principal
3. **Testes**: TinyLlama para validação rápida
4. **Documentação**: Phi3 Mini para textos
5. **Fim do dia**: `docker-compose down` para economizar recursos

### Integração com IDE
```python
# .vscode/tasks.json
{
    "version": "2.0.0",
    "tasks": [
        {
            "label": "RSCA Generate Code",
            "type": "shell",
            "command": "python -c \"from core.agents.code_agent import CodeAgent; agent = CodeAgent(); result = agent.execute_task('${input:task}'); print(result.code)\""
        }
    ]
}
```

## 📚 Recursos Adicionais

### Documentação
- [Arquitetura Geral](docs/ARCHITECTURE.md)
- [Guia de Performance](docs/PERFORMANCE.md) 
- [API Reference](docs/API_REFERENCE.md)
- [Solução de Problemas](docs/TROUBLESHOOTING.md)

### Comunidade
- **Issues**: Reporte problemas específicos com modelos leves
- **Discussions**: Compartilhe configurações otimizadas
- **Wiki**: Casos de uso e exemplos da comunidade

### Monitoramento
```bash
# Script de monitoramento contínuo
watch -n 5 'echo "=== RSCA Status ===" && docker-compose ps && echo && ollama list && echo && free -h'
```

## ⚡ Quick Reference

### Comandos Essenciais
```bash
# Setup completo
python quick_setup_lightweight.py

# Teste rápido
python test_lightweight_models.py

# Executar sistema
python core/main.py

# Dashboard
streamlit run interface/dashboard/streamlit_app.py

# Status
docker-compose ps && ollama list
```

### Modelos por Situação
- **🚀 Pressa/RAM baixa**: `tinyllama:1.1b`
- **💻 Código importante**: `codegemma:2b`  
- **📚 Texto/Docs**: `phi3:mini`
- **🔬 Experimentação**: `llama3.2:1b`

---

## 🎉 Pronto para Começar!

Se seguiu este guia, seu RSCA deve estar funcionando com modelos leves e otimizado para desenvolvimento. 

**Próximo passo**: Execute `python test_lightweight_models.py` e veja a mágica acontecer! 🪄