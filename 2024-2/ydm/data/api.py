#### 한국투자증권 KIS DEVELOPER

#### 라이브러리 Import
import code
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


'''
한국투자증권 API 관련 함수
'''

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




def get_greeks_info(appkey, appsecret, access_token, market_code, item_code):
    '''
    delta: 델타
    gamma: 감마
    theta: 세타
    vega: 베가
    rho: 로
    otst: 미결제약정
    '''
    url = "https://openapi.koreainvestment.com:9443/uapi/domestic-futureoption/v1/quotations/inquire-price"
    
    headers = {
        "content-type": "application/json; charset=utf-8",
        "authorization": f"Bearer {access_token}",
        "appkey": appkey,
        "appsecret": appsecret,
        "tr_id": "FHMIF10000000"
    }
    
    params = {
        "FID_COND_MRKT_DIV_CODE": market_code,  # 예: "F"
        "FID_INPUT_ISCD": item_code             # 예: "101S03"
    }
    
    response = requests.get(url, headers=headers, params=params)
    
    if response.status_code == 200:
        data = response.json()
        if data["rt_cd"] == "0":
            output1 = data.get("output1", {})
            delta = output1.get("delta_val")
            gamma = output1.get("gama")
            theta = output1.get("theta")
            vega = output1.get("vega")
            rho = output1.get("rho")
            otst = output1.get("hts_otst_stpl_qty")
            
            # greeks = {
            #     "Delta": delta,
            #     "Gamma": gamma,
            #     "Theta": theta,
            #     "Vega": vega,
            #     "Rho": rho
            # }
            
            # return greeks

            return delta, gamma, theta, vega, rho, otst
        
        else:
            print("Error:", data.get("msg1"))
    else:
        print("HTTP Error:", response.status_code)
    
    return None

# print(get_greeks_info(APP_KEY, APP_SECRET, TOKEN, "F", "101W12"))



'''지수선물옵션 종목코드(fo_idx_code_mts.mst) 정제 파이썬 파일'''
# https://github.com/koreainvestment/open-trading-api/blob/main/stocks_info/domestic_index_future_code.py

import pandas as pd
import urllib.request
import ssl
import zipfile
import os

base_dir = os.getcwd()

def get_domestic_future_master_dataframe(base_dir):
    # Download file
    print("Downloading...")

    # Bypass SSL verification
    ssl._create_default_https_context = ssl._create_unverified_context
    zip_file_path = os.path.join(base_dir, "fo_idx_code_mts.mst.zip")
    urllib.request.urlretrieve("https://new.real.download.dws.co.kr/common/master/fo_idx_code_mts.mst.zip", zip_file_path)
    os.chdir(base_dir)

    # Extract file
    with zipfile.ZipFile(zip_file_path, 'r') as fo_idx_code_zip:
        fo_idx_code_zip.extractall()

    # Load data into DataFrame
    file_name = os.path.join(base_dir, "fo_idx_code_mts.mst")
    columns = ['상품종류', '단축코드', '표준코드', '한글종목명', 'ATM구분', '행사가', '월물구분코드', '기초자산 단축코드', '기초자산 명']
    df = pd.read_table(file_name, sep='|', encoding='cp949', header=None)
    df.columns = columns

    # Remove downloaded and extracted files
    os.remove(zip_file_path)  # Delete ZIP file
    os.remove(file_name)       # Delete extracted MST file

    return df


