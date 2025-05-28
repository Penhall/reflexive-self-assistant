"""
Cliente Ollama otimizado para modelos leves
Integração com o sistema RSCA existente
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

class OllamaClient:
    """Cliente otimizado para modelos leves via Ollama"""
    
    def __init__(self, host: str = "http://localhost:11434"):
        self.host = host
        self.timeout = 60  # Timeout mais longo para modelos leves
        self.retry_attempts = 2
        
        # Configurações específicas por modelo
        self.model_configs = {
            "tinyllama:1.1b": {
                "temperature": 0.3,
                "top_p": 0.9,
                "num_predict": 512,
                "specialty": "testes_rapidos",
                "ram_usage": "800MB"
            },
            "llama3.2:1b": {
                "temperature": 0.2,
                "top_p": 0.85,
                "num_predict": 1024,
                "specialty": "tarefas_simples", 
                "ram_usage": "1GB"
            },
            "codegemma:2b": {
                "temperature": 0.1,
                "top_p": 0.9,
                "num_predict": 2048,
                "specialty": "codigo",
                "ram_usage": "1.5GB"
            },
            "phi3:mini": {
                "temperature": 0.15,
                "top_p": 0.85,
                "num_predict": 1536,
                "specialty": "equilibrado",
                "ram_usage": "2GB"
            }
        }
        
        # Modelo preferencial por tarefa
        self.task_models = {
            "codigo": "codegemma:2b",
            "testes": "tinyllama:1.1b", 
            "documentacao": "phi3:mini",
            "analise": "llama3.2:1b",
            "geral": "phi3:mini"
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
        preferred = self.task_models.get(task_type.lower(), "phi3:mini")
        if preferred in available_models:
            return preferred
        
        # Fallback para modelos disponíveis em ordem de preferência
        fallback_order = [
            "codegemma:2b",    # Melhor para código
            "phi3:mini",       # Equilibrado
            "llama3.2:1b",     # Simples mas funcional
            "tinyllama:1.1b"   # Ultra-leve
        ]
        
        for model in fallback_order:
            if model in available_models:
                return model
        
        # Se nenhum modelo conhecido, usa o primeiro disponível
        return available_models[0] if available_models else "phi3:mini"
    
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
                "num_predict": model_config.get("num_predict", 1024),
                "num_ctx": 4096,  # Contexto padrão
                "repeat_penalty": 1.1,
                "stop": ["</s>", "\n\n\n"]  # Stop tokens para evitar repetição
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
                    
                    return LLMResponse(
                        content=data.get("response", "").strip(),
                        model=model,
                        tokens_used=data.get("eval_count", 0),
                        generation_time=generation_time,
                        success=True
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
            error=error_msg
        )
    
    def generate_code(self, task: str, context: Optional[Dict] = None) -> LLMResponse:
        """Gera código usando o melhor modelo disponível"""
        model = self.get_best_model_for_task("codigo")
        
        # Construir prompt otimizado para código
        prompt = self._build_code_prompt(task, context)
        
        return self.generate(model, prompt)
    
    def generate_tests(self, code: str, context: Optional[Dict] = None) -> LLMResponse:
        """Gera testes usando modelo leve e rápido"""
        model = self.get_best_model_for_task("testes")
        
        prompt = self._build_test_prompt(code, context)
        
        return self.generate(model, prompt)
    
    def generate_docs(self, code: str, context: Optional[Dict] = None) -> LLMResponse:
        """Gera documentação usando modelo equilibrado"""
        model = self.get_best_model_for_task("documentacao")
        
        prompt = self._build_docs_prompt(code, context)
        
        return self.generate(model, prompt)
    
    def _build_code_prompt(self, task: str, context: Optional[Dict] = None) -> str:
        """Constrói prompt otimizado para geração de código"""
        base_prompt = f"""Você é um assistente de programação especializado em Python.

Tarefa: {task}

Instruções:
- Escreva código Python limpo e funcional
- Inclua docstrings simples
- Use nomes de variáveis descritivos
- Adicione tratamento de erro básico
- Mantenha o código conciso mas legível

Responda APENAS com o código Python, sem explicações extras:"""

        if context and "similar_experiences" in context:
            base_prompt += f"\n\nExemplos similares bem-sucedidos:\n{context['similar_experiences']}"
        
        if context and "patterns" in context:
            base_prompt += f"\n\nPadrões recomendados:\n{context['patterns']}"
        
        return base_prompt
    
    def _build_test_prompt(self, code: str, context: Optional[Dict] = None) -> str:
        """Constrói prompt para geração de testes"""
        return f"""Crie testes em Python para este código:

```python
{code}
```

Instruções:
- Use pytest
- Teste casos normais e edge cases
- Nomes de testes descritivos
- Mantenha simples e direto

Responda APENAS com o código de teste:"""
    
    def _build_docs_prompt(self, code: str, context: Optional[Dict] = None) -> str:
        """Constrói prompt para documentação"""
        return f"""Crie documentação para este código Python:

```python
{code}
```

Instruções:
- Docstrings no formato Google/Numpy
- Descreva parâmetros e retorno
- Adicione exemplo de uso
- Mantenha conciso mas informativo

Responda APENAS com a documentação:"""
    
    def test_model(self, model: str) -> bool:
        """Testa se um modelo específico funciona"""
        try:
            test_prompt = "def hello():\n    return"
            response = self.generate(model, f"Complete: {test_prompt}")
            return response.success and len(response.content.strip()) > 0
        except:
            return False
    
    def test_all_models(self) -> Dict[str, bool]:
        """Testa todos os modelos disponíveis"""
        models = self.list_models()
        results = {}
        
        for model in models:
            print(f"🧪 Testando {model}...")
            results[model] = self.test_model(model)
            status = "✅" if results[model] else "❌"
            print(f"   {status} {model}")
        
        return results
    
    def get_system_info(self) -> Dict[str, Any]:
        """Retorna informações completas do sistema"""
        models_available = self.list_models()
        
        return {
            "ollama_available": self.is_available(),
            "host": self.host,
            "models_available": models_available,
            "recommended_models": self.task_models,
            "model_info": self.model_configs,
            "total_models": len(models_available)
        }
    
    def get_model_stats(self, model: str) -> Dict[str, Any]:
        """Retorna estatísticas de uso de um modelo específico"""
        config = self.model_configs.get(model, {})
        
        return {
            "model": model,
            "specialty": config.get("specialty", "unknown"),
            "ram_usage": config.get("ram_usage", "unknown"),
            "recommended_tasks": [task for task, rec_model in self.task_models.items() 
                                if rec_model == model],
            "temperature": config.get("temperature", 0.2),
            "max_tokens": config.get("num_predict", 1024)
        }
    
    def suggest_model_for_task(self, task_description: str) -> str:
        """Sugere o melhor modelo baseado na descrição da tarefa"""
        task_lower = task_description.lower()
        
        # Palavras-chave por tipo de tarefa
        keywords = {
            "codigo": ["função", "classe", "implementar", "código", "algorithm", "program", "script"],
            "testes": ["teste", "test", "verificar", "validar", "assert", "unittest"],
            "documentacao": ["documentar", "explicar", "readme", "doc", "comment", "describe"],
            "analise": ["analisar", "avaliar", "revisar", "review", "optimize", "refactor"]
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
    """Manager otimizado para modelos leves"""
    
    def __init__(self):
        self.client = ollama_client
        self.current_model = None
        self.usage_stats = {}
    
    def generate_code(self, task: str, context: Optional[Dict] = None) -> LLMResponse:
        """Interface principal para geração de código"""
        # Selecionar modelo automaticamente
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