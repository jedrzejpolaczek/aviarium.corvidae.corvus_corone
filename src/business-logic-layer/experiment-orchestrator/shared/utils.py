"""
Shared utilities and configuration for Experiment Orchestrator
"""
import os
import logging
from typing import Dict, Any, Optional
from pydantic import BaseModel
from datetime import datetime
import httpx

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class OrchestratorConfig:
    """Configuration management for Experiment Orchestrator"""
    
    def __init__(self):
        # Service URLs
        self.tracking_service_url = os.getenv("TRACKING_SERVICE_URL", "http://experiment-tracking:8002")
        self.benchmark_service_url = os.getenv("BENCHMARK_SERVICE_URL", "http://benchmark-definition:8003")
        self.algorithm_registry_url = os.getenv("ALGORITHM_REGISTRY_URL", "http://algorithm-registry:8004")
        self.rabbitmq_url = os.getenv("RABBITMQ_URL", "amqp://admin:admin@rabbitmq:5672")
        
        # Execution configuration
        self.max_concurrent_runs = int(os.getenv("MAX_CONCURRENT_RUNS", "10"))
        self.default_run_timeout = int(os.getenv("DEFAULT_RUN_TIMEOUT", "3600"))  # 1 hour
        self.queue_check_interval = int(os.getenv("QUEUE_CHECK_INTERVAL", "30"))  # 30 seconds
        
        # Resource limits
        self.max_experiments_per_user = int(os.getenv("MAX_EXPERIMENTS_PER_USER", "10"))
        self.max_runs_per_experiment = int(os.getenv("MAX_RUNS_PER_EXPERIMENT", "1000"))
        
        # Logging and monitoring
        self.log_level = os.getenv("LOG_LEVEL", "INFO")
        self.metrics_enabled = os.getenv("METRICS_ENABLED", "true").lower() == "true"

class ServiceClient:
    """HTTP client for communicating with other services"""
    
    def __init__(self, config: OrchestratorConfig):
        self.config = config
        self.client = httpx.AsyncClient(timeout=30.0)
    
    async def validate_algorithm(self, algorithm_id: str) -> bool:
        """Validate that algorithm exists in registry"""
        try:
            response = await self.client.get(f"{self.config.algorithm_registry_url}/algorithms/{algorithm_id}")
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Failed to validate algorithm {algorithm_id}: {e}")
            return False
    
    async def validate_benchmark(self, benchmark_id: str) -> bool:
        """Validate that benchmark exists"""
        try:
            response = await self.client.get(f"{self.config.benchmark_service_url}/benchmarks/{benchmark_id}")
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Failed to validate benchmark {benchmark_id}: {e}")
            return False
    
    async def register_experiment(self, experiment_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Register experiment with tracking service"""
        try:
            response = await self.client.post(
                f"{self.config.tracking_service_url}/experiments",
                json=experiment_data
            )
            if response.status_code == 201:
                return response.json()
            else:
                logger.error(f"Failed to register experiment: HTTP {response.status_code}")
                return None
        except Exception as e:
            logger.error(f"Failed to register experiment: {e}")
            return None
    
    async def update_experiment_status(self, experiment_id: str, status: str) -> bool:
        """Update experiment status in tracking service"""
        try:
            response = await self.client.patch(
                f"{self.config.tracking_service_url}/experiments/{experiment_id}",
                json={"status": status, "updated_at": datetime.utcnow().isoformat()}
            )
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Failed to update experiment status: {e}")
            return False
    
    async def close(self):
        """Close HTTP client"""
        await self.client.aclose()

class ReproducibilityManager:
    """Manages reproducibility aspects of experiments"""
    
    def __init__(self):
        self.reproducibility_configs: Dict[str, Dict[str, Any]] = {}
    
    def generate_seeds(self, num_seeds: int, base_seed: int = 42) -> list[int]:
        """Generate reproducible seeds for experiment runs"""
        import random
        random.seed(base_seed)
        return [random.randint(0, 2**31 - 1) for _ in range(num_seeds)]
    
    def store_reproducibility_info(self, experiment_id: str, info: Dict[str, Any]):
        """Store reproducibility information for an experiment"""
        self.reproducibility_configs[experiment_id] = {
            "stored_at": datetime.utcnow().isoformat(),
            "python_version": info.get("python_version"),
            "package_versions": info.get("package_versions", {}),
            "system_info": info.get("system_info", {}),
            "random_seeds": info.get("random_seeds", []),
            "environment_hash": info.get("environment_hash")
        }
        logger.info(f"Stored reproducibility info for experiment {experiment_id}")
    
    def get_reproducibility_info(self, experiment_id: str) -> Optional[Dict[str, Any]]:
        """Get stored reproducibility information"""
        return self.reproducibility_configs.get(experiment_id)
    
    def generate_environment_fingerprint(self) -> Dict[str, Any]:
        """Generate environment fingerprint for reproducibility"""
        import sys
        import platform
        import hashlib
        
        # Collect environment information
        env_info = {
            "python_version": sys.version,
            "platform": platform.platform(),
            "architecture": platform.architecture(),
            "processor": platform.processor(),
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Generate hash of environment
        env_string = str(sorted(env_info.items()))
        env_hash = hashlib.sha256(env_string.encode()).hexdigest()
        env_info["environment_hash"] = env_hash
        
        return env_info

def get_orchestrator_config() -> OrchestratorConfig:
    """Get orchestrator configuration instance"""
    return OrchestratorConfig()

def create_service_client(config: OrchestratorConfig) -> ServiceClient:
    """Create service client instance"""
    return ServiceClient(config)

def get_reproducibility_manager() -> ReproducibilityManager:
    """Get reproducibility manager instance"""
    return ReproducibilityManager()

# Standard response models
class ExperimentResponse(BaseModel):
    """Standard response for experiment operations"""
    experiment_id: str
    status: str
    message: str
    timestamp: str = datetime.utcnow().isoformat()

class SchedulingResponse(BaseModel):
    """Response for scheduling operations"""
    experiment_id: str
    scheduled_runs: int
    total_runs: int
    estimated_duration_minutes: float
    status: str

class ErrorResponse(BaseModel):
    """Standard error response"""
    error: str
    message: str
    timestamp: str = datetime.utcnow().isoformat()