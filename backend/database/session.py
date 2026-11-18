from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from ..core import config
from ..models.tables import Base

engine = create_engine(config.DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine, autoflush=False)

def init_db(): Base.metadata.create_all(engine)

def get_db():
    db = SessionLocal()
    try: yield db
    finally: db.close()
