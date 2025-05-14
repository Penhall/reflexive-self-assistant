"""
Agente reflexivo que analisa padrões e atualiza a identidade simbólica do sistema.
"""

class ReflectionAgent:
    def reflect_on_tasks(self, agents):
        print("Refletindo sobre o desempenho dos agentes...")
        for agent in agents:
            print(f"Analisando output: {agent.latest_output}")