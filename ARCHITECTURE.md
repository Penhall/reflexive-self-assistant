# Arquitetura do Sistema

## Camadas
- Input Layer: prompt de usuário ou contexto
- Agent Layer (CrewAI):
  - Agents: CodeGen, TestGen, DocGen, Reflector
  - Reflexive Supervisor
- Memory Layer (GraphRAG):
  - Grafo de padrões simbólicos
  - Base de conhecimento de reflexões anteriores
- Output Layer:
  - Código, testes, documentação
  - Relatórios reflexivos