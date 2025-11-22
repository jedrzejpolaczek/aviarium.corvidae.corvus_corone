from fastapi import FastAPI, HTTPException, Depends, Query
from sqlalchemy import create_engine, Column, String, Float, Integer, DateTime, JSON, Text, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from pydantic import BaseModel, Field, field_validator
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
    title="Algorithm Registry Service",
    description="Manages HPO algorithm catalog, versions, and metadata",
    version="1.0.0"
)

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/corvus_corone")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class AlgorithmType(str, Enum):
    RANDOM_SEARCH = "random_search"
    GRID_SEARCH = "grid_search"
    BAYESIAN_OPTIMIZATION = "bayesian_optimization"
    EVOLUTIONARY = "evolutionary"
    GRADIENT_BASED = "gradient_based"
    MULTI_OBJECTIVE = "multi_objective"
    NEURAL_ARCHITECTURE_SEARCH = "neural_architecture_search"
    CUSTOM = "custom"

class AlgorithmStatus(str, Enum):
    ACTIVE = "active"
    DEPRECATED = "deprecated"
    EXPERIMENTAL = "experimental"
    DISABLED = "disabled"

# Database Models
class Algorithm(Base):
    __tablename__ = "algorithms"
    
    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    algorithm_type = Column(String, nullable=False)
    is_builtin = Column(Boolean, default=True)
    description = Column(Text)
    author = Column(String)
    primary_publication_id = Column(String)  # Reference to main publication
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    metadata_json = Column(JSON)
    tags = Column(String)  # Comma-separated tags
    status = Column(String, default="active")

class AlgorithmVersion(Base):
    __tablename__ = "algorithm_versions"
    
    id = Column(String, primary_key=True)
    algorithm_id = Column(String, nullable=False)
    version = Column(String, nullable=False)  # Semantic version
    plugin_location = Column(String)  # Container image or plugin path
    sdk_version = Column(String)  # SDK version used
    status = Column(String, default="active")
    release_notes = Column(Text)
    parameter_schema_json = Column(JSON)  # JSON schema for algorithm parameters
    requirements_json = Column(JSON)  # System requirements (GPU, memory, etc.)
    performance_characteristics_json = Column(JSON)  # Expected performance info
    created_at = Column(DateTime, default=datetime.utcnow)
    created_by = Column(String)
    download_count = Column(Integer, default=0)
    metadata_json = Column(JSON)

# Create tables
Base.metadata.create_all(bind=engine)

# Pydantic models for API
class AlgorithmCreate(BaseModel):
    id: Optional[str] = None
    name: str
    algorithm_type: AlgorithmType
    is_builtin: bool = True
    description: str = ""
    author: str = ""
    primary_publication_id: Optional[str] = None
    metadata: Dict[str, Any] = {}
    tags: List[str] = []

class AlgorithmResponse(BaseModel):
    id: str
    name: str
    algorithm_type: str
    is_builtin: bool
    description: str
    author: str
    primary_publication_id: Optional[str]
    created_at: datetime
    updated_at: datetime
    metadata_json: Dict[str, Any]
    tags: List[str]
    status: str
    version_count: int = 0
    latest_version: Optional[str] = None
    
    class Config:
        from_attributes = True

class AlgorithmVersionCreate(BaseModel):
    algorithm_id: str
    version: str
    plugin_location: Optional[str] = None
    sdk_version: str = "1.0.0"
    release_notes: str = ""
    parameter_schema: Dict[str, Any] = {}
    requirements: Dict[str, Any] = {}
    performance_characteristics: Dict[str, Any] = {}
    created_by: str = ""
    metadata: Dict[str, Any] = {}

