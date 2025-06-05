"""
Configurações centralizadas do Reflexive Self Coding Assistant - VERSÃO CORRIGIDA
Prioriza modelos leves e remove dependências de arquivos legados
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

# Diretório raiz do projeto
PROJECT_ROOT = Path(__file__).parent.parent

# Configurações de LLM - OTIMIZADAS PARA MEMÓRIA BAIXA
LLM_CONFIG = {
    "ollama": {
        "host": os.getenv("OLLAMA_HOST", "http://localhost:11434"),
        "models": {
            # MODELOS LEVES para déficit de memória
            "code": os.getenv("CODE_MODEL", "deepseek-r1:1.5b"),        
            "general": os.getenv("GENERAL_MODEL", "qwen2:1.5b"),     
            "analysis": os.getenv("ANALYSIS_MODEL", "deepseek-r1:1.5b")    
        },
        # Configurações específicas por modelo
        "model_settings": {
            "deepseek-r1:1.5b": {
                "temperature": 0.1,
                "top_p": 0.9,
                "num_predict": 1024,  # Reduzido para economizar memória
                "context_window": 2048,
                "recommended_for": ["codigo", "testes", "refactoring"],
                "memory_usage": "~1.5GB"
            },
            "qwen2:1.5b": {
                "temperature": 0.2,
                "top_p": 0.9,
                "num_predict": 1024,
                "context_window": 2048,
                "recommended_for": ["documentacao", "analise", "geral"],
                "memory_usage": "~1.5GB"
            }
        }
    }
}

# Configurações de banco de dados
DATABASE_CONFIG = {
    "neo4j": {
        "uri": os.getenv("NEO4J_URI", "bolt://localhost:7687"),
        "username": os.getenv("NEO4J_USERNAME", "neo4j"),
        "password": os.getenv("NEO4J_PASSWORD", "rsca_secure_2025"), # Senha atualizada para corresponder ao docker-compose.yml
        "pool_size": int(os.getenv("NEO4J_POOL_SIZE", "5")),  # Reduzido
        "timeout": int(os.getenv("NEO4J_TIMEOUT", "30"))
    },
    "chromadb": {
        "path": PROJECT_ROOT / "data" / "chromadb",
        "collection_name": "coding_experiences",
        "host": os.getenv("CHROMADB_HOST", "localhost"),
        "port": int(os.getenv("CHROMADB_PORT", "8000")),
        "enable_auth": os.getenv("CHROMADB_AUTH", "false").lower() == "true"
    }
}

# Configurações de reflexão
REFLECTION_CONFIG = {
    "cycle_frequency": int(os.getenv("CYCLE_FREQUENCY", "5")),  # minutos
    "max_history": int(os.getenv("MAX_HISTORY", "50")),  # Reduzido para economizar memória
    "pattern_threshold": float(os.getenv("PATTERN_THRESHOLD", "0.7")),
    "consistency_levels": {
        "high_threshold": 4,
        "medium_threshold": 2
    },
    "quality_thresholds": {
        "excellent": 8.5,
        "good": 7.0,
        "acceptable": 5.0,
        "poor": 3.0
    }
}

# ⚡ CONTROLE DE FUNCIONALIDADES LEGADAS
LEGACY_FEATURES = {
    "enable_analysis_history_md": False,  # ❌ DESABILITADO - usar GraphRAG
    "enable_yaml_logging": False,         # ❌ DESABILITADO - não usar mais YAML
    "enable_markdown_exports": False,     # ❌ Economizar I/O
    "verbose_logging": False              # ❌ Reduzir logs para economizar memória
}

# Configurações de logging - OTIMIZADAS
LOGGING_CONFIG = {
    "level": os.getenv("LOG_LEVEL", "WARNING"),  # Menos verboso para economizar memória
    "format": "%(asctime)s - %(levelname)s - %(message)s",  # Formato mais simples
    "file_path": PROJECT_ROOT / "logs" / "system.log",
    "max_file_size": "5MB",  # Reduzido
    "backup_count": 2,       # Reduzido
    "console_output": os.getenv("LOG_CONSOLE", "true").lower() == "true"
}

# Configurações de performance - OTIMIZADAS PARA BAIXA MEMÓRIA
PERFORMANCE_CONFIG = {
    "max_concurrent_agents": int(os.getenv("MAX_CONCURRENT_AGENTS", "2")),  # Reduzido
    "timeout_seconds": int(os.getenv("TIMEOUT_SECONDS", "45")),  
    "retry_attempts": int(os.getenv("RETRY_ATTEMPTS", "2")),  # Reduzido
    "memory_limit_mb": int(os.getenv("MEMORY_LIMIT_MB", "512")),  # Limite mais baixo
    "code_execution": {
        "max_execution_time": 20,  # Reduzido
        "max_file_size_mb": 2,     # Reduzido
        "allowed_imports": [
            "os", "sys", "json", "yaml", "datetime", "time", "re", "math",
            "pathlib", "typing", "dataclasses", "collections"
        ],
        "forbidden_operations": [
            "subprocess", "eval", "exec", "open('/etc')", "__import__"
        ]
    }
}

# Configurações GraphRAG - OTIMIZADAS
GRAPHRAG_CONFIG = {
    "enabled": os.getenv("GRAPHRAG_ENABLED", "true").lower() == "true",
    "vector_store": {
        "model": "all-MiniLM-L6-v2",
        "dimension": 384,
        "similarity_threshold": 0.7,
        "max_results": 3  # Reduzido para economizar memória
    },
    "pattern_discovery": {
        "min_occurrences": 2,  # Reduzido
        "min_success_rate": 0.6,
        "confidence_threshold": 0.8,
        "auto_discovery_interval": 48  # Aumentado para economizar recursos
    },
    "experience_storage": {
        "max_experiences_per_agent": 100,  # Muito reduzido
        "cleanup_threshold": 0.8,  # Limpeza mais agressiva
        "compress_old_experiences": True
    }
}

# Configurações de segurança - SIMPLIFICADAS
SECURITY_CONFIG = {
    "enable_code_sandbox": os.getenv("ENABLE_SANDBOX", "true").lower() == "true",
    "max_code_complexity": 50,  # Reduzido
    "rate_limiting": {
        "max_requests_per_minute": 30,  # Reduzido
        "max_requests_per_hour": 500    # Reduzido
    },
    "content_filtering": {
        "block_sensitive_operations": True,
        "log_all_executions": False  # Desabilitado para economizar I/O
    }
}

# Configurações de desenvolvimento vs produção
ENV = os.getenv("ENVIRONMENT", "development")

DEVELOPMENT_CONFIG = {
    "debug_mode": ENV == "development" and not LEGACY_FEATURES["verbose_logging"],
    "verbose_logging": LEGACY_FEATURES["verbose_logging"],
    "use_mock_llm": os.getenv("USE_MOCK_LLM", "false").lower() == "true",
    "enable_profiling": False,  # Desabilitado para economizar recursos
    "auto_reload": False        # Desabilitado para economizar recursos
}

# Configurações de paths específicos
PATH_CONFIG = {
    "data": PROJECT_ROOT / "data",
    "logs": PROJECT_ROOT / "logs",
    "exports": PROJECT_ROOT / "exports",
    "temp": PROJECT_ROOT / "temp",
    "checkpoints": PROJECT_ROOT / "data" / "checkpoints",
    "experiences": PROJECT_ROOT / "data" / "experiences",
    "patterns": PROJECT_ROOT / "data" / "patterns"
}

# Configurações específicas de prompt - OTIMIZADAS
PROMPT_CONFIG = {
    "code_generation": {
        "system_prompt": """You are a Python coding specialist. Generate clean, syntactically correct code.

