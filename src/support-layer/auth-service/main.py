from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy import create_engine, Column, String, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from pydantic import BaseModel
import hashlib
from jose import JWTError, jwt
from datetime import datetime, timedelta
import uuid
import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Authentication Service",
    description="Handles authentication and authorization",
    version="1.0.0"
)

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/corvus_corone")
JWT_SECRET = os.getenv("JWT_SECRET", "your-super-secret-jwt-key-change-in-production")
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_HOURS = 24

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
# Use simple SHA256 password hashing to avoid bcrypt version issues
def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password_simple(plain_password: str, hashed_password: str) -> bool:
    return hash_password(plain_password) == hashed_password
security = HTTPBearer()

class User(Base):
    __tablename__ = "users"
    
    id = Column(String, primary_key=True)
    username = Column(String, unique=True, nullable=False)
    email = Column(String, unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(String, default="researcher")  # admin, researcher, viewer
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime)

Base.metadata.create_all(bind=engine)

class UserCreate(BaseModel):
    username: str
    email: str
    password: str
    role: str = "researcher"

class UserLogin(BaseModel):
    username: str
    password: str

class UserResponse(BaseModel):
    id: str
    username: str
    email: str
    role: str
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    expires_in: int
    user: UserResponse

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def verify_password(plain_password, hashed_password):
    return verify_password_simple(plain_password, hashed_password)

def get_password_hash(password):
    return hash_password(password)

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(hours=JWT_EXPIRATION_HOURS)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return encoded_jwt

def verify_token(token: str):
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            return None
        return payload
    except JWTError:
        return None

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "auth-service"}

@app.post("/api/auth/register", response_model=UserResponse)
async def register_user(user: UserCreate, db: Session = Depends(get_db)):
    # Check if user already exists
    existing_user = db.query(User).filter(
        (User.username == user.username) | (User.email == user.email)
    ).first()
    
    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Username or email already registered"
        )
    
    # Create new user
    hashed_password = get_password_hash(user.password)
    db_user = User(
        id=str(uuid.uuid4()),
        username=user.username,
        email=user.email,
        hashed_password=hashed_password,
        role=user.role
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return UserResponse.from_orm(db_user)

@app.post("/api/auth/login", response_model=TokenResponse)
async def login_user(user_login: UserLogin, db: Session = Depends(get_db)):
    # Find user
    user = db.query(User).filter(User.username == user_login.username).first()
    
    if not user or not verify_password(user_login.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password"
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account is disabled"
        )
    
    # Update last login
    user.last_login = datetime.utcnow()
    db.commit()
    
    # Create access token
    access_token = create_access_token(
        data={"sub": user.username, "role": user.role, "user_id": user.id}
    )
    
    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in=JWT_EXPIRATION_HOURS * 3600,
        user=UserResponse.from_orm(user)
    )

@app.post("/api/auth/verify")
async def verify_user_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    payload = verify_token(credentials.credentials)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )
    return payload

@app.get("/api/auth/me", response_model=UserResponse)
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    payload = verify_token(credentials.credentials)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )
    
    username = payload.get("sub")
    user = db.query(User).filter(User.username == username).first()
    
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return UserResponse.from_orm(user)

# Create default admin user on startup
@app.on_event("startup")
async def create_default_admin():
    db = SessionLocal()
    try:
        # Check if admin user exists
        admin_user = db.query(User).filter(User.username == "admin").first()
        if not admin_user:
            logger.info("Creating default admin user...")
            
            # Truncate password to avoid bcrypt 72-byte limit
            password = "admin123"[:72]
            hashed_password = get_password_hash(password)
            admin_user = User(
                id=str(uuid.uuid4()),
                username="admin",
                email="admin@corvus-corone.local",
                hashed_password=hashed_password,
                role="admin"
            )
            
            db.add(admin_user)
            db.commit()
            
            logger.info("Default admin user created: admin/admin123")
            logger.warning("Please change the default admin password in production!")
        
        # Create demo researcher user
        researcher_user = db.query(User).filter(User.username == "researcher").first()
        if not researcher_user:
            # Truncate password to avoid bcrypt 72-byte limit
            password = "researcher123"[:72]
            hashed_password = get_password_hash(password)
            researcher_user = User(
                id=str(uuid.uuid4()),
                username="researcher",
                email="researcher@corvus-corone.local",
                hashed_password=hashed_password,
                role="researcher"
            )
            
            db.add(researcher_user)
            db.commit()
            
            logger.info("Demo researcher user created: researcher/researcher123")
            
    except Exception as e:
        logger.error(f"Failed to create default users: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)