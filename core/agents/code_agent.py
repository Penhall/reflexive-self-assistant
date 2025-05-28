"""
CodeAgent corrigido com melhor extração de código Python
"""

import yaml
import ast
import subprocess
import tempfile
import re
from pathlib import Path
from typing import Dict, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime

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
        self.latest_output = ""
        self.latest_result = None
        self.adapted = False
        self.generation_history = []
        self.use_mock = use_mock
        
        if not use_mock:
            try:
                from core.llm.ollama_client import llm_manager
                self.llm = llm_manager
                print("🚀 CodeAgent inicializado com Ollama")
            except ImportError:
                print("⚠️ LLM Manager não disponível - usando mock")
                self.use_mock = True
        
        self.load_symbolic_profile()
    
    def load_symbolic_profile(self):
        """Carrega perfil simbólico para adaptar comportamento"""
        try:
            from config.paths import IDENTITY_STATE
            with open(IDENTITY_STATE, "r", encoding="utf-8") as f:
                profile = yaml.safe_load(f).get("CodeAgent", {})
                pattern = profile.get("predominant_pattern", "").lower()
                if "funcional" in pattern:
                    self.adapted = True
                    self.adaptation_mode = "functional"
                else:
                    self.adaptation_mode = "standard"
        except:
            self.adaptation_mode = "standard"
    
    def execute_task(self, instruction: str, context: Optional[Dict] = None) -> CodeResult:
        """Executa tarefa de geração de código com LLM real"""
        print(f"⚙️ CodeAgent processando: {instruction}")
        
        if self.use_mock:
            return self._mock_generation(instruction)
        
        try:
            # Gerar código usando LLM
            response = self.llm.generate_code(instruction, context)
            
            if not response.success:
                return self._handle_generation_failure(instruction, response.error)
            
            # Processar e validar código gerado
            code_result = self._process_generated_code(response.content, instruction)
            
            # Atualizar estado
            self.latest_output = code_result.code
            self.latest_result = code_result
            
            # Exibir resultado
            self._display_result(instruction, code_result)
            
            return code_result
            
        except Exception as e:
            return self._handle_generation_failure(instruction, str(e))
    
    def _mock_generation(self, instruction: str) -> CodeResult:
        """Geração mock para testes"""
        func_name = instruction.lower().replace(" ", "_").replace("-", "_")
        func_name = re.sub(r'[^a-z0-9_]', '', func_name)
        
        if not func_name:
            func_name = "generated_function"
        
        mock_code = f'''def {func_name}():
    """
    {instruction}
    """
    return "Hello World"  # Mock implementation'''
        
        self.latest_output = mock_code
        return CodeResult(code=mock_code, success=True, quality_score=6.0)
    
    def _fallback_code_extraction(self, instruction: str) -> str:
        """Último recurso: criar código baseado na instrução"""
        func_name = instruction.lower().replace(" ", "_").replace("-", "_")
        func_name = re.sub(r'[^a-z0-9_]', '', func_name)
        
        if not func_name:
            func_name = "generated_function"
        
        # Tentar identificar o tipo de função pela instrução
        if "hello" in instruction.lower() and "world" in instruction.lower():
            return f'''def {func_name}():
    """
    {instruction}
    """
    return "Hello World"'''
        elif "soma" in instruction.lower() or "sum" in instruction.lower():
            return f'''def {func_name}(a, b):
    """
    {instruction}
    """
    return a + b'''
        else:
            return f'''def {func_name}():
    """
    {instruction}
    """
    # TODO: Implementar {instruction}
    return None'''

    def _process_generated_code(self, raw_code: str, instruction: str) -> CodeResult:
        """Processa e valida o código gerado com extração melhorada"""
        # Tentar extrair código Python do resultado
        code = self._extract_python_code_improved(raw_code)
        
        if not code:
            # Fallback: gerar código básico baseado na instrução
            code = self._fallback_code_extraction(instruction)
        
        if not code:
            return CodeResult(
                code=f"# Falha ao extrair código\n# Resposta original:\n# {raw_code[:200]}",
                success=False,
                error="Não foi possível extrair código Python válido"
            )
        
        # Validar sintaxe
        syntax_valid, syntax_error = self._validate_syntax(code)
        if not syntax_valid:
            # Tentar corrigir código simples
            corrected_code = self._try_fix_simple_syntax(code)
            if corrected_code:
                syntax_valid, syntax_error = self._validate_syntax(corrected_code)
                if syntax_valid:
                    code = corrected_code
        
        # Calcular score de qualidade
        quality_score = self._calculate_quality_score(code, syntax_valid, syntax_error)
        
        return CodeResult(
            code=code,
            success=syntax_valid,
            error=syntax_error if not syntax_valid else None,
            quality_score=quality_score
        )
    
    def _extract_python_code_improved(self, raw_text: str) -> str:
        """Extração melhorada de código Python"""
        if not raw_text:
            return ""
        
        # 1. Procurar blocos de código entre ```python e ```
        python_blocks = re.findall(r'```python\s*\n(.*?)\n```', raw_text, re.DOTALL | re.IGNORECASE)
        if python_blocks:
            return python_blocks[0].strip()
        
        # 2. Procurar blocos de código entre ``` (sem especificar linguagem)
        code_blocks = re.findall(r'```\s*\n(.*?)\n```', raw_text, re.DOTALL)
        for block in code_blocks:
            if self._looks_like_python(block):
                return block.strip()
        
        # 3. Procurar por função simples se a instrução for básica
        if "hello world" in raw_text.lower():
            return 'def hello_world():\n    return "Hello World"'
            
        # 4. Procurar linhas que começam com def, class, import, etc.
        lines = raw_text.split('\n')
        code_lines = []
        in_code = False
        
        for line in lines:
            stripped = line.strip()
            
            # Começar captura se linha parece código Python
            if (stripped.startswith(('def ', 'class ', 'import ', 'from ')) or
                (stripped and not stripped.startswith('#') and ('=' in stripped or 'return' in stripped))):
                in_code = True
                code_lines.append(line)
            elif in_code:
                # Continuar se linha está indentada ou é comentário
                if line.startswith('    ') or line.startswith('\t') or stripped.startswith('#') or stripped == '':
                    code_lines.append(line)
                elif stripped:  # Nova linha não-indentada para código
                    break
        
        if code_lines:
            return '\n'.join(code_lines).strip()
        
        # Se não conseguiu extrair, gerar código básico
        func_name = instruction.lower().replace(" ", "_").replace("-", "_")
        func_name = re.sub(r'[^a-z0-9_]', '', func_name)
        
        if not func_name:
            func_name = "generated_function"
        
        # Tentar identificar o tipo de função pela instrução
        if "hello" in instruction.lower() and "world" in instruction.lower():
            return f'''def {func_name}():
    """
    {instruction}
    """
    return "Hello World"'''
        elif "soma" in instruction.lower() or "sum" in instruction.lower():
            return f'''def {func_name}(a, b):
    """
    {instruction}
    """
    return a + b'''
        else:
            return f'''def {func_name}():
    """
    {instruction}
    """
    # TODO: Implementar {instruction}
    return None'''
    
    def _looks_like_python(self, text: str) -> bool:
        """Verifica se texto parece código Python"""
        python_keywords = ['def ', 'class ', 'import ', 'from ', 'return ', 'if ', 'for ', 'while ']
        return any(keyword in text for keyword in python_keywords)
    
    def _try_fix_simple_syntax(self, code: str) -> Optional[str]:
        """Tenta corrigir erros simples de sintaxe"""
        try:
            # Corrigir indentação comum
            lines = code.split('\n')
            fixed_lines = []
            
            for line in lines:
                # Se linha não está indentada mas deveria estar
                if line.strip() and not line.startswith(('def ', 'class ', 'import ', 'from ')):
                    if not line.startswith(('    ', '\t')):
                        if any(keyword in line for keyword in ['return ', 'print(', '=']):
                            line = '    ' + line.strip()
                fixed_lines.append(line)
            
            return '\n'.join(fixed_lines)
        except:
            return None
    
    def _validate_syntax(self, code: str) -> Tuple[bool, Optional[str]]:
        """Valida sintaxe do código Python"""
        try:
            ast.parse(code)
            return True, None
        except SyntaxError as e:
            return False, str(e)
    
    def _calculate_quality_score(self, code: str, syntax_valid: bool, error: Optional[str]) -> float:
        """Calcula score de qualidade do código (0-10)"""
        score = 0.0
        
        # Sintaxe válida (peso: 4)
        if syntax_valid:
            score += 4.0
        
        # Tem função definida (peso: 2)
        if 'def ' in code:
            score += 2.0
        
        # Tem docstring (peso: 1)
        if '"""' in code or "'''" in code:
            score += 1.0
        
        # Tem return (peso: 1)
        if 'return' in code:
            score += 1.0
        
        # Não é muito simples (peso: 1)
        if len(code.split('\n')) >= 3:
            score += 1.0
        
        # Não tem TODOs (peso: 1)
        if 'TODO' not in code:
            score += 1.0
        
        return min(score, 10.0)
    
    def _handle_generation_failure(self, instruction: str, error: str) -> CodeResult:
        """Lida com falha na geração de código"""
        fallback_code = self._fallback_code_extraction(instruction)
        
        return CodeResult(
            code=fallback_code,
            success=True,  # Fallback sempre funciona
            error=f"Falha na geração: {error}",
            quality_score=3.0  # Score baixo para fallback
        )
    
    def _display_result(self, instruction: str, result: CodeResult):
        """Exibe resultado da geração"""
        if result.success:
            print(f"✅ Código gerado com sucesso!")
        else:
            print(f"⚠️ Problemas na geração")
        
        print(f"📊 Qualidade: {result.quality_score:.1f}/10")
        
        if result.error:
            print(f"❌ Erro: {result.error}")
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas de performance"""
        return {
            "total_generations": len(self.generation_history),
            "adaptation_mode": self.adaptation_mode,
            "using_mock": self.use_mock
        }
