import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine

import os
import pymysql

load_dotenv()

host = os.getenv('DB_HOST')
user = os.getenv('DB_USER')
password = os.getenv('DB_PASSWORD')
db_name = os.getenv('DB_NAME')
db_port = os.getenv('DB_PORT')
table_name = os.getenv('TABLE_NAME')

def update_wvkospi(minutes_df: pd.DataFrame):
    engine = create_engine(f"mysql+pymysql://{user}:{password}@{host}:{db_port}/{db_name}?charset=utf8mb4")
    minutes_df.to_sql(name=table_name, con=engine, if_exists='append', index=False)