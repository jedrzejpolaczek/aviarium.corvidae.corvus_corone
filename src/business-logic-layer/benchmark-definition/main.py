from fastapi import FastAPI, HTTPException, Depends, Query
from sqlalchemy import create_engine, Column, String, Float, Integer, DateTime, JSON, Text, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
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
    title="Benchmark Definition Service",
    description="Manages benchmark definitions, problem instances, and datasets",
    version="1.0.0"
)

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/corvus_corone")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class ProblemType(str, Enum):
    CLASSIFICATION = "classification"
    REGRESSION = "regression"
    CLUSTERING = "clustering"
    RANKING = "ranking"
    MULTI_OBJECTIVE = "multi_objective"

# Database Models
class Benchmark(Base):
    __tablename__ = "benchmarks"
    
    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(Text)
    problem_type = Column(String, nullable=False)
    canonical_version = Column(String, default="1.0.0")
    author = Column(String)
    publication_id = Column(String)  # Reference to publication
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    metadata_json = Column(JSON)
    is_active = Column(Boolean, default=True)

class BenchmarkInstance(Base):
    __tablename__ = "benchmark_instances"
    
    id = Column(String, primary_key=True)
    benchmark_id = Column(String, nullable=False)
    name = Column(String, nullable=False)
    dataset_ref = Column(String, nullable=False)  # Reference to dataset in object storage
    config_json = Column(JSON)  # Instance-specific configuration
    best_known_value = Column(Float)  # Best known objective value (if available)
    parameter_space_json = Column(JSON, nullable=False)  # HPO parameter space definition
    evaluation_budget = Column(Integer, default=100)  # Default evaluation budget
    time_limit_seconds = Column(Integer)  # Optional time limit
    difficulty_level = Column(String)  # easy, medium, hard
    created_at = Column(DateTime, default=datetime.utcnow)
    metadata_json = Column(JSON)
    is_active = Column(Boolean, default=True)

# Create tables
Base.metadata.create_all(bind=engine)

# Pydantic models for API
class BenchmarkCreate(BaseModel):
    id: Optional[str] = None
    name: str
    description: str = ""
    problem_type: ProblemType
    author: str = ""
    publication_id: Optional[str] = None
    metadata: Dict[str, Any] = {}

class BenchmarkResponse(BaseModel):
    id: str
    name: str
    description: str
    problem_type: str
    canonical_version: str
    author: str
    publication_id: Optional[str]
    created_at: datetime
    updated_at: datetime
    metadata_json: Dict[str, Any]
    is_active: bool
    instance_count: int = 0
    
    class Config:
        from_attributes = True

class BenchmarkInstanceCreate(BaseModel):
    id: Optional[str] = None
    benchmark_id: str
    name: str
    dataset_ref: str
    config: Dict[str, Any] = {}
    best_known_value: Optional[float] = None
    parameter_space: Dict[str, Any]
    evaluation_budget: int = 100
    time_limit_seconds: Optional[int] = None
    difficulty_level: str = "medium"
    metadata: Dict[str, Any] = {}

class BenchmarkInstanceResponse(BaseModel):
    id: str
    benchmark_id: str
    name: str
    dataset_ref: str
    config_json: Dict[str, Any]
    best_known_value: Optional[float]
    parameter_space_json: Dict[str, Any]
    evaluation_budget: int
    time_limit_seconds: Optional[int]
    difficulty_level: str
    created_at: datetime
    metadata_json: Dict[str, Any]
    is_active: bool
    
    class Config:
        from_attributes = True

class DatasetInfo(BaseModel):
    """Information about dataset for HPO execution"""
    dataset_id: str
    parameter_space: Dict[str, Any]
    objective_function: Dict[str, Any]
    best_known_value: Optional[float]
    evaluation_budget: int
    metadata: Dict[str, Any]

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "benchmark-definition"}

# Benchmark endpoints
@app.post("/api/benchmarks", response_model=BenchmarkResponse)
async def create_benchmark(benchmark: BenchmarkCreate, db: Session = Depends(get_db)):
    """Create new benchmark"""
    # Check if benchmark with same name already exists
    existing = db.query(Benchmark).filter(Benchmark.name == benchmark.name).first()
    if existing:
        raise HTTPException(status_code=400, detail="Benchmark with this name already exists")
    
    db_benchmark = Benchmark(
        id=benchmark.id or str(uuid.uuid4()),
        name=benchmark.name,
        description=benchmark.description,
        problem_type=benchmark.problem_type,
        author=benchmark.author,
        publication_id=benchmark.publication_id,
        metadata_json=benchmark.metadata
    )
    
    db.add(db_benchmark)
    db.commit()
    db.refresh(db_benchmark)
    
    # Get instance count
    instance_count = db.query(BenchmarkInstance).filter(
        BenchmarkInstance.benchmark_id == db_benchmark.id
    ).count()
    
    response = BenchmarkResponse.from_orm(db_benchmark)
    response.instance_count = instance_count
    
    return response

