# Recursos Necessários

## Computacionais
- GPU com no mínimo 8GB VRAM (para LLM local)
- 8 vCPUs, 16GB RAM recomendados
- ArangoDB ou Neo4j operando com suporte a APIs REST

## Bibliotecas
- crewai, langchain, llama-index
- openai, transformers, sentence-transformers, chromadb, networkx, graphdatascience

## Arquivos e Estrutura
```
/agents/
    └── coder_agent.py
    └── test_agent.py
    └── reflector_agent.py
/memory/
    └── memory_graph.json
    └── symbolic_patterns.yaml
/reflection/
    └── prompt_templates/
    └── analysis_history.md
```