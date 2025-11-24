from fastapi import FastAPI, HTTPException, Depends, Query
from sqlalchemy import create_engine, Column, String, Float, Integer, DateTime, JSON, Text, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session, relationship
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime
import uuid
import os
import logging
from enum import Enum

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Experiment Tracking Service",
    description="Tracks experiments, runs, and metrics for HPO benchmarking",
    version="1.0.0"
)

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/corvus_corone")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class RunStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

# Database Models
class Experiment(Base):
    __tablename__ = "experiments"
    
    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(Text)
    goal_type = Column(String)
    created_by_user = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    config_json = Column(JSON)
    tags = Column(String)  # Comma-separated tags
    status = Column(String, default="pending")
    
    # Relationships
    runs = relationship("Run", back_populates="experiment", cascade="all, delete-orphan")

class Run(Base):
    __tablename__ = "runs"
    
    id = Column(String, primary_key=True)
    experiment_id = Column(String, ForeignKey("experiments.id", ondelete="CASCADE"), nullable=False)
    algorithm_version_id = Column(String, nullable=False)
    benchmark_instance_id = Column(String, nullable=False)
    seed = Column(Integer, nullable=False)
    status = Column(String, default="pending")
    start_time = Column(DateTime)
    end_time = Column(DateTime)
    resource_usage_json = Column(JSON)
    environment_snapshot_id = Column(String)
    error_message = Column(Text)
    config_json = Column(JSON)
    
    # Relationships
    experiment = relationship("Experiment", back_populates="runs")
    metrics = relationship("Metric", back_populates="run", cascade="all, delete-orphan")
    artifacts = relationship("Artifact", back_populates="run", cascade="all, delete-orphan")

class Metric(Base):
    __tablename__ = "metrics"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    run_id = Column(String, ForeignKey("runs.id", ondelete="CASCADE"), nullable=False)
    name = Column(String, nullable=False)  # e.g., "objective", "validation_error", "time_elapsed"
    value = Column(Float, nullable=False)
    step = Column(Integer, default=0)  # For multi-step metrics
    timestamp = Column(DateTime, default=datetime.utcnow)
    metadata_json = Column(JSON)  # Additional metric metadata
    
    # Relationships
    run = relationship("Run", back_populates="metrics")

class Artifact(Base):
    __tablename__ = "artifacts"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    run_id = Column(String, ForeignKey("runs.id", ondelete="CASCADE"), nullable=False)
    name = Column(String, nullable=False)  # e.g., "model.pkl", "convergence_plot.png"
    artifact_type = Column(String, nullable=False)  # e.g., "model", "plot", "log"
    storage_path = Column(String, nullable=False)  # Path in object storage
    size_bytes = Column(Integer)
    content_type = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    metadata_json = Column(JSON)
    
    # Relationships
    run = relationship("Run", back_populates="artifacts")

class Tag(Base):
    __tablename__ = "tags"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    entity_type = Column(String, nullable=False)  # "experiment", "run"
    entity_id = Column(String, nullable=False)
    tag_name = Column(String, nullable=False)
    tag_value = Column(String)  # Optional value for key-value tags
    created_at = Column(DateTime, default=datetime.utcnow)

# Create tables
Base.metadata.create_all(bind=engine)

# Pydantic models for API
class ExperimentCreate(BaseModel):
    id: Optional[str] = None
    name: str
    description: str = ""
    goal_type: Optional[str] = None
    created_by_user: str
    config_json: Dict[str, Any] = {}
    tags: List[str] = []

class ExperimentResponse(BaseModel):
    id: str
    name: str
    description: str
    goal_type: Optional[str]
    created_by_user: str
    created_at: datetime
    updated_at: datetime
    config_json: Dict[str, Any]
    tags: List[str]
    status: str
    total_runs: int = 0
    completed_runs: int = 0
    failed_runs: int = 0
    
    class Config:
        from_attributes = True

class RunCreate(BaseModel):
    run_id: Optional[str] = None
    experiment_id: str
    algorithm_version_id: str
    benchmark_instance_id: str
    seed: int
    status: RunStatus = RunStatus.PENDING
    config: Dict[str, Any] = {}

class RunUpdate(BaseModel):
    status: Optional[RunStatus] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    resource_usage: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None

