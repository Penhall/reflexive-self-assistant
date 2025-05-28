# Configuração para CodeLlama
MODEL_NAME = "codellama:7b" 
CONTEXT_LENGTH = 4096
TEMPERATURE = 0.1
TOP_P = 0.9
SYSTEM_PROMPT = """You are a specialized code generation assistant. 
Generate clean, functional, and well-documented code based on the given requirements.
Focus on best practices, error handling, and code maintainability."""

PROMPT_TEMPLATES = {
    "code_generation": """
Task: {task}

Context from similar experiences:
{context}

Generate Python code that:
1. Implements the requested functionality
2. Includes proper error handling
3. Follows Python best practices
4. Is well-documented with docstrings

Code:
""",
    
    "code_improvement": """
Current code:
{current_code}

Issues found:
{issues}

Improve the code addressing the issues while maintaining functionality:
""",
    
    "code_documentation": """
Code to document:
{code}

Generate comprehensive documentation including:
1. Function/class docstrings
2. Inline comments for complex logic
3. Usage examples
4. Parameter descriptions

Documentation:
"""
}
