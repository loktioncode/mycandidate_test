import pytest, os
import pandas as pd
from app import app, db
from main.database.models import Config
from main.database.models.build_db import seed_data_candidates, seed_site_settings
    
def test_excel_file_exists_and_columns_are_not_empty_for_seeding(client):
    temp_excel_file = 'tests/sample_data.xlsx' 
    assert os.path.exists(temp_excel_file)

    df = pd.read_excel(temp_excel_file, sheet_name='site_settings')
    assert not df['data_schemas'].isnull().all()
    assert not df['title'].isnull().all()

    num_config = db.session.query(Config).count()
    assert num_config == 1