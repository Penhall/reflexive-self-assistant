# Instruções de Execução RSCA - GraphRAG Evolution
**Data:** 29 de Maio de 2025  
**Status:** Arquivos Gerados e Prontos  
**Pré-requisito:** Todos os arquivos já salvos nas pastas corretas  

---

## 🎯 **OVERVIEW DE EXECUÇÃO**

Como todos os arquivos necessários já foram gerados e salvos, este guia foca na **execução sequencial** e **validação** de cada componente, sem repetir comandos de criação de arquivos.

### **Estrutura de Execução por Fase**
1. **Validação Inicial** - Verificar se todos os arquivos estão no lugar
2. **Setup de Infraestrutura** - Ativar serviços Docker
3. **Execução Sequencial** - Testar cada componente
4. **Validação Contínua** - Confirmar funcionamento
5. **Testes Integrados** - Validar sistema completo

---

## ✅ **FASE 1: VALIDAÇÃO INICIAL**

### **Verificar Arquivos Principais**
```bash
# Verificar se estrutura está correta
ls -la infrastructure/docker-compose.yml
ls -la memory/hybrid_store.py
ls -la core/agents/code_agent_enhanced.py
ls -la memory/pattern_discovery.py
ls -la scripts/tests/test_graphrag_integration.py
ls -la evolution/checkpointing/agent_checkpoints.py
ls -la interface/dashboard/streamlit_advanced.py
```

**Resultado Esperado:** Todos os arquivos devem existir e ter conteúdo.

### **Verificar Dependências Python**
```bash
# Instalar dependências necessárias (apenas se não instaladas)
pip install neo4j chromadb sentence-transformers scikit-learn networkx plotly streamlit pandas
```

### **Verificar Docker**
```bash
# Confirmar Docker funcionando
docker --version
docker-compose --version

# Verificar portas livres (importantes)
netstat -an | grep -E ":(7474|7687|8000|11434)"
```

**Se portas estiverem ocupadas:** Parar serviços ou alterar portas no docker-compose.yml

---

## 🐳 **FASE 2: SETUP DE INFRAESTRUTURA**

### **Inicializar Serviços**
```bash
# Navegar para diretório do projeto
cd /caminho/para/reflexive-self-assistant

# Inicializar todos os serviços
docker-compose -f infrastructure/docker-compose.yml up -d

# Aguardar inicialização (importante!)
sleep 60

# Verificar status dos serviços
docker-compose -f infrastructure/docker-compose.yml ps
```

**Resultado Esperado:**
```
         Name                        Command                  State                          Ports
---------------------------------------------------------------------------------------------------------
rsca-chromadb            ./docker-entrypoint.sh           Up             0.0.0.0:8000->8000/tcp
rsca-neo4j               tini -g -- /docker-entryp ...   Up             0.0.0.0:7474->7474/tcp, 0.0.0.0:7687->7687/tcp
rsca-ollama              /bin/ollama serve                Up             0.0.0.0:11434->11434/tcp
```

### **Verificar Conectividade**
```bash
# Testar Neo4j
curl http://localhost:7474

# Testar ChromaDB
curl http://localhost:8000/api/v1/heartbeat

# Testar Ollama
curl http://localhost:11434/api/tags
```

### **Configurar Neo4j (Primeira vez)**
```bash
# Acessar Neo4j Browser: http://localhost:7474
# Usuário: neo4j
# Senha: rsca_secure_2025

# Executar schema (via browser ou comando)
docker exec rsca-neo4j cypher-shell -u neo4j -p rsca_secure_2025 -f /docker-entrypoint-initdb.d/01_schema.cypher
```

---

## 🧪 **FASE 3: EXECUÇÃO SEQUENCIAL**

### **Semana 1: Sistema Híbrido**

#### **Teste 1: Armazenamento Híbrido**
```bash
# Testar integração YAML + GraphRAG
python memory/hybrid_store.py
```

**Resultado Esperado:**
```
✅ GraphRAG conectado: Neo4j + ChromaDB
💾 Experiência armazenada: exp_test_001
Encontradas 1 experiências similares
Armazenamento: ✅
```

#### **Teste 2: CodeAgent Enhanced**
```bash
# Testar CodeAgent com memória
python core/agents/code_agent_enhanced.py
```

