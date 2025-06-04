"""
LLM Manager - Versão Corrigida e Padronizada
Resolve inconsistências e unifica interface
"""

import json
import requests
import time
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from config.settings import LLM_CONFIG, PERFORMANCE_CONFIG
import logging

logger = logging.getLogger(__name__)

@dataclass
class LLMResponse:
    """Resposta estruturada do LLM"""
    content: str
    model: str
    tokens_used: int
    generation_time: float
    success: bool
    error: Optional[str] = None
    context_tokens: int = 0
    response_tokens: int = 0

class OllamaClient:
    """Cliente para comunicação com Ollama"""
    
    def __init__(self, host: str = None):
        self.host = host or LLM_CONFIG["ollama"]["host"]
        self.timeout = PERFORMANCE_CONFIG["timeout_seconds"]
        self.retry_attempts = PERFORMANCE_CONFIG["retry_attempts"]
        
        # Configurações otimizadas por modelo - CORRIGIDAS
        self.model_configs = {
            "codellama:7b": {
                "temperature": 0.1,
                "top_p": 0.9,
                "num_predict": 2048,
                "specialty": "codigo_python",
                "quality": "alta"
            },
            "codellama:13b": {
                "temperature": 0.05,
                "top_p": 0.85,
                "num_predict": 3072,
                "specialty": "codigo_complexo",
                "quality": "muito_alta"
            },
            "llama3:8b": {
                "temperature": 0.2,
                "top_p": 0.9,
                "num_predict": 2048,
                "specialty": "geral_balanceado",
                "quality": "media_alta"
            },
            "qwen2:1.5b": {
                "temperature": 0.3,
                "top_p": 0.9,
                "num_predict": 1024,
                "specialty": "tarefas_simples",
                "quality": "baixa",
                "warning": "Modelo leve - pode gerar código com problemas"
            }
        }
        
        # Prioridade de modelos por tarefa - CORRIGIDO
        self.task_models = {
            "codigo": "codellama:7b",        # MUDANÇA: Era qwen2:1.5b
            "testes": "codellama:7b",        # MUDANÇA: Usar CodeLlama para testes
            "documentacao": "llama3:8b",     # Mantido
            "analise": "llama3:8b",          # Mantido
            "geral": "llama3:8b"             # Mantido
        }
    
    def is_available(self) -> bool:
        """Verifica se Ollama está disponível"""
        try:
            response = requests.get(f"{self.host}/api/tags", timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def list_models(self) -> List[str]:
        """Lista modelos disponíveis"""
        try:
            response = requests.get(f"{self.host}/api/tags", timeout=10)
            if response.status_code == 200:
                data = response.json()
                return [model["name"] for model in data.get("models", [])]
        except Exception as e:
            logger.error(f"Erro ao listar modelos: {e}")
        return []
    
    def get_best_model_for_task(self, task_type: str = "geral") -> str:
        """Retorna o melhor modelo disponível para um tipo de tarefa"""
        available_models = self.list_models()
        
        # Primeiro, tenta o modelo especializado
        preferred = self.task_models.get(task_type.lower(), "llama3:8b")
        if preferred in available_models:
            return preferred
        
        # Fallback inteligente por tipo de tarefa
        if task_type.lower() in ["codigo", "testes"]:
            fallback_order = [
                "codellama:13b",       # Melhor para código
                "codellama:7b",        # Bom para código
                "llama3:8b",           # Geral mas decente
                "qwen2:1.5b"          # Último recurso
            ]
        else:
            fallback_order = [
                "llama3:8b",           # Melhor geral
                "codellama:7b",        # Pode fazer outras tarefas
                "codellama:13b",       # Overkill mas funciona
                "qwen2:1.5b"          # Último recurso
            ]
        
        for model in fallback_order:
            if model in available_models:
                return model
        
        # Se nenhum modelo conhecido, usa o primeiro disponível
        return available_models[0] if available_models else "llama3:8b"
    
    def generate(self, model: str, prompt: str, **kwargs) -> LLMResponse:
        """Gera resposta usando modelo especificado"""
        start_time = time.time()
        
        # Usar configurações otimizadas para o modelo
        model_config = self.model_configs.get(model, {})
        
        # Preparar payload com configurações otimizadas
        payload = {
            "model": model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": model_config.get("temperature", 0.2),
                "top_p": model_config.get("top_p", 0.9),
                "num_predict": model_config.get("num_predict", 2048),
                "num_ctx": 4096,
                "repeat_penalty": 1.1,
                "stop": ["</s>", "\n\n\n", "```\n\n"]  # Stop tokens melhorados
            }
        }
        
        # Aplicar kwargs personalizados
        payload["options"].update(kwargs)
        
        for attempt in range(self.retry_attempts):
            try:
                response = requests.post(
                    f"{self.host}/api/generate",
                    json=payload,
                    timeout=self.timeout
                )
                
                if response.status_code == 200:
                    data = response.json()
                    generation_time = time.time() - start_time
                    
                    context_tokens = data.get("prompt_eval_count", 0)
                    response_tokens = data.get("eval_count", 0)
                    total_tokens = context_tokens + response_tokens
                    
                    return LLMResponse(
                        content=data.get("response", "").strip(),
                        model=model,
                        tokens_used=total_tokens,
                        generation_time=generation_time,
                        success=True,
                        context_tokens=context_tokens,
                        response_tokens=response_tokens
                    )
                else:
                    error_msg = f"HTTP {response.status_code}: {response.text}"
                    
            except requests.exceptions.Timeout:
                error_msg = f"Timeout após {self.timeout}s"
            except Exception as e:
                error_msg = str(e)
            
            if attempt < self.retry_attempts - 1:
                logger.warning(f"Tentativa {attempt + 1} falhou: {error_msg}. Tentando novamente...")
                time.sleep(2 ** attempt)
        
        return LLMResponse(
            content="",
            model=model,
            tokens_used=0,
            generation_time=time.time() - start_time,
            success=False,
            error=error_msg,
            context_tokens=0,
            response_tokens=0
        )

