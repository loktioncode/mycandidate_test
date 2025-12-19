import pytest
import os, tempfile
from main.database.session import SessionLocal
from typing import Generator
from app import app, db
from alembic.config import Config
from alembic import command


@pytest.fixture
def client() -> Generator:
    app.config['TESTING'] = True

    # test_db_path = os.path.abspath('tests/test_db.sqlite')
    # app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{test_db_path}'

    client = app.test_client()

    with app.app_context():
        # Create the test database and apply Alembic migrations
        db.create_all()
        alembic_config = Config("alembic.ini") 
        command.upgrade(alembic_config, "head")

    yield client

    with app.app_context():
        # Drop the test database after the test is finished
        db.drop_all() 
