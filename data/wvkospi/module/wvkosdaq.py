'''
라이브러리
- 계산 관련
- 날짜 관련
- 통신 관련
- 데이터 관련
'''
import math
import pandas as pd
import numpy as np
from scipy import interpolate

from datetime import datetime, timedelta

# import requests as re
# from bs4 import BeautifulSoup

# from pykrx import stock
from module import finance_api

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


def get_latest_interest_rate_df(base_date: datetime, lookback_days: int = 14):
    start_date = (base_date - timedelta(days=lookback_days - 1)).strftime('%Y%m%d')
    end_date = base_date.strftime('%Y%m%d')

    rate_df = finance_api.get_interest_df(start=start_date, end=end_date)
    if rate_df.empty:
        raise ValueError(f"ECOS 금리 데이터가 없습니다. 조회 구간: {start_date}~{end_date}")

    rate_df = rate_df.copy()
    rate_df.index = rate_df.index.astype(str)

    for col in ['콜금리', 'CD91일']:
        rate_df[col] = pd.to_numeric(rate_df[col], errors='coerce')

    valid_rate_df = rate_df[['콜금리', 'CD91일']].dropna()
    if valid_rate_df.empty:
        raise ValueError(f"ECOS 금리 유효 데이터가 없습니다. 조회 구간: {start_date}~{end_date}")

    latest_rate_date_str = valid_rate_df.index.max()
    latest_rate_df = valid_rate_df.loc[[latest_rate_date_str]]
    latest_rate_date = datetime.strptime(latest_rate_date_str, '%Y%m%d')

    return latest_rate_date, latest_rate_df


# following_two_cutoff 함수
def following_two_cutoff(option_data: pd.DataFrame):
    strike_diff = pd.to_numeric(option_data['STRIKE_PRICE_DIFF'], errors='coerce').abs()
    valid_diff = strike_diff[(strike_diff > 0) & strike_diff.notna()]
    step = float(valid_diff.median()) if not valid_diff.empty else 0.0
    threshold = max(7.5, step * 1.5) if step > 0 else 7.5

    filter = (strike_diff <= threshold).fillna(True).tolist()
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
    s = series.astype(str).str.replace(',', '', regex=False).str.strip()

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
    ISU_NM에서 next 선택용 Select 추출:
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


def _extract_expiry_yyyymm(series: pd.Series) -> pd.Series:
    s = series.astype(str).str.strip()
    return pd.to_numeric(
        s.str.extract(r'\b(\d{6})\b', expand=False),
        errors='coerce'
    )


def _second_thursday(year: int, month: int) -> datetime:
    first_day = datetime(year, month, 1)
    first_thu_offset = (3 - first_day.weekday()) % 7
    first_thu = first_day + timedelta(days=first_thu_offset)
    return first_thu + timedelta(days=7)


def _extract_session(series: pd.Series) -> pd.Series:
    """
    ISU_NM에서 세션 추출:
    - 코스닥 데이터는 세션 표기가 없을 수 있으므로 기본값을 정규로 처리
    """
    s = series.astype(str)
    return np.where(s.str.contains(r'야간', na=False), '야간', '정규')


def _pick_side_price(side_df: pd.DataFrame):
    if side_df.empty:
        return None

    vol = pd.to_numeric(
        side_df['ACC_TRDVOL'].astype(str).str.replace(',', '', regex=False).str.strip(),
        errors='coerce'
    )
    if vol.notna().any():
        return float(side_df.loc[vol.idxmax(), 'TDD_CLSPRC'])
    return float(side_df['TDD_CLSPRC'].iloc[0])


