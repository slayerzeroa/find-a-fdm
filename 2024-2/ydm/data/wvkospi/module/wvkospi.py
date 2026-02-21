'''
라이브러리
- 계산 관련
- 날짜 관련
- 통신 관련
- 데이터 관련
'''
import math
from click import option
import pandas as pd
import numpy as np
from scipy import interpolate

from datetime import datetime, timedelta

# import requests as re
# from bs4 import BeautifulSoup

# from pykrx import stock
from module import finance_api
# import finance_api

import re
import pandas as pd


'''
날짜 처리 관련 함수
'''
# 매주 옵션 만기일
# 월요일은 0, 목요일은 3
def nth_weekday(the_date, week_day):
    the_date += timedelta(days=1)
    while the_date.weekday() != week_day:
        the_date += timedelta(days=1)
    return the_date

# 근주물 옵션 만기일 구하기
def get_near_due(mydate:datetime)->datetime:
    # 목요일이 near term
    duedate_t = [0, 1, 2]
    # 월요일이 near term
    duedate_m = [3, 4, 5, 6]

    if mydate.weekday() in duedate_t:
      thisweek_duedate = nth_weekday(mydate, 3)
    else:
      thisweek_duedate = nth_weekday(mydate, 0)

    return thisweek_duedate

# 원주물 옵션 만기일 구하기
def get_next_due(mydate:datetime)->datetime:
    # 목요일이 near term
    duedate_t = [0, 1, 2]
    # 월요일이 near term
    duedate_m = [3, 4, 5, 6]

    if mydate.weekday() in duedate_m:
      mydate += timedelta(days=4)
      thisweek_duedate = nth_weekday(mydate, 3)
    elif mydate.weekday() in duedate_t:
      mydate += timedelta(days=4)
      thisweek_duedate = nth_weekday(mydate, 0)

    return thisweek_duedate

# 날짜 차이 구하기
def date_diff(now, future):
    gap = future - now
    return gap.days



'''
전처리 함수
'''
# 금리 interpolation 함수
def rf_inter(target_date:datetime ,near_date_diff, next_date_diff, interest_df):
    # 금리 interpolation
    interest_data = interest_df[interest_df.index==target_date.strftime('%Y%m%d')]
    x = [1, 91]
    y = [float(interest_data['콜금리'].iloc[0]), float(interest_data['CD91일'].iloc[0])]

    spline_func = interpolate.CubicSpline(x, y)

    y1 = float(spline_func(near_date_diff)) / (60*24*365)
    y2 = float(spline_func(next_date_diff) / (60*24*365))
    return [y1, y2]


# following_two_cutoff 함수
def following_two_cutoff(option_data: pd.DataFrame):
    filter = option_data['STRIKE_PRICE_DIFF'] < 7.5
    filter = list(filter)
    center = int(len(filter) / 2)
    flag = True
    while center != 0:
        if filter[center] == False:
            filter[center] = flag
            flag = False
        else:
            filter[center] = flag
        center -= 1

    center = int(len(filter) / 2)
    flag = True
    while center != (len(filter)-1):
        if filter[center] == False:
            flag = False
        filter[center] = flag
        center += 1

    return filter

# Cutoff 함수
def cutoff(option_data: pd.DataFrame, underlying):
    if option_data['RGHT_TP_NM'].unique() == 'CALL':
        data_cutoff = option_data[following_two_cutoff(option_data)]
        data_cutoff = data_cutoff[data_cutoff['STRIKE_PRICE'].astype(float) > underlying]
    elif option_data['RGHT_TP_NM'].unique() == 'PUT':
        data_cutoff = option_data[following_two_cutoff(option_data)]
        data_cutoff = data_cutoff[data_cutoff['STRIKE_PRICE'].astype(float) < underlying]
    return data_cutoff


# -----------------------------
# 안정 추출 헬퍼
# -----------------------------
def _extract_strike_price(series: pd.Series) -> pd.Series:
    """
    ISU_NM에서 행사가를 안정적으로 추출:
    - " ... 505.0 (정규)" -> 505.0
    - 자릿수 변화(100/1000/10000), 소수점 모두 대응
    """
    s = series.astype(str).str.strip()

    # 1차: 문자열 끝 숫자 + optional "(...)"
    strike = pd.to_numeric(
        s.str.extract(r'(\d+(?:\.\d+)?)\s*(?:\([^)]*\))?\s*$', expand=False),
        errors="coerce"
    )

    # 2차 fallback: 문자열 내 "가장 마지막 숫자"
    miss = strike.isna()
    if miss.any():
        strike.loc[miss] = pd.to_numeric(
            s[miss].str.extract(r'(\d+(?:\.\d+)?)(?!.*\d)', expand=False),
            errors="coerce"
        )

    return strike


