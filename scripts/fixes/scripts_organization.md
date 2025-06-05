# 📂 Organização dos Scripts - Eliminando Duplicações

## 🗑️ **Arquivos para EXCLUIR (duplicados/desnecessários)**

```bash
# Scripts duplicados ou obsoletos para remover
rm test_complete_integration.py        # Duplicado
rm test_llm_integration.py            # Duplicado  
rm demo_lightweight_rsca.py           # Duplicado
rm setup_lightweight_models.sh        # Duplicado
rm test_lightweight_complete.py       # Duplicado
rm test_lightweight_models.py         # Duplicado (incompleto)
rm lightweight_models_setup.sh        # Duplicado
rm warm_up_test.py                    # Desnecessário
rm quick_setup_lightweight.py         # Muito complexo
```

## 📁 **Nova Estrutura de Scripts**

```
scripts/
├── config/                    # Configurações e setup
│   ├── setup_system.py       # Setup completo automatizado
│   ├── cleanup_models.py     # Limpeza de modelos grandes
│   └── install_models.py     # Instalação de modelos leves
├── tests/                     # Todos os testes
│   ├── test_system.py        # Teste completo único
│   └── test_quick.py         # Teste rápido
├── fixes/                     # Correções e reparos
│   ├── fix_imports.py        # Corrige imports quebrados
│   └── create_missing.py    # Cria arquivos faltantes
└── utils/                     # Utilitários gerais
    ├── logger.py             # Logging
    └── docker_utils.py       # Funções Docker
```

## ✅ **Arquivos ÚNICOS e ESSENCIAIS**

### 1. **scripts/config/setup_system.py** (substitui quick_setup_lightweight.py)
- Setup completo em uma só execução
- Verifica Docker
- Instala modelos leves
- Configura sistema
- Testa funcionamento

### 2. **scripts/config/cleanup_models.py** (baseado em cleanup_large_models.sh)
- Remove modelos grandes (8B+)  
- Mantém apenas modelos leves
- Libera RAM e espaço

### 3. **scripts/tests/test_system.py** (substitui todos os test_*.py)
- Teste completo único
- Verifica todos os componentes
- Relatório final detalhado

### 4. **scripts/fixes/fix_imports.py**
- Corrige todos os imports quebrados
- Cria arquivos __init__.py faltantes
- Implementa ollama_client simplificado

### 5. **core/llm/ollama_client.py** (versão simplificada única)
- Cliente Ollama funcional
- Suporte a modelos leves
- Fallback para mock

## 🎯 **Comandos Simplificados**

```bash
# Setup completo (substitui tudo)
python scripts/config/setup_system.py

# Limpeza de modelos grandes
python scripts/config/cleanup_models.py  

# Teste completo
python scripts/tests/test_system.py

# Correção de imports (se necessário)
python scripts/fixes/fix_imports.py
```

## 💡 **Benefícios da Nova Organização**

1. **Sem duplicação**: Cada funcionalidade em um arquivo único
2. **Estrutura clara**: Scripts organizados por função
3. **Fácil manutenção**: Encontrar e editar é simples
4. **Comandos diretos**: Um comando para cada ação
5. **Menos confusão**: Elimina arquivos conflitantes