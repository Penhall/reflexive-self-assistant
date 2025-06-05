# Requisitos do RSCA v4.0 (Funcionais e Técnicos)

## Requisitos Técnicos
- **Python**: Versão 3.10+
- **Dependências Principais**:
    - `streamlit`: Dashboard interativo
    - `neo4j`: Banco de dados de grafo (GraphRAG)
    - `chromadb`: Banco de dados vetorial (GraphRAG)
    - `crewai`: Framework para orquestração de agentes
    - `ollama`: Execução de LLMs locais
    - `transformers`, `langchain`: Processamento de linguagem
    - `fastapi`, `pydantic`: API REST (em desenvolvimento)
    - `docker`, `kubernetes`: Implantação e orquestração
    - `prometheus`, `grafana`: Monitoramento

## Requisitos Funcionais
### Core
- **Execução de Tarefas**: Geração de código, testes e documentação
- **Busca Contextual**: Recuperação relevante de experiências do GraphRAG
- **Reflexão Recursiva**: Meta-análise e auto-avaliação
- **Aprendizado Contínuo**: Acúmulo e aplicação de experiências

### GraphRAG
- **Persistência Unificada**: Armazenamento de experiências em Neo4j + ChromaDB
- **Atualização em Tempo Real**: Sincronização imediata de novos dados
- **Busca Semântica**: Recuperação por similaridade contextual
- **Descoberta de Padrões**: Identificação automática de padrões úteis

### Agentes
- **Especialização Automática**: Adaptação a domínios específicos
- **Checkpoints**: Versionamento completo de estado
- **Colaboração**: Interação entre agentes via GraphRAG
- **Auto-documentação**: Geração contextual de documentação

## Requisitos de Infraestrutura
- **RAM**: 6-8GB (Neo4j + ChromaDB + Ollama)
- **Disco**: 20GB para dados e modelos  
- **CPU**: 4+ núcleos recomendado
- **GPU**: Opcional para modelos maiores

## requirements.txt
```
streamlit>=1.32.0
neo4j>=5.14.0
chromadb>=0.4.15
crewai>=0.28.8
ollama>=0.1.27
langchain>=0.1.10
transformers>=4.38.0
fastapi>=0.109.0
pydantic>=2.6.0
docker>=7.0.0
prometheus-client>=0.20.0