def _build_term_option(option_data: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for strike, check in option_data.groupby('STRIKE_PRICE'):
        call_px = _pick_side_price(check[check['RGHT_TP_NM'] == 'CALL'])
        put_px = _pick_side_price(check[check['RGHT_TP_NM'] == 'PUT'])
        if call_px is None or put_px is None:
            continue
        rows.append([float(strike), call_px, put_px, abs(call_px - put_px)])

    term_option = pd.DataFrame(rows, columns=['STRIKE_PRICE', 'CALL', 'PUT', 'DIFFERENCE'])
    if term_option.empty:
        return term_option
    return term_option[(term_option['CALL'] != 0) & (term_option['PUT'] != 0)]


# -----------------------------
# 원래 로직 유지 + Strike/Select만 안정화
# -----------------------------
def preprocess_option(option_data: pd.DataFrame, option_type: str):
    option_data = option_data.copy()  # 원본 보호

    if option_type == 'near':
        # 기존 str[-10:-5] -> 안정 추출
        option_data['STRIKE_PRICE'] = _extract_strike_price(option_data['ISU_NM'])
        option_data['SELECT'] = _extract_select(option_data['ISU_NM'])
        option_data['SESSION'] = _extract_session(option_data['ISU_NM'])
        option_data = option_data[option_data['SESSION'] == '정규']

        valid = option_data['SELECT'].notna()
        if valid.any():
            mx = option_data.loc[valid, 'SELECT'].max()
            option_data = option_data[option_data['SELECT'] == mx]

        term_option = _build_term_option(option_data)
        return term_option, option_data

    elif option_type == 'next':
        # 기존 str[-10:-5] -> 안정 추출
        option_data['STRIKE_PRICE'] = _extract_strike_price(option_data['ISU_NM'])

        # 기존 str[-12].astype(int) -> 안정 추출
        option_data['SELECT'] = _extract_select(option_data['ISU_NM'])
        option_data['SESSION'] = _extract_session(option_data['ISU_NM'])
        option_data = option_data[option_data['SESSION'] == '정규']

        # Select 파싱 성공한 경우에만 max 필터 적용 (실패 시 크래시 방지)
        valid = option_data['SELECT'].notna()
        if valid.any():
            mx = option_data.loc[valid, 'SELECT'].max()
            option_data = option_data[option_data['SELECT'] == mx]

        term_option = _build_term_option(option_data)
        return term_option, option_data



'''
데이터 수집 함수
'''

def get_kosdaq_option_data(t: datetime, near_date: datetime):

    option_df = finance_api.get_option_df(t.strftime('%Y%m%d'), t.strftime('%Y%m%d'))
    # 일반 코스닥150 옵션만 사용 (위클리 제외)
    kosdaq_option_df = option_df[
        option_df['PROD_NM'].astype(str).str.contains('코스닥150 옵션', na=False, regex=False)
    ].copy()

    close_px = pd.to_numeric(
        kosdaq_option_df['TDD_CLSPRC'].astype(str).str.replace(',', '', regex=False).str.strip(),
        errors='coerce'
    )
    base_px = pd.to_numeric(
        kosdaq_option_df['NXTDD_BAS_PRC'].astype(str).str.replace(',', '', regex=False).str.strip(),
        errors='coerce'
    )
    # 코스닥 일반옵션은 거래 미체결이 잦아 종가가 비는 경우가 많아 기준가 fallback 사용
    kosdaq_option_df['TDD_CLSPRC'] = close_px.fillna(base_px)
    kosdaq_option_df = kosdaq_option_df.dropna(subset=['TDD_CLSPRC'])

    kosdaq_option_df['EXPIRY_YYYYMM'] = _extract_expiry_yyyymm(kosdaq_option_df['ISU_NM'])
    kosdaq_option_df = kosdaq_option_df.dropna(subset=['EXPIRY_YYYYMM']).copy()
    kosdaq_option_df['EXPIRY_YYYYMM'] = kosdaq_option_df['EXPIRY_YYYYMM'].astype(int)

    regular_mask = _extract_session(kosdaq_option_df['ISU_NM']) == '정규'
    regular_df = kosdaq_option_df[regular_mask]

    valid_expiries = []
    for exp in sorted(regular_df['EXPIRY_YYYYMM'].unique().tolist()):
        side = regular_df.loc[regular_df['EXPIRY_YYYYMM'] == exp, 'RGHT_TP_NM'].astype(str).unique().tolist()
        if 'CALL' in side and 'PUT' in side:
            valid_expiries.append(exp)

    if len(valid_expiries) < 2:
        raise ValueError(f"코스닥 일반 옵션의 near/next 만기 페어가 부족합니다. date={t}, valid_expiries={valid_expiries}")

    near_expiry = valid_expiries[0]
    next_expiry = valid_expiries[1]

    near_option_data = kosdaq_option_df[kosdaq_option_df['EXPIRY_YYYYMM'] == near_expiry].copy()
    next_option_data = kosdaq_option_df[kosdaq_option_df['EXPIRY_YYYYMM'] == next_expiry].copy()

    near_date = _second_thursday(near_expiry // 100, near_expiry % 100).date()
    next_date = _second_thursday(next_expiry // 100, next_expiry % 100).date()

    return near_option_data, next_option_data, near_date, next_date

def get_date_data(t: datetime):
    near_date = get_near_due(t)
    next_date = get_next_due(t)

    near_date_diff = date_diff(t, near_date)
    next_date_diff = date_diff(t, next_date)

    return near_date, next_date, near_date_diff, next_date_diff


def get_vkosdaq(t):
    t = t.strftime("%Y%m%d")
    vkosdaq_df = finance_api.get_vkosdaq_spot_df(start=t, end=t)
    return float(vkosdaq_df['SPOT_PRC'].iloc[-1])


def _estimate_strike_step(term_option: pd.DataFrame, fallback: float = 25.0) -> float:
    if term_option.empty:
        return fallback
    strikes = term_option['STRIKE_PRICE'].astype(float).sort_values()
    diffs = strikes.diff().abs()
    diffs = diffs[diffs > 0]
    if diffs.empty:
        return fallback
    return float(diffs.median())


def _select_k0_strike(term_option: pd.DataFrame, forward_price: float) -> float:
    strikes = term_option['STRIKE_PRICE'].astype(float)
    lower = strikes[strikes <= forward_price]
    if not lower.empty:
        return float(lower.max())
    return float(strikes.min())

'''
계산 함수
'''
def vix_formula(near_term_option, next_term_option, near_option_data, next_option_data, underlying, rates, near_date_diff, next_date_diff):
    Nt=[60*24*near_date_diff, 60*24*next_date_diff]		#minutes
    T=[Nt[0]/(60*24*365), Nt[1]/(60*24*365)]	#years

    if near_term_option.empty or next_term_option.empty:
        raise ValueError("유효한 근월/원월 옵션 페어 데이터가 부족합니다.")
    
    F1_data = near_term_option[near_term_option['DIFFERENCE'] == near_term_option['DIFFERENCE'].min()]
    F2_data = next_term_option[next_term_option['DIFFERENCE'] == next_term_option['DIFFERENCE'].min()]

    F1 = float(F1_data['STRIKE_PRICE'].iloc[0] + math.exp(rates[0] * T[0]) * (F1_data['CALL'].iloc[0] - F1_data['PUT'].iloc[0]))
    F2 = float(F2_data['STRIKE_PRICE'].iloc[0] + math.exp(rates[1] * T[1]) * (F2_data['CALL'].iloc[0] - F2_data['PUT'].iloc[0]))

    K_0_1 = _select_k0_strike(near_term_option, F1)
    K_0_2 = _select_k0_strike(next_term_option, F2)

    near_step = _estimate_strike_step(near_term_option, fallback=25.0)
    next_step = _estimate_strike_step(next_term_option, fallback=25.0)

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
    near_call['Contribution_by_Strike'] = (near_step/(near_call['STRIKE_PRICE'].astype(float).pow(2))) * math.exp(rates[0] * T[0]) * near_call['TDD_CLSPRC']
    near_put['Contribution_by_Strike'] = (near_step/(near_put['STRIKE_PRICE'].astype(float).pow(2))) * math.exp(rates[0] * T[0]) * near_put['TDD_CLSPRC']
    next_call['Contribution_by_Strike'] = (next_step/(next_call['STRIKE_PRICE'].astype(float).pow(2))) * math.exp(rates[1] * T[1]) * next_call['TDD_CLSPRC']
    next_put['Contribution_by_Strike'] = (next_step/(next_put['STRIKE_PRICE'].astype(float).pow(2))) * math.exp(rates[1] * T[1]) * next_put['TDD_CLSPRC']
    near = pd.concat([near_call, near_put])
    next = pd.concat([next_call, next_put])
    sigmasquared_1 = (2/T[0])*near['Contribution_by_Strike'].sum() - (1/T[0])*((F1/K_0_1)-1)**2
    sigmasquared_2 = (2/T[1])*next['Contribution_by_Strike'].sum() - (1/T[1])*((F2/K_0_2)-1)**2
    N30 = 60*24*5
    N365 = 60*24*365
    VIX = 100 * np.sqrt((T[0]*sigmasquared_1*((Nt[1]-N30)/(Nt[1]-Nt[0]))+T[1]*sigmasquared_2*((N30-Nt[0])/(Nt[1]-Nt[0])))*(N365/N30))
    return VIX


def cal_wvkosdaq(t: datetime, underlying, rate, rate_target_date: datetime):
    near_option_data, next_option_data, near_date, next_date = get_kosdaq_option_data(t, near_date=None)
    near_date_diff = date_diff(t, near_date)
    next_date_diff = date_diff(t, next_date)
    rates = rf_inter(rate_target_date, near_date_diff, next_date_diff, rate)

    near_term_option, near_option_data = preprocess_option(near_option_data, option_type='near')
    next_term_option, next_option_data = preprocess_option(next_option_data, option_type='next')

    VIX = vix_formula(near_term_option, next_term_option, near_option_data, next_option_data, underlying, rates, near_date_diff, next_date_diff)

    return VIX



def get_wvkosdaq(t: datetime):
    # KRX(옵션/기초자산): D-1, ECOS(금리): D-2
    krx_target_date = t
    ecos_target_date = t - timedelta(days=1)

    underlying = (finance_api.get_kosdaq_df(krx_target_date.strftime('%Y%m%d'), krx_target_date.strftime('%Y%m%d')))['CLSPRC_IDX'].astype(float).values[0]
    rate_target_date, rate = get_latest_interest_rate_df(ecos_target_date, lookback_days=14)
    wvkosdaq = cal_wvkosdaq(krx_target_date, underlying, rate, rate_target_date=rate_target_date)

    return underlying, wvkosdaq