def _extract_select(series: pd.Series) -> pd.Series:
    """
    ISU_NM에서 next 선택용 SELECT 추출:
    - 우선: 2510W5 -> 5
    - fallback: W숫자 패턴
    """
    s = series.astype(str).str.strip()

    sel = pd.to_numeric(
        s.str.extract(r'\b\d{4}W(\d+)\b', expand=False),
        errors="coerce"
    )

    miss = sel.isna()
    if miss.any():
        sel.loc[miss] = pd.to_numeric(
            s[miss].str.extract(r'W(\d+)', expand=False),
            errors="coerce"
        )

    return sel

def _extract_session(series: pd.Series) -> pd.Series:
    """
    ISU_NM에서 세션 추출:
    - '(정규)' -> 정규
    - '(야간)' -> 야간
    """
    s = series.astype(str)
    return np.select(
        [
            s.str.contains(r'\(정규\)|\b정규\b', na=False),
            s.str.contains(r'\(야간\)|\b야간\b', na=False),
        ],
        ['정규', '야간'],
        default='기타'
    )


# -----------------------------
# 원래 로직 유지 + Strike/SELECT만 안정화
# -----------------------------
def preprocess_option(option_data: pd.DataFrame, option_type: str):
    option_data = option_data.copy()  # 원본 보호
    # print("option data:", option_data)

    if option_type == 'near':
        term_option = pd.DataFrame()

        # 기존 str[-10:-5] -> 안정 추출
        option_data['STRIKE_PRICE'] = _extract_strike_price(option_data['ISU_NM'])

        option_data['SESSION'] = _extract_session(option_data['ISU_NM'])
        option_data = option_data[option_data['SESSION'] == '정규']


        term_data = []
        for i in option_data['STRIKE_PRICE']:
            check = option_data[option_data['STRIKE_PRICE'] == i]
            if len(check) == 2:
                input_data = []
                input_data.append(float(check['STRIKE_PRICE'].unique()[0]))
                input_data.append(check['TDD_CLSPRC'].to_list()[0])
                input_data.append(check['TDD_CLSPRC'].to_list()[1])
                input_data.append(abs(check['TDD_CLSPRC'].to_list()[0] - check['TDD_CLSPRC'].to_list()[1]))
                if input_data not in term_data:
                    term_data.append(input_data)

        term_option = pd.concat([
            term_option,
            pd.DataFrame(term_data, columns=['STRIKE_PRICE', 'CALL', 'PUT', 'DIFFERENCE'])
        ])
        term_option = term_option[(term_option['CALL'] != 0) & (term_option['PUT'] != 0)]
        return term_option, option_data

    elif option_type == 'next':
        term_option = pd.DataFrame()

        # 기존 str[-10:-5] -> 안정 추출
        option_data['STRIKE_PRICE'] = _extract_strike_price(option_data['ISU_NM'])

        # 기존 str[-12].astype(int) -> 안정 추출
        option_data['SELECT'] = _extract_select(option_data['ISU_NM'])
        option_data['SESSION'] = _extract_session(option_data['ISU_NM'])

        option_data = option_data[option_data['SESSION'] == '정규']


        # SELECT 파싱 성공한 경우에만 max 필터 적용 (실패 시 크래시 방지)
        # SELECT는 당일에 근주물, 근원물 동시 방지
        valid = option_data['SELECT'].notna()
        if valid.any():
            mx = option_data.loc[valid, 'SELECT'].max()
            option_data = option_data[option_data['SELECT'] == mx]


        next_data = []
        for i in option_data['STRIKE_PRICE']:
            check = option_data[option_data['STRIKE_PRICE'] == i]
            if len(check) == 2:
                input_data = []
                input_data.append(float(check['STRIKE_PRICE'].unique()[0]))
                input_data.append(check['TDD_CLSPRC'].to_list()[0])
                input_data.append(check['TDD_CLSPRC'].to_list()[1])
                input_data.append(abs(check['TDD_CLSPRC'].to_list()[0] - check['TDD_CLSPRC'].to_list()[1]))
                if input_data not in next_data:
                    next_data.append(input_data)

        term_option = pd.concat([
            term_option,
            pd.DataFrame(next_data, columns=['STRIKE_PRICE', 'CALL', 'PUT', 'DIFFERENCE'])
        ])
        term_option = term_option[(term_option['CALL'] != 0) & (term_option['PUT'] != 0)]
        return term_option, option_data



