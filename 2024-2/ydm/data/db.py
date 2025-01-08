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
대신증권 테이블 관련함수
'''
def update_minutes_df(minutes_df: pd.DataFrame):
    engine = create_engine(f"mysql+pymysql://{user}:{password}@{host}:{db_port}/{db_name}?charset=utf8mb4")
    minutes_df.to_sql(name='minutes_data', con=engine, if_exists='append', index=False)

'''
한국투자증권 테이블 관련함수
'''
def update_stock_options_daily_data(stock_options_df: pd.DataFrame):
    engine = create_engine(f"mysql+pymysql://{user}:{password}@{host}:{db_port}/{db_name}?charset=utf8mb4")
    stock_options_df.to_sql(name='stock_options_daily_data', con=engine, if_exists='append', index=False)


def update_index_options(index_options_df: pd.DataFrame):
    engine = create_engine(f"mysql+pymysql://{user}:{password}@{host}:{db_port}/{db_name}?charset=utf8mb4")
    index_options_df.to_sql(name='index_option', con=engine, if_exists='append', index=False)


def update_gamma_exposure(gamma_exposure_df: pd.DataFrame):
    engine = create_engine(f"mysql+pymysql://{user}:{password}@{host}:{db_port}/{db_name}?charset=utf8mb4")
    gamma_exposure_df.to_sql(name='gamma_exposure', con=engine, if_exists='append', index=False)


def load_index_options(target_date: str):
    engine = create_engine(f"mysql+pymysql://{user}:{password}@{host}:{db_port}/{db_name}?charset=utf8mb4")
    query = f"SELECT * FROM index_option WHERE `DATE` = '{target_date}'"
    index_options_df = pd.read_sql(query, engine)

    return index_options_df



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