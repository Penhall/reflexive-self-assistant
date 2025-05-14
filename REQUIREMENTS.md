# Requisitos Técnicos e Especiais

## Técnicos
- Python 3.10+
- CrewAI (última versão)
- ArangoDB ou Neo4j (GraphRAG)
- Framework de LLM local: vLLM, Ollama ou LM Studio
- Recomendado: Docker para orquestração dos serviços

## Segurança
- Criptografia de chave para logs sensíveis (opcional)
- Controle de versões e auditoria de reflexões (commit signed para logs simbólicos)
- Sanitização de prompts para evitar fuga de instruções

## Formato
- Memória simbólica persistente via JSON ou YAML + Banco Grafo
- Logs reflexivos em Markdown estruturado
- Modularização de agentes em pastas isoladas

## Privacidade
- Nenhum dado real de usuários será coletado
- Se integrado a repositórios privados, incluir verificação OAuth