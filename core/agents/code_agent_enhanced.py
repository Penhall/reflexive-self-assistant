"""
CodeAgent Enhanced - Integra GraphRAG mantendo compatibilidade total
Evolução do CodeAgent atual com capacidades de memória experiencial

CORREÇÕES APLICADAS:
- Coleta de métricas reais de LLM (context_tokens, response_tokens)
- Armazenamento de latest_llm_response para captura de métricas
- Métricas de generation_time mais precisas
"""

import yaml
import ast
import subprocess
import tempfile
import hashlib
import time
from pathlib import Path
from typing import Dict, Any, Optional, Tuple, List
from dataclasses import dataclass
from datetime import datetime

from memory.hybrid_store import HybridMemoryStore, CodingExperience
from core.llm.llm_manager import llm_manager, MockLLMManager
from config.paths import IDENTITY_STATE
from config.settings import PERFORMANCE_CONFIG


@dataclass 
class CodeResult:
    """Resultado da geração/execução de código (preservado do atual)"""
    code: str
    success: bool
    execution_result: Optional[str] = None
    error: Optional[str] = None
    quality_score: float = 0.0
    execution_time: float = 0.0
    # Novos campos para GraphRAG
    experience_id: Optional[str] = None
    similar_experiences_used: List[Dict] = None
    learning_applied: bool = False
    # CORREÇÃO: Campos para métricas de performance
    generation_time: float = 0.0  # Tempo de geração pelo LLM
    context_tokens: int = 0
    response_tokens: int = 0


