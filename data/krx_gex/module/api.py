#### 한국투자증권 KIS DEVELOPER

#### 라이브러리 Import
import datetime

import os
import requests
import pandas as pd
import numpy as np
from dotenv import load_dotenv

import json
import math
from QuantLib import Date, SouthKorea




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


# 따로 계산하려고 만든 함수
def get_index_option_from_krx(basDd:str=(datetime.datetime.now()-datetime.timedelta(days=2)).strftime('%Y%m%d'), include_fundamental:bool=True, rf:float=0.03):
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

        
        cols_to_fix = ['TDD_CLSPRC', 'CMPPREVDD_PRC', 'TDD_OPNPRC', 'TDD_HGPRC', 'TDD_LWPRC', 'NXTDD_BAS_PRC']
        for col in cols_to_fix:
            # '-' 를 np.nan 으로 치환
            kospi_option_df[col] = kospi_option_df[col].replace('-', np.nan)
            # float로 변환 (에러 발생 시 NaN으로 처리)
            kospi_option_df[col] = pd.to_numeric(kospi_option_df[col], errors='coerce')


        fundamental_price = float(get_fundamental_info(kospi_option_df['BAS_DD'].values[0])['CLSPRC_IDX'])
        kospi_option_df['FUNDAMENTAL'] = fundamental_price
        kospi_option_df['EXPIRATION_DATE'] = kospi_option_df['EXPIRATION_DATE'].astype(str)
        kospi_option_df['BAS_DD'] = kospi_option_df['BAS_DD'].astype(str)
        kospi_option_df['REMAINING_DAYS'] = kospi_option_df.apply(lambda x: get_business_days(x['BAS_DD'], x['EXPIRATION_DATE']), axis=1)
        kospi_option_df['STRIKE_PRICE'] = kospi_option_df['ISU_NM'].apply(lambda x: x.split(' ')[-1])
        kospi_option_df['STRIKE_PRICE'] = kospi_option_df['STRIKE_PRICE'].astype(float)
        kospi_option_df['NXTDD_BAS_PRC'] = kospi_option_df['NXTDD_BAS_PRC'].astype(float)
        kospi_option_df['IMP_VOLT'] = kospi_option_df['IMP_VOLT'].astype(float)
        kospi_option_df['REMAINING_DAYS'] = kospi_option_df['REMAINING_DAYS'].astype(float)

        working_day = 252
        kospi_option_df['DELTA'] = kospi_option_df.apply(lambda x: get_delta(x['FUNDAMENTAL'], x['STRIKE_PRICE'], x['REMAINING_DAYS']/working_day, rf/working_day, x['IMP_VOLT']/100, option_type=x['RGHT_TP_NM']), axis=1)
        kospi_option_df['GAMMA'] = kospi_option_df.apply(lambda x: get_gamma(x['FUNDAMENTAL'], x['STRIKE_PRICE'], x['REMAINING_DAYS']/working_day, rf/working_day, x['IMP_VOLT']/100), axis=1)


    return kospi_option_df


def get_index_market_cap(basDd:str):
    '''
    코스피 200 market_cap 가져오기
    '''

    headers = {
        'AUTH_KEY': KRX_API 
    }

    url = 'http://data-dbg.krx.co.kr/svc/apis/idx/kospi_dd_trd'

    params = {
        'basDd': basDd,
    }

    response = requests.get(url=url, headers=headers, params=params)
    print(response.status_code)
    res_json = response.json()['OutBlock_1']
    res_df = pd.DataFrame(res_json)

    market_cap = float(res_df[res_df['IDX_NM'] == '코스피 200']['MKTCAP'])

    return market_cap


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








'''
계산 관련 함수
'''

def black_scholes_price(S, K, T, r, sigma, option_type="call"):
    from scipy.stats import norm
    """
    Black-Scholes 모델을 사용하여 옵션 가격을 계산.
    S: 기초자산 가격
    K: 행사가격
    T: 옵션 만기까지의 시간 (연 단위)
    r: 무위험 이자율
    sigma: 변동성 (연 단위)
    option_type: 옵션 종류 ("call" 또는 "put")
    """
    d1 = (math.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * math.sqrt(T))
    d2 = d1 - sigma * math.sqrt(T)
    
    if option_type == "call":
        return S * norm.cdf(d1) - K * math.exp(-r * T) * norm.cdf(d2)
    elif option_type == "put":
        return K * math.exp(-r * T) * norm.cdf(-d2) - S * norm.cdf(-d1)
    else:
        raise ValueError("Invalid option type. Use 'call' or 'put'.")

def get_historical_volatility(data: pd.DataFrame, window=20):
    """
    주어진 주가 데이터로부터 과거 변동성을 계산.
    data: 주가 데이터프레임 (Date, Close 컬럼을 가져야 함)
    window: 이동 평균 창 크기
    """
    data["log_return"] = np.log(data["CLSPRC_IDX"] / data["CLSPRC_IDX"].shift(1))
    data["volatility"] = data["log_return"].rolling(window).std() * np.sqrt(252)
    data = data.dropna()
    return data[["BAS_DD", "volatility"]]

