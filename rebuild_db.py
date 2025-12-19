from main.database.models import db
from main.app import app

# Import models to ensure they're registered with SQLAlchemy
from main.database.base import Base, Config
from main.database.models.candidates import get_data

# Seeds
from main.database.models.build_db import (
    seed_site_settings,
    seed_data_candidates
)

with app.app_context():
    # Initialize db
    db.drop_all()
    db.configure_mappers()
    # Use Base.metadata to create tables since models inherit from Base, not db.Model
    Base.metadata.create_all(db.engine)
    
    excel_file_path = f'{app.root_path}/data/MyCandidate Seed Doc.xlsx'
    
    seed_site_settings(db, excel_file_path)
    seed_data_candidates(db, excel_file_path)