class AlgorithmVersionResponse(BaseModel):
    id: str
    algorithm_id: str
    version: str
    plugin_location: Optional[str] = None
    sdk_version: str
    status: str
    release_notes: str
    parameter_schema_json: Dict[str, Any] = {}
    requirements_json: Dict[str, Any] = {}
    performance_characteristics_json: Dict[str, Any] = {}
    created_at: datetime
    created_by: str
    download_count: int
    metadata_json: Dict[str, Any] = {}
    
    @field_validator('parameter_schema_json', 'requirements_json', 'performance_characteristics_json', 'metadata_json', mode='before')
    @classmethod
    def validate_json_fields(cls, v):
        return v if v is not None else {}
    
    class Config:
        from_attributes = True

class AlgorithmCompatibilityCheck(BaseModel):
    algorithm_id: str
    version: str
    benchmark_requirements: Dict[str, Any]
    system_resources: Dict[str, Any]

class CompatibilityResult(BaseModel):
    compatible: bool
    warnings: List[str] = []
    errors: List[str] = []
    recommendations: List[str] = []

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "algorithm-registry"}

# Algorithm endpoints
@app.post("/api/algorithms", response_model=AlgorithmResponse)
async def create_algorithm(algorithm: AlgorithmCreate, db: Session = Depends(get_db)):
    """Create new algorithm"""
    # Check if algorithm with same name already exists
    existing = db.query(Algorithm).filter(Algorithm.name == algorithm.name).first()
    if existing:
        raise HTTPException(status_code=400, detail="Algorithm with this name already exists")
    
    db_algorithm = Algorithm(
        id=algorithm.id or str(uuid.uuid4()),
        name=algorithm.name,
        algorithm_type=algorithm.algorithm_type,
        is_builtin=algorithm.is_builtin,
        description=algorithm.description,
        author=algorithm.author,
        primary_publication_id=algorithm.primary_publication_id,
        metadata_json=algorithm.metadata,
        tags=",".join(algorithm.tags)
    )
    
    db.add(db_algorithm)
    db.commit()
    db.refresh(db_algorithm)
    
    # Get version info
    version_count = db.query(AlgorithmVersion).filter(
        AlgorithmVersion.algorithm_id == db_algorithm.id
    ).count()
    
    latest_version_obj = db.query(AlgorithmVersion).filter(
        AlgorithmVersion.algorithm_id == db_algorithm.id
    ).order_by(AlgorithmVersion.created_at.desc()).first()
    
    response = AlgorithmResponse(
        id=db_algorithm.id,
        name=db_algorithm.name,
        algorithm_type=db_algorithm.algorithm_type,
        is_builtin=db_algorithm.is_builtin,
        description=db_algorithm.description,
        author=db_algorithm.author,
        primary_publication_id=db_algorithm.primary_publication_id,
        created_at=db_algorithm.created_at,
        updated_at=db_algorithm.updated_at,
        metadata_json=db_algorithm.metadata_json or {},
        tags=db_algorithm.tags.split(",") if db_algorithm.tags else [],
        status=db_algorithm.status,
        version_count=version_count,
        latest_version=latest_version_obj.version if latest_version_obj else None
    )
    
    return response

@app.get("/api/algorithms/{algorithm_id}", response_model=AlgorithmResponse)
async def get_algorithm(algorithm_id: str, db: Session = Depends(get_db)):
    """Get algorithm by ID"""
    db_algorithm = db.query(Algorithm).filter(Algorithm.id == algorithm_id).first()
    if not db_algorithm:
        raise HTTPException(status_code=404, detail="Algorithm not found")
    
    # Get version info
    version_count = db.query(AlgorithmVersion).filter(
        AlgorithmVersion.algorithm_id == algorithm_id
    ).count()
    
    latest_version_obj = db.query(AlgorithmVersion).filter(
        AlgorithmVersion.algorithm_id == algorithm_id
    ).order_by(AlgorithmVersion.created_at.desc()).first()
    
    response = AlgorithmResponse(
        id=db_algorithm.id,
        name=db_algorithm.name,
        algorithm_type=db_algorithm.algorithm_type,
        is_builtin=db_algorithm.is_builtin,
        description=db_algorithm.description,
        author=db_algorithm.author,
        primary_publication_id=db_algorithm.primary_publication_id,
        created_at=db_algorithm.created_at,
        updated_at=db_algorithm.updated_at,
        metadata_json=db_algorithm.metadata_json or {},
        tags=db_algorithm.tags.split(",") if db_algorithm.tags else [],
        status=db_algorithm.status,
        version_count=version_count,
        latest_version=latest_version_obj.version if latest_version_obj else None
    )
    
    return response

