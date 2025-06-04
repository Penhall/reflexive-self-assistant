"""
Configurações centralizadas do Reflexive Self Coding Assistant - VERSÃO CORRIGIDA
Prioriza CodeLlama para geração de código e melhora configurações
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

# Diretório raiz do projeto
PROJECT_ROOT = Path(__file__).parent.parent

# Configurações de LLM - CORRIGIDAS
LLM_CONFIG = {
    "ollama": {
        "host": os.getenv("OLLAMA_HOST", "http://localhost:11434"),
        "models": {
            # MUDANÇA CRÍTICA: CodeLlama como padrão para código
            "code": os.getenv("CODE_MODEL", "deepseek-r1:1.5b"),        # Era qwen2:1.5b
            "general": os.getenv("GENERAL_MODEL", "qwen3:4b"),     # Mantido
            "analysis": os.getenv("ANALYSIS_MODEL", "deepseek-r1:1.5b")    # Simplificado
        },
        # Configurações específicas por modelo
        "model_settings": {
            "codellama:7b": {
                "temperature": 0.1,
                "top_p": 0.9,
                "num_predict": 2048,
                "context_window": 4096,
                "recommended_for": ["codigo", "testes", "refactoring"]
            },
            "codellama:13b": {
                "temperature": 0.05,
                "top_p": 0.85,
                "num_predict": 3072,
                "context_window": 4096,
                "recommended_for": ["codigo_complexo", "arquitetura", "otimizacao"]
            },
            "llama3:8b": {
                "temperature": 0.2,
                "top_p": 0.9,
                "num_predict": 2048,
                "context_window": 4096,
                "recommended_for": ["documentacao", "analise", "geral"]
            },
            "qwen2:1.5b": {
                "temperature": 0.3,
                "top_p": 0.9,
                "num_predict": 1024,
                "context_window": 2048,
                "recommended_for": ["tarefas_simples", "prototipagem"],
                "warning": "Modelo leve - pode gerar código com problemas"
            }
        }
    }
}

# Configurações de banco de dados
DATABASE_CONFIG = {
    "neo4j": {
        "uri": os.getenv("NEO4J_URI", "bolt://localhost:7687"),
        "username": os.getenv("NEO4J_USERNAME", "neo4j"),
        "password": os.getenv("NEO4J_PASSWORD", "reflexive123"),
        "pool_size": int(os.getenv("NEO4J_POOL_SIZE", "10")),
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
    "max_history": int(os.getenv("MAX_HISTORY", "100")),
    "pattern_threshold": float(os.getenv("PATTERN_THRESHOLD", "0.7")),
    "consistency_levels": {
        "high_threshold": 4,
        "medium_threshold": 2
    },
    # NOVO: Configurações de qualidade
    "quality_thresholds": {
        "excellent": 8.5,
        "good": 7.0,
        "acceptable": 5.0,
        "poor": 3.0
    }
}

# Configurações de logging
LOGGING_CONFIG = {
    "level": os.getenv("LOG_LEVEL", "INFO"),
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    "file_path": PROJECT_ROOT / "logs" / "system.log",
    "max_file_size": "10MB",
    "backup_count": 5,
    "console_output": os.getenv("LOG_CONSOLE", "true").lower() == "true"
}

# Configurações de performance - MELHORADAS
PERFORMANCE_CONFIG = {
    "max_concurrent_agents": int(os.getenv("MAX_CONCURRENT_AGENTS", "3")),
    "timeout_seconds": int(os.getenv("TIMEOUT_SECONDS", "60")),  # Aumentado para LLMs mais lentos
    "retry_attempts": int(os.getenv("RETRY_ATTEMPTS", "3")),
    "memory_limit_mb": int(os.getenv("MEMORY_LIMIT_MB", "1024")),
    # NOVO: Configurações específicas de código
    "code_execution": {
        "max_execution_time": 30,
        "max_file_size_mb": 5,
        "allowed_imports": [
            "os", "sys", "json", "yaml", "datetime", "time", "re", "math",
            "pathlib", "typing", "dataclasses", "collections", "itertools"
        ],
        "forbidden_operations": [
            "subprocess", "eval", "exec", "open('/etc')", "__import__"
        ]
    }
}

# Configurações GraphRAG - NOVO
GRAPHRAG_CONFIG = {
    "enabled": os.getenv("GRAPHRAG_ENABLED", "true").lower() == "true",
    "vector_store": {
        "model": "all-MiniLM-L6-v2",
        "dimension": 384,
        "similarity_threshold": 0.7,
        "max_results": 5
    },
    "pattern_discovery": {
        "min_occurrences": 3,
        "min_success_rate": 0.6,
        "confidence_threshold": 0.8,
        "auto_discovery_interval": 24  # horas
    },
    "experience_storage": {
        "max_experiences_per_agent": 1000,
        "cleanup_threshold": 0.9,  # 90% do limite
        "compress_old_experiences": True
    }
}

# Configurações de segurança
SECURITY_CONFIG = {
    "enable_code_sandbox": os.getenv("ENABLE_SANDBOX", "true").lower() == "true",
    "max_code_complexity": 100,  # Complexidade ciclomática máxima
    "rate_limiting": {
        "max_requests_per_minute": 60,
        "max_requests_per_hour": 1000
    },
    "content_filtering": {
        "block_sensitive_operations": True,
        "log_all_executions": True
    }
}

# Configurações de desenvolvimento vs produção
ENV = os.getenv("ENVIRONMENT", "development")

DEVELOPMENT_CONFIG = {
    "debug_mode": ENV == "development",
    "verbose_logging": ENV == "development",
    "use_mock_llm": os.getenv("USE_MOCK_LLM", "false").lower() == "true",
    "enable_profiling": ENV == "development",
    "auto_reload": ENV == "development"
}

# Validação de configurações
def validate_config():
    """Valida configurações críticas do sistema"""
    errors = []
    warnings = []
    
    # Verificar configurações de LLM
    if not LLM_CONFIG["ollama"]["host"]:
        errors.append("OLLAMA_HOST não configurado")
    
    # Verificar modelos recomendados
    code_model = LLM_CONFIG["ollama"]["models"]["code"]
    if "qwen2" in code_model:
        warnings.append(f"Modelo {code_model} pode gerar código de baixa qualidade. Recomendado: codellama:7b")
    
    # Verificar configurações de banco
    if not DATABASE_CONFIG["neo4j"]["password"] or DATABASE_CONFIG["neo4j"]["password"] == "password":
        warnings.append("Senha padrão do Neo4j detectada. Altere para produção.")
    
    # Verificar configurações de performance
    if PERFORMANCE_CONFIG["timeout_seconds"] < 30:
        warnings.append("Timeout muito baixo para modelos LLM grandes")
    
    return errors, warnings

# Função para obter configuração por ambiente
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
        "environment": ENV,
        "project_root": PROJECT_ROOT
    }
    
    # Ajustes específicos por ambiente
    if ENV == "production":
        # Configurações de produção
        config["logging"]["level"] = "WARNING"
        config["development"]["debug_mode"] = False
        config["development"]["verbose_logging"] = False
        config["performance"]["timeout_seconds"] = 120
        
    elif ENV == "testing":
        # Configurações de teste
        config["development"]["use_mock_llm"] = True
        config["graphrag"]["enabled"] = False
        config["performance"]["timeout_seconds"] = 10
    
    return config

# Configurações de paths específicos para diferentes componentes
PATH_CONFIG = {
    "data": PROJECT_ROOT / "data",
    "logs": PROJECT_ROOT / "logs",
    "exports": PROJECT_ROOT / "exports",
    "temp": PROJECT_ROOT / "temp",
    "checkpoints": PROJECT_ROOT / "data" / "checkpoints",
    "experiences": PROJECT_ROOT / "data" / "experiences",
    "patterns": PROJECT_ROOT / "data" / "patterns"
}

# Função para criar diretórios necessários
def ensure_directories():
    """Cria todos os diretórios necessários"""
    for path in PATH_CONFIG.values():
        path.mkdir(parents=True, exist_ok=True)

# Configurações específicas de prompt - NOVO
PROMPT_CONFIG = {
    "code_generation": {
        "system_prompt": """You are a Python coding specialist. Generate clean, syntactically correct code.