CRITICAL RULES:
1. ALWAYS close docstrings with triple quotes (\"\"\")
2. Write syntactically valid Python code
3. Keep code concise but functional
4. Include minimal error handling""",
        
        "max_length": 1024,  # Reduzido para economizar tokens
        "temperature": 0.1,
        "stop_sequences": ["```\n\n", "</code>", "# End of code"]
    },
    
    "test_generation": {
        "system_prompt": """Generate simple unit tests using pytest framework.
Keep tests concise and focused.""",
        "max_length": 512,  # Reduzido
        "temperature": 0.2
    },
    
    "documentation": {
        "system_prompt": """Generate concise documentation.
Use simple Python docstring format.""",
        "max_length": 512,  # Reduzido
        "temperature": 0.3
    }
}

def validate_config():
    """Valida configurações críticas do sistema"""
    errors = []
    warnings = []
    
    # Verificar configurações de LLM
    if not LLM_CONFIG["ollama"]["host"]:
        errors.append("OLLAMA_HOST não configurado")
    
    # Verificar configurações de banco
    if not DATABASE_CONFIG["neo4j"]["password"] or DATABASE_CONFIG["neo4j"]["password"] == "password":
        warnings.append("Senha padrão do Neo4j detectada. Altere para produção.")
    
    # Verificar configurações de memória
    if PERFORMANCE_CONFIG["memory_limit_mb"] > 1024:
        warnings.append("Limite de memória alto - pode causar problemas em sistemas com pouca RAM")
    
    return errors, warnings

def get_config():
    """Retorna configuração completa baseada no ambiente"""
    config = {
        "llm": LLM_CONFIG,
        "database": DATABASE_CONFIG,
        "reflection": REFLECTION_CONFIG,
        "logging": LOGGING_CONFIG,
        "performance": PERFORMANCE_CONFIG,
        "graphrag": GRAPHRAG_CONFIG,
        "security": SECURITY_CONFIG,
        "development": DEVELOPMENT_CONFIG,
        "legacy": LEGACY_FEATURES,  # ⭐ Novo campo
        "environment": ENV,
        "project_root": PROJECT_ROOT
    }
    
    # Ajustes específicos por ambiente
    if ENV == "production":
        config["logging"]["level"] = "ERROR"
        config["development"]["debug_mode"] = False
        config["legacy"]["enable_analysis_history_md"] = False
        
    elif ENV == "testing":
        config["development"]["use_mock_llm"] = True
        config["graphrag"]["enabled"] = False
        config["performance"]["timeout_seconds"] = 10
    
    return config

def ensure_directories():
    """Cria apenas diretórios essenciais para economizar I/O"""
    essential_paths = [
        PATH_CONFIG["data"],
        PATH_CONFIG["logs"],
        PATH_CONFIG["exports"],
        PATH_CONFIG["temp"],
        PATH_CONFIG["checkpoints"],
        PATH_CONFIG["experiences"],
        PATH_CONFIG["patterns"]
    ]
    
    for path in essential_paths:
        path.mkdir(parents=True, exist_ok=True)

# Executar validação na importação
if __name__ == "__main__":
    errors, warnings = validate_config()
    
    if errors:
        print("❌ Erros de configuração:")
        for error in errors:
            print(f"   • {error}")
    
    if warnings:
        print("⚠️ Avisos de configuração:")
        for warning in warnings:
            print(f"   • {warning}")
    
    if not errors and not warnings:
        print("✅ Configurações validadas com sucesso!")
    
    # Criar diretórios
    ensure_directories()
    print("📁 Diretórios essenciais criados/verificados")
    
    # Mostrar configuração atual
    print(f"\n📋 Configuração atual:")
    print(f"   Ambiente: {ENV}")
    print(f"   Modelo de código: {LLM_CONFIG['ollama']['models']['code']}")
    print(f"   GraphRAG: {'✅' if GRAPHRAG_CONFIG['enabled'] else '❌'}")
    print(f"   Analysis History MD: {'❌ DESABILITADO' if not LEGACY_FEATURES['enable_analysis_history_md'] else '⚠️ HABILITADO'}")
    print(f"   Limite de memória: {PERFORMANCE_CONFIG['memory_limit_mb']}MB")
else:
    # Executar configuração silenciosa na importação
    ensure_directories()
