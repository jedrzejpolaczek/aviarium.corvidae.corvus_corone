# Test configuration for the layered architecture

import pytest
import asyncio
import logging
from pathlib import Path

# Configure logging for tests
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def pytest_configure(config):
    """Configure pytest with custom markers"""
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests"
    )
    config.addinivalue_line(
        "markers", "performance: marks tests as performance tests"
    )

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
def project_root():
    """Get the project root directory"""
    return Path(__file__).parent.parent

@pytest.fixture
def src_path(project_root):
    """Get the source code path"""
    return project_root / "src"

@pytest.fixture
def docs_path(project_root):
    """Get the documentation path"""
    return project_root / "docs"

# Test data fixtures
@pytest.fixture
def sample_experiment_config():
    """Sample experiment configuration for testing"""
    return {
        "name": "Test Experiment",
        "description": "A test experiment for validation",
        "goal": "g1_evaluation",
        "algorithms": ["random_search", "bayesian_optimization"],
        "benchmarks": ["sphere", "rosenbrock"],
        "budget_type": "evaluations",
        "budget_value": 100,
        "num_seeds": 5,
        "tags": ["test", "validation"]
    }

@pytest.fixture
def sample_algorithm_metadata():
    """Sample algorithm metadata for testing"""
    return {
        "id": "test_algorithm",
        "name": "Test Algorithm",
        "version": "1.0.0",
        "description": "A test algorithm for validation",
        "parameters": {
            "learning_rate": {"type": "float", "range": [0.001, 0.1]},
            "batch_size": {"type": "int", "range": [16, 128]}
        },
        "requirements": ["numpy>=1.20.0", "scipy>=1.7.0"]
    }

@pytest.fixture
def sample_benchmark_metadata():
    """Sample benchmark metadata for testing"""
    return {
        "id": "test_benchmark",
        "name": "Test Benchmark",
        "version": "1.0.0",
        "description": "A test benchmark for validation",
        "problem_type": "continuous_optimization",
        "dimensionality": 10,
        "bounds": [[-5.0, 5.0]] * 10,
        "optimal_value": 0.0
    }

# Mock service fixtures
@pytest.fixture
async def mock_services():
    """Create mock services for testing"""
    from tests.integration.test_performance import MockServiceClient
    
    services = {
        "auth": MockServiceClient(response_delay=0.01),
        "orchestrator": MockServiceClient(response_delay=0.02),
        "tracking": MockServiceClient(response_delay=0.015),
        "metrics": MockServiceClient(response_delay=0.025),
        "algorithms": MockServiceClient(response_delay=0.01),
        "benchmarks": MockServiceClient(response_delay=0.01)
    }
    
    yield services
    
    # Cleanup if needed
    for service in services.values():
        if hasattr(service, 'cleanup'):
            await service.cleanup()

# Environment setup for tests
@pytest.fixture(autouse=True)
def setup_test_environment(monkeypatch):
    """Setup test environment variables"""
    monkeypatch.setenv("LOG_LEVEL", "DEBUG")
    monkeypatch.setenv("TESTING", "true")
    monkeypatch.setenv("DATABASE_URL", "sqlite:///:memory:")
    monkeypatch.setenv("RABBITMQ_URL", "memory://")
    monkeypatch.setenv("REDIS_URL", "redis://localhost:6379/15")  # Use test database