def get_index_option_dataframe():

    df = get_domestic_future_master_dataframe(base_dir)
    print("Done")

    # 전처리
    kospi_option_df = df[df['기초자산 명']=='KOSPI200']
    kospi_option_df.loc[:, '시장분류코드'] = kospi_option_df.loc[:,'한글종목명'].apply(lambda x: x[0])
    kospi_call_option_df = kospi_option_df[kospi_option_df.loc[:,'시장분류코드']=='C']
    kospi_put_option_df = kospi_option_df[kospi_option_df.loc[:,'시장분류코드']=='P']

    kospi_call_option_df.loc[:, '만기'] = kospi_call_option_df.loc[:,'한글종목명'].apply(lambda x: x.split(' ')[1])
    kospi_put_option_df.loc[:, '만기'] = kospi_put_option_df.loc[:, '한글종목명'].apply(lambda x: x.split(' ')[1])


    ### 콜옵션 그릭스 정보 가져오기
    code_list = list(kospi_call_option_df['단축코드'])

    delta_list = []
    gamma_list = []
    theta_list = []
    vega_list = []
    rho_list = []
    otst_list = []

    for i in code_list:
        time.sleep(0.05)
        delta, gamma, theta, vega, rho, otst = (get_greeks_info(APP_KEY, APP_SECRET, TOKEN, "O", i))
        delta_list.append(delta)
        gamma_list.append(gamma)
        theta_list.append(theta)
        vega_list.append(vega)
        rho_list.append(rho)
        otst_list.append(otst)

        print(i, delta, gamma, theta, vega, rho, otst)

    kospi_call_option_df['delta'] = delta_list
    kospi_call_option_df['gamma'] = gamma_list
    kospi_call_option_df['theta'] = theta_list
    kospi_call_option_df['vega'] = vega_list
    kospi_call_option_df['rho'] = rho_list
    kospi_call_option_df['otst'] = otst_list
    kospi_call_option_df['date'] = datetime.datetime.now().strftime('%Y%m%d')


    ### 풋옵션 그릭스 정보 가져오기
    code_list = list(kospi_put_option_df['단축코드'])

    delta_list = []
    gamma_list = []
    theta_list = []
    vega_list = []
    rho_list = []
    otst_list = []

    for i in code_list:
        time.sleep(0.05)
        delta, gamma, theta, vega, rho, otst = (get_greeks_info(APP_KEY, APP_SECRET, TOKEN, "O", i))
        delta_list.append(delta)
        gamma_list.append(gamma)
        theta_list.append(theta)
        vega_list.append(vega)
        rho_list.append(rho)
        otst_list.append(otst)

        print(i, delta, gamma, theta, vega, rho, otst)

    kospi_put_option_df['delta'] = delta_list
    kospi_put_option_df['gamma'] = gamma_list
    kospi_put_option_df['theta'] = theta_list
    kospi_put_option_df['vega'] = vega_list
    kospi_put_option_df['rho'] = rho_list
    kospi_put_option_df['otst'] = otst_list
    kospi_put_option_df['date'] = datetime.datetime.now().strftime('%Y%m%d')

    ### Type Casting
    kospi_call_option_df['delta'] = kospi_call_option_df['delta'].astype(float)
    kospi_call_option_df['gamma'] = kospi_call_option_df['gamma'].astype(float)
    kospi_call_option_df['theta'] = kospi_call_option_df['theta'].astype(float)
    kospi_call_option_df['vega'] = kospi_call_option_df['vega'].astype(float)
    kospi_call_option_df['rho'] = kospi_call_option_df['rho'].astype(float)
    kospi_call_option_df['otst'] = kospi_call_option_df['otst'].astype(int)

    kospi_put_option_df['delta'] = kospi_put_option_df['delta'].astype(float)
    kospi_put_option_df['gamma'] = kospi_put_option_df['gamma'].astype(float)
    kospi_put_option_df['theta'] = kospi_put_option_df['theta'].astype(float)
    kospi_put_option_df['vega'] = kospi_put_option_df['vega'].astype(float)
    kospi_put_option_df['rho'] = kospi_put_option_df['rho'].astype(float)
    kospi_put_option_df['otst'] = kospi_put_option_df['otst'].astype(int)



    ### Gamma Exposure 계산
    kospi_call_option_df['gamma_exposure'] = kospi_call_option_df['gamma'] * kospi_call_option_df['otst']
    kospi_put_option_df['gamma_exposure'] = kospi_put_option_df['gamma'] * kospi_put_option_df['otst']


    call_total_gamma = kospi_call_option_df['gamma_exposure'].sum()
    put_total_gamma = kospi_put_option_df['gamma_exposure'].sum()

    print("call total gamma:", call_total_gamma, "put total gamma:", put_total_gamma)

    print("net GEX:", call_total_gamma - put_total_gamma)
    print("P/C GEX:", put_total_gamma / call_total_gamma)

    kospi_call_option_df.columns = ['PRODUCT_TYPE', 'SHORT_CODE', 'STANDARD_CODE', 'KOREAN_NAME', 'ATM_DIVISION', 'STRIKE_PRICE', 'EXPIRATION_DATE_CODE', 'UNDERLYING_ASSET_SHORT_CODE', 'UNDERLYING_ASSET_NAME', 'MARKET_CODE', 'EXPIRATION_DATE', 'DELTA', 'GAMMA', 'THETA', 'VEGA', 'RHO', 'OPEN_INTEREST', 'DATE', 'GAMMA_EXPOSURE']
    kospi_put_option_df.columns = ['PRODUCT_TYPE', 'SHORT_CODE', 'STANDARD_CODE', 'KOREAN_NAME', 'ATM_DIVISION', 'STRIKE_PRICE', 'EXPIRATION_DATE_CODE', 'UNDERLYING_ASSET_SHORT_CODE', 'UNDERLYING_ASSET_NAME', 'MARKET_CODE', 'EXPIRATION_DATE', 'DELTA', 'GAMMA', 'THETA', 'VEGA', 'RHO', 'OPEN_INTEREST', 'DATE', 'GAMMA_EXPOSURE']

    return kospi_call_option_df, kospi_put_option_df

# ## 데이터 저장
# kospi_call_option_df.to_csv('C:/Users/slaye/VscodeProjects/find-a-fdm/2024-2/ydm/data/kospi_call_option.csv', index=False)
# kospi_put_option_df.to_csv('C:/Users/slaye/VscodeProjects/find-a-fdm/2024-2/ydm/data/kospi_put_option.csv', index=False)


# print(df['단축코드'])
# print(df['한글종목명'])

# print(kospi_option_df[''])