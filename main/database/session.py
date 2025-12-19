import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from ..app import app

SQLALCHEMY_DATABASE_URL = os.environ.get('DATABASE_URL') or "sqlite:///:memory:"
if app.config["ENV"] == 'production':
    SQLALCHEMY_DATABASE_URL = os.environ.get('DATABASE_URL').replace('postgres', 'postgresql')
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)