'''
데이터 수집 함수
'''

def get_kospi_option_data(t: datetime, near_date: datetime):

    option_df = finance_api.get_weekly_option_df(t.strftime('%Y%m%d'), t.strftime('%Y%m%d'))
    # print(option_df)
    # 옵션 데이터 전처리
    kospi_option_df = option_df[option_df['ISU_NM'].str.contains('코스피')]
    option_data_m = kospi_option_df[kospi_option_df['PROD_NM'].str.contains('월')]
    option_data_t = kospi_option_df[kospi_option_df['PROD_NM'].str.contains('목')]

    # print("option_data_m:", option_data_m)
    # print("option_data_t:", option_data_t)

    option_data_t = option_data_t[option_data_t['TDD_CLSPRC'] != '-']
    option_data_m = option_data_m[option_data_m['TDD_CLSPRC'] != '-']

    option_data_t['TDD_CLSPRC'] = option_data_t['TDD_CLSPRC'].astype(float)
    option_data_m['TDD_CLSPRC'] = option_data_m['TDD_CLSPRC'].astype(float)

    if near_date.weekday() == 0:
        near_option_data = option_data_m
        next_option_data = option_data_t
    else:
        near_option_data = option_data_t
        next_option_data = option_data_m

    return near_option_data, next_option_data

def get_date_data(t: datetime):
    near_date = get_near_due(t)
    next_date = get_next_due(t)

    near_date_diff = date_diff(t, near_date)
    next_date_diff = date_diff(t, next_date)

    return near_date, next_date, near_date_diff, next_date_diff


def get_vkospi(t):
    t = t.strftime("%Y%m%d")
    vkospi_df = finance_api.get_vkospi_spot_df(start=t, end=t)
    # print('vkospi_df', vkospi_df)
    return float(vkospi_df['SPOT_PRC'])

'''
계산 함수
'''
def vix_formula(near_term_option, next_term_option, near_option_data, next_option_data, underlying, rates, near_date_diff, next_date_diff):
    Nt=[60*24*near_date_diff, 60*24*next_date_diff]		#minutes
    T=[Nt[0]/(60*24*365), Nt[1]/(60*24*365)]	#years
    
    F1_data = near_term_option[near_term_option['DIFFERENCE'] == near_term_option['DIFFERENCE'].min()]
    F2_data = next_term_option[next_term_option['DIFFERENCE'] == next_term_option['DIFFERENCE'].min()]

    # print("near term option data:", near_term_option)
    # print("next term option data:", next_term_option)

    # print("F1_data:", F1_data)
    # print("F2_data:", F2_data)

    F1 = float(F1_data['STRIKE_PRICE'].iloc[0] + math.exp(rates[0] * T[0]) * (F1_data['CALL'].iloc[0] - F1_data['PUT'].iloc[0]))
    F2 = float(F2_data['STRIKE_PRICE'].iloc[0] + math.exp(rates[1] * T[1]) * (F2_data['CALL'].iloc[0] - F2_data['PUT'].iloc[0]))

    K_0_1 = near_term_option[(near_term_option['STRIKE_PRICE'].astype(float) - F1 < 1)].DIFFERENCE == near_term_option[(near_term_option['STRIKE_PRICE'].astype(float) - F1 < 1)].DIFFERENCE.min()
    K_0_1 = float((near_term_option[(near_term_option['STRIKE_PRICE'].astype(float) - F1 < 1)][K_0_1].STRIKE_PRICE).iloc[0])
    K_0_2 = next_term_option[(next_term_option['STRIKE_PRICE'].astype(float) - F2 < 1)].DIFFERENCE == next_term_option[(next_term_option['STRIKE_PRICE'].astype(float) - F2 < 1)].DIFFERENCE.min()
    K_0_2 = float((next_term_option[(next_term_option['STRIKE_PRICE'].astype(float) - F2 < 1)][K_0_2].STRIKE_PRICE).iloc[0])

    near_option_data_call = near_option_data[near_option_data['RGHT_TP_NM'] == 'CALL'].copy()
    near_option_data_put = near_option_data[near_option_data['RGHT_TP_NM'] == 'PUT'].copy()
    next_option_data_call = next_option_data[next_option_data['RGHT_TP_NM'] == 'CALL'].copy()
    next_option_data_put = next_option_data[next_option_data['RGHT_TP_NM'] == 'PUT'].copy()

    near_option_data_call['STRIKE_PRICE_DIFF'] = near_option_data_call['STRIKE_PRICE'].astype(float).diff()
    near_option_data_put['STRIKE_PRICE_DIFF'] = near_option_data_put['STRIKE_PRICE'].astype(float).diff()
    next_option_data_call['STRIKE_PRICE_DIFF'] = next_option_data_call['STRIKE_PRICE'].astype(float).diff()
    next_option_data_put['STRIKE_PRICE_DIFF'] = next_option_data_put['STRIKE_PRICE'].astype(float).diff()

    near_call = cutoff(near_option_data_call, underlying)
    near_put = cutoff(near_option_data_put, underlying)
    next_call = cutoff(next_option_data_call, underlying)
    next_put = cutoff(next_option_data_put, underlying)
    near_call['Contribution_by_Strike'] = (2.5/(near_call['STRIKE_PRICE'].astype(float).pow(2))) * math.exp(rates[0] * T[0]) * near_call['TDD_CLSPRC']
    near_put['Contribution_by_Strike'] = (2.5/(near_put['STRIKE_PRICE'].astype(float).pow(2))) * math.exp(rates[0] * T[0]) * near_put['TDD_CLSPRC']
    next_call['Contribution_by_Strike'] = (2.5/(next_call['STRIKE_PRICE'].astype(float).pow(2))) * math.exp(rates[1] * T[1]) * next_call['TDD_CLSPRC']
    next_put['Contribution_by_Strike'] = (2.5/(next_put['STRIKE_PRICE'].astype(float).pow(2))) * math.exp(rates[1] * T[1]) * next_put['TDD_CLSPRC']
    near = pd.concat([near_call, near_put])
    next = pd.concat([next_call, next_put])
    sigmasquared_1 = (2/T[0])*near['Contribution_by_Strike'].sum() - (1/T[0])*((F1/K_0_1)-1)**2
    sigmasquared_2 = (2/T[1])*next['Contribution_by_Strike'].sum() - (1/T[1])*((F2/K_0_2)-1)**2
    N30 = 60*24*5
    N365 = 60*24*365
    VIX = 100 * np.sqrt((T[0]*sigmasquared_1*((Nt[1]-N30)/(Nt[1]-Nt[0]))+T[1]*sigmasquared_2*((N30-Nt[0])/(Nt[1]-Nt[0])))*(N365/N30))
    return VIX


