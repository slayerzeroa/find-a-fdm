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
# import finance_api


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
    filter = option_data['Strike_Price_Diff'] < 7.5
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
    if option_data['Option_Type'].unique() == 'C':
        data_cutoff = option_data[following_two_cutoff(option_data)]
        data_cutoff = data_cutoff[data_cutoff['Strike_Price'].astype(float) > underlying]
    elif option_data['Option_Type'].unique() == 'P':
        data_cutoff = option_data[following_two_cutoff(option_data)]
        data_cutoff = data_cutoff[data_cutoff['Strike_Price'].astype(float) < underlying]
    return data_cutoff

def preprocess_option(option_data: pd.DataFrame, option_type:str):
    if option_type == 'near':
        term_option = pd.DataFrame()

        option_data['Strike_Price'] = option_data['ISU_NM'].str[-5:]
        option_data['Option_Type'] = option_data['ISU_NM'].str[-14]

        term_data = []
        for i in option_data.Strike_Price:
            check = option_data[option_data.Strike_Price == i]
            if len(check) == 2:
                input_data = []
                # [Strike Price, Call Close, Put Close, Difference]
                input_data.append(float(check['Strike_Price'].unique()[0]))
                input_data.append(check['TDD_CLSPRC'].to_list()[0])
                input_data.append(check['TDD_CLSPRC'].to_list()[1])
                input_data.append(abs(check['TDD_CLSPRC'].to_list()[0]-check['TDD_CLSPRC'].to_list()[1]))
                if input_data not in term_data:
                    term_data.append(input_data)
                else:
                    pass

        term_option = pd.concat([term_option, pd.DataFrame(term_data)])
        term_option.columns = ['Strike_Price', 'Call', 'Put', 'Difference']
        term_option = term_option[(term_option['Call']!=0) & (term_option['Put']!=0)]

        return term_option
    
    elif option_type == 'next':
        term_option = pd.DataFrame()

        option_data['Strike_Price'] = option_data['ISU_NM'].str[-5:]
        option_data['Option_Type'] = option_data['ISU_NM'].str[-14]

        # 월, 목 옵션 동시 존재 에러 해결
        # 예시) 월요일에는 월요일 만기 옵션이 두 종류 존재 (오늘 만기, 다음주 만기)
        # 다음주 만기 옵션 데이터만 남기기 (롤오버)
        option_data['Select'] = (option_data['ISU_NM'].str[-13:-8] + option_data['ISU_NM'].str[-7:-6]).astype(int)
        option_data = option_data[option_data['Select'] == option_data['Select'].max()]

        next_data = []
        for i in option_data.Strike_Price:
            check = option_data[option_data.Strike_Price == i]
            if len(check) == 2:
                input_data = []
                # [Strike Price, Call Close, Put Close, Difference]
                input_data.append(float(check['Strike_Price'].unique()[0]))
                input_data.append(check['TDD_CLSPRC'].to_list()[0])
                input_data.append(check['TDD_CLSPRC'].to_list()[1])
                input_data.append(abs(check['TDD_CLSPRC'].to_list()[0]-check['TDD_CLSPRC'].to_list()[1]))
                if input_data not in next_data:
                    next_data.append(input_data)
                else:
                    pass

        term_option = pd.concat([term_option, pd.DataFrame(next_data)])
        term_option.columns = ['Strike_Price', 'Call', 'Put', 'Difference']
        term_option = term_option[(term_option['Call']!=0) & (term_option['Put']!=0)]
    
        return term_option


'''
데이터 수집 함수
'''

def get_option_data(t: datetime, near_date: datetime):

    option_df = finance_api.get_weekly_option_df(t.strftime('%Y%m%d'), t.strftime('%Y%m%d'))

    # 옵션 데이터 전처리
    option_data_m = option_df[option_df['PROD_NM'].str.contains('월')]
    option_data_t = option_df[option_df['PROD_NM'].str.contains('목')]

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
    return float(vkospi_df['SPOT_PRC'])

