# Resumo da Migração - 2025-05-25 20:13:27

## Estrutura Antiga → Nova

### Diretórios Principais
- `agents/` → `core/agents/`
- `utils/` → `memory/graph_rag/` e `scripts/`
- `config/` → `config/` (reestruturado)
- `reflection/` → `reflection/` (reorganizado)
- `dashboard/` → `interface/dashboard/`
- `tests/` → `tests/` (reorganizado)

### Estados YAML Organizados
- **Identidade**: `reflection/state/identity/`
- **Emocional**: `reflection/state/emotional/`
- **Temporal**: `reflection/state/temporal/`
- **Governança**: `reflection/state/governance/`

### Novos Componentes
- `memory/` - Sistema de memória GraphRAG
- `evolution/` - Sistema de evolução de agentes
- `interface/` - Interfaces de usuário
- `infrastructure/` - Docker e configurações

## Arquivos de Configuração Criados
- `config/settings.py` - Configurações centralizadas
- `config/paths.py` - Paths organizados
- `config/model_configs/` - Configurações de modelos
- `config/environment/.env.example` - Variáveis de ambiente

## Próximos Passos
1. Verificar se todos os imports foram atualizados
2. Testar execução básica do sistema
3. Implementar componentes faltantes (LLM, GraphRAG)
4. Executar testes de integração

## Rollback
Para reverter as mudanças:
```bash
git checkout .  # Se usando Git
# ou restaurar backup manual
```
