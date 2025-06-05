# Recursos do RSCA v4.0

O Reflexive Self Coding Assistant (RSCA) utiliza e gera uma variedade de recursos para seu funcionamento, persistência de dados e interação, baseado inteiramente em GraphRAG.

## Armazenamento de Dados
- **Neo4j**: Banco de dados de grafo para armazenar experiências, padrões e relações complexas no GraphRAG.
- **ChromaDB**: Banco de dados vetorial para armazenar embeddings de experiências e padrões, facilitando a busca por similaridade.
- **`data/`**: Diretório principal para persistência de dados, incluindo:
    - `neo4j/`: Dados do banco de dados Neo4j (grafo de conhecimento)
    - `chromadb/`: Dados do banco de dados ChromaDB (vetores)
    - `checkpoints/`: Snapshots completos de agentes para versionamento e especialização

## Interfaces e Monitoramento
- **Streamlit Dashboard Avançado**: Interface visual para:
    - Monitoramento em tempo real
    - Análise de GraphRAG
    - Evolução de agentes
    - Padrões descobertos
    - Gerenciamento de checkpoints
    - Métricas de performance
- **Logs e Snapshots**:
    - `logs/`: Diretório para logs de ciclo e relatórios de teste
    - `exports/reports/`: Relatórios gerados em PDF/HTML
    - `exports/identities/`: Perfis de identidade de agentes exportados
- **APIs e Ferramentas**:
    - **Python API**: Para integração programática
    - **REST endpoints**: Planejados para acesso via HTTP
    - **CLI tools**: Para automação e scripts

## Modelos de Linguagem (LLMs)
- **Ollama**: Cliente para execução de modelos LLM locais:
    - CodeLlama (7B/13B): Geração de código
    - Llama3 (8B): Tarefas gerais
    - Qwen2 (1.5B): Testes rápidos
- **LightweightLLMManager**: Gerenciador com:
    - Seleção automática de modelo
    - Configurações otimizadas por tarefa
    - Fallback inteligente

## Documentação e Diagramas
- **GitHub Repository**: Repositório principal do projeto
- **Diagramas de Arquitetura**: Incluindo:
    - Ciclo de reflexão do agente
    - Estrutura do sistema GraphRAG
    - Fluxo de dados unificado
- **Roadmap Estratégico**: Plano de evolução para:
    - Distributed GraphRAG
    - Advanced specialization algorithms
    - Real-time collaboration
    - Cloud deployment options

## Requisitos Técnicos
- **RAM**: 6-8GB (Neo4j + ChromaDB + Ollama)
- **Disk**: 20GB para dados e modelos
- **CPU**: 4+ cores recomendado
- **GPU**: Opcional para modelos maiores

## Backup e Recuperação
- **Backup automático** diário dos dados
- **Point-in-time recovery** do Neo4j
- **Checkpoints** como snapshots de estado
- **Replicação** para alta disponibilidade