@app.get("/api/algorithms", response_model=List[AlgorithmResponse])
async def list_algorithms(
    limit: int = Query(50, le=200),
    offset: int = Query(0, ge=0),
    algorithm_type: Optional[AlgorithmType] = None,
    is_builtin: Optional[bool] = None,
    status: Optional[AlgorithmStatus] = None,
    tags: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """List algorithms with filtering"""
    query = db.query(Algorithm)
    
    if algorithm_type:
        query = query.filter(Algorithm.algorithm_type == algorithm_type)
    
    if is_builtin is not None:
        query = query.filter(Algorithm.is_builtin == is_builtin)
    
    if status:
        query = query.filter(Algorithm.status == status)
    
    if tags:
        query = query.filter(Algorithm.tags.contains(tags))
    
    algorithms = query.order_by(Algorithm.created_at.desc()).offset(offset).limit(limit).all()
    
    responses = []
    for algorithm in algorithms:
        version_count = db.query(AlgorithmVersion).filter(
            AlgorithmVersion.algorithm_id == algorithm.id
        ).count()
        
        latest_version_obj = db.query(AlgorithmVersion).filter(
            AlgorithmVersion.algorithm_id == algorithm.id
        ).order_by(AlgorithmVersion.created_at.desc()).first()
        
        response = AlgorithmResponse(
            id=algorithm.id,
            name=algorithm.name,
            algorithm_type=algorithm.algorithm_type,
            is_builtin=algorithm.is_builtin,
            description=algorithm.description,
            author=algorithm.author,
            primary_publication_id=algorithm.primary_publication_id,
            created_at=algorithm.created_at,
            updated_at=algorithm.updated_at,
            metadata_json=algorithm.metadata_json or {},
            tags=algorithm.tags.split(",") if algorithm.tags else [],
            status=algorithm.status,
            version_count=version_count,
            latest_version=latest_version_obj.version if latest_version_obj else None
        )
        responses.append(response)
    
    return responses

# Algorithm Version endpoints
@app.post("/api/algorithms/{algorithm_id}/versions", response_model=AlgorithmVersionResponse)
async def create_algorithm_version(
    algorithm_id: str, 
    version: AlgorithmVersionCreate, 
    db: Session = Depends(get_db)
):
    """Create new algorithm version"""
    # Verify algorithm exists
    db_algorithm = db.query(Algorithm).filter(Algorithm.id == algorithm_id).first()
    if not db_algorithm:
        raise HTTPException(status_code=404, detail="Algorithm not found")
    
    # Check if version already exists
    existing_version = db.query(AlgorithmVersion).filter(
        AlgorithmVersion.algorithm_id == algorithm_id,
        AlgorithmVersion.version == version.version
    ).first()
    
    if existing_version:
        raise HTTPException(status_code=400, detail="Version already exists")
    
    # Override algorithm_id from URL
    version.algorithm_id = algorithm_id
    
    db_version = AlgorithmVersion(
        id=str(uuid.uuid4()),
        algorithm_id=version.algorithm_id,
        version=version.version,
        plugin_location=version.plugin_location,
        sdk_version=version.sdk_version,
        release_notes=version.release_notes,
        parameter_schema_json=version.parameter_schema,
        requirements_json=version.requirements,
        performance_characteristics_json=version.performance_characteristics,
        created_by=version.created_by,
        metadata_json=version.metadata
    )
    
    db.add(db_version)
    db.commit()
    db.refresh(db_version)
    
    return AlgorithmVersionResponse.from_orm(db_version)

@app.get("/api/algorithms/{algorithm_id}/versions", response_model=List[AlgorithmVersionResponse])
async def get_algorithm_versions(
    algorithm_id: str,
    limit: int = Query(50, le=200),
    offset: int = Query(0, ge=0),
    status: Optional[AlgorithmStatus] = None,
    db: Session = Depends(get_db)
):
    """Get versions for algorithm"""
    # Verify algorithm exists
    db_algorithm = db.query(Algorithm).filter(Algorithm.id == algorithm_id).first()
    if not db_algorithm:
        raise HTTPException(status_code=404, detail="Algorithm not found")
    
    query = db.query(AlgorithmVersion).filter(AlgorithmVersion.algorithm_id == algorithm_id)
    
    if status:
        query = query.filter(AlgorithmVersion.status == status)
    
    versions = query.order_by(AlgorithmVersion.created_at.desc()).offset(offset).limit(limit).all()
    
    return [AlgorithmVersionResponse.from_orm(version) for version in versions]

@app.get("/api/algorithms/{algorithm_id}/versions/{version}", response_model=AlgorithmVersionResponse)
async def get_algorithm_version(
    algorithm_id: str, 
    version: str, 
    db: Session = Depends(get_db)
):
    """Get specific algorithm version"""
    db_version = db.query(AlgorithmVersion).filter(
        AlgorithmVersion.algorithm_id == algorithm_id,
        AlgorithmVersion.version == version
    ).first()
    
    if not db_version:
        raise HTTPException(status_code=404, detail="Algorithm version not found")
    
    # Increment download count
    db_version.download_count += 1
    db.commit()
    
    return AlgorithmVersionResponse.from_orm(db_version)

# Compatibility checking
@app.post("/api/algorithms/compatibility", response_model=CompatibilityResult)
async def check_algorithm_compatibility(
    check: AlgorithmCompatibilityCheck, 
    db: Session = Depends(get_db)
):
    """Check algorithm compatibility with benchmark and system requirements"""
    # Get algorithm version
    db_version = db.query(AlgorithmVersion).filter(
        AlgorithmVersion.algorithm_id == check.algorithm_id,
        AlgorithmVersion.version == check.version
    ).first()
    
    if not db_version:
        raise HTTPException(status_code=404, detail="Algorithm version not found")
    
    result = CompatibilityResult(compatible=True)
    
    # Check system requirements
    requirements = db_version.requirements_json or {}
    
    # GPU requirement check
    if requirements.get("requires_gpu", False):
        if not check.system_resources.get("gpu_available", False):
            result.compatible = False
            result.errors.append("Algorithm requires GPU but none available")
    
    # Memory requirement check
    required_memory = requirements.get("min_memory_gb", 0)
    available_memory = check.system_resources.get("memory_gb", 0)
    if required_memory > available_memory:
        result.compatible = False
        result.errors.append(f"Algorithm requires {required_memory}GB memory, only {available_memory}GB available")
    
    # Parameter space compatibility (basic check)
    param_schema = db_version.parameter_schema_json or {}
    benchmark_params = check.benchmark_requirements.get("parameter_types", [])
    
    # Add warnings for performance characteristics
    performance = db_version.performance_characteristics_json or {}
    if performance.get("high_memory_usage", False):
        result.warnings.append("Algorithm may use significant memory")
    
    if performance.get("slow_convergence", False):
        result.warnings.append("Algorithm may require many evaluations to converge")
    
    # Recommendations
    if requirements.get("recommended_budget"):
        result.recommendations.append(
            f"Recommended evaluation budget: {requirements['recommended_budget']}"
        )
    
    return result

# Seed some default algorithms
@app.on_event("startup")
async def seed_default_algorithms():
    """Seed default built-in algorithms on startup"""
    db = SessionLocal()
    try:
        # Check if we already have algorithms
        existing_count = db.query(Algorithm).count()
        if existing_count > 0:
            logger.info(f"Found {existing_count} existing algorithms, skipping seed")
            return
        
        logger.info("Seeding default algorithms...")
        
        # Random Search
        random_search = Algorithm(
            id="random_search",
            name="Random Search",
            algorithm_type="random_search",
            is_builtin=True,
            description="Classic random search algorithm for hyperparameter optimization",
            author="Corvus Corone Built-in",
            metadata_json={
                "complexity": "low",
                "parallelizable": True,
                "parameter_types": ["continuous", "discrete", "categorical"]
            },
            tags="baseline,simple,parallel"
        )
        db.add(random_search)
        
        # Random Search Version
        random_search_v1 = AlgorithmVersion(
            id=str(uuid.uuid4()),
            algorithm_id="random_search",
            version="1.0.0",
            sdk_version="1.0.0",
            release_notes="Initial built-in implementation",
            parameter_schema_json={
                "type": "object",
                "properties": {
                    "seed": {"type": "integer", "default": 42}
                }
            },
            requirements_json={
                "min_memory_gb": 1,
                "requires_gpu": False,
                "recommended_budget": 100
            },
            performance_characteristics_json={
                "high_memory_usage": False,
                "slow_convergence": False,
                "good_for_baselines": True
            },
            created_by="system"
        )
        db.add(random_search_v1)
        
        # Bayesian Optimization
        bayesian_opt = Algorithm(
            id="bayesian_optimization",
            name="Bayesian Optimization (TPE)",
            algorithm_type="bayesian_optimization",
            is_builtin=True,
            description="Tree-structured Parzen Estimator for Bayesian optimization",
            author="Corvus Corone Built-in",
            metadata_json={
                "complexity": "medium",
                "parallelizable": False,
                "parameter_types": ["continuous", "discrete"]
            },
            tags="bayesian,efficient,sequential"
        )
        db.add(bayesian_opt)
        
        # Bayesian Optimization Version
        bayesian_opt_v1 = AlgorithmVersion(
            id=str(uuid.uuid4()),
            algorithm_id="bayesian_optimization",
            version="1.0.0",
            sdk_version="1.0.0",
            release_notes="Initial TPE implementation",
            parameter_schema_json={
                "type": "object",
                "properties": {
                    "n_startup_trials": {"type": "integer", "default": 10},
                    "n_ei_candidates": {"type": "integer", "default": 24}
                }
            },
            requirements_json={
                "min_memory_gb": 2,
                "requires_gpu": False,
                "recommended_budget": 50
            },
            performance_characteristics_json={
                "high_memory_usage": False,
                "slow_convergence": False,
                "good_for_optimization": True
            },
            created_by="system"
        )
        db.add(bayesian_opt_v1)
        
        # Grid Search
        grid_search = Algorithm(
            id="grid_search",
            name="Grid Search",
            algorithm_type="grid_search",
            is_builtin=True,
            description="Exhaustive search over parameter grid",
            author="Corvus Corone Built-in",
            metadata_json={
                "complexity": "low",
                "parallelizable": True,
                "parameter_types": ["discrete", "categorical"]
            },
            tags="exhaustive,baseline,parallel"
        )
        db.add(grid_search)
        
        # Grid Search Version
        grid_search_v1 = AlgorithmVersion(
            id=str(uuid.uuid4()),
            algorithm_id="grid_search",
            version="1.0.0",
            sdk_version="1.0.0",
            release_notes="Initial grid search implementation",
            parameter_schema_json={
                "type": "object",
                "properties": {
                    "grid_resolution": {"type": "integer", "default": 10}
                }
            },
            requirements_json={
                "min_memory_gb": 1,
                "requires_gpu": False,
                "recommended_budget": 200
            },
            performance_characteristics_json={
                "high_memory_usage": False,
                "slow_convergence": True,
                "good_for_baselines": True
            },
            created_by="system"
        )
        db.add(grid_search_v1)
        
        db.commit()
        logger.info("Default algorithms seeded successfully")
        
    except Exception as e:
        logger.error(f"Failed to seed algorithms: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8004)