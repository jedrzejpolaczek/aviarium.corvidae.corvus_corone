"""
Experiment configuration and validation components
"""
import logging
from typing import Dict, List, Any, Optional
from pydantic import BaseModel, Field, validator
from enum import Enum
import uuid
from datetime import datetime

logger = logging.getLogger(__name__)

class ExperimentStatus(str, Enum):
    DRAFT = "draft"
    VALIDATING = "validating"
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class ExperimentGoal(str, Enum):
    G1_EVALUATION = "g1_evaluation"  # Algorithm performance evaluation
    G2_COMPARISON = "g2_comparison"   # Comparison of algorithms
    G3_SENSITIVITY = "g3_sensitivity" # Sensitivity/robustness analysis

class BudgetType(str, Enum):
    EVALUATIONS = "evaluations"
    TIME = "time"
    CUSTOM = "custom"

class ExperimentConfig(BaseModel):
    """Experiment configuration model"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    goal: ExperimentGoal
    
    # Algorithm and benchmark configuration
    algorithms: List[str] = Field(..., min_items=1)  # Algorithm IDs
    benchmarks: List[str] = Field(..., min_items=1)  # Benchmark IDs
    
    # Budget configuration
    budget_type: BudgetType = BudgetType.EVALUATIONS
    budget_value: int = Field(..., gt=0)
    
    # Run configuration
    num_seeds: int = Field(10, ge=1, le=100)
    seeds: Optional[List[int]] = None
    parallel_runs: int = Field(1, ge=1, le=50)
    
    # Metadata
    tags: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    status: ExperimentStatus = ExperimentStatus.DRAFT
    
    @validator('seeds')
    def validate_seeds(cls, v, values):
        if v is not None and 'num_seeds' in values:
            if len(v) != values['num_seeds']:
                raise ValueError(f"Number of seeds ({len(v)}) must match num_seeds ({values['num_seeds']})")
        return v

class ExperimentConfigManager:
    """Manages experiment configuration and validation"""
    
    def __init__(self):
        self.active_experiments: Dict[str, ExperimentConfig] = {}
    
    async def create_experiment(self, config_data: Dict[str, Any]) -> ExperimentConfig:
        """Create and validate new experiment configuration"""
        try:
            config = ExperimentConfig(**config_data)
            
            # Generate seeds if not provided
            if config.seeds is None:
                import random
                random.seed(42)  # For reproducibility
                config.seeds = [random.randint(0, 2**31 - 1) for _ in range(config.num_seeds)]
            
            # Validate algorithms and benchmarks exist
            await self._validate_algorithms(config.algorithms)
            await self._validate_benchmarks(config.benchmarks)
            
            self.active_experiments[config.id] = config
            logger.info(f"Created experiment configuration: {config.id}")
            
            return config
            
        except Exception as e:
            logger.error(f"Failed to create experiment configuration: {e}")
            raise ValueError(f"Invalid experiment configuration: {str(e)}")
    
    async def update_experiment(self, experiment_id: str, updates: Dict[str, Any]) -> ExperimentConfig:
        """Update existing experiment configuration"""
        if experiment_id not in self.active_experiments:
            raise ValueError(f"Experiment {experiment_id} not found")
        
        config = self.active_experiments[experiment_id]
        
        # Only allow updates if experiment is in draft state
        if config.status != ExperimentStatus.DRAFT:
            raise ValueError(f"Cannot update experiment in {config.status} state")
        
        # Apply updates
        for key, value in updates.items():
            if hasattr(config, key):
                setattr(config, key, value)
        
        # Re-validate
        await self._validate_algorithms(config.algorithms)
        await self._validate_benchmarks(config.benchmarks)
        
        logger.info(f"Updated experiment configuration: {experiment_id}")
        return config
    
    async def get_experiment(self, experiment_id: str) -> Optional[ExperimentConfig]:
        """Get experiment configuration by ID"""
        return self.active_experiments.get(experiment_id)
    
    async def list_experiments(self, status: Optional[ExperimentStatus] = None) -> List[ExperimentConfig]:
        """List experiment configurations with optional status filter"""
        experiments = list(self.active_experiments.values())
        if status:
            experiments = [exp for exp in experiments if exp.status == status]
        return experiments
    
    async def update_status(self, experiment_id: str, status: ExperimentStatus) -> ExperimentConfig:
        """Update experiment status"""
        if experiment_id not in self.active_experiments:
            raise ValueError(f"Experiment {experiment_id} not found")
        
        config = self.active_experiments[experiment_id]
        old_status = config.status
        config.status = status
        
        logger.info(f"Updated experiment {experiment_id} status: {old_status} -> {status}")
        return config
    
    async def _validate_algorithms(self, algorithm_ids: List[str]):
        """Validate that algorithms exist in registry"""
        # This would make actual HTTP requests to algorithm registry
        # For now, just log the validation
        logger.debug(f"Validating algorithms: {algorithm_ids}")
        # TODO: Implement actual validation against algorithm registry
    
    async def _validate_benchmarks(self, benchmark_ids: List[str]):
        """Validate that benchmarks exist in registry"""
        # This would make actual HTTP requests to benchmark service
        # For now, just log the validation
        logger.debug(f"Validating benchmarks: {benchmark_ids}")
        # TODO: Implement actual validation against benchmark service

# Global instance
experiment_config_manager = ExperimentConfigManager()