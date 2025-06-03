"""
LLM Manager - Integração real com Ollama para LLMs locais
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
    context_tokens: int = 0  # Adicionado
    response_tokens: int = 0 # Adicionado

class OllamaClient:
    """Cliente para comunicação com Ollama"""
    
    def __init__(self, host: str = None):
        self.host = host or LLM_CONFIG["ollama"]["host"]
        self.timeout = PERFORMANCE_CONFIG["timeout_seconds"]
        self.retry_attempts = PERFORMANCE_CONFIG["retry_attempts"]
    
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
    
    def pull_model(self, model_name: str) -> bool:
        """Baixa um modelo se não estiver disponível"""
        try:
            payload = {"name": model_name}
            response = requests.post(
                f"{self.host}/api/pull", 
                json=payload,
                timeout=300  # 5 minutos para download
            )
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Erro ao baixar modelo {model_name}: {e}")
            return False
    
    def generate(self, model: str, prompt: str, **kwargs) -> LLMResponse:
        """Gera resposta usando o modelo especificado"""
        start_time = time.time()
        
        for attempt in range(self.retry_attempts):
            try:
                payload = {
                    "model": model,
                    "prompt": prompt,
                    "stream": False,
                    **kwargs
                }
                
                response = requests.post(
                    f"{self.host}/api/generate",
                    json=payload,
                    timeout=self.timeout
                )
                
                if response.status_code == 200:
                    data = response.json()
                    generation_time = time.time() - start_time
                    
                    # Usar prompt_eval_count para context_tokens e eval_count para response_tokens
                    context_tokens = data.get("prompt_eval_count", 0)
                    response_tokens = data.get("eval_count", 0)
                    total_tokens_used = context_tokens + response_tokens # Ou apenas eval_count se for o total
                    
                    return LLMResponse(
                        content=data.get("response", ""),
                        model=model,
                        tokens_used=total_tokens_used, # Manter para compatibilidade, mas usar os novos campos
                        generation_time=generation_time,
                        success=True,
                        context_tokens=context_tokens, # Passar os novos campos
                        response_tokens=response_tokens # Passar os novos campos
                    )
                
            except Exception as e:
                logger.warning(f"Tentativa {attempt + 1} falhou: {e}")
                if attempt < self.retry_attempts - 1:
                    time.sleep(2 ** attempt)  # Backoff exponencial
        
        return LLMResponse(
            content="",
            model=model,
            tokens_used=0,
            generation_time=time.time() - start_time,
            success=False,
            error="Falha após todas as tentativas",
            context_tokens=0, # Garantir que sejam 0 em caso de falha
            response_tokens=0  # Garantir que sejam 0 em caso de falha
        )

class LLMManager:
    """Gerenciador principal de LLMs"""
    
    def __init__(self):
        self.client = OllamaClient()
        self.models = LLM_CONFIG["ollama"]["models"]
        self.model_cache = {}
        self._initialize_models()
    
    def _initialize_models(self):
        """Inicializa e verifica modelos disponíveis"""
        if not self.client.is_available():
            logger.warning("Ollama não está disponível. Usando modo mock.")
            return
        
        available_models = self.client.list_models()
        
        for model_type, model_name in self.models.items():
            if model_name not in available_models:
                logger.info(f"Baixando modelo {model_name}...")
                if self.client.pull_model(model_name):
                    logger.info(f"Modelo {model_name} baixado com sucesso!")
                else:
                    logger.error(f"Falha ao baixar modelo {model_name}")
    
    def generate_code(self, task: str, context: Optional[Dict] = None) -> LLMResponse:
        """Gera código usando o modelo especializado"""
        model = self.models["code"]
        
        # Construir prompt contextualizado
        prompt = self._build_code_prompt(task, context)
        
        return self.client.generate(
            model=model,
            prompt=prompt,
            temperature=0.1,
            top_p=0.9
        )
    
    def generate_tests(self, code: str, context: Optional[Dict] = None) -> LLMResponse:
        """Gera testes para o código fornecido"""
        model = self.models["general"]
        
        prompt = self._build_test_prompt(code, context)
        
        return self.client.generate(
            model=model,
            prompt=prompt,
            temperature=0.2
        )
    
    def generate_documentation(self, code: str, context: Optional[Dict] = None) -> LLMResponse:
        """Gera documentação para o código"""
        model = self.models["general"]
        
        prompt = self._build_docs_prompt(code, context)
        
        return self.client.generate(
            model=model,
            prompt=prompt,
            temperature=0.3
        )
    
    def analyze_patterns(self, data: str, context: Optional[Dict] = None) -> LLMResponse:
        """Analisa padrões usando modelo de análise"""
        model = self.models["analysis"]
        
        prompt = self._build_analysis_prompt(data, context)
        
        return self.client.generate(
            model=model,
            prompt=prompt,
            temperature=0.4
        )
    
    def _build_code_prompt(self, task: str, context: Optional[Dict] = None) -> str:
        """Constrói prompt para geração de código"""
        base_prompt = f"""You are a Python code generation specialist. Generate clean, functional code.