class RunResponse(BaseModel):
    id: str
    experiment_id: str
    algorithm_version_id: str
    benchmark_instance_id: str
    seed: int
    status: str
    start_time: Optional[datetime]
    end_time: Optional[datetime]
    resource_usage_json: Optional[Dict[str, Any]]
    error_message: Optional[str]
    config_json: Dict[str, Any]
    
    class Config:
        from_attributes = True

class MetricCreate(BaseModel):
    run_id: str
    name: str
    value: float
    step: int = 0
    metadata: Dict[str, Any] = {}

class MetricResponse(BaseModel):
    id: str
    run_id: str
    name: str
    value: float
    step: int
    timestamp: datetime
    metadata_json: Optional[Dict[str, Any]]
    
    class Config:
        from_attributes = True

class ArtifactCreate(BaseModel):
    run_id: str
    name: str
    artifact_type: str
    storage_path: str
    size_bytes: Optional[int] = None
    content_type: Optional[str] = None
    metadata: Dict[str, Any] = {}

class ArtifactResponse(BaseModel):
    id: str
    run_id: str
    name: str
    artifact_type: str
    storage_path: str
    size_bytes: Optional[int]
    content_type: Optional[str]
    created_at: datetime
    metadata_json: Optional[Dict[str, Any]]
    
    class Config:
        from_attributes = True

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "experiment-tracking"}

# Experiment endpoints
@app.post("/api/tracking/experiments", response_model=ExperimentResponse)
async def create_experiment(experiment: ExperimentCreate, db: Session = Depends(get_db)):
    """Create new experiment"""
    db_experiment = Experiment(
        id=experiment.id or str(uuid.uuid4()),
        name=experiment.name,
        description=experiment.description,
        goal_type=experiment.goal_type,
        created_by_user=experiment.created_by_user,
        config_json=experiment.config_json,
        tags=",".join(experiment.tags)
    )
    
    db.add(db_experiment)
    try:
        db.commit()
        db.refresh(db_experiment)
        logger.info(f"Created experiment {db_experiment.id} in database")
    except Exception as e:
        logger.error(f"Failed to commit experiment {db_experiment.id}: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to create experiment: {e}")
    
    # Convert to response model
    response = ExperimentResponse(
        id=db_experiment.id,
        name=db_experiment.name,
        description=db_experiment.description,
        goal_type=db_experiment.goal_type,
        created_by_user=db_experiment.created_by_user,
        created_at=db_experiment.created_at,
        updated_at=db_experiment.updated_at,
        config_json=db_experiment.config_json,
        status=db_experiment.status,
        tags=db_experiment.tags.split(",") if db_experiment.tags else []
    )
    
    return response

@app.get("/api/tracking/experiments/{experiment_id}", response_model=ExperimentResponse)
async def get_experiment(experiment_id: str, db: Session = Depends(get_db)):
    """Get experiment by ID"""
    db_experiment = db.query(Experiment).filter(Experiment.id == experiment_id).first()
    if not db_experiment:
        raise HTTPException(status_code=404, detail="Experiment not found")
    
    # Get run statistics
    total_runs = db.query(Run).filter(Run.experiment_id == experiment_id).count()
    completed_runs = db.query(Run).filter(
        Run.experiment_id == experiment_id,
        Run.status == "completed"
    ).count()
    failed_runs = db.query(Run).filter(
        Run.experiment_id == experiment_id,
        Run.status == "failed"
    ).count()
    
    response = ExperimentResponse(
        id=db_experiment.id,
        name=db_experiment.name,
        description=db_experiment.description,
        goal_type=db_experiment.goal_type,
        created_by_user=db_experiment.created_by_user,
        created_at=db_experiment.created_at,
        updated_at=db_experiment.updated_at,
        config_json=db_experiment.config_json,
        status=db_experiment.status,
        tags=db_experiment.tags.split(",") if db_experiment.tags else [],
        total_runs=total_runs,
        completed_runs=completed_runs,
        failed_runs=failed_runs
    )
    
    return response

