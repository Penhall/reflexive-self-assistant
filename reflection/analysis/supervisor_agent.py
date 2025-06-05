"""
Agente Supervisor: Orquestra a execução dos agentes e a reflexão.
"""

import logging
from core.agents.code_agent_enhanced import CodeAgent
from core.agents.test_agent import TestAgent
from core.agents.doc_agent import DocumentationAgent
from core.agents.reflection_agent import ReflectionAgent
from core.crew.crew_manager import CrewManager
from config.settings import AGENT_CONFIGS
from config.paths import LOG_FILE_PATH
from datetime import datetime
import os

# Configuração de logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SupervisorAgent:
    def __init__(self):
        self.code_agent = CodeAgent(AGENT_CONFIGS["code_agent"])
        self.test_agent = TestAgent(AGENT_CONFIGS["test_agent"])
        self.doc_agent = DocumentationAgent(AGENT_CONFIGS["doc_agent"])
        self.reflection_agent = ReflectionAgent(AGENT_CONFIGS["reflection_agent"])
        self.crew_manager = CrewManager()
        self.log_file = LOG_FILE_PATH

    def execute_cycle(self, task_description: str):
        """
        Executa um ciclo completo de desenvolvimento e reflexão.
        """
        logger.info(f"Iniciando novo ciclo para a tarefa: {task_description}")
        self._log_cycle_start(task_description)

        try:
            # 1. Execução da Crew principal (Code, Test, Doc)
            logger.info("Iniciando execução da Crew principal...")
            main_crew_result = self.crew_manager.run_main_crew(
                task_description,
                self.code_agent,
                self.test_agent,
                self.doc_agent
            )
            logger.info(f"Resultado da Crew principal: {main_crew_result}")

            # 2. Reflexão
            logger.info("Iniciando processo de reflexão...")
            reflection_result = self.reflection_agent.reflect(
                task_description,
                main_crew_result,
                [self.code_agent, self.test_agent, self.doc_agent]
            )
            logger.info(f"Resultado da Reflexão: {reflection_result}")

            # 3. Adaptação (se necessário)
            if self.reflection_agent.needs_adaptation(reflection_result):
                logger.info("Adaptação necessária. Iniciando Crew de Adaptação...")
                adaptation_result = self.crew_manager.run_adaptation_crew(
                    reflection_result,
                    self.code_agent,
                    self.test_agent,
                    self.doc_agent,
                    self.reflection_agent
                )
                logger.info(f"Resultado da Adaptação: {adaptation_result}")
                final_result = adaptation_result
            else:
                logger.info("Nenhuma adaptação necessária neste ciclo.")
                final_result = main_crew_result

            self._log_cycle_end(final_result)
            logger.info(f"Ciclo concluído. Resultado final: {final_result}")
            return final_result

        except Exception as e:
            logger.error(f"Erro durante a execução do ciclo: {e}", exc_info=True)
            self._log_cycle_end(f"Erro: {e}")
            raise

    def _log_cycle_start(self, task_description: str):
        """Registra o início de um ciclo no arquivo de log."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"--- Ciclo Iniciado: {timestamp} ---\n"
        log_entry += f"Tarefa: {task_description}\n"
        self._write_to_log(log_entry)

    def _log_cycle_end(self, result: str):
        """Registra o fim de um ciclo no arquivo de log."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"Resultado: {result}\n"
        log_entry += f"--- Ciclo Concluído: {timestamp} ---\n\n"
        self._write_to_log(log_entry)

    def _write_to_log(self, content: str):
        """Escreve conteúdo no arquivo de log."""
        try:
            with open(self.log_file, "a", encoding="utf-8") as f:
                f.write(content)
        except IOError as e:
            logger.error(f"Não foi possível escrever no arquivo de log {self.log_file}: {e}")

if __name__ == "__main__":
    # Exemplo de uso
    supervisor = SupervisorAgent()
    # Certifique-se de que os caminhos de configuração estão corretos para o ambiente de teste
    # Ex: AGENT_CONFIGS pode precisar ser mockado ou configurado para um ambiente de teste
    # Para um teste real, você precisaria de um LLM configurado e acessível.
    
    # Exemplo de tarefa
    test_task = "Desenvolver uma função Python para calcular o fatorial de um número."
    # supervisor.execute_cycle(test_task)
    print(f"SupervisorAgent inicializado. Para executar, chame supervisor.execute_cycle('{test_task}')")
