"""
Módulo de memória simbólica para armazenamento e recuperação de estados identitários dos agentes.
"""

import yaml
from pathlib import Path
from typing import Dict, Any

class SymbolicMemory:
    def __init__(self, memory_file: str = None):
        """
        Inicializa a memória simbólica.
        
        Args:
            memory_file (str, optional): Caminho para arquivo de persistência. Defaults to None.
        """
        self.memory: Dict[str, Any] = {}
        self.memory_file = memory_file
        
    def update_memory(self, identity_state: Dict[str, Any]) -> None:
        """
        Atualiza o estado da memória simbólica com novos dados.
        
        Args:
            identity_state (Dict[str, Any]): Estado identitário dos agentes
        """
        self.memory.update(identity_state)
        
        if self.memory_file:
            self._persist_memory()
            
    def _persist_memory(self) -> None:
        """Persiste o estado da memória em arquivo YAML."""
        try:
            with Path(self.memory_file).open('w', encoding='utf-8') as f:
                yaml.safe_dump(self.memory, f)
        except Exception as e:
            print(f"Erro ao persistir memória simbólica: {e}")
            
    def load_memory(self) -> None:
        """Carrega o estado da memória a partir do arquivo."""
        if self.memory_file and Path(self.memory_file).exists():
            try:
                with Path(self.memory_file).open('r', encoding='utf-8') as f:
                    self.memory = yaml.safe_load(f) or {}
            except Exception as e:
                print(f"Erro ao carregar memória simbólica: {e}")