#### 한국투자증권 KIS DEVELOPER

#### 라이브러리 Import
import datetime
import time

import os
import json

import requests
import pandas as pd
import numpy as np
from dotenv import load_dotenv
from bs4 import BeautifulSoup



#### 환경변수 세팅
load_dotenv()
APP_KEY = os.getenv("APP_KEY")
APP_SECRET = os.getenv("APP_SECRET")
KRX_API = os.getenv("KRX_API")  
ECOS_API = os.getenv("ECOS_API")



'''
기타 툴 함수
'''


def json2df(json_data):
    df = pd.DataFrame(json_data)
    return df


def get_minutes_list(reversed=False):
    '''
    9:00 ~ 15:30 사이의 시간 리스트를 반환합니다. (30분 간격)
    '''

    # 시작 시간과 종료 시간 설정
    start_time = datetime.datetime.strptime("09:00", "%H:%M")
    end_time = datetime.datetime.strptime("15:30", "%H:%M")

    # 시간 간격 설정 (30분)
    time_interval = datetime.timedelta(minutes=30)

    # 시간 리스트 생성
    minutes_list = []
    current_time = start_time
    while current_time <= end_time:
        minutes_list.append(current_time.strftime("%H%M%S"))
        current_time += time_interval

    if reversed:
        minutes_list.reverse()

    return minutes_list


minutes_list = get_minutes_list(reversed=True)
today = datetime.datetime.today().strftime('%Y%m%d')

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

# try:
#     TOKEN = get_access_token()
#     txt_path = 'C:/Users/slaye/VscodeProjects/find-a-fdm/2024-2/ydm/env/token.txt'
#     with open(txt_path, 'w') as f:
#         f.write(TOKEN)
# except:
#     txt_path = 'C:/Users/slaye/VscodeProjects/find-a-fdm/2024-2/ydm/env/token.txt'
#     with open(txt_path, 'r') as f:
#         TOKEN = f.read()


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

    TOKEN = get_access_token()
    
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


def check_business_day(TOKEN: str):
    # 휴장일 조회
    '''
    input: date (str) ex) 
    output: Y or N
    '''

    headers = {
        "content-type": "application/json; charset=utf-8",
        "authorization": f"Bearer {TOKEN}",
        "appkey": APP_KEY,
        "appsecret": APP_SECRET,
        "tr_id": "HHMCM000002C0",
        "custtype": "P"
    }
    
    url = "https://openapivts.koreainvestment.com:29443/uapi/domestic-stock/v1/quotations/market-time"

    response = requests.get(url, headers=headers)
    response_json = response.json()
    print(response_json)
    output = response_json['output1']
    business_day_list = [output['date1'], output['date2'], output['date3'], output['date4'], output['date5']]
    today = output['today']
    if today in business_day_list:
        return 'Y'
    else:
        return 'N'




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


def get_index_option_dataframe(TOKEN: str):
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


    n = 0
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


    # call_total_gamma = kospi_call_option_df['gamma_exposure'].sum()
    # put_total_gamma = kospi_put_option_df['gamma_exposure'].sum()

    # print("call total gamma:", call_total_gamma, "put total gamma:", put_total_gamma)

    # print("net GEX:", call_total_gamma - put_total_gamma)
    # print("P/C GEX:", put_total_gamma / call_total_gamma)

    kospi_call_option_df.columns = ['PRODUCT_TYPE', 'SHORT_CODE', 'STANDARD_CODE', 'KOREAN_NAME', 'ATM_DIVISION', 'STRIKE_PRICE', 'EXPIRATION_DATE_CODE', 'UNDERLYING_ASSET_SHORT_CODE', 'UNDERLYING_ASSET_NAME', 'MARKET_CODE', 'EXPIRATION_DATE', 'DELTA', 'GAMMA', 'THETA', 'VEGA', 'RHO', 'OPEN_INTEREST', 'DATE', 'GAMMA_EXPOSURE']
    kospi_put_option_df.columns = ['PRODUCT_TYPE', 'SHORT_CODE', 'STANDARD_CODE', 'KOREAN_NAME', 'ATM_DIVISION', 'STRIKE_PRICE', 'EXPIRATION_DATE_CODE', 'UNDERLYING_ASSET_SHORT_CODE', 'UNDERLYING_ASSET_NAME', 'MARKET_CODE', 'EXPIRATION_DATE', 'DELTA', 'GAMMA', 'THETA', 'VEGA', 'RHO', 'OPEN_INTEREST', 'DATE', 'GAMMA_EXPOSURE']

    return kospi_call_option_df, kospi_put_option_df


