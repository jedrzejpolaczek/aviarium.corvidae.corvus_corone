from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy import create_engine, Column, String, Integer, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import uuid
import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Publication Service",
    description="Manages scientific publications and references",
    version="1.0.0"
)

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/corvus_corone")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Publication(Base):
    __tablename__ = "publications"
    
    id = Column(String, primary_key=True)
    title = Column(String, nullable=False)
    authors = Column(String, nullable=False)
    year = Column(Integer, nullable=False)
    venue = Column(String)
    doi = Column(String)
    bibtex = Column(Text)
    url = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

Base.metadata.create_all(bind=engine)

class PublicationCreate(BaseModel):
    title: str
    authors: str
    year: int
    venue: str = ""
    doi: str = ""
    bibtex: str = ""
    url: str = ""

class PublicationResponse(BaseModel):
    id: str
    title: str
    authors: str
    year: int
    venue: str
    doi: str
    bibtex: str
    url: str
    created_at: datetime
    
    class Config:
        from_attributes = True

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "publication-service"}

@app.post("/api/publications", response_model=PublicationResponse)
async def create_publication(publication: PublicationCreate, db: Session = Depends(get_db)):
    db_publication = Publication(
        id=str(uuid.uuid4()),
        **publication.dict()
    )
    db.add(db_publication)
    db.commit()
    db.refresh(db_publication)
    return PublicationResponse.from_orm(db_publication)

@app.get("/api/publications", response_model=List[PublicationResponse])
async def list_publications(limit: int = 50, offset: int = 0, db: Session = Depends(get_db)):
    publications = db.query(Publication).offset(offset).limit(limit).all()
    return [PublicationResponse.from_orm(pub) for pub in publications]

@app.get("/api/publications/{publication_id}", response_model=PublicationResponse)
async def get_publication(publication_id: str, db: Session = Depends(get_db)):
    publication = db.query(Publication).filter(Publication.id == publication_id).first()
    if not publication:
        raise HTTPException(status_code=404, detail="Publication not found")
    return PublicationResponse.from_orm(publication)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8006)