@app.put("/api/tracking/experiments/{experiment_id}", response_model=ExperimentResponse)
async def update_experiment(experiment_id: str, experiment_update: dict, db: Session = Depends(get_db)):
    """Update experiment (e.g., status)"""
    db_experiment = db.query(Experiment).filter(Experiment.id == experiment_id).first()
    if not db_experiment:
        raise HTTPException(status_code=404, detail="Experiment not found")
    
    # Update fields
    updated = False
    if "status" in experiment_update:
        old_status = db_experiment.status
        db_experiment.status = experiment_update["status"]
        logger.info(f"Updated experiment {experiment_id} status: {old_status} -> {experiment_update['status']}")
        updated = True
    
    if "name" in experiment_update:
        db_experiment.name = experiment_update["name"]
        updated = True
        
    if "description" in experiment_update:
        db_experiment.description = experiment_update["description"]
        updated = True
    
    if updated:
        db_experiment.updated_at = datetime.utcnow()
        try:
            db.commit()
            db.refresh(db_experiment)
        except Exception as e:
            logger.error(f"Failed to update experiment {experiment_id}: {e}")
            db.rollback()
            raise HTTPException(status_code=500, detail=f"Failed to update experiment: {e}")
    
    # Return updated experiment with run statistics
    return await get_experiment(experiment_id, db)

