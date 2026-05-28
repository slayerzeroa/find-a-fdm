# # # import datetime
# # # import time

# # # import os
# # # import json
# # # from tracemalloc import start

# # # from arrow import get
# # # import requests
# # # import pandas as pd
# # # import numpy as np
# # # from dotenv import load_dotenv

# # # from data.db import update_stock_options_daily_data


# # # #### 환경변수 세팅
# # # load_dotenv(dotenv_path='C:/Users/slaye/VscodeProjects/find-a-fdm/2024-2/ydm/env/.env')
# # # APP_KEY = os.getenv("APP_KEY")
# # # APP_SECRET = os.getenv("APP_SECRET")
# # # KRX_API = os.getenv("KRX_API")  


# # # def get_stock_list(market:str='KOSPI', date:str=(datetime.datetime.now())):
# # #     '''
# # #     market에 따른 종목코드 리스트 반환
# # #     '''
# # #     ## 근데 왜 당일 데이터가 안나오지?
# # #     if market == 'KOSPI' or market == 'kospi' or market == '코스피':
# # #         market_code = 'stk'
# # #     elif market == 'KOSDAQ' or market == 'kosdaq' or market == '코스닥':
# # #         market_code = 'ksq'
# # #     else:
# # #         return 'Invalid market code'
        
# # #     headers = {
# # #         'AUTH_KEY': KRX_API 
# # #     }

# # #     url = f'http://data-dbg.krx.co.kr/svc/apis/sto/{market_code}_isu_base_info?basDd={date}'

# # #     response = requests.get(url=url, headers=headers)
# # #     res_json = response.json()['OutBlock_1']
# # #     res_df = pd.DataFrame(res_json)

# # #     stock_list = res_df['ISU_SRT_CD'].tolist()

# # #     return stock_list



# # # def get_option_data(date:str=(datetime.datetime.now())):
# # #     '''
# # #     파생상품시장의 주식옵션 중 기초자산이 유가증권시장에 속하는 주식옵션의 거래정보 제공
# # #     '''
# # #     headers = {
# # #         'AUTH_KEY': KRX_API
# # #     }

# # #     url = f'http://data-dbg.krx.co.kr/svc/apis/drv/eqsop_bydd_trd?basDd={date}'

# # #     response = requests.get(url=url, headers=headers)
# # #     res_json = response.json()['OutBlock_1']
# # #     res_df = pd.DataFrame(res_json)

# # #     return res_df




# # # start_date = "20100415"


# # # while start_date != "20241006":
# # #     data = get_option_data(date=start_date)

# # #     if data.empty:
# # #         print(f"{start_date}에 해당하는 데이터가 없습니다.")
# # #         pass
# # #     else:
# # #         print(f"{start_date}에 해당하는 데이터 업데이트 중...")
# # #         update_stock_options_daily_data(data)
    
# # #     start_date = get(start_date).shift(days=1).format("YYYYMMDD")

# # #     time.sleep(4)


# # import pandas as pd
# # from data.api import *
# # from data.db import *
# # from data.helpful_functions import *


# # pd.set_option('display.max_columns', None)

# # result_df = pd.DataFrame()

# # basDd = "20241007"

# # for i in range(1, 10):
# #     try:
# #         option_df = get_index_option_from_krx(basDd=basDd, include_fundamental=True)
# #         result_df = pd.concat([result_df, option_df])
# #         basDd = get(basDd).shift(days=1).format("YYYYMMDD")
# #     except:
# #         print(f"{basDd}에 해당하는 데이터가 없습니다.")
# #         basDd = get(basDd).shift(days=1).format("YYYYMMDD")


# # test_df = cal_greeks(result_df)

# # # print(test_df)


# # print(test_df.iloc[230:239, :])


# '''
# 옵션 그릭스 직접 계산
# '''

# from click import option
# from matplotlib.pyplot import hist
# from scipy.fft import hfft
# import data.api as api
# import data.helpful_functions as hf
# import data.db as db
# import pandas as pd
# import numpy as np
# from datetime import datetime, timedelta
# from QuantLib import Date, SouthKorea
# import math


# target_date = '20241213'
# option_df = api.get_index_option_from_krx(basDd=target_date, include_fundamental=True)
# rf = float(api.get_interest_df(start=target_date, end=target_date)['콜금리'])

# ## 옵션 만기가 세번째 금요일이니
# ## 해당 월의 세번째 금요일을 찾아주는 함수
# def get_third_friday(year: int, month: int):
#     # The 15th is the lowest third Friday can be
#     third_friday = 15 + (4 - datetime(year, month, 15).weekday()) % 7
#     return datetime(year, month, third_friday)

# ## 만기일까지 남은 일수를 계산해주는 함수
# def get_remaining_days(from_date: str, to_date: str):
#     year = int(to_date[:4])
#     month = int(to_date[4:6])
#     third_friday = get_third_friday(year, month)
#     today = datetime.strptime(from_date, '%Y%m%d')
#     remaining_days = (third_friday - today).days
#     return remaining_days