def get_fundamental_info(basDd):

    headers = {
        'AUTH_KEY': KRX_API 
    }

    params = {
        'basDd': basDd,
    }
    
    url = 'http://data-dbg.krx.co.kr/svc/apis/idx/kospi_dd_trd'
    response = requests.get(url=url, headers=headers, params=params)
    res_json = response.json()['OutBlock_1']
    res_df = pd.DataFrame(res_json)

    if res_df.empty:
        return res_df

    fundamental_df = res_df[res_df['IDX_NM'] == '코스피 200'].copy()

    return fundamental_df


def get_fundamental_series(start:str, end:str):
    result = pd.DataFrame()
    for date in pd.date_range(start=start, end=end):
        date = date.strftime('%Y%m%d')
        df = get_fundamental_info(date)
        result = pd.concat([result, df], axis=0)
    return result


# 따로 계산하려고 만든 함수 중요 X
def get_index_option_from_krx(basDd:str=(datetime.datetime.now()-datetime.timedelta(days=2)).strftime('%Y%m%d'), include_fundamental:bool=True):
    '''
    한국거래소에서 지수옵션 데이터 가져오기
    '''
    headers = {
        'AUTH_KEY': KRX_API 
    }

    url = 'http://data-dbg.krx.co.kr/svc/apis/drv/opt_bydd_trd'

    params = {
        'basDd': basDd,
    }

    response = requests.get(url=url, headers=headers, params=params)
    print(response.status_code)
    res_json = response.json()['OutBlock_1']
    res_df = pd.DataFrame(res_json)

    # print(res_df)

    kospi_option_df = res_df[res_df['PROD_NM'] == '코스피200 옵션'].copy()
    kospi_option_df.loc[:, 'EXPIRATION_DATE'] = kospi_option_df.loc[:, 'ISU_NM'].apply(lambda x: x.split(' ')[2])
    
    # print(kospi_option_df)

    if include_fundamental:
        fundamental_df = get_fundamental_info(basDd=basDd)
        fundamental_df = fundamental_df[['BAS_DD', 'CLSPRC_IDX']]
        fundamental_df.columns = ['BAS_DD', 'FUNDAMENTAL_CLSPRC']

        kospi_option_df = pd.merge(kospi_option_df, fundamental_df, how='left', left_on='BAS_DD', right_on='BAS_DD')

    return kospi_option_df


'''
무위험이자율 가져오는 함수
'''

def get_interest_df(start: str, end: str=today):
    '''
    start: 시작일자 (예시) 20210101
    end: 종료일자 (예시) 20240101
    '''

    code_dict = {'콜금리':'010101000', 'CD91일':'010502000', '국고채_2년':'010195000'}

    result_df = pd.DataFrame()
    for key, value in code_dict.items():
        url = f'https://ecos.bok.or.kr/api/StatisticSearch/{ECOS_API}/json/kr/1/100000/817Y002/D/{start}/{end}/{value}'
        response = requests.get(url)
        res_df = interest_json_df(response)
        temp_df = res_df[['TIME', 'DATA_VALUE']]
        temp_df = temp_df.set_index('TIME')
        temp_df.columns = [key]
        result_df = pd.concat([result_df, temp_df], axis=1)
    
    return result_df


def interest_json_df(response):
    contents = response.json()['StatisticSearch']['row']
    res_df = pd.DataFrame(contents)
    return res_df

# print(get_interest_df('20200102', '20241202'))


'''
계산함수
'''

### 옵션 + 기초자산 df의 델타, 감마 계산 함수
def cal_greeks(df):
    result = pd.DataFrame()
    isu_list = df['ISU_CD'].unique().tolist()
    df[['TDD_CLSPRC', 'FUNDAMENTAL_CLSPRC']] = df[['NXTDD_BAS_PRC', 'FUNDAMENTAL_CLSPRC']].apply(pd.to_numeric, errors='coerce').copy()

    for isu in isu_list:
        temp_df = df[df['ISU_CD'] == isu].copy()
        temp_df['OPTION_DIFF'] = temp_df['TDD_CLSPRC'].copy().diff()
        temp_df['FUNDA_DIFF'] = temp_df['FUNDAMENTAL_CLSPRC'].copy().diff()
        temp_df['DELTA'] = (temp_df['OPTION_DIFF'] / temp_df['FUNDA_DIFF']).copy()
        temp_df['GAMMA'] = (temp_df['DELTA'].diff() / temp_df['FUNDA_DIFF']).copy()
        result = pd.concat([result, temp_df], axis=0)

    result = result.sort_values(by=['ISU_NM']).copy()
    result = result.reset_index(drop=True).copy()

    return result

