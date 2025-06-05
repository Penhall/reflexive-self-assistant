"""
Módulo para gerenciar o fechamento de ciclos de reflexão e a consolidação de aprendizados.
"""

import logging
import yaml
from datetime import datetime
import os
from config.paths import CLOSURE_LOG_PATH, SYMBOLIC_IMPACT_LOG_PATH

logger = logging.getLogger(__name__)

class ClosureManager:
    def __init__(self):
        self.closure_log_file = CLOSURE_LOG_PATH
        self.symbolic_impact_log_file = SYMBOLIC_IMPACT_LOG_PATH
        self._ensure_files_exist()

    def _ensure_files_exist(self):
        """Garante que os arquivos de log existam."""
        if not os.path.exists(self.closure_log_file):
            with open(self.closure_log_file, 'w', encoding='utf-8') as f:
                yaml.safe_dump({"closures": []}, f)
        if not os.path.exists(self.symbolic_impact_log_file):
            with open(self.symbolic_impact_log_file, 'w', encoding='utf-8') as f:
                yaml.safe_dump({"impacts": []}, f)

    def record_closure(self, cycle_id: str, summary: str, key_learnings: list, recommendations: list):
        """
        Registra o fechamento de um ciclo de reflexão.
        """
        closure_entry = {
            "timestamp": datetime.now().isoformat(),
            "cycle_id": cycle_id,
            "summary": summary,
            "key_learnings": key_learnings,
            "recommendations": recommendations
        }
        try:
            with open(self.closure_log_file, 'r+', encoding='utf-8') as f:
                data = yaml.safe_load(f)
                if data is None:
                    data = {"closures": []}
                data["closures"].append(closure_entry)
                f.seek(0)
                yaml.safe_dump(data, f, indent=2, sort_keys=False, allow_unicode=True)
            logger.info(f"Fechamento do ciclo {cycle_id} registrado com sucesso.")
        except Exception as e:
            logger.error(f"Erro ao registrar fechamento do ciclo {cycle_id}: {e}")

    def record_symbolic_impact(self, agent_name: str, symbolic_change: str, impact_description: str, timestamp: str = None):
        """
        Registra o impacto de uma mudança simbólica na identidade do agente.
        """
        if timestamp is None:
            timestamp = datetime.now().isoformat()

        impact_entry = {
            "timestamp": timestamp,
            "agent_name": agent_name,
            "symbolic_change": symbolic_change,
            "impact_description": impact_description
        }
        try:
            with open(self.symbolic_impact_log_file, 'r+', encoding='utf-8') as f:
                data = yaml.safe_load(f)
                if data is None:
                    data = {"impacts": []}
                data["impacts"].append(impact_entry)
                f.seek(0)
                yaml.safe_dump(data, f, indent=2, sort_keys=False, allow_unicode=True)
            logger.info(f"Impacto simbólico para {agent_name} registrado com sucesso.")
        except Exception as e:
            logger.error(f"Erro ao registrar impacto simbólico para {agent_name}: {e}")

    def get_all_closures(self):
        """
        Retorna todos os registros de fechamento.
        """
        try:
            with open(self.closure_log_file, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
                return data.get("closures", []) if data else []
        except FileNotFoundError:
            return []
        except Exception as e:
            logger.error(f"Erro ao carregar registros de fechamento: {e}")
            return []

    def get_all_symbolic_impacts(self):
        """
        Retorna todos os registros de impacto simbólico.
        """
        try:
            with open(self.symbolic_impact_log_file, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
                return data.get("impacts", []) if data else []
        except FileNotFoundError:
            return []
        except Exception as e:
            logger.error(f"Erro ao carregar registros de impacto simbólico: {e}")
            return []

# Exemplo de uso
if __name__ == "__main__":
    # Define caminhos temporários para teste
    temp_closure_log = "temp_closure_log.yaml"
    temp_symbolic_impact_log = "temp_symbolic_impact_log.yaml"

    # Sobrescreve os caminhos no config.paths para o teste
    from unittest.mock import patch
    with patch('config.paths.CLOSURE_LOG_PATH', temp_closure_log), \
         patch('config.paths.SYMBOLIC_IMPACT_LOG_PATH', temp_symbolic_impact_log):
        
        manager = ClosureManager()

        # Teste de registro de fechamento
        manager.record_closure(
            cycle_id="cycle-001",
            summary="Implementação da função de fatorial concluída.",
            key_learnings=["Melhoria na detecção de padrões de código.", "Aumento da eficiência do TestAgent."],
            recommendations=["Explorar otimização de prompts para CodeAgent."]
        )

        # Teste de registro de impacto simbólico
        manager.record_symbolic_impact(
            agent_name="CodeAgent",
            symbolic_change="Padrão predominante: 'Funcional'",
            impact_description="Agente focado em implementação direta de funcionalidades."
        )

        # Teste de recuperação de registros
        print("\nRegistros de Fechamento:")
        closures = manager.get_all_closures()
        print(yaml.dump(closures, indent=2, sort_keys=False, allow_unicode=True))

        print("\nRegistros de Impacto Simbólico:")
        impacts = manager.get_all_symbolic_impacts()
        print(yaml.dump(impacts, indent=2, sort_keys=False, allow_unicode=True))

    # Limpeza dos arquivos temporários
    if os.path.exists(temp_closure_log):
        os.remove(temp_closure_log)
    if os.path.exists(temp_symbolic_impact_log):
        os.remove(temp_symbolic_impact_log)
