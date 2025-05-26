from core.agents.code_agent import CodeAgent
from core.agents.test_agent import TestAgent

# Executar o agente de código
code = CodeAgent()
code.execute_task("Crie uma função que multiplica dois números")

# Gerar teste com base no código criado
test = TestAgent()
test.generate_tests(code.latest_output, function_name="multiplicar")