class CodeAgentEnhanced:
    """
    CodeAgent com capacidades GraphRAG - Preserva interface atual + adiciona evolução
    """
    
    def __init__(self, use_mock: bool = False, enable_graphrag: bool = True):
        # Configuração atual preservada
        self.llm = MockLLMManager() if use_mock else llm_manager
        self.latest_output = ""
        self.latest_result = None
        self.adapted = False
        self.generation_history = []
        
        # CORREÇÃO: Armazenar resposta do LLM para capturar métricas
        self.latest_llm_response = None
        
        # Nova capacidade: Memória experiencial
        self.memory = HybridMemoryStore(enable_graphrag=enable_graphrag) if enable_graphrag else None
        self.enable_learning = enable_graphrag
        
        # Carrega perfil simbólico (compatibilidade)
        self.load_symbolic_profile()
        
        print(f"🤖 CodeAgent inicializado {'com GraphRAG' if enable_graphrag else 'modo atual'}")
    
    def load_symbolic_profile(self):
        """Carrega perfil simbólico para adaptar comportamento (preservado)"""
        try:
            with open(IDENTITY_STATE, "r", encoding="utf-8") as f:
                profile = yaml.safe_load(f).get("CodeAgent", {})
                
                pattern = profile.get("predominant_pattern", "").lower()
                if "funcional" in pattern:
                    self.adapted = True
                    self.adaptation_mode = "functional"
                elif "otimizado" in pattern:
                    self.adapted = True
                    self.adaptation_mode = "optimized"
                else:
                    self.adaptation_mode = "standard"
                    
        except FileNotFoundError:
            self.adaptation_mode = "standard"
    
    def execute_task(self, instruction: str, context: Optional[Dict] = None) -> CodeResult:
        """
        Executa tarefa com GraphRAG - Interface mantida, capacidades expandidas
        """
        print(f"⚙️ CodeAgent processando: {instruction}")
        
        # NOVA CAPACIDADE: Buscar experiências similares
        similar_experiences = []
        if self.enable_learning and self.memory:
            similar_experiences = self.memory.retrieve_similar_experiences(instruction, k=3)
            if similar_experiences:
                print(f"🧠 Encontradas {len(similar_experiences)} experiências similares")
        
        # Preparar contexto enriquecido com experiências
        enhanced_context = self._prepare_enhanced_context(instruction, context, similar_experiences)
        
        # CORREÇÃO: Gerar código usando LLM e capturar resposta completa
        llm_response = self.llm.generate_code(instruction, enhanced_context)
        self.latest_llm_response = llm_response  # CORREÇÃO: Armazenar para métricas
        
        if not llm_response.success:
            return self._handle_generation_failure(instruction, llm_response.error)
        
        # CORREÇÃO: Processar e validar código gerado com métricas do LLM
        code_result = self._process_generated_code(llm_response.content, instruction, llm_response)
        
        # NOVA CAPACIDADE: Armazenar experiência no GraphRAG
        if self.enable_learning and self.memory:
            experience_id = self._store_experience(instruction, code_result, similar_experiences)
            code_result.experience_id = experience_id
            code_result.similar_experiences_used = similar_experiences
            code_result.learning_applied = len(similar_experiences) > 0
        
        # Atualizar estado atual (preservado)
        self._update_generation_history(instruction, code_result)
        self.latest_output = code_result.code
        self.latest_result = code_result
        
        # Exibir resultado (melhorado)
        self._display_enhanced_result(instruction, code_result)
        
        return code_result
    
    def _prepare_enhanced_context(self, instruction: str, base_context: Optional[Dict], 
                                 similar_experiences: List[Dict]) -> Dict:
        """Prepara contexto enriquecido com experiências passadas"""
        context = base_context or {}
        
        # Contexto atual preservado
        if self.generation_history:
            successful_patterns = [
                h for h in self.generation_history[-5:] 
                if h.get("success", False)
            ]
            if successful_patterns:
                context["successful_patterns"] = successful_patterns
        
        # Adaptação simbólica (preservada)
        if self.adaptation_mode == "functional":
            context["focus"] = "Create simple, direct, functional code"
            context["style"] = "minimalist"
        elif self.adaptation_mode == "optimized":
            context["focus"] = "Optimize for performance and efficiency"
            context["style"] = "optimized"
        else:
            context["focus"] = "Create well-structured, maintainable code"
            context["style"] = "standard"
        
        # NOVO: Contexto de experiências similares
        if similar_experiences:
            context["similar_experiences"] = self._format_experiences_for_context(similar_experiences)
            context["learning_mode"] = True
            
            # Extrair padrões bem-sucedidos
            successful_patterns = [
                exp for exp in similar_experiences 
                if exp.get("quality", 0) >= 7.0
            ]
            
            if successful_patterns:
                context["proven_approaches"] = [
                    f"Tarefa similar: {exp.get('task', '')} (Qualidade: {exp.get('quality', 0):.1f})"
                    for exp in successful_patterns[:2]
                ]
        
        return context
    
    def _format_experiences_for_context(self, experiences: List[Dict]) -> str:
        """Formata experiências para inclusão no prompt do LLM"""
        if not experiences:
            return ""
        
        formatted = "Experiências similares bem-sucedidas:\n"
        
        for i, exp in enumerate(experiences[:2], 1):  # Máximo 2 para não sobrecarregar prompt
            if exp.get("source") == "graphrag":
                formatted += f"{i}. Tarefa: {exp.get('task', 'N/A')}\n"
                formatted += f"   Qualidade: {exp.get('quality', 0):.1f}/10\n"
                if exp.get('code'):
                    # Mostrar apenas primeiras linhas do código
                    code_preview = '\n'.join(exp['code'].split('\n')[:3])
                    formatted += f"   Abordagem: {code_preview}...\n"
            else:
                formatted += f"{i}. Padrão: {exp.get('pattern', 'N/A')}\n"
            
            formatted += "\n"
        
        return formatted.strip()
    
    def _store_experience(self, instruction: str, result: CodeResult, 
                         similar_experiences: List[Dict]) -> str:
        """Armazena experiência no sistema híbrido"""
        try:
            experience_id = f"exp_{hashlib.md5(f'{instruction}_{datetime.now()}'.encode()).hexdigest()[:8]}"
            
            experience = CodingExperience(
                id=experience_id,
                task_description=instruction,
                code_generated=result.code,
                quality_score=result.quality_score,
                execution_success=result.success,
                agent_name="CodeAgent",
                llm_model=getattr(self.latest_llm_response, 'model', 'unknown'),
                timestamp=datetime.now(),
                context={
                    "adaptation_mode": self.adaptation_mode,
                    "similar_experiences_count": len(similar_experiences),
                    "learning_applied": len(similar_experiences) > 0,
                    "execution_time": result.execution_time,
                    "generation_time": result.generation_time,  # CORREÇÃO: Incluir tempo de geração
                    "context_tokens": result.context_tokens,
                    "response_tokens": result.response_tokens
                },
                yaml_cycle=len(self.generation_history) + 1
            )
            
            success = self.memory.store_experience(experience)
            
            if success:
                print(f"💾 Experiência armazenada: {experience_id}")
                return experience_id
            else:
                print(f"⚠️ Falha ao armazenar experiência")
                return None
                
        except Exception as e:
            print(f"❌ Erro ao armazenar experiência: {e}")
            return None
    
    def _process_generated_code(self, raw_code: str, instruction: str, 
                               llm_response=None) -> CodeResult:
        """
        CORRIGIDO: Processa e valida o código gerado com métricas do LLM
        """
        start_time = time.time()
        
        code = self._extract_python_code(raw_code)
        
        if not code:
            processing_time = time.time() - start_time
            return CodeResult(
                code=f"# Falha ao extrair código válido\n# Instrução: {instruction}",
                success=False,
                error="Não foi possível extrair código Python válido",
                generation_time=processing_time,
                # CORREÇÃO: Capturar métricas do LLM se disponível
                context_tokens=getattr(llm_response, 'context_tokens', 0),
                response_tokens=getattr(llm_response, 'response_tokens', 0)
            )
        
        # Validar sintaxe
        syntax_valid, syntax_error = self._validate_syntax(code)
        if not syntax_valid:
            processing_time = time.time() - start_time
            return CodeResult(
                code=code,
                success=False,
                error=f"Erro de sintaxe: {syntax_error}",
                generation_time=processing_time,
                # CORREÇÃO: Capturar métricas do LLM
                context_tokens=getattr(llm_response, 'context_tokens', 0),
                response_tokens=getattr(llm_response, 'response_tokens', 0)
            )
        
        # Executar código (se seguro)
        execution_result, execution_error, exec_time = self._safe_execution(code)
        
        # Calcular score de qualidade (melhorado)
        quality_score = self._calculate_enhanced_quality_score(
            code, syntax_valid, execution_result, execution_error, instruction
        )
        
        processing_time = time.time() - start_time
        
        return CodeResult(
            code=code,
            success=syntax_valid and execution_error is None,
            execution_result=execution_result,
            error=execution_error,
            quality_score=quality_score,
            execution_time=exec_time,
            # CORREÇÃO: Incluir tempo de processamento e métricas do LLM
            generation_time=processing_time,
            context_tokens=getattr(llm_response, 'context_tokens', 0),
            response_tokens=getattr(llm_response, 'response_tokens', 0)
        )
    
    def _calculate_enhanced_quality_score(self, code: str, syntax_valid: bool, 
                                        execution_result: Optional[str], 
                                        execution_error: Optional[str],
                                        instruction: str) -> float:
        """Calcula score de qualidade melhorado (0-10)"""
        score = 0.0
        
        # Critérios básicos (preservados)
        if syntax_valid:
            score += 3.0
        
        if execution_error is None:
            score += 3.0
        
        # Critérios de qualidade de código (preservados)
        if '"""' in code or "'''" in code:
            score += 1.0
        
        if 'try:' in code or 'except:' in code:
            score += 0.5
        
        if 'def ' in code and '(' in code and ')' in code:
            score += 1.0
        
        if '#' in code:
            score += 0.5
        
        lines = code.split('\n')
        if 5 <= len(lines) <= 50:
            score += 1.0
        
        # NOVOS critérios baseados em aprendizado
        
        # Relevância para instrução
        instruction_words = set(instruction.lower().split())
        code_words = set(code.lower().split())
        relevance = len(instruction_words.intersection(code_words)) / max(len(instruction_words), 1)
        score += relevance * 0.5
        
        # Penalidades por código muito simples ou genérico
        if len(code.strip()) < 50:  # Código muito curto
            score -= 0.5
        
        if code.count('pass') > 1:  # Muitos placeholders
            score -= 1.0
        
        # Bônus por boas práticas
        if 'return' in code and 'def' in code:  # Função com retorno
            score += 0.5
        
        if any(word in code.lower() for word in ['validate', 'check', 'verify']):  # Validação
            score += 0.3
        
        return min(max(score, 0.0), 10.0)
    
    def _extract_python_code(self, raw_text: str) -> str:
        """Extrai código Python do texto gerado pelo LLM (melhorado)"""
        lines = raw_text.split('\n')
        code_lines = []
        in_code_block = False
        
        # Estratégia 1: Blocos markdown ```python
        for line in lines:
            if line.strip().startswith('```python'):
                in_code_block = True
                continue
            elif line.strip().startswith('```') and in_code_block:
                break
            elif in_code_block:
                code_lines.append(line)
        
        # Estratégia 2: Blocos genéricos ```
        if not code_lines:
            in_code_block = False
            for line in lines:
                if line.strip() == '```':
                    if not in_code_block:
                        in_code_block = True
                        continue
                    else:
                        break
                elif in_code_block:
                    code_lines.append(line)
        
        # Estratégia 3: Detecção automática de código Python
        if not code_lines:
            for line in lines:
                stripped = line.strip()
                if (stripped.startswith(('def ', 'class ', 'import ', 'from ')) or
                    '=' in stripped or
                    stripped.startswith(('if ', 'for ', 'while ', 'try:', 'with ')) or
                    line.startswith('    ')):  # Indentação
                    code_lines.append(line)
                    in_code_block = True
                elif in_code_block and not stripped:
                    code_lines.append(line)  # Linha vazia dentro do código
                elif in_code_block and not any(c.isalnum() for c in stripped):
                    continue  # Linha com apenas símbolos
                elif in_code_block:
                    break  # Fim do bloco de código
        
        # Estratégia 4: Pegar tudo se parecer código
        if not code_lines:
            potential_code = '\n'.join(lines)
            if any(keyword in potential_code for keyword in ['def ', 'return ', 'import ', '=']):
                return potential_code.strip()
        
        return '\n'.join(code_lines).strip()
    
    def _validate_syntax(self, code: str) -> Tuple[bool, Optional[str]]:
        """Valida sintaxe do código Python (preservado)"""
        try:
            ast.parse(code)
            return True, None
        except SyntaxError as e:
            return False, str(e)
    
    def _safe_execution(self, code: str) -> Tuple[Optional[str], Optional[str], float]:
        """Executa código de forma segura (preservado)"""
        start_time = time.time()
        
        try:
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, encoding='utf-8') as f:
                f.write(code)
                temp_file = f.name
            
            result = subprocess.run(
                ['python', temp_file],
                capture_output=True,
                text=True,
                timeout=PERFORMANCE_CONFIG["timeout_seconds"],
                encoding='utf-8' # Adicionado encoding para subprocess
            )
            
            execution_time = time.time() - start_time
            
            Path(temp_file).unlink(missing_ok=True)
            
            if result.returncode == 0:
                return result.stdout, None, execution_time
            else:
                return None, result.stderr, execution_time
                
        except subprocess.TimeoutExpired:
            return None, "Timeout: Código demorou muito para executar", time.time() - start_time
        except Exception as e:
            return None, f"Erro na execução: {str(e)}", time.time() - start_time
    
    def _handle_generation_failure(self, instruction: str, error: str) -> CodeResult:
        """Lida com falha na geração de código (preservado)"""
        fallback_code = f'''# Falha na geração automática de código
# Instrução: {instruction}
# Erro: {error}

def {instruction.lower().replace(" ", "_").replace("-", "_")}():
    """
    {instruction}
    
    Implementação de fallback - requer implementação manual.
    """
    # TODO: Implementar {instruction}
    raise NotImplementedError("Implementação pendente")
    
if __name__ == "__main__":
    print("Código gerado em modo fallback")
'''
        
        return CodeResult(
            code=fallback_code,
            success=False,
            error=f"Falha na geração: {error}",
            quality_score=2.0,
            # CORREÇÃO: Incluir métricas mesmo para fallback
            generation_time=0.1,  # Tempo mínimo para fallback
            context_tokens=getattr(self.latest_llm_response, 'context_tokens', 0),
            response_tokens=0  # Sem resposta do LLM para fallback
        )
    
    def _update_generation_history(self, instruction: str, result: CodeResult):
        """CORRIGIDO: Atualiza histórico de gerações com métricas completas"""
        self.generation_history.append({
            "timestamp": datetime.now().isoformat(),
            "instruction": instruction,
            "success": result.success,
            "quality_score": result.quality_score,
            "execution_time": result.execution_time,
            "adaptation_mode": self.adaptation_mode,
            "experience_id": getattr(result, 'experience_id', None),
            "learning_applied": getattr(result, 'learning_applied', False),
            # CORREÇÃO: Adicionar métricas de LLM ao histórico
            "generation_time": result.generation_time,
            "context_tokens": result.context_tokens,
            "response_tokens": result.response_tokens,
            "llm_model": getattr(self.latest_llm_response, 'model', 'unknown')
        })
        
        # Manter apenas últimas 20 gerações
        if len(self.generation_history) > 20:
            self.generation_history = self.generation_history[-20:]
    
    def _display_enhanced_result(self, instruction: str, result: CodeResult):
        """CORRIGIDO: Exibe resultado da geração com métricas"""
        if result.success:
            print(f"✅ Código gerado com sucesso (qualidade: {result.quality_score:.1f}/10)")
            if getattr(result, 'learning_applied', False):
                print(f"🧠 Aprendizado aplicado ({len(getattr(result, 'similar_experiences_used', []))} experiências)")
            if result.execution_result:
                print(f"📤 Saída: {result.execution_result.strip()}")
        else:
            print(f"⚠️ Problemas na geração (qualidade: {result.quality_score:.1f}/10)")
            if result.error:
                print(f"❌ Erro: {result.error}")
        
        # CORREÇÃO: Exibir métricas de performance se disponíveis
        if result.generation_time > 0:
            print(f"⏱️ Tempo de geração: {result.generation_time:.2f}s")
        if result.context_tokens > 0 or result.response_tokens > 0:
            print(f"🔢 Tokens: {result.context_tokens} contexto + {result.response_tokens} resposta = {result.context_tokens + result.response_tokens} total")
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """CORRIGIDO: Retorna estatísticas de performance com métricas de LLM"""
        if not self.generation_history:
            return {"total_generations": 0}
        
        successful = [h for h in self.generation_history if h["success"]]
        quality_scores = [h["quality_score"] for h in self.generation_history]
        learning_applied = [h for h in self.generation_history if h.get("learning_applied", False)]
        
        stats = {
            "total_generations": len(self.generation_history),
            "success_rate": len(successful) / len(self.generation_history),
            "average_quality": sum(quality_scores) / len(quality_scores),
            "best_quality": max(quality_scores),
            "adaptation_mode": self.adaptation_mode,
            "recent_trend": quality_scores[-5:] if len(quality_scores) >= 5 else quality_scores,
            # Novas métricas de aprendizado
            "learning_applied_rate": len(learning_applied) / len(self.generation_history),
            "experiences_stored": len([h for h in self.generation_history if h.get("experience_id")]),
            "graphrag_enabled": self.enable_learning
        }
        
        # CORREÇÃO: Adicionar métricas de tokens e performance de LLM
        generation_times = [h.get("generation_time", 0) for h in self.generation_history if h.get("generation_time", 0) > 0]
        context_tokens = [h.get("context_tokens", 0) for h in self.generation_history]
        response_tokens = [h.get("response_tokens", 0) for h in self.generation_history]
        
        if generation_times:
            stats["avg_generation_time"] = sum(generation_times) / len(generation_times)
            stats["max_generation_time"] = max(generation_times)
            stats["min_generation_time"] = min(generation_times)
        
        if context_tokens:
            stats["total_context_tokens"] = sum(context_tokens)
            stats["avg_context_tokens"] = sum(context_tokens) / len(context_tokens)
        
        if response_tokens:
            stats["total_response_tokens"] = sum(response_tokens)
            stats["avg_response_tokens"] = sum(response_tokens) / len(response_tokens)
        
        if context_tokens and response_tokens:
            total_tokens = sum(context_tokens) + sum(response_tokens)
            stats["total_tokens_used"] = total_tokens
            stats["avg_tokens_per_generation"] = total_tokens / len(self.generation_history)
        
        return stats
    
    def get_learning_insights(self) -> Dict[str, Any]:
        """Retorna insights sobre aprendizado (NOVO)"""
        if not self.enable_learning or not self.memory:
            return {"learning_enabled": False}
        
        try:
            # Estatísticas básicas
            with_learning = [h for h in self.generation_history if h.get("learning_applied", False)]
            without_learning = [h for h in self.generation_history if not h.get("learning_applied", False)]
            
            # Comparar qualidade com e sem aprendizado
            avg_quality_with_learning = (
                sum(h["quality_score"] for h in with_learning) / len(with_learning)
                if with_learning else 0
            )
            
            avg_quality_without_learning = (
                sum(h["quality_score"] for h in without_learning) / len(without_learning)
                if without_learning else 0
            )
            
            improvement = avg_quality_with_learning - avg_quality_without_learning
            
            return {
                "learning_enabled": True,
                "total_experiences_stored": len(self.generation_history),
                "learning_applied_count": len(with_learning),
                "avg_quality_with_learning": avg_quality_with_learning,
                "avg_quality_without_learning": avg_quality_without_learning,
                "quality_improvement": improvement,
                "improvement_percentage": (improvement / avg_quality_without_learning * 100) if avg_quality_without_learning > 0 else 0
            }
            
        except Exception as e:
            return {"learning_enabled": True, "error": str(e)}
    
    def close(self):
        """Fecha conexões (NOVO)"""
        if self.memory:
            self.memory.close()