@app.get("/api/tracking/experiments", response_model=List[ExperimentResponse])
async def list_experiments(
    limit: int = Query(50, le=200),
    offset: int = Query(0, ge=0),
    status: Optional[str] = None,
    tags: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """List experiments with filtering"""
    query = db.query(Experiment)
    
    if status:
        query = query.filter(Experiment.status == status)
    
    if tags:
        # Simple tag filtering (contains)
        query = query.filter(Experiment.tags.contains(tags))
    
    experiments = query.order_by(Experiment.created_at.desc()).offset(offset).limit(limit).all()
    
    responses = []
    for exp in experiments:
        # Calculate run statistics for each experiment
        total_runs = db.query(Run).filter(Run.experiment_id == exp.id).count()
        completed_runs = db.query(Run).filter(
            Run.experiment_id == exp.id,
            Run.status == "completed"
        ).count()
        failed_runs = db.query(Run).filter(
            Run.experiment_id == exp.id,
            Run.status == "failed"
        ).count()
        
        response = ExperimentResponse(
            id=exp.id,
            name=exp.name,
            description=exp.description,
            goal_type=exp.goal_type,
            created_by_user=exp.created_by_user,
            created_at=exp.created_at,
            updated_at=exp.updated_at,
            config_json=exp.config_json,
            status=exp.status,
            tags=exp.tags.split(",") if exp.tags else [],
            total_runs=total_runs,
            completed_runs=completed_runs,
            failed_runs=failed_runs
        )
        responses.append(response)
    
    return responses

# Helper function to update experiment status
def update_experiment_status(experiment_id: str, db: Session):
    """Update experiment status based on run completion"""
    experiment = db.query(Experiment).filter(Experiment.id == experiment_id).first()
    if not experiment:
        return
    
    # Get run statistics
    total_runs = db.query(Run).filter(Run.experiment_id == experiment_id).count()
    completed_runs = db.query(Run).filter(
        Run.experiment_id == experiment_id,
        Run.status == "completed"
    ).count()
    failed_runs = db.query(Run).filter(
        Run.experiment_id == experiment_id,
        Run.status == "failed"
    ).count()
    running_runs = db.query(Run).filter(
        Run.experiment_id == experiment_id,
        Run.status == "running"
    ).count()
    
    # Update status based on run states
    old_status = experiment.status
    if total_runs == 0:
        new_status = "pending"
    elif running_runs > 0:
        new_status = "running"
    elif completed_runs + failed_runs == total_runs:
        # All runs finished
        if failed_runs == 0:
            new_status = "completed"
        elif completed_runs == 0:
            new_status = "failed"
        else:
            new_status = "completed_with_failures"
    else:
        new_status = "running"
    
    # Update if status changed
    if old_status != new_status:
        experiment.status = new_status
        experiment.updated_at = datetime.utcnow()
        db.commit()
        logger.info(f"Updated experiment {experiment_id} status: {old_status} -> {new_status}")

# Run endpoints
@app.post("/api/tracking/runs", response_model=RunResponse)
async def create_run(run: RunCreate, db: Session = Depends(get_db)):
    """Create new run"""
    db_run = Run(
        id=run.run_id or str(uuid.uuid4()),
        experiment_id=run.experiment_id,
        algorithm_version_id=run.algorithm_version_id,
        benchmark_instance_id=run.benchmark_instance_id,
        seed=run.seed,
        status=run.status,
        config_json=run.config
    )
    
    db.add(db_run)
    try:
        db.commit()
        db.refresh(db_run)
        logger.info(f"Created run {db_run.id} for experiment {run.experiment_id} in database")
        
        # Update experiment status
        update_experiment_status(run.experiment_id, db)
    except Exception as e:
        logger.error(f"Failed to commit run {db_run.id}: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to create run: {e}")
    
    return RunResponse.from_orm(db_run)

@app.get("/api/tracking/runs/{run_id}", response_model=RunResponse)
async def get_run(run_id: str, db: Session = Depends(get_db)):
    """Get run by ID"""
    db_run = db.query(Run).filter(Run.id == run_id).first()
    if not db_run:
        raise HTTPException(status_code=404, detail="Run not found")
    
    return RunResponse.from_orm(db_run)

@app.put("/api/tracking/runs/{run_id}", response_model=RunResponse)
async def update_run(run_id: str, run_update: RunUpdate, db: Session = Depends(get_db)):
    """Update run status and metadata"""
    db_run = db.query(Run).filter(Run.id == run_id).first()
    if not db_run:
        raise HTTPException(status_code=404, detail="Run not found")
    
    # Update fields
    if run_update.status:
        db_run.status = run_update.status
    if run_update.start_time:
        db_run.start_time = run_update.start_time
    if run_update.end_time:
        db_run.end_time = run_update.end_time
    if run_update.resource_usage:
        db_run.resource_usage_json = run_update.resource_usage
    if run_update.error_message:
        db_run.error_message = run_update.error_message
    
    try:
        db.commit()
        db.refresh(db_run)
        logger.info(f"Updated run {db_run.id} with status {run_update.status}")
        
        # Update experiment status when run status changes
        if run_update.status:
            update_experiment_status(db_run.experiment_id, db)
    except Exception as e:
        logger.error(f"Failed to update run {db_run.id}: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to update run: {e}")
    
    return RunResponse.from_orm(db_run)

@app.get("/api/tracking/experiments/{experiment_id}/runs", response_model=List[RunResponse])
async def get_experiment_runs(
    experiment_id: str,
    limit: int = Query(100, le=500),
    offset: int = Query(0, ge=0),
    status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get runs for experiment"""
    query = db.query(Run).filter(Run.experiment_id == experiment_id)
    
    if status:
        query = query.filter(Run.status == status)
    
    runs = query.order_by(Run.start_time.desc().nullslast()).offset(offset).limit(limit).all()
    
    return [RunResponse.from_orm(run) for run in runs]

# Metric endpoints
@app.post("/api/tracking/metrics", response_model=MetricResponse)
async def log_metric(metric: MetricCreate, db: Session = Depends(get_db)):
    """Log metric for run"""
    # Verify run exists
    db_run = db.query(Run).filter(Run.id == metric.run_id).first()
    if not db_run:
        raise HTTPException(status_code=404, detail="Run not found")
    
    db_metric = Metric(
        run_id=metric.run_id,
        name=metric.name,
        value=metric.value,
        step=metric.step,
        metadata_json=metric.metadata
    )
    
    db.add(db_metric)
    db.commit()
    db.refresh(db_metric)
    
    return MetricResponse.from_orm(db_metric)

@app.post("/api/tracking/metrics/batch")
async def log_metrics_batch(metrics: List[MetricCreate], db: Session = Depends(get_db)):
    """Log multiple metrics in batch"""
    db_metrics = []
    for metric in metrics:
        db_metric = Metric(
            run_id=metric.run_id,
            name=metric.name,
            value=metric.value,
            step=metric.step,
            metadata_json=metric.metadata
        )
        db_metrics.append(db_metric)
    
    db.add_all(db_metrics)
    db.commit()
    
    return {"message": f"Logged {len(metrics)} metrics"}

@app.get("/api/tracking/runs/{run_id}/metrics", response_model=List[MetricResponse])
async def get_run_metrics(run_id: str, db: Session = Depends(get_db)):
    """Get all metrics for run"""
    metrics = db.query(Metric).filter(Metric.run_id == run_id).order_by(Metric.timestamp).all()
    return [MetricResponse.from_orm(metric) for metric in metrics]

@app.get("/api/tracking/experiments/{experiment_id}/metrics", response_model=List[MetricResponse])
async def get_experiment_metrics(experiment_id: str, db: Session = Depends(get_db)):
    """Get all metrics for experiment"""
    # Get all metrics for runs belonging to this experiment
    metrics = db.query(Metric).join(Run).filter(
        Run.experiment_id == experiment_id
    ).order_by(Metric.timestamp).all()
    return [MetricResponse.from_orm(metric) for metric in metrics]

# Artifact endpoints
@app.post("/api/tracking/artifacts", response_model=ArtifactResponse)
async def create_artifact(artifact: ArtifactCreate, db: Session = Depends(get_db)):
    """Register artifact for run"""
    # Verify run exists
    db_run = db.query(Run).filter(Run.id == artifact.run_id).first()
    if not db_run:
        raise HTTPException(status_code=404, detail="Run not found")
    
    db_artifact = Artifact(
        run_id=artifact.run_id,
        name=artifact.name,
        artifact_type=artifact.artifact_type,
        storage_path=artifact.storage_path,
        size_bytes=artifact.size_bytes,
        content_type=artifact.content_type,
        metadata_json=artifact.metadata
    )
    
    db.add(db_artifact)
    db.commit()
    db.refresh(db_artifact)
    
    return ArtifactResponse.from_orm(db_artifact)

@app.get("/api/tracking/runs/{run_id}/artifacts", response_model=List[ArtifactResponse])
async def get_run_artifacts(run_id: str, db: Session = Depends(get_db)):
    """Get all artifacts for run"""
    artifacts = db.query(Artifact).filter(Artifact.run_id == run_id).order_by(Artifact.created_at).all()
    return [ArtifactResponse.from_orm(artifact) for artifact in artifacts]

@app.delete("/api/tracking/experiments/{experiment_id}")
async def delete_experiment(experiment_id: str, db: Session = Depends(get_db)):
    """Delete experiment and all associated data (runs, metrics, artifacts)"""
    # Check if experiment exists
    experiment = db.query(Experiment).filter(Experiment.id == experiment_id).first()
    if not experiment:
        raise HTTPException(status_code=404, detail="Experiment not found")
    
    try:
        # Delete will cascade due to foreign key constraints
        # This will automatically delete all runs, metrics, and artifacts associated with the experiment
        db.delete(experiment)
        db.commit()
        
        logger.info(f"Successfully deleted experiment {experiment_id} and all associated data")
        return {"message": "Experiment and all associated data deleted successfully", "experiment_id": experiment_id}
        
    except Exception as e:
        db.rollback()
        logger.error(f"Failed to delete experiment {experiment_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to delete experiment: {str(e)}")

@app.get("/api/experiments/{experiment_id}/runs")
async def get_experiment_runs(experiment_id: str, db: Session = Depends(get_db)):
    """Get all runs for a specific experiment"""
    logger.info(f"Getting runs for experiment {experiment_id}")
    
    # Check if experiment exists
    experiment = db.query(Experiment).filter(Experiment.id == experiment_id).first()
    if not experiment:
        raise HTTPException(status_code=404, detail="Experiment not found")
    
    # Get all runs for the experiment
    runs = db.query(Run).filter(Run.experiment_id == experiment_id).all()
    
    return [
        {
            "id": run.id,
            "experiment_id": run.experiment_id,
            "algorithm_id": run.algorithm_id,
            "benchmark_id": run.benchmark_id,
            "status": run.status,
            "best_score": run.best_score,
            "runtime_seconds": run.runtime_seconds,
            "started_at": run.started_at,
            "completed_at": run.completed_at,
            "config": run.config_json,
            "metadata": run.metadata_json
        }
        for run in runs
    ]

@app.get("/api/experiments/{experiment_id}/metrics")
async def get_experiment_metrics(experiment_id: str, db: Session = Depends(get_db)):
    """Get all metrics for a specific experiment"""
    logger.info(f"Getting metrics for experiment {experiment_id}")
    
    # Check if experiment exists
    experiment = db.query(Experiment).filter(Experiment.id == experiment_id).first()
    if not experiment:
        raise HTTPException(status_code=404, detail="Experiment not found")
    
    # Get all metrics for all runs in the experiment
    metrics = db.query(Metric).join(Run).filter(Run.experiment_id == experiment_id).all()
    
    return [
        {
            "id": metric.id,
            "run_id": metric.run_id,
            "name": metric.name,
            "value": metric.value,
            "step": metric.step,
            "timestamp": metric.timestamp,
            "metadata": metric.metadata_json
        }
        for metric in metrics
    ]

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)