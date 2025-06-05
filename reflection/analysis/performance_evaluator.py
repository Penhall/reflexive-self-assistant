"""
Módulo para avaliação de desempenho e otimização de agentes.
"""

import logging
import time
from collections import defaultdict
import json
import os
from config.paths import PERFORMANCE_LOG_PATH

logger = logging.getLogger(__name__)

class PerformanceEvaluator:
    def __init__(self):
        self.metrics = defaultdict(lambda: {'total_time': 0, 'calls': 0, 'errors': 0})
        self.start_times = {}
        self.log_file = PERFORMANCE_LOG_PATH

    def start_timer(self, agent_name: str, method_name: str):
        """Inicia o timer para uma operação específica."""
        key = f"{agent_name}.{method_name}"
        self.start_times[key] = time.time()
        logger.debug(f"Timer iniciado para {key}")

    def stop_timer(self, agent_name: str, method_name: str):
        """Para o timer e registra o tempo decorrido."""
        key = f"{agent_name}.{method_name}"
        if key in self.start_times:
            elapsed_time = time.time() - self.start_times[key]
            self.metrics[key]['total_time'] += elapsed_time
            self.metrics[key]['calls'] += 1
            logger.debug(f"Timer parado para {key}. Tempo decorrido: {elapsed_time:.4f}s")
            del self.start_times[key]
        else:
            logger.warning(f"Timer para {key} não foi iniciado ou já foi parado.")

    def record_error(self, agent_name: str, method_name: str):
        """Registra um erro para uma operação específica."""
        key = f"{agent_name}.{method_name}"
        self.metrics[key]['errors'] += 1
        logger.error(f"Erro registrado para {key}")

    def get_metrics(self):
        """Retorna as métricas de desempenho atuais."""
        report = {}
        for key, data in self.metrics.items():
            avg_time = data['total_time'] / data['calls'] if data['calls'] > 0 else 0
            report[key] = {
                'total_time': data['total_time'],
                'calls': data['calls'],
                'avg_time_per_call': avg_time,
                'errors': data['errors']
            }
        return report

    def generate_report(self):
        """Gera um relatório de desempenho formatado."""
        report = self.get_metrics()
        if not report:
            return "Nenhum dado de desempenho disponível."

        output = ["--- Relatório de Desempenho ---"]
        for key, data in report.items():
            output.append(f"\nOperação: {key}")
            output.append(f"  Chamadas: {data['calls']}")
            output.append(f"  Tempo Total: {data['total_time']:.4f}s")
            output.append(f"  Tempo Médio por Chamada: {data['avg_time_per_call']:.4f}s")
            output.append(f"  Erros: {data['errors']}")
        output.append("\n-----------------------------")
        return "\n".join(output)

    def save_report(self):
        """Salva o relatório de desempenho em um arquivo JSON."""
        report_data = self.get_metrics()
        try:
            with open(self.log_file, 'w', encoding='utf-8') as f:
                json.dump(report_data, f, indent=4)
            logger.info(f"Relatório de desempenho salvo em {self.log_file}")
        except IOError as e:
            logger.error(f"Não foi possível salvar o relatório de desempenho em {self.log_file}: {e}")

    def load_report(self):
        """Carrega métricas de desempenho de um arquivo JSON."""
        if os.path.exists(self.log_file):
            try:
                with open(self.log_file, 'r', encoding='utf-8') as f:
                    loaded_metrics = json.load(f)
                    for key, data in loaded_metrics.items():
                        self.metrics[key].update(data)
                logger.info(f"Métricas de desempenho carregadas de {self.log_file}")
            except json.JSONDecodeError as e:
                logger.error(f"Erro ao decodificar JSON do arquivo {self.log_file}: {e}")
            except IOError as e:
                logger.error(f"Não foi possível carregar o relatório de desempenho de {self.log_file}: {e}")
        else:
            logger.info(f"Arquivo de log de desempenho não encontrado em {self.log_file}. Iniciando com métricas vazias.")

# Exemplo de uso:
if __name__ == "__main__":
    evaluator = PerformanceEvaluator()

    # Simulação de operações
    evaluator.start_timer("CodeAgent", "generate_code")
    time.sleep(0.5)
    evaluator.stop_timer("CodeAgent", "generate_code")

    evaluator.start_timer("TestAgent", "run_tests")
    time.sleep(0.3)
    evaluator.stop_timer("TestAgent", "run_tests")

    evaluator.start_timer("CodeAgent", "generate_code")
    time.sleep(0.7)
    evaluator.record_error("CodeAgent", "generate_code")
    evaluator.stop_timer("CodeAgent", "generate_code") # Mesmo com erro, o tempo é registrado

    print(evaluator.generate_report())
    evaluator.save_report()

    # Para demonstrar o carregamento
    new_evaluator = PerformanceEvaluator()
    new_evaluator.load_report()
    print("\nMétricas carregadas:")
    print(new_evaluator.generate_report())