**Resultado Esperado:**
```
🤖 CodeAgent inicializado com GraphRAG
⚙️ CodeAgent processando: criar função que soma dois números
✅ Código gerado com sucesso (qualidade: X.X/10)
💾 Experiência armazenada: exp_xxxxxxxx

⚙️ CodeAgent processando: criar função que adiciona dois valores  
🧠 Encontradas 1 experiências similares
✅ Código gerado com sucesso (qualidade: X.X/10)
Aprendizado aplicado: True
```

### **Semana 2: Pattern Discovery**

#### **Teste 3: Descoberta de Padrões**
```bash
# Executar discovery após gerar algumas experiências
python memory/pattern_discovery.py
```

**Resultado Esperado:**
```
🔍 Iniciando descoberta de padrões...
✅ X padrões descobertos
🔗 X padrões integrados ao sistema simbólico

📊 RESUMO DOS PADRÕES DESCOBERTOS:
Total: X

🔹 Padrão de Código
   Descrição: Padrão comum para...
   Taxa de sucesso: XX%
   Impacto na qualidade: X.X
   Confiança: XX%
```

### **Semana 3: Testes Integrados**

#### **Teste 4: Suite GraphRAG Completa**
```bash
# Executar suite completa de testes
python scripts/tests/test_graphrag_integration.py
```

**Resultado Esperado:**
```
🧪 INICIANDO TESTES DE INTEGRAÇÃO GRAPHRAG
==========================================================

🔌 Teste: database_connectivity
   Neo4j: ✅
   ChromaDB: ✅

💾 Teste: hybrid_storage
   Armazenamento: ✅
   YAML atualizado: ✅
   GraphRAG: ✅

[... outros testes ...]

==========================================================
📊 RESUMO DOS TESTES GRAPHRAG
==========================================================
🧪 Total de testes: 8
✅ Sucessos: 7
❌ Falhas: 1
📈 Taxa de sucesso: 87.5%
🏆 Status geral: PASSED
```

### **Semana 4-5: Sistema de Checkpoints**

#### **Teste 5: Checkpoints de Agentes**
```bash
# Testar sistema de checkpoints
python evolution/checkpointing/agent_checkpoints.py
```

**Resultado Esperado:**
```
🤖 Criando agente de exemplo...
   Tarefa: criar função que retorna saudação - Qualidade: X.X
   [...]

💾 Criando checkpoint do CodeAgentEnhanced...
✅ Checkpoint criado: codeagent_xxxxxxxx
   Versão: v1.0_test
   Especialização: general_purpose
   Experiências: X
   Qualidade média: X.XX

📋 Checkpoints disponíveis:
   codeagent_xxxxxxxx - CodeAgentEnhanced vv1.0_test (general_purpose)

🔄 Testando carregamento do checkpoint...
📂 Carregando agente do checkpoint: codeagent_xxxxxxxx
✅ Agente CodeAgentEnhanced restaurado
   Teste pós-restauração: Qualidade X.X

✅ Teste do sistema de checkpoints concluído!
```

---

## 🎛️ **FASE 4: DASHBOARD E MONITORAMENTO**

### **Executar Dashboard Avançado**
```bash
# Iniciar dashboard (nova aba do terminal)
streamlit run interface/dashboard/streamlit_advanced.py
```

**Acesso:** http://localhost:8501

**Funcionalidades a Testar:**
1. **Visão Geral** - Métricas do sistema
2. **GraphRAG Analytics** - Visualizações do grafo
3. **Evolução de Agentes** - Histórico de melhoria
4. **Padrões Descobertos** - Lista e análise de padrões
5. **Checkpoints** - Gerenciamento de versões
6. **Performance** - Métricas de sistema

### **Verificar Funcionalidades Dashboard**
- [ ] Métricas principais carregam
- [ ] Gráficos de qualidade aparecem
- [ ] Rede de conhecimento visualizada
- [ ] Lista de padrões populada
- [ ] Checkpoints listados
- [ ] Performance dentro do esperado

---

## 🔬 **FASE 5: TESTES DE PERFORMANCE**

### **Executar Testes de Performance**
```bash
# Testes específicos de performance (quando disponível)
python scripts/tests/test_full_system_performance.py
```

### **Monitoramento Manual**
```bash
# Verificar uso de recursos
docker stats

# Verificar logs de erros
docker-compose -f infrastructure/docker-compose.yml logs --tail=50

# Verificar status Neo4j
curl http://localhost:7474/db/neo4j/tx/commit \
  -H "Content-Type: application/json" \
  -d '{"statements":[{"statement":"MATCH (n) RETURN count(n) as total"}]}'

# Verificar ChromaDB
curl http://localhost:8000/api/v1/collections
```

