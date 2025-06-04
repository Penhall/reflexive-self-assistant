"""
Cliente Ollama Melhorado - Versão com Prompts Corrigidos
Foca em CodeLlama e resolução de problemas de docstrings
"""

import requests
import time
import json
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime

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
    """Cliente otimizado para modelos CodeLlama e correção de problemas"""
    
    def __init__(self, host: str = "http://localhost:11434"):
        self.host = host
        self.timeout = 60
        self.retry_attempts = 2
        
        # Configurações CORRIGIDAS - CodeLlama como foco
        self.model_configs = {
            "codellama:7b": {
                "temperature": 0.1,  # Baixa para código mais determinístico
                "top_p": 0.9,
                "num_predict": 2048,
                "specialty": "codigo_python",
                "ram_usage": "8GB",
                "quality": "alta"
            },
            "codellama:13b": {
                "temperature": 0.05,  # Muito baixa para código complexo
                "top_p": 0.85,
                "num_predict": 3072,
                "specialty": "codigo_complexo",
                "ram_usage": "16GB", 
                "quality": "muito_alta"
            },
            "llama3:8b": {
                "temperature": 0.2,
                "top_p": 0.9,
                "num_predict": 2048,
                "specialty": "geral_balanceado",
                "ram_usage": "8GB",
                "quality": "media_alta"
            },
            "qwen2:1.5b": {
                "temperature": 0.3,
                "top_p": 0.9,
                "num_predict": 1024,
                "specialty": "testes_rapidos",
                "ram_usage": "2GB",
                "quality": "baixa",
                "warning": "Pode gerar código com problemas de sintaxe"
            }
        }
        
        # Modelo preferencial por tarefa - CORRIGIDO
        self.task_models = {
            "codigo": "codellama:7b",       # MUDANÇA CRÍTICA: Era qwen2:1.5b
            "testes": "codellama:7b",       # MUDANÇA: CodeLlama para testes também
            "documentacao": "llama3:8b",    # Mantido
            "analise": "llama3:8b",         # Mantido
            "geral": "llama3:8b"            # Mantido
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
            print(f"Erro ao listar modelos: {e}")
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
            # Para código, priorizar CodeLlama
            fallback_order = [
                "codellama:13b",    # Melhor qualidade
                "codellama:7b",     # Boa qualidade, menos RAM
                "llama3:8b",        # Geral mas decente
                "qwen2:1.5b"        # Último recurso (problemático)
            ]
        else:
            # Para outras tarefas, priorizar modelos gerais
            fallback_order = [
                "llama3:8b",        # Melhor geral
                "codellama:7b",     # Pode fazer outras tarefas
                "codellama:13b",    # Overkill mas funciona
                "qwen2:1.5b"        # Último recurso
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
        
        # Preparar payload com configurações melhoradas
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
                # Stop tokens MELHORADOS para evitar problemas
                "stop": [
                    "</s>", 
                    "\n\n\n",           # Evitar repetição excessiva
                    "```\n\n",          # Parar após blocos de código
                    "# End of code",    # Parar em comentários de fim
                    "Human:",           # Evitar continuação de diálogo
                    "Assistant:"        # Evitar continuação de diálogo
                ]
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
                    
                    # Extrair métricas de tokens corretamente
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
                print(f"⚠️ Tentativa {attempt + 1} falhou: {error_msg}. Tentando novamente...")
                time.sleep(2 ** attempt)  # Backoff exponencial
        
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
    
    def generate_code(self, task: str, context: Optional[Dict] = None) -> LLMResponse:
        """Gera código usando o melhor modelo disponível"""
        model = self.get_best_model_for_task("codigo")
        
        # Construir prompt ROBUSTO para código
        prompt = self._build_robust_code_prompt(task, context)
        
        return self.generate(model, prompt)
    
    def generate_tests(self, code: str, context: Optional[Dict] = None) -> LLMResponse:
        """Gera testes usando modelo otimizado"""
        model = self.get_best_model_for_task("testes")
        
        prompt = self._build_robust_test_prompt(code, context)
        
        return self.generate(model, prompt)
    
    def generate_docs(self, code: str, context: Optional[Dict] = None) -> LLMResponse:
        """Gera documentação usando modelo equilibrado"""
        model = self.get_best_model_for_task("documentacao")
        
        prompt = self._build_robust_docs_prompt(code, context)
        
        return self.generate(model, prompt)
    
    def _build_robust_code_prompt(self, task: str, context: Optional[Dict] = None) -> str:
        """Constrói prompt ROBUSTO para geração de código - CORREÇÃO PRINCIPAL"""
        
        # Template base com regras críticas
        base_prompt = f"""You are an expert Python developer. Write clean, syntactically perfect code.

CRITICAL REQUIREMENTS (MUST FOLLOW):
1. ALWAYS close docstrings with triple quotes (\"\"\")
2. NEVER leave docstrings unterminated - this causes syntax errors
3. Use exactly 4 spaces for indentation
4. Write complete, executable Python code
5. Include proper error handling
6. Follow PEP 8 style guidelines

TASK: {task}

CODE STANDARDS:
- Include complete docstrings with parameters and return values
- Add inline comments for complex logic
- Use descriptive variable and function names
- Handle edge cases and errors appropriately
- Write testable, maintainable code"""

        # Adicionar contexto de experiências similares se disponível
        if context and "similar_experiences" in context:
            experiences = context["similar_experiences"]
            if experiences and len(experiences.strip()) > 0:
                base_prompt += f"\n\nSUCCESSFUL EXAMPLES:\n{experiences}"
        
        # Adicionar padrões recomendados se disponível
        if context and "patterns" in context:
            patterns = context["patterns"]
            if patterns:
                base_prompt += f"\n\nRECOMMENDED PATTERNS:\n{patterns}"
        
        # Instruções finais CRÍTICAS
        base_prompt += """

OUTPUT INSTRUCTIONS:
- Respond with ONLY the Python code
- NO explanations, markdown, or extra text
- Ensure ALL docstrings are properly closed
- Make sure the code is syntactically valid

Python code:"""
        
        return base_prompt
    
    def _build_robust_test_prompt(self, code: str, context: Optional[Dict] = None) -> str:
        """Constrói prompt robusto para geração de testes"""
        return f"""Generate comprehensive Python unit tests for this code:

```python
{code}
```

CRITICAL REQUIREMENTS:
1. ALWAYS close docstrings with triple quotes (\"\"\")
2. Use pytest framework
3. Write syntactically correct test code
4. Include all necessary imports

TEST REQUIREMENTS:
- Test normal execution paths
- Test edge cases and boundary conditions
- Test error conditions with appropriate assertions
- Use descriptive test function names
- Include proper test docstrings (FULLY CLOSED)
- Make tests executable and independent

OUTPUT: Only the test code, no explanations.

Test code:"""
    
    def _build_robust_docs_prompt(self, code: str, context: Optional[Dict] = None) -> str:
        """Constrói prompt robusto para documentação"""
        return f"""Generate comprehensive documentation for this Python code:

```python
{code}
```

CRITICAL REQUIREMENTS:
1. ALWAYS close docstrings with triple quotes (\"\"\")
2. Use proper Python docstring format (Google or NumPy style)
3. Include complete parameter and return descriptions

DOCUMENTATION REQUIREMENTS:
- Module/class/function docstrings (PROPERLY CLOSED)
- Parameter descriptions with types
- Return value descriptions with types
- Usage examples with expected output
- Important notes about behavior or limitations
- Proper formatting and structure

OUTPUT: Only the documentation code, no explanations.

Documentation:"""
    
    def test_model(self, model: str) -> bool:
        """Testa se um modelo específico funciona corretamente"""
        try:
            test_prompt = """Write a simple Python function that returns 'Hello World':

def hello():"""
            
            response = self.generate(model, test_prompt)
            
            # Verificar se a resposta é válida
            return (response.success and 
                    len(response.content.strip()) > 0 and
                    "def " in response.content)
        except:
            return False
    
    def test_all_models(self) -> Dict[str, bool]:
        """Testa todos os modelos disponíveis"""
        models = self.list_models()
        results = {}
        
        print("🧪 Testando modelos disponíveis...")
        for model in models:
            print(f"   Testando {model}...")
            results[model] = self.test_model(model)
            status = "✅" if results[model] else "❌"
            config = self.model_configs.get(model, {})
            quality = config.get("quality", "unknown")
            print(f"   {status} {model} (qualidade: {quality})")
            
            # Aviso especial para qwen2
            if "qwen2" in model and results[model]:
                print(f"   ⚠️ {model}: {config.get('warning', '')}")
        
        return results
    
    def get_system_info(self) -> Dict[str, Any]:
        """Retorna informações completas do sistema"""
        models_available = self.list_models()
        
        # Verificar se temos modelos adequados para código
        code_models = [m for m in models_available if "codellama" in m.lower()]
        has_good_code_model = len(code_models) > 0
        
        return {
            "ollama_available": self.is_available(),
            "host": self.host,
            "models_available": models_available,
            "code_models": code_models,
            "has_good_code_model": has_good_code_model,
            "recommended_models": self.task_models,
            "model_info": self.model_configs,
            "total_models": len(models_available),
            "warnings": [
                "qwen2:1.5b pode gerar código com problemas de sintaxe",
                "CodeLlama é recomendado para melhor qualidade de código"
            ] if not has_good_code_model else []
        }
    
    def get_model_stats(self, model: str) -> Dict[str, Any]:
        """Retorna estatísticas de um modelo específico"""
        config = self.model_configs.get(model, {})
        
        return {
            "model": model,
            "specialty": config.get("specialty", "unknown"),
            "quality": config.get("quality", "unknown"),
            "ram_usage": config.get("ram_usage", "unknown"),
            "recommended_tasks": [task for task, rec_model in self.task_models.items() 
                                if rec_model == model],
            "temperature": config.get("temperature", 0.2),
            "max_tokens": config.get("num_predict", 2048),
            "warning": config.get("warning", None)
        }
    
    def suggest_model_for_task(self, task_description: str) -> str:
        """Sugere o melhor modelo baseado na descrição da tarefa"""
        task_lower = task_description.lower()
        
        # Palavras-chave por tipo de tarefa
        keywords = {
            "codigo": [
                "função", "classe", "implementar", "código", "algorithm", 
                "program", "script", "def", "class", "python", "código"
            ],
            "testes": [
                "teste", "test", "verificar", "validar", "assert", 
                "unittest", "pytest", "testing"
            ],
            "documentacao": [
                "documentar", "explicar", "readme", "doc", "comment", 
                "describe", "documentation", "manual"
            ],
            "analise": [
                "analisar", "avaliar", "revisar", "review", "optimize", 
                "refactor", "pattern", "análise"
            ]
        }
        
        # Contar matches por categoria
        scores = {}
        for task_type, words in keywords.items():
            scores[task_type] = sum(1 for word in words if word in task_lower)
        
        # Retornar categoria com maior score
        best_task_type = max(scores, key=scores.get) if any(scores.values()) else "geral"
        return self.get_best_model_for_task(best_task_type)

# Instância global para uso no sistema
ollama_client = OllamaClient()

class LightweightLLMManager:
    """Manager otimizado para modelos leves com melhor qualidade"""
    
    def __init__(self):
        self.client = ollama_client
        self.current_model = None
        self.usage_stats = {}
    
    def generate_code(self, task: str, context: Optional[Dict] = None) -> LLMResponse:
        """Interface principal para geração de código - CORRIGIDA"""
        # Selecionar modelo automaticamente (MUDANÇA: CodeLlama primeiro)
        model = self.client.suggest_model_for_task(task)
        self.current_model = model
        
        # Log da operação
        self._log_usage("code_generation", model)
        
        return self.client.generate_code(task, context)
    
    def generate_tests(self, code: str, context: Optional[Dict] = None) -> LLMResponse:
        """Interface para geração de testes"""
        model = self.client.get_best_model_for_task("testes")
        self.current_model = model
        
        self._log_usage("test_generation", model)
        
        return self.client.generate_tests(code, context)
    
    def generate_documentation(self, code: str, context: Optional[Dict] = None) -> LLMResponse:
        """Interface para geração de documentação"""
        model = self.client.get_best_model_for_task("documentacao")
        self.current_model = model
        
        self._log_usage("doc_generation", model)
        
        return self.client.generate_docs(code, context)
    
    def _log_usage(self, operation: str, model: str):
        """Log de uso para estatísticas"""
        timestamp = datetime.now().isoformat()
        
        if operation not in self.usage_stats:
            self.usage_stats[operation] = []
        
        self.usage_stats[operation].append({
            "model": model,
            "timestamp": timestamp
        })
    
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
    
    def get_model_info(self) -> Dict[str, Any]:
        """Retorna informações do sistema - MÉTODO CRÍTICO"""
        return self.client.get_system_info()
    
    def is_ready(self) -> bool:
        """Verifica se o sistema está pronto para uso"""
        return self.client.is_available() and len(self.client.list_models()) > 0
    
    def get_system_status(self) -> Dict[str, Any]:
        """Status completo do sistema"""
        return {
            "ready": self.is_ready(),
            "system_info": self.client.get_system_info(),
            "usage_stats": self.get_usage_stats()
        }

# Instância global para integração com o sistema existente
llm_manager = LightweightLLMManager()