class LLMManager:
    """Gerenciador principal unificado de LLMs"""
    
    def __init__(self):
        self.client = OllamaClient()
        self.models = LLM_CONFIG["ollama"]["models"]
        self.current_model = None
        self.usage_stats = {}
        self._initialize_models()
    
    def _initialize_models(self):
        """Inicializa e verifica modelos disponíveis"""
        if not self.client.is_available():
            logger.warning("Ollama não está disponível. Funcionalidade limitada.")
            return
        
        available_models = self.client.list_models()
        logger.info(f"Modelos disponíveis: {available_models}")
        
        # Verificar se temos pelo menos um modelo para código
        code_models = ["codellama:7b", "codellama:13b"]
        has_code_model = any(model in available_models for model in code_models)
        
        if not has_code_model:
            logger.warning("Nenhum modelo CodeLlama disponível. Qualidade de código pode ser baixa.")
    
    def generate_code(self, task: str, context: Optional[Dict] = None) -> LLMResponse:
        """Gera código usando o melhor modelo disponível"""
        model = self.client.get_best_model_for_task("codigo")
        self.current_model = model
        
        # Construir prompt otimizado para código
        prompt = self._build_robust_code_prompt(task, context)
        
        # Log da operação
        self._log_usage("code_generation", model)
        
        return self.client.generate(
            model=model,
            prompt=prompt,
            temperature=0.1,  # Baixa temperatura para código
            top_p=0.9
        )
    
    def generate_tests(self, code: str, context: Optional[Dict] = None) -> LLMResponse:
        """Gera testes para o código fornecido"""
        model = self.client.get_best_model_for_task("testes")
        self.current_model = model
        
        prompt = self._build_robust_test_prompt(code, context)
        
        self._log_usage("test_generation", model)
        
        return self.client.generate(
            model=model,
            prompt=prompt,
            temperature=0.2
        )
    
    def generate_documentation(self, code: str, context: Optional[Dict] = None) -> LLMResponse:
        """Gera documentação para o código"""
        model = self.client.get_best_model_for_task("documentacao")
        self.current_model = model
        
        prompt = self._build_robust_docs_prompt(code, context)
        
        self._log_usage("doc_generation", model)
        
        return self.client.generate(
            model=model,
            prompt=prompt,
            temperature=0.3
        )
    
    def analyze_patterns(self, data: str, context: Optional[Dict] = None) -> LLMResponse:
        """Analisa padrões usando modelo de análise"""
        model = self.client.get_best_model_for_task("analise")
        self.current_model = model
        
        prompt = self._build_analysis_prompt(data, context)
        
        self._log_usage("pattern_analysis", model)
        
        return self.client.generate(
            model=model,
            prompt=prompt,
            temperature=0.4
        )
    
    def _build_robust_code_prompt(self, task: str, context: Optional[Dict] = None) -> str:
        """Constrói prompt ROBUSTO para geração de código - CORRIGIDO"""
        
        base_prompt = f"""You are a Python coding specialist. Generate clean, syntactically correct code.

CRITICAL RULES:
1. ALWAYS close docstrings with triple quotes (\"\"\")
2. NEVER leave docstrings unterminated
3. Use proper Python indentation (4 spaces)
4. Write executable, syntactically valid code
5. Include error handling when appropriate

Task: {task}

Requirements:
- Write production-ready Python code
- Include proper docstrings (FULLY CLOSED with triple quotes)
- Add clear comments
- Follow PEP 8 standards
- Make code testable and maintainable"""

        # Contexto de experiências similares (se disponível)
        if context and "similar_experiences" in context:
            experiences_text = context["similar_experiences"]
            if len(experiences_text.strip()) > 0:
                base_prompt += f"\n\nSimilar successful implementations:\n{experiences_text}"
        
        # Padrões recomendados (se disponível)
        if context and "patterns" in context:
            base_prompt += f"\n\nRecommended patterns:\n{context['patterns']}"
        
        # Instruções finais críticas
        base_prompt += """

IMPORTANT: Respond with ONLY the Python code. Do NOT include explanations or markdown.
Ensure all docstrings are properly closed with triple quotes.

Python code:"""
        
        return base_prompt
    
    def _build_robust_test_prompt(self, code: str, context: Optional[Dict] = None) -> str:
        """Constrói prompt robusto para geração de testes"""
        return f"""Generate comprehensive unit tests for this Python code:

```python
{code}
```

CRITICAL RULES:
1. ALWAYS close docstrings with triple quotes (\"\"\")
2. Use pytest framework
3. Write syntactically correct test code
4. Include proper imports

Requirements:
- Test normal cases and edge cases
- Include error condition tests
- Use meaningful test names
- Add properly closed docstrings
- Make tests executable

IMPORTANT: Respond with ONLY the test code. No explanations.

Test code:"""
    
    def _build_robust_docs_prompt(self, code: str, context: Optional[Dict] = None) -> str:
        """Constrói prompt robusto para documentação"""
        return f"""Generate comprehensive documentation for this Python code:

```python
{code}
```

CRITICAL RULES:
1. ALWAYS close docstrings with triple quotes (\"\"\")
2. Use proper Python docstring format
3. Include parameter and return descriptions

Include:
1. Module/function docstrings (PROPERLY CLOSED)
2. Parameter descriptions with types
3. Return value descriptions
4. Usage examples
5. Important notes

IMPORTANT: Respond with ONLY the documentation. No explanations.

Documentation:"""
    
    def _build_analysis_prompt(self, data: str, context: Optional[Dict] = None) -> str:
        """Constrói prompt para análise de padrões"""
        return f"""Analyze the following data for patterns and insights:

{data}

Provide:
1. Key patterns identified
2. Trends and correlations
3. Recommendations for improvement
4. Potential issues or concerns
5. Actionable insights

Analysis:"""
    
    def _log_usage(self, operation: str, model: str):
        """Log de uso para estatísticas"""
        from datetime import datetime
        timestamp = datetime.now().isoformat()
        
        if operation not in self.usage_stats:
            self.usage_stats[operation] = []
        
        self.usage_stats[operation].append({
            "model": model,
            "timestamp": timestamp
        })
    
    def get_model_info(self) -> Dict[str, Any]:
        """Retorna informações sobre modelos disponíveis - MÉTODO CRÍTICO ADICIONADO"""
        return {
            "configured_models": self.models,
            "available_models": self.client.list_models() if self.client.is_available() else [],
            "ollama_available": self.client.is_available(),
            "host": self.client.host,
            "current_model": self.current_model,
            "task_models": self.client.task_models,
            "model_configs": self.client.model_configs
        }
    
    def get_usage_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas de uso"""
        return {
            "current_model": self.current_model,
            "usage_history": self.usage_stats,
            "total_operations": sum(len(ops) for ops in self.usage_stats.values()),
            "models_used": list(set(
                entry["model"] 
                for ops in self.usage_stats.values() 
                for entry in ops
            ))
        }
    
    def is_ready(self) -> bool:
        """Verifica se o sistema está pronto para uso"""
        return self.client.is_available() and len(self.client.list_models()) > 0
    
    def get_system_status(self) -> Dict[str, Any]:
        """Status completo do sistema"""
        return {
            "ready": self.is_ready(),
            "model_info": self.get_model_info(),
            "usage_stats": self.get_usage_stats()
        }
    
    def suggest_model_for_task(self, task_description: str) -> str:
        """Sugere o melhor modelo baseado na descrição da tarefa"""
        task_lower = task_description.lower()
        
        # Palavras-chave por tipo de tarefa
        keywords = {
            "codigo": ["função", "classe", "implementar", "código", "algorithm", "program", "script", "def", "class"],
            "testes": ["teste", "test", "verificar", "validar", "assert", "unittest", "pytest"],
            "documentacao": ["documentar", "explicar", "readme", "doc", "comment", "describe", "documentation"],
            "analise": ["analisar", "avaliar", "revisar", "review", "optimize", "refactor", "pattern"]
        }
        
        # Contar matches por categoria
        scores = {}
        for task_type, words in keywords.items():
            scores[task_type] = sum(1 for word in words if word in task_lower)
        
        # Retornar categoria com maior score
        best_task_type = max(scores, key=scores.get) if any(scores.values()) else "geral"
        return self.client.get_best_model_for_task(best_task_type)

# Mock para desenvolvimento/testes
class MockLLMManager:
    """Versão mock para desenvolvimento quando LLMs não estão disponíveis"""
    
    def __init__(self):
        self.current_model = "mock-codellama"
        self.usage_stats = {}
    
    def generate_code(self, task: str, context: Optional[Dict] = None) -> LLMResponse:
        func_name = task.lower().replace(" ", "_").replace("-", "_")
        func_name = "".join(c for c in func_name if c.isalnum() or c == "_")
        
        if not func_name or func_name[0].isdigit():
            func_name = "generated_function"
        
        mock_code = f'''def {func_name}():
    """
    {task}
    
    Returns:
        str: Mock implementation result
    """
    return "Mock implementation of {task}"

# Example usage
if __name__ == "__main__":
    result = {func_name}()
    print(result)'''
        
        return LLMResponse(
            content=mock_code,
            model="mock-codellama",
            tokens_used=80,
            generation_time=0.1,
            success=True,
            context_tokens=30,
            response_tokens=50
        )
    
    def generate_tests(self, code: str, context: Optional[Dict] = None) -> LLMResponse:
        func_name = "test_function"
        if "def " in code:
            try:
                func_name = code.split("def ")[1].split("(")[0].strip()
            except:
                pass
        
        mock_tests = f'''import pytest

def test_{func_name}():
    """
    Test for {func_name} function.
    """
    # Mock test implementation
    assert True, "Mock test always passes"

if __name__ == "__main__":
    pytest.main([__file__])'''
        
        return LLMResponse(
            content=mock_tests,
            model="mock-codellama",
            tokens_used=60,
            generation_time=0.1,
            success=True,
            context_tokens=25,
            response_tokens=35
        )
    
    def generate_documentation(self, code: str, context: Optional[Dict] = None) -> LLMResponse:
        return LLMResponse(
            content='''"""