CRITICAL RULES:
1. ALWAYS close docstrings with triple quotes (\"\"\")
2. NEVER leave docstrings unterminated
3. Use proper Python indentation (4 spaces)
4. Write executable, syntactically valid code
5. Include error handling when appropriate""",
        
        "max_length": 2048,
        "temperature": 0.1,
        "stop_sequences": ["```\n\n", "</code>", "# End of code"]
    },
    
    "test_generation": {
        "system_prompt": """Generate comprehensive unit tests using pytest framework.
Ensure all docstrings are properly closed and tests are executable.""",
        "max_length": 1536,
        "temperature": 0.2
    },
    
    "documentation": {
        "system_prompt": """Generate clear, comprehensive documentation.
Use proper Python docstring format with triple quotes properly closed.""",
        "max_length": 1024,
        "temperature": 0.3
    }
}

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
    print("📁 Diretórios criados/verificados")
    
    # Mostrar configuração atual
    print(f"\n📋 Configuração atual:")
    print(f"   Ambiente: {ENV}")
    print(f"   Modelo de código: {LLM_CONFIG['ollama']['models']['code']}")
    print(f"   GraphRAG: {'✅' if GRAPHRAG_CONFIG['enabled'] else '❌'}")
    print(f"   Debug: {'✅' if DEVELOPMENT_CONFIG['debug_mode'] else '❌'}")
else:
    # Executar configuração silenciosa na importação
    ensure_directories()