@app.get("/api/benchmarks/{benchmark_id}", response_model=BenchmarkResponse)
async def get_benchmark(benchmark_id: str, db: Session = Depends(get_db)):
    """Get benchmark by ID"""
    db_benchmark = db.query(Benchmark).filter(Benchmark.id == benchmark_id).first()
    if not db_benchmark:
        raise HTTPException(status_code=404, detail="Benchmark not found")
    
    # Get instance count
    instance_count = db.query(BenchmarkInstance).filter(
        BenchmarkInstance.benchmark_id == benchmark_id
    ).count()
    
    response = BenchmarkResponse.from_orm(db_benchmark)
    response.instance_count = instance_count
    
    return response

@app.get("/api/benchmarks", response_model=List[BenchmarkResponse])
async def list_benchmarks(
    limit: int = Query(50, le=200),
    offset: int = Query(0, ge=0),
    problem_type: Optional[ProblemType] = None,
    active_only: bool = Query(True),
    db: Session = Depends(get_db)
):
    """List benchmarks with filtering"""
    query = db.query(Benchmark)
    
    if active_only:
        query = query.filter(Benchmark.is_active == True)
    
    if problem_type:
        query = query.filter(Benchmark.problem_type == problem_type)
    
    benchmarks = query.order_by(Benchmark.created_at.desc()).offset(offset).limit(limit).all()
    
    responses = []
    for benchmark in benchmarks:
        instance_count = db.query(BenchmarkInstance).filter(
            BenchmarkInstance.benchmark_id == benchmark.id
        ).count()
        
        response = BenchmarkResponse.from_orm(benchmark)
        response.instance_count = instance_count
        responses.append(response)
    
    return responses

# Benchmark Instance endpoints
@app.post("/api/benchmarks/{benchmark_id}/instances", response_model=BenchmarkInstanceResponse)
async def create_benchmark_instance(
    benchmark_id: str, 
    instance: BenchmarkInstanceCreate, 
    db: Session = Depends(get_db)
):
    """Create new benchmark instance"""
    # Verify benchmark exists
    db_benchmark = db.query(Benchmark).filter(Benchmark.id == benchmark_id).first()
    if not db_benchmark:
        raise HTTPException(status_code=404, detail="Benchmark not found")
    
    # Override benchmark_id from URL
    instance.benchmark_id = benchmark_id
    
    db_instance = BenchmarkInstance(
        id=instance.id or str(uuid.uuid4()),
        benchmark_id=instance.benchmark_id,
        name=instance.name,
        dataset_ref=instance.dataset_ref,
        config_json=instance.config,
        best_known_value=instance.best_known_value,
        parameter_space_json=instance.parameter_space,
        evaluation_budget=instance.evaluation_budget,
        time_limit_seconds=instance.time_limit_seconds,
        difficulty_level=instance.difficulty_level,
        metadata_json=instance.metadata
    )
    
    db.add(db_instance)
    db.commit()
    db.refresh(db_instance)
    
    return BenchmarkInstanceResponse.from_orm(db_instance)

@app.get("/api/benchmarks/{benchmark_id}/instances", response_model=List[BenchmarkInstanceResponse])
async def get_benchmark_instances(
    benchmark_id: str,
    limit: int = Query(100, le=500),
    offset: int = Query(0, ge=0),
    active_only: bool = Query(True),
    db: Session = Depends(get_db)
):
    """Get instances for benchmark"""
    # Verify benchmark exists
    db_benchmark = db.query(Benchmark).filter(Benchmark.id == benchmark_id).first()
    if not db_benchmark:
        raise HTTPException(status_code=404, detail="Benchmark not found")
    
    query = db.query(BenchmarkInstance).filter(BenchmarkInstance.benchmark_id == benchmark_id)
    
    if active_only:
        query = query.filter(BenchmarkInstance.is_active == True)
    
    instances = query.order_by(BenchmarkInstance.created_at).offset(offset).limit(limit).all()
    
    return [BenchmarkInstanceResponse.from_orm(instance) for instance in instances]

