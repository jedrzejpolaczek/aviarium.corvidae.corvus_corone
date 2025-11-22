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
    runs = relationship("Run", back_populates="experiment")

class Run(Base):
    __tablename__ = "runs"
    
    id = Column(String, primary_key=True)
    experiment_id = Column(String, ForeignKey("experiments.id"), nullable=False)
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
    metrics = relationship("Metric", back_populates="run")
    artifacts = relationship("Artifact", back_populates="run")

class Metric(Base):
    __tablename__ = "metrics"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    run_id = Column(String, ForeignKey("runs.id"), nullable=False)
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
    run_id = Column(String, ForeignKey("runs.id"), nullable=False)
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
    db.commit()
    db.refresh(db_experiment)
    
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
            tags=exp.tags.split(",") if exp.tags else []
        )
        responses.append(response)
    
    return responses

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
    db.commit()
    db.refresh(db_run)
    
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
    
    db.commit()
    db.refresh(db_run)
    
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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)