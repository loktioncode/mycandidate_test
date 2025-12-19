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
        db.create_all()
        # Only run Alembic migrations if alembic.ini exists
        if os.path.exists("alembic.ini"):
            alembic_config = Config("alembic.ini")
            alembic_config.set_main_option("sqlalchemy.url", app.config['SQLALCHEMY_DATABASE_URI'])
            command.upgrade(alembic_config, "head")

    yield client

    with app.app_context():
        # Drop the test database after the test is finished
        db.drop_all() 