@app.get("/api/benchmarks/{benchmark_id}/instances/{instance_id}", response_model=BenchmarkInstanceResponse)
async def get_benchmark_instance(
    benchmark_id: str, 
    instance_id: str, 
    db: Session = Depends(get_db)
):
    """Get specific benchmark instance"""
    db_instance = db.query(BenchmarkInstance).filter(
        BenchmarkInstance.id == instance_id,
        BenchmarkInstance.benchmark_id == benchmark_id
    ).first()
    
    if not db_instance:
        raise HTTPException(status_code=404, detail="Benchmark instance not found")
    
    return BenchmarkInstanceResponse.from_orm(db_instance)

@app.get("/api/benchmarks/{benchmark_id}/instances/{instance_id}/data", response_model=DatasetInfo)
async def get_benchmark_instance_data(
    benchmark_id: str, 
    instance_id: str, 
    db: Session = Depends(get_db)
):
    """Get benchmark instance data for HPO execution"""
    db_instance = db.query(BenchmarkInstance).filter(
        BenchmarkInstance.id == instance_id,
        BenchmarkInstance.benchmark_id == benchmark_id
    ).first()
    
    if not db_instance:
        raise HTTPException(status_code=404, detail="Benchmark instance not found")
    
    # Return dataset information for HPO execution
    return DatasetInfo(
        dataset_id=instance_id,
        parameter_space=db_instance.parameter_space_json,
        objective_function={
            "type": "ml_model_training",
            "metric": "validation_error",
            "direction": "minimize"
        },
        best_known_value=db_instance.best_known_value,
        evaluation_budget=db_instance.evaluation_budget,
        metadata=db_instance.metadata_json or {}
    )

# Seed some default benchmarks
@app.on_event("startup")
async def seed_default_benchmarks():
    """Seed default benchmarks on startup"""
    db = SessionLocal()
    try:
        # Check if we already have benchmarks
        existing_count = db.query(Benchmark).count()
        if existing_count > 0:
            logger.info(f"Found {existing_count} existing benchmarks, skipping seed")
            return
        
        logger.info("Seeding default benchmarks...")
        
        # UCI Wine Dataset benchmark
        wine_benchmark = Benchmark(
            id="uci_wine",
            name="UCI Wine Classification",
            description="Wine recognition dataset for hyperparameter optimization of classification algorithms",
            problem_type="classification",
            author="UCI ML Repository",
            metadata_json={
                "features": 13,
                "samples": 178,
                "classes": 3,
                "url": "https://archive.ics.uci.edu/ml/datasets/wine"
            }
        )
        db.add(wine_benchmark)
        
        # Wine instance with hyperparameter space for SVM
        wine_instance = BenchmarkInstance(
            id="uci_wine_svm",
            benchmark_id="uci_wine",
            name="Wine SVM Hyperparameter Optimization",
            dataset_ref="datasets/uci_wine.csv",
            parameter_space_json={
                "C": {"type": "float", "min": 0.001, "max": 1000.0, "log": True},
                "gamma": {"type": "float", "min": 0.001, "max": 1.0, "log": True},
                "kernel": {"type": "categorical", "choices": ["rbf", "poly", "sigmoid"]}
            },
            evaluation_budget=50,
            difficulty_level="easy",
            metadata_json={"algorithm": "SVM", "metric": "accuracy"}
        )
        db.add(wine_instance)
        
        # Synthetic 2D function benchmark
        synthetic_benchmark = Benchmark(
            id="synthetic_2d",
            name="Synthetic 2D Function",
            description="Simple 2D synthetic optimization function for testing HPO algorithms",
            problem_type="regression",
            author="Corvus Corone",
            metadata_json={
                "dimensions": 2,
                "function_type": "Rosenbrock-like"
            }
        )
        db.add(synthetic_benchmark)
        
        # Synthetic instance
        synthetic_instance = BenchmarkInstance(
            id="synthetic_2d_basic",
            benchmark_id="synthetic_2d",
            name="Basic 2D Optimization",
            dataset_ref="synthetic/rosenbrock_2d",
            parameter_space_json={
                "x": {"type": "float", "min": -5.0, "max": 5.0},
                "y": {"type": "float", "min": -5.0, "max": 5.0}
            },
            best_known_value=0.0,
            evaluation_budget=100,
            difficulty_level="easy",
            metadata_json={"global_minimum": [1.0, 1.0]}
        )
        db.add(synthetic_instance)
        
        db.commit()
        logger.info("Default benchmarks seeded successfully")
        
    except Exception as e:
        logger.error(f"Failed to seed benchmarks: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8003)