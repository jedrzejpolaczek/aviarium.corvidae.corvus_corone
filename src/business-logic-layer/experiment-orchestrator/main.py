from fastapi import FastAPI, HTTPException, BackgroundTasks
from typing import List, Dict, Any, Optional
from enum import Enum
from pydantic import BaseModel, Field
import logging
from datetime import datetime
import httpx
import os
import uuid

# Import components and shared utilities
from components import (
    experiment_config_manager,
    experiment_plan_builder,
    run_scheduler,
    ExperimentConfig,
    ExperimentPlan,
    RunConfig
)
from shared import (
    get_orchestrator_config,
    create_service_client,
    get_reproducibility_manager,
    ExperimentResponse,
    SchedulingResponse,
    ErrorResponse
)

# Configure logging and initialize
config = get_orchestrator_config()
logging.basicConfig(level=getattr(logging, config.log_level))
logger = logging.getLogger(__name__)

# Service URLs
ALGORITHM_REGISTRY_URL = os.getenv("ALGORITHM_REGISTRY_URL", "http://algorithm-registry:8004")
BENCHMARK_SERVICE_URL = os.getenv("BENCHMARK_SERVICE_URL", "http://benchmark-definition:8003")

app = FastAPI(
    title="Experiment Orchestrator Service",
    description="Manages experiment configuration, planning, and execution orchestration",
    version="1.0.0"
)

# Initialize global services
service_client = create_service_client(config)
reproducibility_manager = get_reproducibility_manager()

class ExperimentStatus(str, Enum):
    DRAFT = "draft"
    VALIDATING = "validating"
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class RunStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class ExperimentGoal(str, Enum):
    G1_EVALUATION = "g1_evaluation"  # Algorithm performance evaluation
    G2_COMPARISON = "g2_comparison"   # Comparison of algorithms
    G3_SENSITIVITY = "g3_sensitivity" # Sensitivity/robustness analysis
    G4_EXTRAPOLATION = "g4_extrapolation" # Extrapolation/generalization
    G5_THEORY = "g5_theory"          # Theory and algorithm development

class AlgorithmConfig(BaseModel):
    algorithm_id: str
    version: str
    parameters: Dict[str, Any] = {}
    budget_limit: Optional[int] = None  # Max evaluations
    time_limit: Optional[int] = None    # Max seconds

class BenchmarkConfig(BaseModel):
    benchmark_id: str
    instance_ids: List[str] = []
    include_all_instances: bool = False

class ExperimentConfig(BaseModel):
    name: str
    description: str = ""
    goals: List[ExperimentGoal]
    algorithms: List[AlgorithmConfig]
    benchmarks: List[BenchmarkConfig]
    seeds: List[int] = Field(default_factory=lambda: [42, 123, 456, 789, 999])
    priority: int = Field(default=1, ge=1, le=10)  # 1=low, 10=high
    max_parallel_runs: int = Field(default=4, ge=1, le=50)
    retry_failed_runs: bool = True
    tags: List[str] = []
    metadata: Dict[str, Any] = {}

class CreateExperimentRequest(BaseModel):
    config: ExperimentConfig
    start_immediately: bool = False

class ExperimentResponse(BaseModel):
    id: str
    status: ExperimentStatus
    config: ExperimentConfig
    created_at: datetime
    updated_at: datetime
    total_runs: int
    completed_runs: int
    failed_runs: int
    estimated_completion: Optional[datetime] = None

class RunPlan(BaseModel):
    run_id: str
    experiment_id: str
    algorithm_config: AlgorithmConfig
    benchmark_id: str
    instance_id: str
    seed: int
    priority: int
    estimated_duration: Optional[int] = None  # seconds

