import csv
import json
from . import *  # noqa
from ...app import app
import pandas as pd
import os

CHUNK_SIZE = 3500
records = []

def seed_site_settings(db, excel_file_path):
    xls = pd.ExcelFile(f'{excel_file_path}')
    df = pd.read_excel(xls, 'site_settings')
    for index, row in df[df['title'].notna()].iterrows():
        if row["title"]:
            # Check if it exists
            instance = db.session.query(Config).filter(
                                Config.title == row["title"]).filter(
                                    Config.favicon_logo == row["favicon_link"]
                                ).first()

            # Flag to track if a matching province is found in records
            found_matching_config = False
            
            # Check if it exists in queryset
            if instance is not None:
                found_matching_config = True
                print("existing")
                break

            if not found_matching_config:
                print('creating new')
                config = Config(
                    title=row["title"],
                    title_short=row["title_short"],
                    favicon_logo=row["favicon_link"],
                    logo_colour=row["logo_colour"],
                    footer_colour=row["footer_colour"],
                    nav_bars_colour=row["nav_bars_colour"],
                    body_foreground_colour=row["body_foreground_colour"],
                    body_background_colour=row["body_background_colour"],
                    find_candidates_button=row["find_candidates_button"],
                    candidate_names_colour=row["candidate_names_colour"],
                    data_schemas=row["data_schemas"],
                    partner_name=row["partner_name"] if row["partner_name"] else None,
                    partner_website=row["partner_website"] if row["partner_website"] else None,	
                    google_analytics_key=row["google_analytics_key"] if row["google_analytics_key"] else None,	
                    gtag_script=row["gTag_script"] if row["gTag_script"] else None,
                    organization_name=row["organization_name"] if row["organization_name"] else None,
                    organization_link=row["organization_link"] if row["organization_link"] else None,
                    regional_explainer=row["regional_explainer"] if row["regional_explainer"] else None,
                    provincial_explainer=row["provincial_explainer"] if row["provincial_explainer"] else None,
                    national_explainer=row["national_explainer"] if row["national_explainer"] else None

                )
            
                # Dynamically handle additional columns
                for column in df.columns:
                    if column not in ["title", "title_short", "favicon_link", "primary_colour", "secondary_colour"]:
                        setattr(config, column, row[column])
                        # print(column, row[column])
                db.session.add(config)
    try:
        db.session.commit()
    except Exception as e:
        print(e)    

from collections import Counter
def seed_data_candidates(db, excel_file_path):
    """Generate a candidate table and add a candidate_type column from the `data_schema` object keys and populate the table by candidate_type. 
    Args:
        db (session): Database uses sessions and alembic migrations
        excel_file_path (xlsx): Read from excel file
    Results: 
        db: session commited and candidate table created created in the db
    """
    xls = pd.ExcelFile(f'{excel_file_path}')
    df = pd.read_excel(xls, 'site_settings')
    records = []
    
    for index, row in df[df['data_schemas'].notna()].iterrows():
        if row["data_schemas"]:
            try:
                # Directly use the string as a dictionary
                data_schemas = json.loads(row["data_schemas"])
            except Exception as e:
                data_schemas = eval(row["data_schemas"])
                print("Error:", e)
            print(data_schemas)
            for table_name, csv_filename in data_schemas.items():
                print("Table: ", table_name)
                    
                # Dictionary to map table names to candidate types
                table_to_candidate_type = {
                    table_name: table_name,
                    table_name: table_name,
                    table_name: table_name,
                    table_name: table_name,
                    table_name: table_name
                }
                file_root = f'{app.root_path}/data/{csv_filename["file"]}'
                csv_df = pd.read_csv(file_root, quotechar='"')

                cleaned_columns = [col.replace(' ', '_') for col in csv_df.columns]

                locator_values = [col for col in csv_filename["locator"]]
                # Insert data into the created table
                for _, row_data in csv_df.iterrows():
                    row_data_adjusted = {col.replace(' ', '_'): val.title() if isinstance(val, str) else val for col, val in row_data.to_dict().items()}
                    row_data_adjusted['candidate_type'] = table_to_candidate_type.get(table_name, 'unknown')
                    row_data_adjusted['locator'] = locator_values
                    # print(row_data_adjusted)
                    # Generate the CREATE TABLE candidates query dynamically
                    create_table_query = f"""
                        CREATE TABLE IF NOT EXISTS candidates ({', '.join([col + ' TEXT' for col in row_data_adjusted.keys()])})
                    """
                    db.session.execute(create_table_query)

                    # Generate the INSERT INTO candidates query
                    insert_query = f"""
                        INSERT INTO candidates ({', '.join(row_data_adjusted.keys())}) 
                        VALUES ({', '.join([':' + col for col in row_data_adjusted.keys()])})
                    """
                    db.session.execute(insert_query, row_data_adjusted)
        else:
            print("no such column")
            continue

    try:
        db.session.commit()
        print("Session commit to db")
    except Exception as e:
        db.session.rollback()
        print("DB exception: ", e)
        raise
    finally:
        db.session.close()
