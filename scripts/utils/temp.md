Analisando os documentos, aqui está o plano para os próximos passos:

1. **Situação Atual**:
   - Testes unitários de pattern_discovery concluídos com sucesso (4/4 testes passaram)
   - Sistema está na Semana 3 da Fase 2A (GraphRAG)
   - Pronto para avançar para Semana 4: Validação e Testes GraphRAG

2. **Próximas Ações**:
   - Executar suite de testes integrados:
     ```bash
     python scripts/tests/test_graphrag_integration.py
     ```
   - Validar métricas de aprendizado:
     ```bash
     python -c "
     from memory.hybrid_store import HybridMemoryStore
     memory = HybridMemoryStore(enable_graphrag=True)
     # Código para verificar métricas
     memory.close()
     "
     ```
   - Monitorar performance:
     ```bash
     docker stats
     ```

3. **Critérios de Sucesso**:
   - Pelo menos 80% dos testes GraphRAG passando
   - Melhoria de qualidade comprovada nas experiências
   - Tempo de resposta abaixo de 30s por ciclo

4. **Fluxo Recomendado**:
   ```mermaid
   graph TD
     A[Iniciar serviços Docker] --> B[Executar testes integrados]
     B --> C{Passou nos testes?}
     C -->|Sim| D[Validar métricas de aprendizado]
     C -->|Não| E[Corrigir problemas]
     D --> F[Verificar performance]
     F --> G{Performance OK?}
     G -->|Sim| H[Concluir validação]
     G -->|Não| I[Otimizar queries/indexes]
   ```

5. **Documentos de Referência**:
   - `docs/instrucoes_execucao_20250529.md` (passo-a-passo detalhado)
   - `docs/plano_implementacao_20250529.md` (critérios de aceite)
   - `docs/rsca_complete_roadmap 29.05.2025.md` (contexto geral)

Precisa de mais detalhes sobre alguma parte específica deste plano ou posso prosseguir com a execução?