'''
계산 함수
'''
def vix_formula(near_term_option, next_term_option, near_option_data, next_option_data, underlying, rates, near_date_diff, next_date_diff):
    Nt=[60*24*near_date_diff, 60*24*next_date_diff]		#minutes
    T=[Nt[0]/(60*24*365), Nt[1]/(60*24*365)]	#years
    
    F1_data = near_term_option[near_term_option['Difference'] == near_term_option['Difference'].min()]
    F2_data = next_term_option[next_term_option['Difference'] == next_term_option['Difference'].min()]

    F1 = float(F1_data['Strike_Price'].iloc[0] + math.exp(rates[0] * T[0]) * (F1_data['Call'].iloc[0] - F1_data['Put'].iloc[0]))
    F2 = float(F2_data['Strike_Price'].iloc[0] + math.exp(rates[1] * T[1]) * (F2_data['Call'].iloc[0] - F2_data['Put'].iloc[0]))

    K_0_1 = near_term_option[(near_term_option['Strike_Price'].astype(float) - F1 < 1)].Difference == near_term_option[(near_term_option['Strike_Price'].astype(float) - F1 < 1)].Difference.min()
    K_0_1 = float((near_term_option[(near_term_option['Strike_Price'].astype(float) - F1 < 1)][K_0_1].Strike_Price).iloc[0])
    K_0_2 = next_term_option[(next_term_option['Strike_Price'].astype(float) - F2 < 1)].Difference == next_term_option[(next_term_option['Strike_Price'].astype(float) - F2 < 1)].Difference.min()
    K_0_2 = float((next_term_option[(next_term_option['Strike_Price'].astype(float) - F2 < 1)][K_0_2].Strike_Price).iloc[0])

    near_option_data_call = near_option_data[near_option_data['Option_Type'] == 'C']
    near_option_data_put = near_option_data[near_option_data['Option_Type'] == 'P']
    next_option_data_call = next_option_data[next_option_data['Option_Type'] == 'C']
    next_option_data_put = next_option_data[next_option_data['Option_Type'] == 'P']

    near_option_data_call = near_option_data_call.copy()
    near_option_data_put = near_option_data_put.copy()
    next_option_data_call = next_option_data_call.copy()
    next_option_data_put = next_option_data_put.copy()

    near_option_data_call['Strike_Price_Diff'] = near_option_data_call['Strike_Price'].astype(float).diff()
    near_option_data_put['Strike_Price_Diff'] = near_option_data_put['Strike_Price'].astype(float).diff()
    next_option_data_call['Strike_Price_Diff'] = next_option_data_call['Strike_Price'].astype(float).diff()
    next_option_data_put['Strike_Price_Diff'] = next_option_data_put['Strike_Price'].astype(float).diff()

    near_call = cutoff(near_option_data_call, underlying)
    near_put = cutoff(near_option_data_put, underlying)
    next_call = cutoff(next_option_data_call, underlying)
    next_put = cutoff(next_option_data_put, underlying)
    near_call['Contribution_by_Strike'] = (2.5/(near_call['Strike_Price'].astype(float).pow(2))) * math.exp(rates[0] * T[0]) * near_call['TDD_CLSPRC']
    near_put['Contribution_by_Strike'] = (2.5/(near_put['Strike_Price'].astype(float).pow(2))) * math.exp(rates[0] * T[0]) * near_put['TDD_CLSPRC']
    next_call['Contribution_by_Strike'] = (2.5/(next_call['Strike_Price'].astype(float).pow(2))) * math.exp(rates[1] * T[1]) * next_call['TDD_CLSPRC']
    next_put['Contribution_by_Strike'] = (2.5/(next_put['Strike_Price'].astype(float).pow(2))) * math.exp(rates[1] * T[1]) * next_put['TDD_CLSPRC']
    near = pd.concat([near_call, near_put])
    next = pd.concat([next_call, next_put])
    sigmasquared_1 = (2/T[0])*near['Contribution_by_Strike'].sum() - (1/T[0])*((F1/K_0_1)-1)**2
    sigmasquared_2 = (2/T[1])*next['Contribution_by_Strike'].sum() - (1/T[1])*((F2/K_0_2)-1)**2
    N30 = 60*24*5
    N365 = 60*24*365
    VIX = 100 * np.sqrt((T[0]*sigmasquared_1*((Nt[1]-N30)/(Nt[1]-Nt[0]))+T[1]*sigmasquared_2*((N30-Nt[0])/(Nt[1]-Nt[0])))*(N365/N30))
    return VIX


def cal_wvkospi(t: datetime, underlying, rate):
    near_date, next_date, near_date_diff, next_date_diff = get_date_data(t)
    rates = rf_inter(t, near_date_diff, next_date_diff, rate)
    near_option_data, next_option_data = get_option_data(t, near_date=near_date)

    near_term_option = preprocess_option(near_option_data, option_type='near')
    next_term_option = preprocess_option(next_option_data, option_type='next')

    VIX = vix_formula(near_term_option, next_term_option, near_option_data, next_option_data, underlying, rates, near_date_diff, next_date_diff)

    return VIX



def get_wvkospi(t: datetime):
    underlying = (finance_api.get_kospi_df(t.strftime('%Y%m%d'), t.strftime('%Y%m%d')))['CLSPRC_IDX'].astype(float).values[0]
    rate = finance_api.get_interest_df(start=t.strftime('%Y%m%d'), end=t.strftime('%Y%m%d')).astype(float)
    wvkospi = cal_wvkospi(t, underlying, rate)

    return underlying, wvkospi


# target_date = datetime(2024, 10, 24).date()
# # target_date_str = target_date.strftime('%Y%m%d')
# rate_df = finance_api.get_interest_df(start=target_date.strftime('%Y%m%d'), end=target_date.strftime('%Y%m%d')).astype(float)
# print(cal_wvkospi(target_date, rate_df))