# def get_business_days(from_date: str, to_date: str):
#     # 날짜 문자열을 datetime 객체로 변환
#     from_date = datetime.strptime(from_date, '%Y%m%d')

#     year = int(to_date[:4])
#     month = int(to_date[4:6])
#     third_friday = get_third_friday(year, month)
#     to_date = third_friday

#     # datetime 객체를 QuantLib Date 객체로 변환
#     start_qldate = Date(from_date.day, from_date.month, from_date.year)
#     end_qldate = Date(to_date.day, to_date.month, to_date.year)

#     # 한국 영업일 달력 생성
#     calendar = SouthKorea()

#     # 시작일부터 종료일까지 영업일 리스트 생성
#     business_days = []
#     current_date = start_qldate
#     while current_date <= end_qldate:
#         if calendar.isBusinessDay(current_date):
#             # QuantLib Date 객체를 문자열로 변환
#             date_str = datetime(current_date.year(), current_date.month(), current_date.dayOfMonth()).strftime('%Y%m%d')
#             business_days.append(date_str)
#         current_date = current_date + 1  # 하루 증가

#     return len(business_days)


# fundamental_price = float(api.get_fundamental_info(option_df['BAS_DD'].values[0])['CLSPRC_IDX'])
# option_df['FUNDAMENTAL'] = fundamental_price
# option_df['EXPIRATION_DATE'] = option_df['EXPIRATION_DATE'].astype(str)
# option_df['BAS_DD'] = option_df['BAS_DD'].astype(str)
# option_df['REMAINING_DAYS'] = option_df.apply(lambda x: get_business_days(x['BAS_DD'], x['EXPIRATION_DATE']), axis=1)
# option_df['STRIKE_PRICE'] = option_df['ISU_NM'].apply(lambda x: x.split(' ')[-1])
# option_df['STRIKE_PRICE'] = option_df['STRIKE_PRICE'].astype(float)
# option_df['NXTDD_BAS_PRC'] = option_df['NXTDD_BAS_PRC'].astype(float)
# option_df['IMP_VOLT'] = option_df['IMP_VOLT'].astype(float)
# option_df['REMAINING_DAYS'] = option_df['REMAINING_DAYS'].astype(float)

# working_day = 252
# option_df['DELTA'] = option_df.apply(lambda x: hf.get_delta(x['FUNDAMENTAL'], x['STRIKE_PRICE'], x['REMAINING_DAYS']/working_day, rf/working_day, x['IMP_VOLT']/100, option_type=x['RGHT_TP_NM']), axis=1)
# option_df['GAMMA'] = option_df.apply(lambda x: hf.get_gamma(x['FUNDAMENTAL'], x['STRIKE_PRICE'], x['REMAINING_DAYS']/working_day, rf/working_day, x['IMP_VOLT']/100), axis=1)

# cols_to_fix = ['TDD_CLSPRC', 'CMPPREVDD_PRC', 'TDD_OPNPRC', 'TDD_HGPRC', 'TDD_LWPRC']
# for col in cols_to_fix:
#     # '-' 를 np.nan 으로 치환
#     option_df[col] = option_df[col].replace('-', np.nan)
#     # float로 변환 (에러 발생 시 NaN으로 처리)
#     option_df[col] = pd.to_numeric(option_df[col], errors='coerce')

# # ooption_df = option_df[['ISU_CD', 'DELTA', 'GAMMA']]
# # ooption_df = ooption_df.sort_values(by='ISU_CD')

# pd.set_option('display.max_columns', None)
# print(option_df[option_df['ISU_NM'] == '코스피200 C 202505 310.0'])

# db.update_krx_index_option(option_df[option_df['ISU_NM'] == '코스피200 C 202505 310.0'])

# # from arrow import get
# pd.set_option('display.max_columns', None)

# result_df = pd.DataFrame()

# basDd = target_date

# for i in range(1, 4):
#     try:
#         option_df = api.get_index_option_from_krx(basDd=basDd, include_fundamental=True)
#         result_df = pd.concat([result_df, option_df])
#         basDd = get(basDd).shift(days=1).format("YYYYMMDD")
#     except:
#         print(f"{basDd}에 해당하는 데이터가 없습니다.")
#         basDd = get(basDd).shift(days=1).format("YYYYMMDD")


# print(result_df)


# test_df = api.cal_greeks(result_df)

# test_df = test_df[test_df['BAS_DD'] == target_date]

# test_df = test_df[['ISU_CD', 'DELTA', 'GAMMA']]


# print('Using BSM')
# print(ooption_df.iloc[230:239, :])

# print('Using Discrete Difference')
# print(test_df.iloc[230:239, :])




'''
db에서 필요한 데이터 받아오기
'''

import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine

import os
import pymysql

import copy

import datetime

load_dotenv(dotenv_path='2024-2/ydm/env/.env')

host = os.getenv('DB_HOST')
user = os.getenv('DB_USER')
password = os.getenv('DB_PASSWORD')
db_name = os.getenv('DB_NAME')
db_port = os.getenv('DB_PORT')

def load_index_minute_data(target_date: str):
    engine = create_engine(f"mysql+pymysql://{user}:{password}@{host}:{db_port}/{db_name}?charset=utf8mb4")
    query = f"SELECT * FROM index_minutes_data WHERE `stck_bsop_date` = '{target_date}'"
    index_minute_df = pd.read_sql(query, engine)

    return index_minute_df


def load_gex_data(target_date: str):
    engine = create_engine(f"mysql+pymysql://{user}:{password}@{host}:{db_port}/{db_name}?charset=utf8mb4")
    query = f"SELECT * FROM krx_gamma_exposure WHERE `DATE` = '{target_date}'"
    gex_df = pd.read_sql(query, engine)

    return gex_df


def load_gex_returns(target_date: str):
    """
    - load_index_minute_data(target_date)로부터 분봉 데이터를 얻는다.
    - KOSPI 및 특정 시각 이후(1521)만 필터링한다.
    - 9분 전 대비 수익률(returns) 계산 후 NaN 제거.
    - 마지막 행의 'returns' 값을 float(last_returns)로 추출한다.
    - load_gex_data(target_date)에서 GEX 데이터를 불러온 뒤 last_returns를 합쳐 반환.
    - 에러 발생 시 None을 반환.
    """
    try:
        # 1) 분봉 데이터 읽어오기 + 복사
        #    ※ 여기서 한 번 .copy() 해두면 이후 체인할당 경고가 줄어듭니다.
        index_minute_df = load_index_minute_data(target_date).copy()

        # 2) KOSPI 데이터만 필터링
        index_minute_df = index_minute_df.loc[index_minute_df['market'] == 'KOSPI'].copy()

        # 3) 시각 필터링
        index_minute_df = index_minute_df.loc[index_minute_df['stck_cntg_hour'] >= '1521'].copy()

        # 4) returns 계산 (9분 전 대비 수익률)
        #    pct_change(9)을 계산 후 바로 할당 → 필요시 .copy()는 생략 가능
        index_minute_df['returns'] = index_minute_df['stck_prpr'].pct_change(9)

        # 5) NaN 제거 (returns 컬럼 기준)
        #    dropna(subset=['returns'])를 사용하면 returns가 NaN인 행만 제거
        index_minute_df.dropna(subset=['returns'], inplace=True)

        # 6) 마지막 행(또는 특정 행)의 'returns'를 float로 변환
        #    예시로 마지막 행의 returns 값을 사용
        if len(index_minute_df) == 0:
            # 데이터가 없으면 None
            return None
        last_returns = float(index_minute_df['returns'].iloc[-1])

        # 7) GEX 데이터 불러오기 + last_returns 합치기
        gex_df = load_gex_data(target_date).copy()
        gex_df['last_returns'] = last_returns

        return gex_df

    except Exception as e:
        # 디버깅을 위해 실제 오류 메시지를 출력하고 싶다면 다음과 같이 작성
        # print(f"load_gex_returns Error: {e}")
        return None


def load_gex_df(start_date: str, end_date: str):
    """
    start_date부터 end_date까지(YYYYMMDD) 순회하며
    각 날짜의 GEX 데이터 + returns를 합쳐 만든 DF를 반환.

    예:
        gex_df = load_gex_df('20230101', '20230110')
    """
    # 날짜 문자열 -> datetime 객체로 변환
    start_dt = datetime.datetime.strptime(start_date, '%Y%m%d')
    end_dt   = datetime.datetime.strptime(end_date, '%Y%m%d')

    # 결과를 담을 리스트
    result_list = []

    # 현재 날짜 포인터
    current_dt = start_dt

    while current_dt <= end_dt:
        # YYYYMMDD 문자열로 변환
        target_date_str = current_dt.strftime('%Y%m%d')

        # load_gex_returns() 호출
        gex_data = load_gex_returns(target_date_str)
        
        if gex_data is not None:
            # gex_data 자체가 DataFrame일 것이므로 list에 append
            result_list.append(gex_data)

        # 날짜 +1일
        current_dt += datetime.timedelta(days=1)

    # 리스트가 비어있지 않다면 concat
    if len(result_list) > 0:
        # 여러 날짜의 DF를 세로로 붙이기
        final_df = pd.concat(result_list, ignore_index=True)
        return final_df
    else:
        # 해당 구간에 데이터를 하나도 못 불러온 경우
        return pd.DataFrame()    



# import pandas as pd
# import data

# df = pd.read_csv("2024-2/ydm/data/test_202412.csv", encoding="euc-kr")
# print(df)