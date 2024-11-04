import datetime
import time

import os
import json
from tracemalloc import start

from arrow import get
import requests
import pandas as pd
import numpy as np
from dotenv import load_dotenv

from data.db import update_stock_options_daily_data


#### 환경변수 세팅
load_dotenv(dotenv_path='C:/Users/slaye/VscodeProjects/find-a-fdm/2024-2/ydm/env/.env')
APP_KEY = os.getenv("APP_KEY")
APP_SECRET = os.getenv("APP_SECRET")
KRX_API = os.getenv("KRX_API")  


def get_stock_list(market:str='KOSPI', date:str=(datetime.datetime.now())):
    '''
    market에 따른 종목코드 리스트 반환
    '''
    ## 근데 왜 당일 데이터가 안나오지?
    if market == 'KOSPI' or market == 'kospi' or market == '코스피':
        market_code = 'stk'
    elif market == 'KOSDAQ' or market == 'kosdaq' or market == '코스닥':
        market_code = 'ksq'
    else:
        return 'Invalid market code'
        
    headers = {
        'AUTH_KEY': KRX_API 
    }

    url = f'http://data-dbg.krx.co.kr/svc/apis/sto/{market_code}_isu_base_info?basDd={date}'

    response = requests.get(url=url, headers=headers)
    res_json = response.json()['OutBlock_1']
    res_df = pd.DataFrame(res_json)

    stock_list = res_df['ISU_SRT_CD'].tolist()

    return stock_list



def get_option_data(date:str=(datetime.datetime.now())):
    '''
    파생상품시장의 주식옵션 중 기초자산이 유가증권시장에 속하는 주식옵션의 거래정보 제공
    '''
    headers = {
        'AUTH_KEY': KRX_API
    }

    url = f'http://data-dbg.krx.co.kr/svc/apis/drv/eqsop_bydd_trd?basDd={date}'

    response = requests.get(url=url, headers=headers)
    res_json = response.json()['OutBlock_1']
    res_df = pd.DataFrame(res_json)

    return res_df




start_date = "20100415"


while start_date != "20241006":
    data = get_option_data(date=start_date)

    if data.empty:
        print(f"{start_date}에 해당하는 데이터가 없습니다.")
        pass
    else:
        print(f"{start_date}에 해당하는 데이터 업데이트 중...")
        update_stock_options_daily_data(data)
    
    start_date = get(start_date).shift(days=1).format("YYYYMMDD")

    time.sleep(4)
