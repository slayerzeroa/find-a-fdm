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


# def update_minutes_df(minutes_df: pd.DataFrame):
#     engine = create_engine(f"mysql+pymysql://{user}:{password}@{host}:{db_port}/{db_name}?charset=utf8mb4")
#     minutes_df.to_sql(name='minutes_data', con=engine, if_exists='append', index=False)


# 커넥션 풀링을 설정한 데이터베이스 엔진 생성
engine = create_engine(
    f"mysql+pymysql://{user}:{password}@{host}:{db_port}/{db_name}?charset=utf8mb4", 
    pool_size=5,  # 최대 5개의 커넥션 유지
    max_overflow=10  # 추가적으로 최대 10개의 커넥션까지 허용
)

def update_minutes_df(minutes_df: pd.DataFrame):
    # 연결을 가져와서 데이터 삽입
    with engine.connect() as connection:
        minutes_df.to_sql(name='minutes_data', con=connection, if_exists='append', index=False)