# Manter compatibilidade com sistema atual
class CodeAgent(CodeAgentEnhanced):
    """Alias para compatibilidade com código existente"""
    pass


# Teste de funcionalidade
if __name__ == "__main__":
    # Teste com GraphRAG
    agent = CodeAgentEnhanced(enable_graphrag=True, use_mock=True)  # Mock para teste
    
    # Primeira geração (sem experiências)
    result1 = agent.execute_task("criar função que soma dois números")
    print(f"Resultado 1: {result1.success}, Qualidade: {result1.quality_score}")
    print(f"Métricas: {result1.generation_time:.2f}s, {result1.context_tokens} + {result1.response_tokens} tokens")
    
    # Segunda geração similar (deve usar experiência anterior)
    result2 = agent.execute_task("criar função que adiciona dois valores")
    print(f"Resultado 2: {result2.success}, Qualidade: {result2.quality_score}")
    print(f"Aprendizado aplicado: {result2.learning_applied}")
    print(f"Métricas: {result2.generation_time:.2f}s, {result2.context_tokens} + {result2.response_tokens} tokens")
    
    # Estatísticas
    stats = agent.get_performance_stats()
    print(f"Estatísticas: {stats}")
    
    insights = agent.get_learning_insights()
    print(f"Insights de aprendizado: {insights}")
    
    agent.close()