def cal_wvkospi(t: datetime, underlying, rate, rate_target_date: datetime):
    near_date, next_date, near_date_diff, next_date_diff = get_date_data(t)
    rates = rf_inter(rate_target_date, near_date_diff, next_date_diff, rate)
    
    near_option_data, next_option_data = get_kospi_option_data(t, near_date=near_date)

    print("before near option data:", near_option_data)
    print("before next option data:", next_option_data)
    
    near_term_option, near_option_data = preprocess_option(near_option_data, option_type='near')
    next_term_option, next_option_data = preprocess_option(next_option_data, option_type='next')

    print("after near option data:", near_term_option)
    print("after next option data:", next_term_option)

    VIX = vix_formula(near_term_option, next_term_option, near_option_data, next_option_data, underlying, rates, near_date_diff, next_date_diff)

    return VIX




from datetime import timedelta
def get_wvkospi(t: datetime):
    # KRX(옵션/기초자산): D-1, ECOS(금리): D-2
    krx_target_date = t
    ecos_target_date = t - timedelta(days=1)

    underlying = (finance_api.get_kospi_df(krx_target_date.strftime('%Y%m%d'), krx_target_date.strftime('%Y%m%d')))['CLSPRC_IDX'].astype(float).values[0]
    print("underlying:", underlying)
    rate = finance_api.get_interest_df(
        start=ecos_target_date.strftime('%Y%m%d'),
        end=ecos_target_date.strftime('%Y%m%d')
    ).astype(float)
    print("rate:", rate)
    wvkospi = cal_wvkospi(krx_target_date, underlying, rate, rate_target_date=ecos_target_date)
    vkospi = get_vkospi(krx_target_date)

    return underlying, wvkospi, vkospi


# target_date = datetime(2024, 10, 24).date()
# # target_date_str = target_date.strftime('%Y%m%d')
# rate_df = finance_api.get_interest_df(start=target_date.strftime('%Y%m%d'), end=target_date.strftime('%Y%m%d')).astype(float)
# print(cal_wvkospi(target_date, rate_df))