Module Documentation

This module contains auto-generated documentation for development purposes.

Functions:
    - Mock functions with proper documentation
    
Usage:
    from module import function
    result = function()
"""''',
            model="mock-llama",
            tokens_used=40,
            generation_time=0.1,
            success=True,
            context_tokens=15,
            response_tokens=25
        )
    
    def analyze_patterns(self, data: str, context: Optional[Dict] = None) -> LLMResponse:
        return LLMResponse(
            content="Mock pattern analysis: System is in development mode with mock responses.",
            model="mock-analysis",
            tokens_used=30,
            generation_time=0.1,
            success=True,
            context_tokens=10,
            response_tokens=20
        )
    
    def get_model_info(self) -> Dict[str, Any]:
        """Método compatível para mock - CRÍTICO"""
        return {
            "configured_models": {"mock": "development"},
            "available_models": ["mock-codellama", "mock-llama"],
            "ollama_available": False,
            "host": "mock://localhost",
            "current_model": self.current_model,
            "task_models": {"codigo": "mock-codellama", "geral": "mock-llama"},
            "model_configs": {}
        }
    
    def get_usage_stats(self) -> Dict[str, Any]:
        return {
            "current_model": self.current_model,
            "usage_history": self.usage_stats,
            "total_operations": 0,
            "models_used": ["mock-codellama", "mock-llama"]
        }
    
    def is_ready(self) -> bool:
        return True
    
    def get_system_status(self) -> Dict[str, Any]:
        return {
            "ready": True,
            "model_info": self.get_model_info(),
            "usage_stats": self.get_usage_stats()
        }
    
    def suggest_model_for_task(self, task_description: str) -> str:
        return "mock-codellama" if "codigo" in task_description.lower() else "mock-llama"

# Instância global UNIFICADA - resolve problema de inconsistência
llm_manager = LLMManager()

# Alias para compatibilidade total - CRÍTICO
LightweightLLMManager = LLMManager