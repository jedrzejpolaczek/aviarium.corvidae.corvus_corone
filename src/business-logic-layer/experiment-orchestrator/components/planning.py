"""
Experiment execution planning and run scheduling components
"""
import logging
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from enum import Enum
import uuid
from datetime import datetime
import itertools
from .config import ExperimentConfig, ExperimentStatus

logger = logging.getLogger(__name__)

class RunStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class RunConfig(BaseModel):
    """Configuration for a single experiment run"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    experiment_id: str
    algorithm_id: str
    benchmark_id: str
    seed: int
    budget_type: str
    budget_value: int
    status: RunStatus = RunStatus.PENDING
    created_at: datetime = Field(default_factory=datetime.utcnow)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    worker_id: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)

class ExperimentPlan(BaseModel):
    """Complete execution plan for an experiment"""
    experiment_id: str
    total_runs: int
    runs: List[RunConfig]
    estimated_duration_minutes: Optional[float] = None
    resource_requirements: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)

class ExperimentPlanBuilder:
    """Builds execution plans for experiments"""
    
    def __init__(self):
        self.active_plans: Dict[str, ExperimentPlan] = {}
    
    async def build_plan(self, experiment_config: ExperimentConfig) -> ExperimentPlan:
        """Build execution plan from experiment configuration"""
        try:
            runs = []
            
            # Generate all combinations of algorithms, benchmarks, and seeds
            combinations = itertools.product(
                experiment_config.algorithms,
                experiment_config.benchmarks,
                experiment_config.seeds
            )
            
            for algorithm_id, benchmark_id, seed in combinations:
                run_config = RunConfig(
                    experiment_id=experiment_config.id,
                    algorithm_id=algorithm_id,
                    benchmark_id=benchmark_id,
                    seed=seed,
                    budget_type=experiment_config.budget_type.value,
                    budget_value=experiment_config.budget_value,
                    metadata={
                        "experiment_name": experiment_config.name,
                        "goal": experiment_config.goal.value,
                        "tags": experiment_config.tags
                    }
                )
                runs.append(run_config)
            
            # Estimate resource requirements
            resource_requirements = await self._estimate_resources(runs)
            
            # Estimate duration
            estimated_duration = await self._estimate_duration(runs)
            
            plan = ExperimentPlan(
                experiment_id=experiment_config.id,
                total_runs=len(runs),
                runs=runs,
                estimated_duration_minutes=estimated_duration,
                resource_requirements=resource_requirements
            )
            
            self.active_plans[experiment_config.id] = plan
            logger.info(f"Built execution plan for experiment {experiment_config.id}: {len(runs)} runs")
            
            return plan
            
        except Exception as e:
            logger.error(f"Failed to build execution plan: {e}")
            raise ValueError(f"Cannot build execution plan: {str(e)}")
    
    async def get_plan(self, experiment_id: str) -> Optional[ExperimentPlan]:
        """Get execution plan by experiment ID"""
        return self.active_plans.get(experiment_id)
    
    async def update_run_status(self, run_id: str, status: RunStatus, worker_id: Optional[str] = None) -> Optional[RunConfig]:
        """Update status of a specific run"""
        for plan in self.active_plans.values():
            for run in plan.runs:
                if run.id == run_id:
                    old_status = run.status
                    run.status = status
                    
                    if status == RunStatus.RUNNING and not run.started_at:
                        run.started_at = datetime.utcnow()
                        run.worker_id = worker_id
                    elif status in [RunStatus.COMPLETED, RunStatus.FAILED, RunStatus.CANCELLED]:
                        run.completed_at = datetime.utcnow()
                    
                    logger.info(f"Updated run {run_id} status: {old_status} -> {status}")
                    return run
        
        logger.warning(f"Run {run_id} not found for status update")
        return None
    
    async def get_pending_runs(self, experiment_id: str, limit: Optional[int] = None) -> List[RunConfig]:
        """Get pending runs for an experiment"""
        plan = self.active_plans.get(experiment_id)
        if not plan:
            return []
        
        pending_runs = [run for run in plan.runs if run.status == RunStatus.PENDING]
        
        if limit:
            pending_runs = pending_runs[:limit]
        
        return pending_runs
    
    async def get_experiment_progress(self, experiment_id: str) -> Dict[str, Any]:
        """Get experiment execution progress"""
        plan = self.active_plans.get(experiment_id)
        if not plan:
            return {"error": "Plan not found"}
        
        status_counts = {}
        for status in RunStatus:
            status_counts[status.value] = sum(1 for run in plan.runs if run.status == status)
        
        completed_runs = status_counts.get(RunStatus.COMPLETED.value, 0)
        total_runs = plan.total_runs
        progress_percent = (completed_runs / total_runs * 100) if total_runs > 0 else 0
        
        return {
            "experiment_id": experiment_id,
            "total_runs": total_runs,
            "status_counts": status_counts,
            "progress_percent": round(progress_percent, 2),
            "estimated_duration_minutes": plan.estimated_duration_minutes,
            "resource_requirements": plan.resource_requirements
        }
    
    async def _estimate_resources(self, runs: List[RunConfig]) -> Dict[str, Any]:
        """Estimate resource requirements for runs"""
        # Simple resource estimation - in practice this would be more sophisticated
        return {
            "cpu_cores": min(len(runs), 10),  # Max 10 parallel runs
            "memory_gb": len(runs) * 0.5,     # 500MB per run
            "disk_gb": len(runs) * 0.1,       # 100MB per run
            "estimated_cost_usd": len(runs) * 0.05  # $0.05 per run
        }
    
    async def _estimate_duration(self, runs: List[RunConfig]) -> float:
        """Estimate total execution duration in minutes"""
        # Simple duration estimation - in practice this would use historical data
        base_duration_per_run = 5.0  # 5 minutes base per run
        parallel_factor = 0.1  # 10% parallelization efficiency
        
        total_sequential_time = len(runs) * base_duration_per_run
        estimated_parallel_time = total_sequential_time * parallel_factor
        
        return max(estimated_parallel_time, base_duration_per_run)

# Global instance
experiment_plan_builder = ExperimentPlanBuilder()