def get_delta(S, K, T, r, sigma, option_type="call"):
    from scipy.stats import norm
    """
    Delta 계산.
    S: 기초자산 가격
    K: 행사가격
    T: 옵션 만기까지의 시간 (연 단위)
    r: 무위험 이자율
    sigma: 변동성 (연 단위)
    option_type: 옵션 종류 ("call" 또는 "put")
    """
    d1 = (math.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * math.sqrt(T))
    if (option_type == "call") or (option_type == "CALL"):
        return norm.cdf(d1)
    elif (option_type == "put") or (option_type == "PUT"):
        return norm.cdf(d1) - 1
    else:
        raise ValueError("Invalid option type. Use 'call' or 'put'.")
    

def get_gamma(S, K, T, r, sigma):
    """
    Gamma 계산.
    S: 기초자산 가격
    K: 행사가격
    T: 옵션 만기까지의 시간 (연 단위)
    r: 무위험 이자율
    sigma: 변동성 (연 단위)
    """
    d1 = (math.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * math.sqrt(T))
    gamma = 1/(sigma * S  * math.sqrt(2*math.pi*T)) * np.exp(-d1**2/2)
    return gamma


def cal_gamma_exposure(option_df: pd.DataFrame):
    '''
    option_df 내 데이터는 모두 같은 날짜의 데이터여야 함.
    '''

    call_df = option_df[option_df['MARKET_CODE'] == 'C']
    put_df = option_df[option_df['MARKET_CODE'] == 'P']

    call_df.loc[:, 'GAMMA_EXPOSURE'] = call_df.loc[:, 'GAMMA_EXPOSURE'].astype(float).copy()
    put_df.loc[:, 'GAMMA_EXPOSURE'] = put_df.loc[:, 'GAMMA_EXPOSURE'].astype(float).copy()


    call_total_gamma = call_df['GAMMA_EXPOSURE'].sum()
    put_total_gamma = put_df['GAMMA_EXPOSURE'].sum()

    net_gex = call_total_gamma - put_total_gamma
    pc_gex = put_total_gamma / call_total_gamma

    return net_gex, pc_gex



def cal_gamma_exposure_krx(option_df: pd.DataFrame):
    '''
    option_df 내 데이터는 모두 같은 날짜의 데이터여야 함.
    '''

    call_df = option_df[option_df['RGHT_TP_NM'] == 'CALL']
    put_df = option_df[option_df['RGHT_TP_NM'] == 'PUT']

    call_df.loc[:, 'GAMMA_EXPOSURE'] = (call_df.loc[:, 'GAMMA'].astype(float) * call_df.loc[:, 'ACC_OPNINT_QTY'].astype(float) * 250000 * call_df.loc[:, 'FUNDAMENTAL'].astype(float)).copy()
    put_df.loc[:, 'GAMMA_EXPOSURE'] = (put_df.loc[:, 'GAMMA'].astype(float) * put_df.loc[:, 'ACC_OPNINT_QTY'].astype(float) * 250000 * put_df.loc[:, 'FUNDAMENTAL'].astype(float)).copy()


    call_total_gamma = call_df['GAMMA_EXPOSURE'].sum()
    put_total_gamma = put_df['GAMMA_EXPOSURE'].sum()

    net_gex = call_total_gamma - put_total_gamma
    pc_gex = put_total_gamma / call_total_gamma

    return net_gex, pc_gex


'''
날짜 관련 함수
'''

## 옵션 만기가 두번째 목요일이니
## 해당 월의 두번째 목요일을 찾아주는 함수
def get_second_thursday(year: int, month: int) -> datetime.datetime:
    # 8일은 최소 "두 번째 주"에 해당
    # (목요일의 weekday() = 3)
    second_thursday = 8 + (3 - datetime.datetime(year, month, 8).weekday()) % 7
    return datetime.datetime(year, month, second_thursday)

## 만기일까지 남은 일수를 계산해주는 함수
def get_remaining_days(from_date: str, to_date: str):
    year = int(to_date[:4])
    month = int(to_date[4:6])
    third_friday = get_second_thursday(year, month)
    today = datetime.datetime.strptime(from_date, '%Y%m%d')
    remaining_days = (third_friday - today).days
    return remaining_days


def get_business_days(from_date: str, to_date: str):
    # 날짜 문자열을 datetime 객체로 변환
    from_date = datetime.datetime.strptime(from_date, '%Y%m%d')

    year = int(to_date[:4])
    month = int(to_date[4:6])
    third_friday = get_second_thursday(year, month)
    to_date = third_friday

    # datetime 객체를 QuantLib Date 객체로 변환
    start_qldate = Date(from_date.day, from_date.month, from_date.year)
    end_qldate = Date(to_date.day, to_date.month, to_date.year)

    # 한국 영업일 달력 생성
    calendar = SouthKorea()

    # 시작일부터 종료일까지 영업일 리스트 생성
    business_days = []
    current_date = start_qldate
    while current_date <= end_qldate:
        if calendar.isBusinessDay(current_date):
            # QuantLib Date 객체를 문자열로 변환
            date_str = datetime.datetime(current_date.year(), current_date.month(), current_date.dayOfMonth()).strftime('%Y%m%d')
            business_days.append(date_str)
        current_date = current_date + 1  # 하루 증가

    return len(business_days)