# 🐳 Configuração do Neo4j para RSCA

## Problema Atual
O sistema está usando MockGraphMemory devido a erro de autenticação:
`Neo.ClientError.Security.Unauthorized`

## Solução

### 1. Iniciar Neo4j com Docker
```bash
docker run -d --name rsca-neo4j \
  -p 7474:7474 -p 7687:7687 \
  -e NEO4J_AUTH=neo4j/reflexive123 \
  neo4j:latest
```

### 2. Aguardar inicialização
```bash
# Aguardar ~30 segundos
sleep 30

# Verificar se está rodando
docker logs rsca-neo4j
```

### 3. Testar conexão
```bash
python -c "
from memory.graph_rag.graph_interface import GraphMemory
try:
    graph = GraphMemory()
    graph.get_categories_and_counts()
    print('✅ Neo4j conectado!')
    graph.close()
except Exception as e:
    print(f'❌ Erro: {e}')
"
```

### 4. Configurar .env (opcional)
```bash
# .env
NEO4J_URI=bolt://localhost:7687
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=reflexive123
```

## Interface Web
- URL: http://localhost:7474
- Usuário: neo4j
- Senha: reflexive123

## Troubleshooting

### Porta já em uso
```bash
docker stop rsca-neo4j
docker rm rsca-neo4j
# Repetir comando de inicialização
```

### Verificar se Docker está rodando
```bash
docker --version
docker ps
```
