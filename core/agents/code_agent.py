"""
CodeAgent atualizado com integração real de LLM
"""

import yaml
import ast
import subprocess
import tempfile
from pathlib import Path
from typing import Dict, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime

from core.llm.llm_manager import llm_manager, MockLLMManager
from config.paths import IDENTITY_STATE
from config.settings import PERFORMANCE_CONFIG

@dataclass
class CodeResult:
    """Resultado da geração/execução de código"""
    code: str
    success: bool
    execution_result: Optional[str] = None
    error: Optional[str] = None
    quality_score: float = 0.0
    execution_time: float = 0.0

class CodeAgent:
    """Agente responsável por gerar código funcional usando LLMs reais"""
    
    def __init__(self, use_mock: bool = False):
        self.llm = MockLLMManager() if use_mock else llm_manager
        self.latest_output = ""
        self.latest_result = None
        self.adapted = False
        self.generation_history = []
        self.load_symbolic_profile()
    
    def load_symbolic_profile(self):
        """Carrega perfil simbólico para adaptar comportamento"""
        try:
            with open(IDENTITY_STATE, "r", encoding="utf-8") as f:
                profile = yaml.safe_load(f).get("CodeAgent", {})
                
                # Adaptação baseada em padrão predominante
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
        """Executa tarefa de geração de código com LLM real"""
        print(f"⚙️ CodeAgent processando: {instruction}")
        
        # Preparar contexto baseado na adaptação simbólica
        enhanced_context = self._prepare_context(instruction, context)
        
        # Gerar código usando LLM
        llm_response = self.llm.generate_code(instruction, enhanced_context)
        
        if not llm_response.success:
            return self._handle_generation_failure(instruction, llm_response.error)
        
        # Processar e validar código gerado
        code_result = self._process_generated_code(llm_response.content, instruction)
        
        # Atualizar histórico e estado
        self._update_generation_history(instruction, code_result)
        self.latest_output = code_result.code
        self.latest_result = code_result
        
        # Exibir resultado
        self._display_result(instruction, code_result)
        
        return code_result
    
    def _prepare_context(self, instruction: str, base_context: Optional[Dict] = None) -> Dict:
        """Prepara contexto enriquecido baseado na adaptação simbólica"""
        context = base_context or {}
        
        # Adicionar histórico de sucesso
        if self.generation_history:
            successful_patterns = [
                h for h in self.generation_history[-5:] 
                if h.get("success", False)
            ]
            if successful_patterns:
                context["successful_patterns"] = successful_patterns
        
        # Adaptação baseada no modo simbólico
        if self.adaptation_mode == "functional":
            context["focus"] = "Create simple, direct, functional code"
            context["style"] = "minimalist"
        elif self.adaptation_mode == "optimized":
            context["focus"] = "Optimize for performance and efficiency"
            context["style"] = "optimized"
        else:
            context["focus"] = "Create well-structured, maintainable code"
            context["style"] = "standard"
        
        return context
    
    def _process_generated_code(self, raw_code: str, instruction: str) -> CodeResult:
        """Processa e valida o código gerado"""
        # Extrair código Python do resultado
        code = self._extract_python_code(raw_code)
        
        if not code:
            return CodeResult(
                code=f"# Falha ao extrair código válido\n# Instrução: {instruction}",
                success=False,
                error="Não foi possível extrair código Python válido"
            )
        
        # Validar sintaxe
        syntax_valid, syntax_error = self._validate_syntax(code)
        if not syntax_valid:
            return CodeResult(
                code=code,
                success=False,
                error=f"Erro de sintaxe: {syntax_error}"
            )
        
        # Executar código (se seguro)
        execution_result, execution_error, exec_time = self._safe_execution(code)
        
        # Calcular score de qualidade
        quality_score = self._calculate_quality_score(code, syntax_valid, execution_result, execution_error)
        
        return CodeResult(
            code=code,
            success=syntax_valid and execution_error is None,
            execution_result=execution_result,
            error=execution_error,
            quality_score=quality_score,
            execution_time=exec_time
        )
    
    def _extract_python_code(self, raw_text: str) -> str:
        """Extrai código Python do texto gerado pelo LLM"""
        # Procurar por blocos de código Python
        lines = raw_text.split('\n')
        code_lines = []
        in_code_block = False
        
        for line in lines:
            if line.strip().startswith('```python'):
                in_code_block = True
                continue
            elif line.strip().startswith('```') and in_code_block:
                break
            elif in_code_block:
                code_lines.append(line)
            elif line.strip().startswith('def ') or line.strip().startswith('class '):
                # Código sem marcação de bloco
                code_lines.append(line)
                in_code_block = True
            elif in_code_block and (line.startswith('    ') or line.strip() == ''):
                code_lines.append(line)
            elif in_code_block and not line.startswith('    '):
                break
        
        # Se não encontrou bloco de código, pegar tudo que parece código
        if not code_lines:
            for line in lines:
                if (line.strip().startswith(('def ', 'class ', 'import ', 'from ')) or
                    line.strip().startswith('#') or
                    '=' in line or
                    line.startswith('    ')):
                    code_lines.append(line)
        
        return '\n'.join(code_lines).strip()
    
    def _validate_syntax(self, code: str) -> Tuple[bool, Optional[str]]:
        """Valida sintaxe do código Python"""
        try:
            ast.parse(code)
            return True, None
        except SyntaxError as e:
            return False, str(e)
    
    def _safe_execution(self, code: str) -> Tuple[Optional[str], Optional[str], float]:
        """Executa código de forma segura em ambiente isolado"""
        import time
        start_time = time.time()
        
        try:
            # Criar arquivo temporário com encoding UTF-8
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, encoding='utf-8') as f:
                # Adicionar declaração de encoding UTF-8
                if not code.startswith('# -*- coding: utf-8 -*-'):
                    code = '# -*- coding: utf-8 -*-\n\n' + code
                f.write(code)
                temp_file = f.name
            
            # Executar com timeout
            result = subprocess.run(
                ['python', temp_file],
                capture_output=True,
                text=True,
                timeout=PERFORMANCE_CONFIG["timeout_seconds"]
            )
            
            execution_time = time.time() - start_time
            
            # Limpar arquivo temporário
            Path(temp_file).unlink(missing_ok=True)
            
            if result.returncode == 0:
                return result.stdout, None, execution_time
            else:
                return None, result.stderr, execution_time
                
        except subprocess.TimeoutExpired:
            return None, "Timeout: Código demorou muito para executar", time.time() - start_time
        except Exception as e:
            return None, f"Erro na execução: {str(e)}", time.time() - start_time
    
    def _calculate_quality_score(self, code: str, syntax_valid: bool, 
                                execution_result: Optional[str], 
                                execution_error: Optional[str]) -> float:
        """Calcula score de qualidade do código (0-10)"""
        score = 0.0
        
        # Sintaxe válida (peso: 3)
        if syntax_valid:
            score += 3.0
        
        # Execução sem erro (peso: 3)
        if execution_error is None:
            score += 3.0
        
        # Qualidade do código (peso: 4)
        # Docstrings
        if '"""' in code or "'''" in code:
            score += 1.0
        
        # Tratamento de erro
        if 'try:' in code or 'except:' in code:
            score += 0.5
        
        # Funções bem definidas
        if 'def ' in code and '(' in code and ')' in code:
            score += 1.0
        
        # Comentários
        if '#' in code:
            score += 0.5
        
        # Não muito longo nem muito curto
        lines = code.split('\n')
        if 5 <= len(lines) <= 50:
            score += 1.0
        
        return min(score, 10.0)
    
    def _handle_generation_failure(self, instruction: str, error: str) -> CodeResult:
        """Lida com falha na geração de código"""
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
            quality_score=2.0  # Score baixo para fallback
        )
    
    def _update_generation_history(self, instruction: str, result: CodeResult):
        """Atualiza histórico de gerações"""
        self.generation_history.append({
            "timestamp": datetime.now().isoformat(),
            "instruction": instruction,
            "success": result.success,
            "quality_score": result.quality_score,
            "execution_time": result.execution_time,
            "adaptation_mode": self.adaptation_mode
        })
        
        # Manter apenas últimas 20 gerações
        if len(self.generation_history) > 20:
            self.generation_history = self.generation_history[-20:]
    
    def _display_result(self, instruction: str, result: CodeResult):
        """Exibe resultado da geração"""
        if result.success:
            print(f"✅ Código gerado com sucesso (qualidade: {result.quality_score:.1f}/10)")
            if result.execution_result:
                print(f"📤 Saída: {result.execution_result.strip()}")
        else:
            print(f"⚠️ Problemas na geração (qualidade: {result.quality_score:.1f}/10)")
            if result.error:
                print(f"❌ Erro: {result.error}")
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas de performance"""
        if not self.generation_history:
            return {"total_generations": 0}
        
        successful = [h for h in self.generation_history if h["success"]]
        quality_scores = [h["quality_score"] for h in self.generation_history]
        
        return {
            "total_generations": len(self.generation_history),
            "success_rate": len(successful) / len(self.generation_history),
            "average_quality": sum(quality_scores) / len(quality_scores),
            "best_quality": max(quality_scores),
            "adaptation_mode": self.adaptation_mode,
            "recent_trend": quality_scores[-5:] if len(quality_scores) >= 5 else quality_scores
        }
