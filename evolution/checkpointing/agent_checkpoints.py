# evolution/checkpointing/agent_checkpoints.py
"""
Sistema de Checkpoints para Agentes - Permite versionamento e evolução
Integra com GraphRAG para armazenar experiências e especializações
"""

import json
import yaml
import pickle
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
import shutil

from memory.hybrid_store import HybridMemoryStore
from config.paths import DATA_DIR, CHECKPOINTS_DIR


@dataclass
class AgentCheckpoint:
    """Representa um checkpoint de agente"""
    id: str
    agent_name: str
    version: str
    creation_date: datetime
    specialization: str
    performance_metrics: Dict[str, float]
    identity_state: Dict[str, Any]
    experience_count: int
    quality_average: float
    llm_model: str
    configuration: Dict[str, Any]
    metadata: Dict[str, Any]
    file_path: Optional[str] = None


class AgentCheckpointManager:
    """
    Gerencia checkpoints de agentes - criação, armazenamento, carregamento
    """
    
    def __init__(self, storage_path: Path = None):
        self.storage_path = storage_path or CHECKPOINTS_DIR
        self.storage_path.mkdir(parents=True, exist_ok=True)
        
        # Diretórios organizados
        self.agents_dir = self.storage_path / "agents"
        self.metadata_dir = self.storage_path / "metadata"
        self.experiences_dir = self.storage_path / "experiences"
        
        for dir_path in [self.agents_dir, self.metadata_dir, self.experiences_dir]:
            dir_path.mkdir(exist_ok=True)
        
        # Índice de checkpoints
        self.index_file = self.storage_path / "checkpoint_index.json"
        self.checkpoint_index = self._load_index()
    
    def create_checkpoint(self, agent, version_tag: str = None, 
                         specialization: str = "general") -> str:
        """
        Cria checkpoint completo do agente
        """
        print(f"💾 Criando checkpoint do {agent.__class__.__name__}...")
        
        # Gerar ID único
        timestamp = datetime.now()
        checkpoint_id = self._generate_checkpoint_id(
            agent.__class__.__name__, version_tag, timestamp
        )
        
        # Coletar dados do agente
        identity_state = self._extract_identity_state(agent)
        performance_metrics = self._extract_performance_metrics(agent)
        configuration = self._extract_configuration(agent)
        
        # Exportar experiências (se GraphRAG habilitado)
        experience_snapshot = self._export_agent_experiences(agent, checkpoint_id)
        
        # Criar checkpoint
        checkpoint = AgentCheckpoint(
            id=checkpoint_id,
            agent_name=agent.__class__.__name__,
            version=version_tag or f"auto_{timestamp.strftime('%Y%m%d_%H%M%S')}",
            creation_date=timestamp,
            specialization=specialization,
            performance_metrics=performance_metrics,
            identity_state=identity_state,
            experience_count=len(getattr(agent, 'generation_history', [])),
            quality_average=performance_metrics.get('average_quality', 0.0),
            llm_model=getattr(agent.llm, 'current_model', 'unknown'),
            configuration=configuration,
            metadata={
                "creation_method": "manual",
                "source_agent": agent.__class__.__name__,
                "experience_snapshot": experience_snapshot,
                "compatibility_version": "2.0"
            }
        )
        
        # Salvar checkpoint
        checkpoint_path = self._save_checkpoint_to_disk(checkpoint, agent)
        checkpoint.file_path = str(checkpoint_path)
        
        # Atualizar índice
        self._update_index(checkpoint)
        
        print(f"✅ Checkpoint criado: {checkpoint_id}")
        print(f"   Versão: {checkpoint.version}")
        print(f"   Especialização: {specialization}")
        print(f"   Experiências: {checkpoint.experience_count}")
        print(f"   Qualidade média: {checkpoint.quality_average:.2f}")
        
        return checkpoint_id
    
    def load_agent_from_checkpoint(self, checkpoint_id: str, 
                                  target_llm_config: Dict = None) -> Any:
        """
        Reconstrói agente a partir de checkpoint
        """
        print(f"📂 Carregando agente do checkpoint: {checkpoint_id}")
        
        # Carregar metadata do checkpoint
        checkpoint_info = self.get_checkpoint_info(checkpoint_id)
        if not checkpoint_info:
            raise ValueError(f"Checkpoint {checkpoint_id} não encontrado")
        
        # Carregar dados completos
        checkpoint_data = self._load_checkpoint_from_disk(checkpoint_id)
        
        # Reconstruir agente
        agent = self._reconstruct_agent(checkpoint_data, target_llm_config)
        
        # Restaurar experiências
        if checkpoint_data.metadata.get("experience_snapshot"):
            self._restore_agent_experiences(agent, checkpoint_data)
        
        print(f"✅ Agente {checkpoint_data.agent_name} restaurado")
        print(f"   Versão: {checkpoint_data.version}")
        print(f"   Experiências restauradas: {checkpoint_data.experience_count}")
        
        return agent
    
    def _generate_checkpoint_id(self, agent_name: str, version: str, 
                               timestamp: datetime) -> str:
        """Gera ID único para checkpoint"""
        base_string = f"{agent_name}_{version}_{timestamp.isoformat()}"
        hash_object = hashlib.md5(base_string.encode())
        return f"{agent_name.lower()}_{hash_object.hexdigest()[:8]}"
    
    def _extract_identity_state(self, agent) -> Dict[str, Any]:
        """Extrai estado de identidade do agente"""
        identity = {}
        
        # Atributos básicos
        basic_attrs = [
            'adaptation_mode', 'adapted', 'latest_output', 
            'enable_learning', 'current_model'
        ]
        
        for attr in basic_attrs:
            if hasattr(agent, attr):
                value = getattr(agent, attr)
                if isinstance(value, (str, int, float, bool, list, dict)):
                    identity[attr] = value
        
        # Histórico de geração
        if hasattr(agent, 'generation_history'):
            identity['generation_history'] = agent.generation_history[-50:]  # Últimos 50
        
        # Configuração simbólica (se disponível)
        try:
            from config.paths import IDENTITY_STATE
            with open(IDENTITY_STATE, 'r') as f:
                symbolic_data = yaml.safe_load(f)
                if agent.__class__.__name__ in symbolic_data:
                    identity['symbolic_profile'] = symbolic_data[agent.__class__.__name__]
        except:
            pass
        
        return identity
    
    def _extract_performance_metrics(self, agent) -> Dict[str, float]:
        """Extrai métricas de performance do agente"""
        metrics = {}
        
        if hasattr(agent, 'get_performance_stats'):
            stats = agent.get_performance_stats()
            
            # Converter para tipos serializáveis
            for key, value in stats.items():
                if isinstance(value, (int, float)):
                    metrics[key] = float(value)
                elif isinstance(value, list) and all(isinstance(x, (int, float)) for x in value):
                    metrics[f"{key}_list"] = [float(x) for x in value]
        
        # Métricas básicas se método não disponível
        if not metrics and hasattr(agent, 'generation_history'):
            history = agent.generation_history
            if history:
                qualities = [h.get('quality_score', 0) for h in history]
                successes = [h.get('success', False) for h in history]
                
                metrics = {
                    'total_generations': len(history),
                    'success_rate': sum(successes) / len(successes),
                    'average_quality': sum(qualities) / len(qualities),
                    'best_quality': max(qualities) if qualities else 0.0
                }
        
        return metrics
    
    def _extract_configuration(self, agent) -> Dict[str, Any]:
        """Extrai configuração do agente"""
        config = {}
        
        # Configuração do LLM
        if hasattr(agent, 'llm'):
            llm_config = {}
            llm = agent.llm
            
            if hasattr(llm, 'current_model'):
                llm_config['model'] = llm.current_model
            if hasattr(llm, 'config'):
                llm_config['config'] = llm.config
            
            config['llm'] = llm_config
        
        # Configuração de memória
        if hasattr(agent, 'memory'):
            config['memory_enabled'] = agent.memory is not None
            config['graphrag_enabled'] = getattr(agent, 'enable_learning', False)
        
        # Outras configurações
        config_attrs = ['use_mock', 'enable_graphrag', 'adaptation_mode']
        for attr in config_attrs:
            if hasattr(agent, attr):
                config[attr] = getattr(agent, attr)
        
        return config
    
    def _export_agent_experiences(self, agent, checkpoint_id: str) -> Optional[str]:
        """Exporta experiências do agente para arquivo separado"""
        if not hasattr(agent, 'memory') or not agent.memory:
            return None
        
        try:
            experiences_file = self.experiences_dir / f"{checkpoint_id}_experiences.json"
            
            # Coletar experiências do GraphRAG
            experiences = []
            
            if agent.memory.enable_graphrag:
                # Extrair do Neo4j
                with agent.memory.neo4j.session() as session:
                    result = session.run("""
                        MATCH (e:Experience)-[:PERFORMED_BY]->(a:Agent {name: $agent_name})
                        MATCH (e)-[:GENERATED_CODE]->(c:Code)
                        RETURN e, c
                        ORDER BY e.timestamp DESC
                        LIMIT 1000
                    """, agent_name=agent.__class__.__name__)
                    
                    for record in result:
                        exp = record['e']
                        code = record['c']
                        experiences.append({
                            'id': exp['id'],
                            'task': exp['task_description'],
                            'code': code['content'],
                            'quality': exp['quality_score'],
                            'success': exp['execution_success'],
                            'timestamp': exp['timestamp'],
                            'agent': exp['agent_name']
                        })
            
            # Adicionar experiências do histórico local
            if hasattr(agent, 'generation_history'):
                for i, hist in enumerate(agent.generation_history):
                    experiences.append({
                        'id': f"local_{i}",
                        'task': hist.get('instruction', 'Unknown'),
                        'code': 'N/A',  # Código não armazenado no histórico
                        'quality': hist.get('quality_score', 0),
                        'success': hist.get('success', False),
                        'timestamp': hist.get('timestamp', ''),
                        'source': 'local_history'
                    })
            
            # Salvar experiências
            with open(experiences_file, 'w', encoding='utf-8') as f:
                json.dump(experiences, f, indent=2, ensure_ascii=False, default=str)
            
            print(f"   💾 {len(experiences)} experiências exportadas")
            return str(experiences_file)
            
        except Exception as e:
            print(f"   ⚠️ Falha ao exportar experiências: {e}")
            return None
    
    def _save_checkpoint_to_disk(self, checkpoint: AgentCheckpoint, agent) -> Path:
        """Salva checkpoint no disco"""
        checkpoint_file = self.agents_dir / f"{checkpoint.id}.pkl"
        metadata_file = self.metadata_dir / f"{checkpoint.id}.json"
        
        # Salvar dados do agente (pickle para objetos complexos)
        checkpoint_data = {
            'checkpoint_info': asdict(checkpoint),
            'agent_state': self._serialize_agent_state(agent),
            'creation_timestamp': datetime.now().isoformat()
        }
        
        with open(checkpoint_file, 'wb') as f:
            pickle.dump(checkpoint_data, f)
        
        # Salvar metadata (JSON para leitura fácil)
        metadata = asdict(checkpoint)
        metadata['creation_date'] = checkpoint.creation_date.isoformat()
        
        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False, default=str)
        
        return checkpoint_file
    
    def _serialize_agent_state(self, agent) -> Dict[str, Any]:
        """Serializa estado do agente de forma segura"""
        state = {}
        
        # Atributos serializáveis
        serializable_attrs = [
            'latest_output', 'adapted', 'generation_history',
            'adaptation_mode', 'enable_learning'
        ]
        
        for attr in serializable_attrs:
            if hasattr(agent, attr):
                value = getattr(agent, attr)
                try:
                    # Testar se é serializável
                    json.dumps(value, default=str)
                    state[attr] = value
                except:
                    # Se não for serializável, converter para string
                    state[attr] = str(value)
        
        return state
    
    def _load_checkpoint_from_disk(self, checkpoint_id: str) -> AgentCheckpoint:
        """Carrega checkpoint do disco"""
        checkpoint_file = self.agents_dir / f"{checkpoint_id}.pkl"
        
        if not checkpoint_file.exists():
            raise FileNotFoundError(f"Checkpoint file not found: {checkpoint_file}")
        
        with open(checkpoint_file, 'rb') as f:
            checkpoint_data = pickle.load(f)
        
        # Reconstruir objeto AgentCheckpoint
        checkpoint_info = checkpoint_data['checkpoint_info']
        checkpoint_info['creation_date'] = datetime.fromisoformat(
            checkpoint_info['creation_date']
        )
        
        checkpoint = AgentCheckpoint(**checkpoint_info)
        checkpoint.metadata['agent_state'] = checkpoint_data.get('agent_state', {})
        
        return checkpoint
    
    def _reconstruct_agent(self, checkpoint: AgentCheckpoint, 
                          target_llm_config: Dict = None):
        """Reconstrói agente a partir do checkpoint"""
        # Importar classe do agente dinamicamente
        agent_class_name = checkpoint.agent_name
        
        if agent_class_name == "CodeAgent" or agent_class_name == "CodeAgentEnhanced":
            from core.agents.code_agent_enhanced import CodeAgentEnhanced
            agent_class = CodeAgentEnhanced
        else:
            raise ValueError(f"Classe de agente desconhecida: {agent_class_name}")
        
        # Reconstruir com configuração
        config = checkpoint.configuration
        agent = agent_class(
            use_mock=config.get('use_mock', False),
            enable_graphrag=config.get('graphrag_enabled', True)
        )
        
        # Restaurar estado
        agent_state = checkpoint.metadata.get('agent_state', {})
        
        for attr, value in agent_state.items():
            if hasattr(agent, attr):
                try:
                    setattr(agent, attr, value)
                except:
                    pass  # Ignorar atributos que não podem ser definidos
        
        # Restaurar configuração simbólica
        if 'symbolic_profile' in checkpoint.identity_state:
            self._restore_symbolic_profile(agent, checkpoint.identity_state['symbolic_profile'])
        
        return agent
    
    def _restore_agent_experiences(self, agent, checkpoint: AgentCheckpoint):
        """Restaura experiências do agente"""
        experiences_file = checkpoint.metadata.get("experience_snapshot")
        if not experiences_file or not Path(experiences_file).exists():
            return
        
        try:
            with open(experiences_file, 'r', encoding='utf-8') as f:
                experiences = json.load(f)
            
            # Restaurar no GraphRAG se disponível
            if hasattr(agent, 'memory') and agent.memory and agent.memory.enable_graphrag:
                from memory.hybrid_store import CodingExperience
                
                for exp_data in experiences[:100]:  # Limitar a 100 experiências
                    if exp_data.get('source') != 'local_history':
                        try:
                            experience = CodingExperience(
                                id=exp_data['id'],
                                task_description=exp_data['task'],
                                code_generated=exp_data['code'],
                                quality_score=exp_data['quality'],
                                execution_success=exp_data['success'],
                                agent_name=exp_data['agent'],
                                llm_model='restored',
                                timestamp=datetime.fromisoformat(exp_data['timestamp']),
                                context={'restored': True},
                                yaml_cycle=0
                            )
                            
                            agent.memory.store_experience(experience)
                            
                        except Exception as e:
                            print(f"   ⚠️ Erro ao restaurar experiência {exp_data['id']}: {e}")
            
            print(f"   ✅ {len(experiences)} experiências processadas para restauração")
            
        except Exception as e:
            print(f"   ⚠️ Erro ao restaurar experiências: {e}")
    
    def _restore_symbolic_profile(self, agent, symbolic_profile: Dict):
        """Restaura perfil simbólico do agente"""
        try:
            from config.paths import IDENTITY_STATE
            
            # Carregar estado atual
            with open(IDENTITY_STATE, 'r') as f:
                identity_data = yaml.safe_load(f) or {}
            
            # Atualizar com perfil restaurado
            identity_data[agent.__class__.__name__] = symbolic_profile
            
            # Salvar
            with open(IDENTITY_STATE, 'w') as f:
                yaml.safe_dump(identity_data, f, allow_unicode=True, sort_keys=False)
            
            print(f"   🔗 Perfil simbólico restaurado")
            
        except Exception as e:
            print(f"   ⚠️ Erro ao restaurar perfil simbólico: {e}")
    
    def _update_index(self, checkpoint: AgentCheckpoint):
        """Atualiza índice de checkpoints"""
        self.checkpoint_index[checkpoint.id] = {
            'id': checkpoint.id,
            'agent_name': checkpoint.agent_name,
            'version': checkpoint.version,
            'creation_date': checkpoint.creation_date.isoformat(),
            'specialization': checkpoint.specialization,
            'quality_average': checkpoint.quality_average,
            'experience_count': checkpoint.experience_count,
            'file_path': checkpoint.file_path
        }
        
        self._save_index()
    
    def _load_index(self) -> Dict[str, Any]:
        """Carrega índice de checkpoints"""
        if self.index_file.exists():
            try:
                with open(self.index_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return {}
        return {}
    
    def _save_index(self):
        """Salva índice de checkpoints"""
        with open(self.index_file, 'w', encoding='utf-8') as f:
            json.dump(self.checkpoint_index, f, indent=2, ensure_ascii=False, default=str)
    
    def list_checkpoints(self, agent_name: str = None, 
                        specialization: str = None) -> List[Dict[str, Any]]:
        """Lista checkpoints disponíveis"""
        checkpoints = list(self.checkpoint_index.values())
        
        # Filtrar por agente
        if agent_name:
            checkpoints = [cp for cp in checkpoints if cp['agent_name'] == agent_name]
        
        # Filtrar por especialização
        if specialization:
            checkpoints = [cp for cp in checkpoints if cp['specialization'] == specialization]
        
        # Ordenar por data (mais recente primeiro)
        checkpoints.sort(key=lambda x: x['creation_date'], reverse=True)
        
        return checkpoints
    
    def get_checkpoint_info(self, checkpoint_id: str) -> Optional[Dict[str, Any]]:
        """Obtém informações de um checkpoint específico"""
        return self.checkpoint_index.get(checkpoint_id)
    
    def delete_checkpoint(self, checkpoint_id: str) -> bool:
        """Remove checkpoint do disco"""
        try:
            # Remover arquivos
            checkpoint_file = self.agents_dir / f"{checkpoint_id}.pkl"
            metadata_file = self.metadata_dir / f"{checkpoint_id}.json"
            experiences_file = self.experiences_dir / f"{checkpoint_id}_experiences.json"
            
            for file_path in [checkpoint_file, metadata_file, experiences_file]:
                if file_path.exists():
                    file_path.unlink()
            
            # Remover do índice
            if checkpoint_id in self.checkpoint_index:
                del self.checkpoint_index[checkpoint_id]
                self._save_index()
            
            print(f"✅ Checkpoint {checkpoint_id} removido")
            return True
            
        except Exception as e:
            print(f"❌ Erro ao remover checkpoint: {e}")
            return False
    
    def create_agent_variant(self, base_checkpoint_id: str, 
                           specialization_config: Dict[str, Any]) -> str:
        """Cria variante especializada de um agente"""
        print(f"🔄 Criando variante especializada do checkpoint: {base_checkpoint_id}")
        
        # Carregar agente base
        base_agent = self.load_agent_from_checkpoint(base_checkpoint_id)
        
        # Aplicar especialização
        specialized_agent = self._apply_specialization(base_agent, specialization_config)
        
        # Criar novo checkpoint
        variant_version = f"variant_{specialization_config.get('name', 'custom')}"
        checkpoint_id = self.create_checkpoint(
            specialized_agent, 
            version_tag=variant_version,
            specialization=specialization_config.get('specialization', 'custom')
        )
        
        print(f"✅ Variante criada: {checkpoint_id}")
        return checkpoint_id
    
    def _apply_specialization(self, agent, config: Dict[str, Any]):
        """Aplica configuração de especialização ao agente"""
        # Configurações de especialização
        if 'adaptation_mode' in config:
            agent.adaptation_mode = config['adaptation_mode']
        
        if 'focus_areas' in config:
            # Implementar lógica de foco específica
            pass
        
        if 'quality_threshold' in config:
            # Implementar threshold de qualidade
            pass
        
        return agent
    
    def export_checkpoint_summary(self) -> Dict[str, Any]:
        """Exporta resumo de todos os checkpoints"""
        checkpoints = list(self.checkpoint_index.values())
        
        # Estatísticas gerais
        total_checkpoints = len(checkpoints)
        agents_types = list(set(cp['agent_name'] for cp in checkpoints))
        specializations = list(set(cp['specialization'] for cp in checkpoints))
        
        # Métricas de qualidade
        qualities = [cp['quality_average'] for cp in checkpoints if cp['quality_average'] > 0]
        avg_quality = sum(qualities) / len(qualities) if qualities else 0
        
        return {
            'total_checkpoints': total_checkpoints,
            'agent_types': agents_types,
            'specializations': specializations,
            'average_quality': avg_quality,
            'checkpoints': checkpoints,
            'storage_path': str(self.storage_path),
            'summary_date': datetime.now().isoformat()
        }


# Exemplo de uso e testes
if __name__ == "__main__":
    # Inicializar sistema de checkpoints
    checkpoint_manager = AgentCheckpointManager()
    
    # Criar agente de exemplo
    from core.agents.code_agent_enhanced import CodeAgentEnhanced
    
    print("🤖 Criando agente de exemplo...")
    test_agent = CodeAgentEnhanced(use_mock=True, enable_graphrag=True)
    
    # Gerar algumas experiências
    test_tasks = [
        "criar função que retorna saudação",
        "implementar validação de email",
        "criar função de cálculo matemático"
    ]
    
    for task in test_tasks:
        result = test_agent.execute_task(task)
        print(f"   Tarefa: {task} - Qualidade: {result.quality_score:.1f}")
    
    # Criar checkpoint
    checkpoint_id = checkpoint_manager.create_checkpoint(
        test_agent,
        version_tag="v1.0_test",
        specialization="general_purpose"
    )
    
    # Listar checkpoints
    print(f"\n📋 Checkpoints disponíveis:")
    checkpoints = checkpoint_manager.list_checkpoints()
    for cp in checkpoints:
        print(f"   {cp['id']} - {cp['agent_name']} v{cp['version']} ({cp['specialization']})")
    
    # Testar carregamento
    print(f"\n🔄 Testando carregamento do checkpoint...")
    loaded_agent = checkpoint_manager.load_agent_from_checkpoint(checkpoint_id)
    
    # Testar agente carregado
    test_result = loaded_agent.execute_task("teste de agente restaurado")
    print(f"   Teste pós-restauração: Qualidade {test_result.quality_score:.1f}")
    
    # Limpar
    test_agent.close()
    loaded_agent.close()
    
    print(f"\n✅ Teste do sistema de checkpoints concluído!")