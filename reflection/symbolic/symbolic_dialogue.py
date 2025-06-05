"""
Gerencia o diálogo simbólico e a tomada de decisão.
"""

import yaml
import os
from datetime import datetime
from config.paths import DIALOGUE_DECISION_PATH, SYMBOLIC_DIALOGUE_PATH

class SymbolicDialogueManager:
    def __init__(self):
        self.dialogue_file = SYMBOLIC_DIALOGUE_PATH
        self.decision_file = DIALOGUE_DECISION_PATH
        self._ensure_files_exist()

    def _ensure_files_exist(self):
        """Garante que os arquivos de diálogo e decisão existam."""
        if not os.path.exists(self.dialogue_file):
            with open(self.dialogue_file, 'w', encoding='utf-8') as f:
                yaml.safe_dump({"dialogue_history": []}, f)
        if not os.path.exists(self.decision_file):
            with open(self.decision_file, 'w', encoding='utf-8') as f:
                yaml.safe_dump({"decisions": []}, f)

    def load_dialogue_history(self):
        """Carrega o histórico de diálogo simbólico."""
        with open(self.dialogue_file, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)

    def save_dialogue_entry(self, speaker: str, message: str, context: dict = None):
        """Salva uma nova entrada no histórico de diálogo."""
        history = self.load_dialogue_history()
        entry = {
            "timestamp": datetime.now().isoformat(),
            "speaker": speaker,
            "message": message,
            "context": context if context else {}
        }
        history["dialogue_history"].append(entry)
        with open(self.dialogue_file, 'w', encoding='utf-8') as f:
            yaml.safe_dump(history, f, indent=2, sort_keys=False, allow_unicode=True)

    def load_decisions(self):
        """Carrega as decisões tomadas."""
        with open(self.decision_file, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)

    def save_decision(self, decision_type: str, description: str, rationale: str, outcome: str, related_dialogue_index: int = None):
        """Salva uma nova decisão."""
        decisions_data = self.load_decisions()
        decision_entry = {
            "timestamp": datetime.now().isoformat(),
            "type": decision_type,
            "description": description,
            "rationale": rationale,
            "outcome": outcome,
            "related_dialogue_index": related_dialogue_index
        }
        decisions_data["decisions"].append(decision_entry)
        with open(self.decision_file, 'w', encoding='utf-8') as f:
            yaml.safe_dump(decisions_data, f, indent=2, sort_keys=False, allow_unicode=True)

    def get_latest_dialogue_entry(self):
        """Retorna a última entrada do histórico de diálogo."""
        history = self.load_dialogue_history()
        if history and history["dialogue_history"]:
            return history["dialogue_history"][-1]
        return None

    def get_latest_decision(self):
        """Retorna a última decisão tomada."""
        decisions_data = self.load_decisions()
        if decisions_data and decisions_data["decisions"]:
            return decisions_data["decisions"][-1]
        return None

# Exemplo de uso
if __name__ == "__main__":
    # Define caminhos temporários para teste
    temp_dialogue_file = "temp_symbolic_dialogue.yaml"
    temp_decision_file = "temp_dialogue_decision.yaml"
    
    # Sobrescreve os caminhos no config.paths para o teste
    from unittest.mock import patch
    with patch('config.paths.SYMBOLIC_DIALOGUE_PATH', temp_dialogue_file), \
         patch('config.paths.DIALOGUE_DECISION_PATH', temp_decision_file):
        
        manager = SymbolicDialogueManager()

        # Teste de salvar diálogo
        manager.save_dialogue_entry("System", "Iniciando análise de requisitos.", {"task_id": "T001"})
        manager.save_dialogue_entry("Agent", "Requisitos claros. Propondo solução A.", {"solution": "A"})
        
        # Teste de carregar diálogo
        history = manager.load_dialogue_history()
        print("Histórico de Diálogo:")
        print(yaml.dump(history, indent=2, sort_keys=False, allow_unicode=True))
        
        # Teste de obter última entrada
        latest_entry = manager.get_latest_dialogue_entry()
        print("\nÚltima Entrada de Diálogo:")
        print(yaml.dump(latest_entry, indent=2, sort_keys=False, allow_unicode=True))

        # Teste de salvar decisão
        manager.save_decision("Strategy", "Adotar Solução A", "É a mais eficiente.", "Aprovada", 1)
        
        # Teste de carregar decisões
        decisions = manager.load_decisions()
        print("\nDecisões:")
        print(yaml.dump(decisions, indent=2, sort_keys=False, allow_unicode=True))

        # Teste de obter última decisão
        latest_decision = manager.get_latest_decision()
        print("\nÚltima Decisão:")
        print(yaml.dump(latest_decision, indent=2, sort_keys=False, allow_unicode=True))

    # Limpeza dos arquivos temporários
    if os.path.exists(temp_dialogue_file):
        os.remove(temp_dialogue_file)
    if os.path.exists(temp_decision_file):
        os.remove(temp_decision_file)
