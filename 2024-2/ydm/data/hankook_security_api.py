#### 한국투자증권 KIS DEVELOPER

#### 라이브러리 Import
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

from .db import update_minutes_df

from .helpful_functions import json2df, get_minutes_list

#### 환경변수 세팅
load_dotenv(dotenv_path='C:/Users/slaye/VscodeProjects/find-a-fdm/2024-2/ydm/env/.env')
APP_KEY = os.getenv("APP_KEY")
APP_SECRET = os.getenv("APP_SECRET")
KRX_API = os.getenv("KRX_API")  

minutes_list = get_minutes_list(reversed=True)



#### 최초 실시간 (웹소켓) 접속키 발급

def get_websocket_token():
    headers = {"content-type":"application/json"}

    body = {
        "grant_type": "client_credentials",
        "appkey": APP_KEY,
        "secretkey": APP_SECRET
    }

    url = "https://openapivts.koreainvestment.com:29443/oauth2/Approval"

    response = requests.post(url, headers=headers, data=json.dumps(body))
    response_data = response.json()

    approval_key = response_data['approval_key']
    return approval_key


#### 접근토큰 발급

def get_access_token():
    headers = {"content-type":"application/json"}

    body = {
        "grant_type": "client_credentials",
        "appkey": APP_KEY,
        "appsecret": APP_SECRET
    }

    url = "https://openapivts.koreainvestment.com:29443/oauth2/tokenP"

    response = requests.post(url, headers=headers, data=json.dumps(body))
    response_data = response.json()

    access_token = response_data['access_token']
    return access_token

try:
    TOKEN = get_access_token()
    txt_path = 'C:/Users/slaye/VscodeProjects/find-a-fdm/2024-2/ydm/env/token.txt'
    with open(txt_path, 'w') as f:
        f.write(TOKEN)
except:
    txt_path = 'C:/Users/slaye/VscodeProjects/find-a-fdm/2024-2/ydm/env/token.txt'
    with open(txt_path, 'r') as f:
        TOKEN = f.read()


'''
데이터 관련 함수
'''

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


def get_minute_data(ticker:str='005930', minutes:str='093000'):
    #### 1분봉 데이터 요청
    headers = {
        "content-type": "application/json; charset=utf-8",
        "authorization": f"Bearer {TOKEN}",
        "appkey": APP_KEY,
        "appsecret": APP_SECRET,
        "tr_id": "FHKST03010200",
        "custtype": "P"
    }

    params = {
        "fid_cond_mrkt_div_code": "J",
        "fid_etc_cls_code": "",
        "fid_input_hour_1": minutes,
        "fid_input_iscd": ticker,
        "fid_pw_data_incu_yn": "Y"
    }

    url = "https://openapivts.koreainvestment.com:29443/uapi/domestic-stock/v1/quotations/inquire-time-itemchartprice"

    res = requests.get(url, params=params, headers=headers)
    rescode = res.status_code
    if rescode == 200:
        df = json2df(res.json()['output2'])
        return df
    else:
        return ("Error Code : " + str(rescode) + " | " + res.text)


def get_every_minutes_data(ticker:str='005930'):
    '''
    종목코드에 대한 당일 1분봉 데이터 반환
    '''
    result = pd.DataFrame()
    for minutes in minutes_list:
        df = get_minute_data(ticker=ticker, minutes=minutes)
        result = pd.concat([result, df], axis=0)
        time.sleep(0.03)


    today = datetime.datetime.now().strftime('%Y%m%d')
    result = result[result['stck_bsop_date'] == today]

    result['ticker'] = ticker 

    return result


def get_every_stock_data(market:str='KOSPI'):
    stock_list = get_stock_list(market=market)
    result = pd.DataFrame()
    for stock in stock_list:
        df = get_every_minutes_data(ticker=stock)
        result = pd.concat([result, df], axis=0)
    result['market'] = market
    return result



# df = get_every_minutes_data('005930')
# df = df.reset_index(drop=True)

# pd.set_option('display.max_columns', None)
# print(df)

# update_minutes_df(df)


# #### 일별 주가 데이터
# headers = {
#     "content-type": "application/json; charset=utf-8",
#     "authorization": f"Bearer {TOKEN}",
#     "appkey": APP_KEY,
#     "appsecret": APP_SECRET,
#     "tr_id": "FHKST01010400",
#     "custtype": "P"
# }

# params =  {
#     "fid_cond_mrkt_div_code": "J",
#     "fid_input_iscd": "000660",
#     "fid_org_adj_prc": "0000000001",
#     "fid_period_div_code": "D"
# }

# url = "https://openapivts.koreainvestment.com:29443/uapi/domestic-stock/v1/quotations/inquire-daily-price"

# res = requests.get(url, params=params, headers=headers)
# rescode = res.status_code
# if rescode == 200:
#     # print(res.headers)
#     # print(str(rescode) + " | " + res.text)
#     print('Success')
# else:
#     print("Error Code : " + str(rescode) + " | " + res.text)


# # print(res.json()['output'])
# print(res.json())

# pd.set_option('display.max_columns', None)
# print(json2df(res.json()['output']))