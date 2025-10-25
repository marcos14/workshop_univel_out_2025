from sqlalchemy import create_engine, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

DATABASE_URI = os.getenv("DATABASE_URI", "postgresql+psycopg2://postgres:lib_pass_2024@localhost:5437/library_db")

engine = create_engine(DATABASE_URI, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
metadata = MetaData()

def get_db():
    """Dependency para obter sessão do banco de dados"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_tables():
    """Criar todas as tabelas"""
    Base.metadata.create_all(bind=engine)