---

## 🚀 **FASE 6: TESTES END-TO-END**

### **Fluxo Completo de Validação**
```bash
# 1. Executar sistema principal com GraphRAG
python core/main.py

# 2. Aguardar alguns ciclos (Ctrl+C para parar)

# 3. Verificar dados no Neo4j
# Acessar http://localhost:7474 e executar:
# MATCH (e:Experience) RETURN count(e) as total_experiences

# 4. Verificar padrões descobertos
python -c "
from memory.hybrid_store import HybridMemoryStore
from memory.pattern_discovery import PatternDiscoveryEngine

memory = HybridMemoryStore(enable_graphrag=True)
discovery = PatternDiscoveryEngine(memory)
patterns = discovery.discover_patterns()
print(f'Padrões descobertos: {len(patterns)}')
memory.close()
"

# 5. Criar e testar checkpoint
python -c "
from core.agents.code_agent_enhanced import CodeAgentEnhanced
from evolution.checkpointing.agent_checkpoints import AgentCheckpointManager

# Criar agente treinado
agent = CodeAgentEnhanced(enable_graphrag=True)
for i in range(3):
    result = agent.execute_task(f'criar função exemplo {i}')
    print(f'Qualidade {i}: {result.quality_score:.1f}')

# Salvar checkpoint
manager = AgentCheckpointManager()
checkpoint_id = manager.create_checkpoint(agent, 'final_test')
print(f'Checkpoint salvo: {checkpoint_id}')

agent.close()
"
```

---

## 📊 **VALIDAÇÃO FINAL**

### **Checklist de Funcionalidades**
- [ ] **Infraestrutura**: Todos os serviços Docker rodando
- [ ] **Armazenamento**: Experiências salvas em YAML + GraphRAG
- [ ] **Aprendizado**: Qualidade melhora com experiências
- [ ] **Padrões**: Sistema descobre padrões automaticamente
- [ ] **Checkpoints**: Agentes podem ser salvos/restaurados
- [ ] **Dashboard**: Interface visual funcionando
- [ ] **Performance**: Tempo de resposta <30s
- [ ] **Compatibilidade**: Sistema YAML atual preservado

### **Métricas de Validação**
```bash
# Verificar métricas finais
python -c "
import yaml
from pathlib import Path

# Verificar identidades
with open('reflection/state/identity/identity_state.yaml', 'r') as f:
    identity = yaml.safe_load(f)
    print(f'Agentes com identidade: {len(identity)}')

# Verificar memória
with open('reflection/state/identity/memory_log.yaml', 'r') as f:
    memory = yaml.safe_load(f)
    total_cycles = sum(agent.get('ciclos_totais', 0) for agent in memory.values())
    print(f'Total de ciclos executados: {total_cycles}')

print('✅ Sistema validado!')
"
```

---

## 🔧 **TROUBLESHOOTING**

### **Problemas Comuns**

#### **Docker não sobe**
```bash
# Verificar portas
sudo lsof -i :7474
sudo lsof -i :7687
sudo lsof -i :8000

# Parar serviços conflitantes
sudo systemctl stop neo4j  # Se Neo4j instalado local
docker stop $(docker ps -q)  # Parar outros containers

# Limpar e reiniciar
docker-compose -f infrastructure/docker-compose.yml down
docker system prune -f
docker-compose -f infrastructure/docker-compose.yml up -d
```

#### **Neo4j não conecta**
```bash
# Verificar logs
docker logs rsca-neo4j

# Resetar senha se necessário
docker exec rsca-neo4j cypher-shell -u neo4j -p neo4j "ALTER USER neo4j SET PASSWORD 'rsca_secure_2025'"
```

#### **Python imports não funcionam**
```bash
# Verificar PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# Ou rodar com módulo
python -m memory.hybrid_store
python -m core.agents.code_agent_enhanced
```

#### **Testes falham**
```bash
# Executar diagnóstico
python scripts/tests/test_quick.py

# Verificar dependências
pip install -r requirements.txt

# Verificar se serviços estão rodando
curl -f http://localhost:7474 || echo "Neo4j não disponível"
curl -f http://localhost:8000/api/v1/heartbeat || echo "ChromaDB não disponível"
```

---

## 📋 **COMANDOS DE REFERÊNCIA RÁPIDA**

### **Inicialização Completa**
```bash
# Setup completo em um bloco
cd /caminho/para/reflexive-self-assistant
docker-compose -f infrastructure/docker-compose.yml up -