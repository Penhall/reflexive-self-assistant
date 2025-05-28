"""
Configurações centralizadas do Reflexive Self Coding Assistant.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

# Diretório raiz do projeto
PROJECT_ROOT = Path(__file__).parent.parent

# Configurações de LLM
LLM_CONFIG = {
    "ollama": {
        "host": os.getenv("OLLAMA_HOST", "http://localhost:11434"),
        "models": {
            "code": os.getenv("CODE_MODEL", "codellama:7b"),
            "general": os.getenv("GENERAL_MODEL", "llama3:8b"),
            "analysis": os.getenv("ANALYSIS_MODEL", "codellama:13b")
        }
    }
}

# Configurações de banco de dados
DATABASE_CONFIG = {
    "neo4j": {
        "uri": os.getenv("NEO4J_URI", "bolt://localhost:7687"),
        "username": os.getenv("NEO4J_USERNAME", "neo4j"),
        "password": os.getenv("NEO4J_PASSWORD", "password")
    },
    "chromadb": {
        "path": PROJECT_ROOT / "data" / "chromadb",
        "collection_name": "coding_experiences"
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
    }
}

# Configurações de logging
LOGGING_CONFIG = {
    "level": os.getenv("LOG_LEVEL", "INFO"),
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    "file_path": PROJECT_ROOT / "logs" / "system.log"
}

# Configurações de performance
PERFORMANCE_CONFIG = {
    "max_concurrent_agents": int(os.getenv("MAX_CONCURRENT_AGENTS", "3")),
    "timeout_seconds": int(os.getenv("TIMEOUT_SECONDS", "30")),
    "retry_attempts": int(os.getenv("RETRY_ATTEMPTS", "3"))
}
