import os
from sqlalchemy import create_engine # connection factory and pool manager
from sqlalchemy.orm import sessionmaker, declarative_base # session objects, base class for ORM models
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread":False}
)

# SessionLocal is a callable
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# every ORM model will inherit from this
Base = declarative_base()

# DB dependency, yield so to have hook on request lifecycle for later cleanup using db.close()
def get_db():
    db = SessionLocal()
    try:
        yield db # injects session into routes
    finally:
        db.close() # executes when request finishes