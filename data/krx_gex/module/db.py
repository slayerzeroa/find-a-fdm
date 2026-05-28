import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine

import os
import pymysql

load_dotenv(dotenv_path='.env')

host = os.getenv('DB_HOST')
user = os.getenv('DB_USER')
password = os.getenv('DB_PASSWORD')
db_name = os.getenv('DB_NAME')
db_port = os.getenv('DB_PORT')

'''
KRX 테이블 관련 함수
'''
def update_krx_index_option(krx_index_option_df: pd.DataFrame):
    engine = create_engine(f"mysql+pymysql://{user}:{password}@{host}:{db_port}/{db_name}?charset=utf8mb4")
    krx_index_option_df.to_sql(name='krx_index_option', con=engine, if_exists='append', index=False)


def update_krx_gamma_exposure(krx_gamma_exposure_df: pd.DataFrame):
    engine = create_engine(f"mysql+pymysql://{user}:{password}@{host}:{db_port}/{db_name}?charset=utf8mb4")
    krx_gamma_exposure_df.to_sql(name='krx_gamma_exposure', con=engine, if_exists='append', index=False)


def load_krx_index_options(target_date: str):
    engine = create_engine(f"mysql+pymysql://{user}:{password}@{host}:{db_port}/{db_name}?charset=utf8mb4")
    query = f"SELECT * FROM krx_index_option WHERE `BAS_DD` = '{target_date}'"
    krx_index_options = pd.read_sql(query, engine)

    return krx_index_options