# Message broker connection
def get_rabbitmq_connection():
    """Get RabbitMQ connection with retry logic"""
    max_retries = 5
    for i in range(max_retries):
        try:
            connection = pika.BlockingConnection(pika.URLParameters(RABBITMQ_URL))
            return connection
        except Exception as e:
            logger.warning(f"RabbitMQ connection attempt {i+1}/{max_retries} failed: {e}")
            if i < max_retries - 1:
                time.sleep(2 ** i)  # Exponential backoff
            else:
                raise

# In-memory storage for development (replace with database in production)
experiments_store: Dict[str, Dict] = {}
run_plans_store: Dict[str, List[RunPlan]] = {}

class ExperimentConfigManager:
    """Validates experiment configuration"""
    
    async def validate_config(self, config: ExperimentConfig) -> Dict[str, Any]:
        """Validate experiment configuration against available algorithms and benchmarks"""
        validation_result = {
            "valid": True,
            "errors": [],
            "warnings": []
        }
        
        # Validate algorithms
        for algo_config in config.algorithms:
            try:
                async with httpx.AsyncClient() as client:
                    response = await client.get(
                        f"{ALGORITHM_REGISTRY_URL}/api/algorithms/{algo_config.algorithm_id}"
                    )
                    if response.status_code != 200:
                        validation_result["errors"].append(
                            f"Algorithm {algo_config.algorithm_id} not found"
                        )
                        validation_result["valid"] = False
            except Exception as e:
                validation_result["errors"].append(
                    f"Failed to validate algorithm {algo_config.algorithm_id}: {e}"
                )
                validation_result["valid"] = False
        
        # Validate benchmarks
        for bench_config in config.benchmarks:
            try:
                async with httpx.AsyncClient() as client:
                    response = await client.get(
                        f"{BENCHMARK_SERVICE_URL}/api/benchmarks/{bench_config.benchmark_id}"
                    )
                    if response.status_code != 200:
                        validation_result["errors"].append(
                            f"Benchmark {bench_config.benchmark_id} not found"
                        )
                        validation_result["valid"] = False
            except Exception as e:
                validation_result["errors"].append(
                    f"Failed to validate benchmark {bench_config.benchmark_id}: {e}"
                )
                validation_result["valid"] = False
        
        # Validate resource requirements
        total_estimated_runs = sum(
            len(config.algorithms) * 
            (len(bench.instance_ids) if bench.instance_ids else 10) *  # Estimate 10 instances if all
            len(config.seeds)
            for bench in config.benchmarks
        )
        
        if total_estimated_runs > 10000:
            validation_result["warnings"].append(
                f"Large experiment with {total_estimated_runs} runs may take a long time"
            )
        
        return validation_result

class ExperimentPlanBuilder:
    """Creates execution plan for experiments"""
    
    async def build_plan(self, experiment_id: str, config: ExperimentConfig) -> List[RunPlan]:
        """Build execution plan with all algorithm x benchmark x seed combinations"""
        plan = []
        
        for algo_config in config.algorithms:
            for bench_config in config.benchmarks:
                # Get benchmark instances
                instance_ids = bench_config.instance_ids
                if bench_config.include_all_instances or not instance_ids:
                    # Fetch all instances for this benchmark
                    try:
                        async with httpx.AsyncClient() as client:
                            response = await client.get(
                                f"{BENCHMARK_SERVICE_URL}/api/benchmarks/{bench_config.benchmark_id}/instances"
                            )
                            if response.status_code == 200:
                                instances = response.json()
                                instance_ids = [inst["id"] for inst in instances]
                            else:
                                logger.error(f"Failed to fetch instances for benchmark {bench_config.benchmark_id}")
                                continue
                    except Exception as e:
                        logger.error(f"Error fetching benchmark instances: {e}")
                        continue
                
                # Create runs for each seed
                for seed in config.seeds:
                    for instance_id in instance_ids:
                        run_plan = RunPlan(
                            run_id=str(uuid.uuid4()),
                            experiment_id=experiment_id,
                            algorithm_config=algo_config,
                            benchmark_id=bench_config.benchmark_id,
                            instance_id=instance_id,
                            seed=seed,
                            priority=config.priority
                        )
                        plan.append(run_plan)
        
        return plan

