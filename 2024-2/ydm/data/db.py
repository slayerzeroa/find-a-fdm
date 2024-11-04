import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine

import os
import pymysql

load_dotenv(dotenv_path='C:/Users/slaye/VscodeProjects/find-a-fdm/2024-2/ydm/env/.env')

host = os.getenv('DB_HOST')
user = os.getenv('DB_USER')
password = os.getenv('DB_PASSWORD')
db_name = os.getenv('DB_NAME')
db_port = os.getenv('DB_PORT')

def update_minutes_df(minutes_df: pd.DataFrame):
    engine = create_engine(f"mysql+pymysql://{user}:{password}@{host}:{db_port}/{db_name}?charset=utf8mb4")
    minutes_df.to_sql(name='minutes_data', con=engine, if_exists='append', index=False)



def update_stock_options_daily_data(stock_options_df: pd.DataFrame):
    engine = create_engine(f"mysql+pymysql://{user}:{password}@{host}:{db_port}/{db_name}?charset=utf8mb4")
    stock_options_df.to_sql(name='stock_options_daily_data', con=engine, if_exists='append', index=False)