Task: {task}

Requirements:
- Write production-ready Python code
- Include proper error handling
- Add docstrings and comments
- Follow PEP 8 standards
- Make code testable and maintainable"""

        if context and "similar_experiences" in context:
            base_prompt += f"\n\nSimilar successful implementations:\n{context['similar_experiences']}"
        
        if context and "patterns" in context:
            base_prompt += f"\n\nRecommended patterns:\n{context['patterns']}"
        
        base_prompt += "\n\nGenerate only the Python code:"
        
        return base_prompt
    
    def _build_test_prompt(self, code: str, context: Optional[Dict] = None) -> str:
        """Constrói prompt para geração de testes"""
        return f"""Generate comprehensive unit tests for this Python code:

```python
{code}
```

Requirements:
- Use pytest framework
- Test normal cases and edge cases
- Include error condition tests
- Use meaningful test names
- Add docstrings to test functions
- Achieve high code coverage

Generate only the test code:"""
    
    def _build_docs_prompt(self, code: str, context: Optional[Dict] = None) -> str:
        """Constrói prompt para documentação"""
        return f"""Generate comprehensive documentation for this Python code:

```python
{code}
```

Include:
1. Module/function docstrings
2. Parameter descriptions with types
3. Return value descriptions
4. Usage examples
5. Any important notes or warnings

Generate the documentation:"""
    
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

    def get_model_info(self) -> Dict[str, Any]:
        """Retorna informações sobre modelos disponíveis"""
        return {
            "configured_models": self.models,
            "available_models": self.client.list_models() if self.client.is_available() else [],
            "ollama_available": self.client.is_available(),
            "host": self.client.host
        }

# Instância global para uso em outros módulos
llm_manager = LLMManager()

# Mock para desenvolvimento/testes
class MockLLMManager:
    """Versão mock para desenvolvimento quando LLMs não estão disponíveis"""
    
    def generate_code(self, task: str, context: Optional[Dict] = None) -> LLMResponse:
        mock_code = f'''def {task.lower().replace(" ", "_")}():
    """
    {task}
    Generated by MockLLMManager for development.
    """
    # TODO: Implement {task}
    return True'''
        
        return LLMResponse(
            content=mock_code,
            model="mock-codellama",
            tokens_used=50,
            generation_time=0.1,
            success=True,
            context_tokens=20, # Valores mock para teste
            response_tokens=30  # Valores mock para teste
        )
    
    def generate_tests(self, code: str, context: Optional[Dict] = None) -> LLMResponse:
        mock_tests = f'''import pytest

def test_{code.split("def ")[1].split("(")[0] if "def " in code else "function"}():
    """Test generated by MockLLMManager"""
    # TODO: Implement comprehensive tests
    assert True'''
        
        return LLMResponse(
            content=mock_tests,
            model="mock-llama",
            tokens_used=30,
            generation_time=0.1,
            success=True,
            context_tokens=10, # Valores mock para teste
            response_tokens=20  # Valores mock para teste
        )
    
    def generate_documentation(self, code: str, context: Optional[Dict] = None) -> LLMResponse:
        return LLMResponse(
            content="# Documentation\nGenerated by MockLLMManager for development.",
            model="mock-llama",
            tokens_used=20,
            generation_time=0.1,
            success=True,
            context_tokens=5, # Valores mock para teste
            response_tokens=15  # Valores mock para teste
        )
    
    def analyze_patterns(self, data: str, context: Optional[Dict] = None) -> LLMResponse:
        return LLMResponse(
            content="Pattern analysis: Mock analysis for development purposes.",
            model="mock-analysis",
            tokens_used=25,
            generation_time=0.1,
            success=True,
            context_tokens=10, # Valores mock para teste
            response_tokens=15  # Valores mock para teste
        )
    
    def get_model_info(self) -> Dict[str, Any]:
        return {
            "configured_models": {"mock": "development"},
            "available_models": ["mock-codellama", "mock-llama"],
            "ollama_available": False,
            "host": "mock://localhost"
        }