class RunScheduler:
    """Schedules runs for execution"""
    
    def __init__(self):
        self.connection = None
        self.channel = None
        self._setup_queues()
    
    def _setup_queues(self):
        """Setup RabbitMQ queues"""
        try:
            self.connection = get_rabbitmq_connection()
            self.channel = self.connection.channel()
            
            # Declare queues
            self.channel.queue_declare(queue='hpo_runs', durable=True)
            self.channel.queue_declare(queue='run_results', durable=True)
            
            logger.info("RabbitMQ queues set up successfully")
        except Exception as e:
            logger.error(f"Failed to setup RabbitMQ queues: {e}")
    
    async def schedule_runs(self, runs: List[RunPlan]):
        """Schedule runs for execution"""
        if not self.channel:
            self._setup_queues()
        
        for run in runs:
            try:
                # Send run to worker queue
                message = {
                    "run_id": run.run_id,
                    "experiment_id": run.experiment_id,
                    "algorithm_config": run.algorithm_config.dict(),
                    "benchmark_id": run.benchmark_id,
                    "instance_id": run.instance_id,
                    "seed": run.seed,
                    "priority": run.priority
                }
                
                self.channel.basic_publish(
                    exchange='',
                    routing_key='hpo_runs',
                    body=json.dumps(message),
                    properties=pika.BasicProperties(
                        delivery_mode=2,  # Make message persistent
                        priority=run.priority
                    )
                )
                
                # Register run with tracking service
                await self._register_run_with_tracking(run)
                
                logger.info(f"Scheduled run {run.run_id}")
                
            except Exception as e:
                logger.error(f"Failed to schedule run {run.run_id}: {e}")
    
    async def _register_run_with_tracking(self, run: RunPlan):
        """Register run with tracking service"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{TRACKING_SERVICE_URL}/api/tracking/runs",
                    json={
                        "run_id": run.run_id,
                        "experiment_id": run.experiment_id,
                        "algorithm_version_id": f"{run.algorithm_config.algorithm_id}:{run.algorithm_config.version}",
                        "benchmark_instance_id": run.instance_id,
                        "seed": run.seed,
                        "status": RunStatus.PENDING,
                        "config": run.algorithm_config.dict()
                    }
                )
                if response.status_code != 201:
                    logger.error(f"Failed to register run {run.run_id} with tracking service")
        except Exception as e:
            logger.error(f"Error registering run with tracking: {e}")

# Service instances
config_manager = ExperimentConfigManager()
plan_builder = ExperimentPlanBuilder()
run_scheduler = RunScheduler()

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "experiment-orchestrator"}

@app.post("/api/experiments", response_model=ExperimentResponse)
async def create_experiment(request: CreateExperimentRequest, background_tasks: BackgroundTasks):
    """Create new experiment"""
    # Validate configuration
    validation = await config_manager.validate_config(request.config)
    if not validation["valid"]:
        raise HTTPException(
            status_code=400,
            detail={"message": "Invalid experiment configuration", "errors": validation["errors"]}
        )
    
    # Generate experiment ID
    experiment_id = str(uuid.uuid4())
    
    # Create experiment record
    experiment = {
        "id": experiment_id,
        "status": ExperimentStatus.VALIDATING,
        "config": request.config.dict(),
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
        "total_runs": 0,
        "completed_runs": 0,
        "failed_runs": 0
    }
    
    experiments_store[experiment_id] = experiment
    
    # Build execution plan
    background_tasks.add_task(build_and_schedule_experiment, experiment_id, request.config, request.start_immediately)
    
    return ExperimentResponse(**experiment)

@app.get("/api/experiments/{experiment_id}", response_model=ExperimentResponse)
async def get_experiment(experiment_id: str):
    """Get experiment details"""
    if experiment_id not in experiments_store:
        raise HTTPException(status_code=404, detail="Experiment not found")
    
    experiment = experiments_store[experiment_id]
    return ExperimentResponse(**experiment)

@app.get("/api/experiments", response_model=List[ExperimentResponse])
async def list_experiments(
    status: Optional[ExperimentStatus] = None,
    limit: int = 50,
    offset: int = 0
):
    """List experiments with optional filtering"""
    experiments = list(experiments_store.values())
    
    if status:
        experiments = [exp for exp in experiments if exp["status"] == status]
    
    # Sort by created_at descending
    experiments.sort(key=lambda x: x["created_at"], reverse=True)
    
    # Apply pagination
    experiments = experiments[offset:offset + limit]
    
    return [ExperimentResponse(**exp) for exp in experiments]

@app.post("/api/experiments/{experiment_id}/start")
async def start_experiment(experiment_id: str, background_tasks: BackgroundTasks):
    """Start experiment execution"""
    if experiment_id not in experiments_store:
        raise HTTPException(status_code=404, detail="Experiment not found")
    
    experiment = experiments_store[experiment_id]
    if experiment["status"] not in [ExperimentStatus.PENDING, ExperimentStatus.DRAFT]:
        raise HTTPException(status_code=400, detail="Experiment cannot be started in current status")
    
    # Schedule runs
    if experiment_id in run_plans_store:
        background_tasks.add_task(execute_experiment, experiment_id)
        experiment["status"] = ExperimentStatus.RUNNING
        experiment["updated_at"] = datetime.utcnow()
    
    return {"message": "Experiment started", "experiment_id": experiment_id}

@app.post("/api/experiments/{experiment_id}/cancel")
async def cancel_experiment(experiment_id: str):
    """Cancel experiment execution"""
    if experiment_id not in experiments_store:
        raise HTTPException(status_code=404, detail="Experiment not found")
    
    experiment = experiments_store[experiment_id]
    experiment["status"] = ExperimentStatus.CANCELLED
    experiment["updated_at"] = datetime.utcnow()
    
    return {"message": "Experiment cancelled", "experiment_id": experiment_id}

async def build_and_schedule_experiment(experiment_id: str, config: ExperimentConfig, start_immediately: bool):
    """Background task to build execution plan and optionally start experiment"""
    try:
        # Build execution plan
        runs = await plan_builder.build_plan(experiment_id, config)
        run_plans_store[experiment_id] = runs
        
        # Update experiment with run count
        experiment = experiments_store[experiment_id]
        experiment["total_runs"] = len(runs)
        experiment["status"] = ExperimentStatus.PENDING
        experiment["updated_at"] = datetime.utcnow()
        
        logger.info(f"Built execution plan for experiment {experiment_id} with {len(runs)} runs")
        
        # Start immediately if requested
        if start_immediately:
            await execute_experiment(experiment_id)
            
    except Exception as e:
        logger.error(f"Failed to build plan for experiment {experiment_id}: {e}")
        experiment = experiments_store[experiment_id]
        experiment["status"] = ExperimentStatus.FAILED
        experiment["updated_at"] = datetime.utcnow()

async def execute_experiment(experiment_id: str):
    """Execute experiment by scheduling all runs"""
    try:
        runs = run_plans_store.get(experiment_id, [])
        if not runs:
            logger.error(f"No runs found for experiment {experiment_id}")
            return
        
        # Schedule runs
        await run_scheduler.schedule_runs(runs)
        
        # Update experiment status
        experiment = experiments_store[experiment_id]
        experiment["status"] = ExperimentStatus.RUNNING
        experiment["updated_at"] = datetime.utcnow()
        
        logger.info(f"Started execution of experiment {experiment_id} with {len(runs)} runs")
        
    except Exception as e:
        logger.error(f"Failed to execute experiment {experiment_id}: {e}")
        experiment = experiments_store[experiment_id]
        experiment["status"] = ExperimentStatus.FAILED
        experiment["updated_at"] = datetime.utcnow()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)