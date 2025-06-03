import pytest
from datetime import datetime
from unittest.mock import MagicMock
from memory.pattern_discovery import (
    PatternDiscoveryEngine, 
    DiscoveredPattern
)
from memory.hybrid_store import HybridMemoryStore

@pytest.fixture
def mock_engine():
    # Configurar mock do HybridMemoryStore
    mock_store = MagicMock(spec=HybridMemoryStore)
    mock_store.enable_graphrag = False
    return PatternDiscoveryEngine(mock_store)

@pytest.fixture
def sample_pattern():
    return DiscoveredPattern(
        id="test_pattern_1",
        name="Test Pattern",
        description="Pattern for testing",
        template="def test():\n    pass",
        success_rate=0.9,
        usage_count=5,
        contexts=["testing"],
        quality_impact=8.5,
        discovery_date=datetime.now(),
        related_experiences=["exp1", "exp2"],
        confidence_score=0.85
    )

def test_engine_initialization(mock_engine):
    assert mock_engine is not None
    assert len(mock_engine.discovered_patterns) == 0

def test_discover_patterns(mock_engine):
    # Configurar mock para retornar experiências
    mock_engine._collect_recent_experiences = MagicMock(return_value=[
        {
            'id': 'exp1',
            'task': 'test task',
            'code': 'def test():\n    return True',
            'quality': 8.0,
            'success': True,
            'agent': 'test_agent',
            'timestamp': datetime.now().isoformat()
        }
    ])
    
    patterns = mock_engine.discover_patterns()
    assert isinstance(patterns, list)

def test_pattern_recommendations(mock_engine, sample_pattern):
    mock_engine.discovered_patterns = [sample_pattern]
    recommendations = mock_engine.get_pattern_recommendations("test task")
    assert len(recommendations) > 0
    assert recommendations[0]['pattern'].id == "test_pattern_1"

def test_export_patterns(mock_engine, sample_pattern):
    mock_engine.discovered_patterns = [sample_pattern]
    summary = mock_engine.export_patterns_summary()
    assert summary['total_patterns'] == 1
    assert summary['patterns'][0]['name'] == "Test Pattern"
