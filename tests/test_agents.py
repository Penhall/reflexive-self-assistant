"""
Testes unitários para os agentes.
"""

def test_code_agent():
    from agents.code_agent import CodeAgent
    agent = CodeAgent()
    agent.execute_task("Criar endpoint")
    assert "Criar endpoint" in agent.latest_output