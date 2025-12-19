from main.database.models import db
from main.app import app
from main.database.base import Base

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

