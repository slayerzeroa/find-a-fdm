from dotenv import load_dotenv
import os
import pandas as pd
import numpy as np
import requests
import json
# from wvkospi import *

import datetime
# import yfinance as yf

'''
환경변수 설정
'''
load_dotenv()
ECOS_API = os.getenv("ECOS_API")
KRX_API = os.getenv("KRX_API")

today = datetime.datetime.today().strftime('%Y%m%d')


# requests headers 설정
headers = {
    'AUTH_KEY': KRX_API 
}


'''
전처리 함수
'''
def json2df(response):
    contents = response.json()['StatisticSearch']['row']
    res_df = pd.DataFrame(contents)
    return res_df


'''
데이터 수집 함수
'''


# def get_kospi_daily_data(start_date, end_date):
#     """
#     코스피(KOSPI) 일별 가격 정보를 받아오는 함수.

#     Parameters:
#         start_date (str): 조회 시작 날짜 (형식: 'YYYY-MM-DD')
#         end_date (str): 조회 종료 날짜 (형식: 'YYYY-MM-DD')

#     Returns:
#         pandas.DataFrame: 코스피 일별 가격 데이터 (날짜, 종가, 시가, 고가, 저가, 거래량)
#     """
#     # KOSPI 지수의 티커 (symbol)
#     kospi_ticker = '^KS200'
    
#     # yfinance에서 데이터 다운로드
#     kospi_data = yf.download(kospi_ticker, start=start_date, end=end_date)

#     # 데이터가 존재할 경우, 데이터프레임 반환
#     # if not kospi_data.empty:
#     #     return kospi_data[['Open', 'High', 'Low', 'Close', 'Volume']]
#     if not kospi_data.empty:
#         return kospi_data
#     else:
#         print("데이터가 없습니다.")
#         return pd.DataFrame()



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
        res_df = json2df(response)
        temp_df = res_df[['TIME', 'DATA_VALUE']]
        temp_df = temp_df.set_index('TIME')
        temp_df.columns = [key]
        result_df = pd.concat([result_df, temp_df], axis=1)
    
    return result_df


def get_weekly_option_df(start: str='20230801', end: str=today):
    '''
    월요일 만기 주간 옵션 신규 상장일
    2023-08-01
    '''
    start_date = datetime.datetime.strptime(start, '%Y%m%d')
    end_date = datetime.datetime.strptime(end, '%Y%m%d')

    result = pd.DataFrame()
    while start_date <= end_date:
        url = f'http://data-dbg.krx.co.kr/svc/apis/drv/opt_bydd_trd?basDd={start_date.strftime("%Y%m%d")}'
        response = requests.get(url=url, headers=headers)
        res_json = response.json()['OutBlock_1']

        res_df = pd.DataFrame(res_json)
        if res_df.empty:
            start_date += datetime.timedelta(days=1)
            continue

        else:
            part_df = res_df[res_df['PROD_NM'].str.contains('위클리')]
            result = pd.concat([result, part_df], axis=0)
            start_date += datetime.timedelta(days=1)

        # print(start_date)

    return result


def get_vkospi_spot_df(start: str='20230801', end: str=today):
    start_date = datetime.datetime.strptime(start, '%Y%m%d')
    end_date = datetime.datetime.strptime(end, '%Y%m%d')

    result = pd.DataFrame()

    while start_date <= end_date:
        url = f'http://data-dbg.krx.co.kr/svc/apis/drv/fut_bydd_trd?basDd={start_date.strftime("%Y%m%d")}'
        response = requests.get(url=url, headers=headers)
        res_json = response.json()['OutBlock_1']

        res_df = pd.DataFrame(res_json)
        if res_df.empty:
            start_date += datetime.timedelta(days=1)
            continue

        else:
            part_df = res_df[res_df['ISU_NM'].str.contains('변동성지수 F')].iloc[0:1, :]
            result = pd.concat([result, part_df], axis=0)
            start_date += datetime.timedelta(days=1)

    result = result[['BAS_DD', 'SPOT_PRC']]

    return result



def get_kospi_df(start: str='20230801', end: str=today):
    '''
    Underlying Index: KOSPI 200
    '''
    start_date = datetime.datetime.strptime(start, '%Y%m%d')
    end_date = datetime.datetime.strptime(end, '%Y%m%d')

    result = pd.DataFrame()
    while start_date <= end_date:
        url = f'http://data-dbg.krx.co.kr/svc/apis/idx/kospi_dd_trd?basDd={start_date.strftime("%Y%m%d")}'
        response = requests.get(url=url, headers=headers)
        res_json = response.json()['OutBlock_1']

        res_df = pd.DataFrame(res_json)
        if res_df.empty:
            start_date += datetime.timedelta(days=1)
            continue

        else:
            part_df = res_df[res_df['IDX_NM'] == '코스피 200']

            result = pd.concat([result, part_df], axis=0)
            start_date += datetime.timedelta(days=1)

        # print(start_date)

    return result


# weekly_df = get_weekly_option_df()

# weekly_df.to_csv('data/weekly_option.csv', index=False)


# weekly_df = pd.read_csv('data/weekly_option.csv')
# # print(weekly_df)

# pd.set_option('display.max_columns', None)

# target_date = str(20230801)

# test_df = weekly_df[weekly_df['BAS_DD'] == int(20230801)]

# # 코스피 데이터 수집
# start_date = '20230801'
# end_date = '20241023'

# start_date = target_date
# end_date = target_date
# underlying = get_kospi_df(start_date, end_date)[['BAS_DD' ,'CLSPRC_IDX']]
# underlying = underlying.set_index('BAS_DD')
# underlying['CLSPRC_IDX'] = underlying['CLSPRC_IDX'].astype(float)

# # 옵션 데이터 전처리
# option_data_m = test_df[test_df['PROD_NM'].str.contains('월')]
# option_data_t = test_df[test_df['PROD_NM'].str.contains('목')]

# option_data_t.dropna(axis = 1, how='all', inplace=True)
# option_data_t.dropna(axis = 0, how='any', inplace=True)
# option_data_m.dropna(axis = 1, how='all', inplace=True)
# option_data_m.dropna(axis = 0, how='any', inplace=True)

# option_data_t = option_data_t[option_data_t['TDD_CLSPRC'] != '-']
# option_data_m = option_data_m[option_data_m['TDD_CLSPRC'] != '-']

# option_data_t['TDD_CLSPRC'] = option_data_t['TDD_CLSPRC'].astype(float)
# option_data_m['TDD_CLSPRC'] = option_data_m['TDD_CLSPRC'].astype(float)


# t = datetime.datetime.strptime(target_date, '%Y%m%d')
# near_date = get_near_due(t)
# next_date = get_next_due(t)


# near_date_diff = date_diff(t, near_date)
# next_date_diff = date_diff(t, next_date)

# # print(near_date_diff)
# # print(next_date_diff)


# rate_df = get_interest_df('20230801', '20241023')
# # print(rate_df)

# rates = rf_inter(t.strftime('%Y%m%d'), near_date_diff, next_date_diff, rate_df)
# # print(rates)


# Nt=[60*24*near_date_diff, 60*24*next_date_diff]		#minutes
# T=[Nt[0]/(60*24*365), Nt[1]/(60*24*365)]	#years

# if near_date.weekday() == 0:
#     near_option_data = option_data_m
#     next_option_data = option_data_t
# else:
#     near_option_data = option_data_t
#     next_option_data = option_data_m

# near_term_option = pd.DataFrame()

# near_option_data['Strike_Price'] = near_option_data['ISU_NM'].str[-5:]
# near_option_data['Option_Type'] = near_option_data['ISU_NM'].str[-14]

# near_data = []
# for i in near_option_data.Strike_Price:
#     check = near_option_data[near_option_data.Strike_Price == i]
#     if len(check) == 2:
#         input_data = []
#         # [Strike Price, Call Close, Put Close, Difference]
#         input_data.append(float(check['Strike_Price'].unique()))
#         input_data.append(check['TDD_CLSPRC'].to_list()[0])
#         input_data.append(check['TDD_CLSPRC'].to_list()[1])
#         input_data.append(abs(check['TDD_CLSPRC'].to_list()[0]-check['TDD_CLSPRC'].to_list()[1]))
#         if input_data not in near_data:
#             near_data.append(input_data)
#         else:
#             pass


# near_term_option = pd.concat([near_term_option, pd.DataFrame(near_data)])


# near_term_option.columns = ['Strike_Price', 'Call', 'Put', 'Difference']
# near_term_option = near_term_option[(near_term_option['Call']!=0) & (near_term_option['Put']!=0)]

# next_term_option = pd.DataFrame()

# next_option_data['Strike_Price'] = next_option_data['ISU_NM'].str[-5:]
# next_option_data['Option_Type'] = next_option_data['ISU_NM'].str[-14]

# # 월, 목 옵션 동시 존재 에러 해결
# # 예시) 월요일에는 월요일 만기 옵션이 두 종류 존재 (오늘 만기, 다음주 만기)
# # 다음주 만기 옵션 데이터만 남기기 (롤오버)
# next_option_data['Select'] = (next_option_data['ISU_NM'].str[-13:-8] + next_option_data['ISU_NM'].str[-7:-6]).astype(int)
# next_option_data = next_option_data[next_option_data['Select'] == next_option_data['Select'].max()]

# next_data = []
# for i in next_option_data.Strike_Price:
#     check = next_option_data[next_option_data.Strike_Price == i]
#     if len(check) == 2:
#         input_data = []
#         # [Strike Price, Call Close, Put Close, Difference]
#         input_data.append(float(check['Strike_Price'].unique()))
#         input_data.append(check['TDD_CLSPRC'].to_list()[0])
#         input_data.append(check['TDD_CLSPRC'].to_list()[1])
#         input_data.append(abs(check['TDD_CLSPRC'].to_list()[0]-check['TDD_CLSPRC'].to_list()[1]))
#         if input_data not in next_data:
#             next_data.append(input_data)
#         else:
#             pass

# next_term_option = pd.concat([next_term_option, pd.DataFrame(next_data)])
# next_term_option.columns = ['Strike_Price', 'Call', 'Put', 'Difference']
# next_term_option = next_term_option[(next_term_option['Call']!=0) & (next_term_option['Put']!=0)]

# F1_data = near_term_option[near_term_option['Difference'] == near_term_option['Difference'].min()]
# F2_data = next_term_option[next_term_option['Difference'] == next_term_option['Difference'].min()]

# F1 = float(F1_data['Strike_Price'] + math.exp(rates[0] * T[0]) * (F1_data['Call'] - F1_data['Put']))
# F2 = float(F2_data['Strike_Price'] + math.exp(rates[1] * T[1]) * (F2_data['Call'] - F2_data['Put']))

# K_0_1 = near_term_option[(near_term_option['Strike_Price'].astype(float) - F1 < 1)].Difference == near_term_option[(near_term_option['Strike_Price'].astype(float) - F1 < 1)].Difference.min()
# K_0_1 = float(near_term_option[(near_term_option['Strike_Price'].astype(float) - F1 < 1)][K_0_1].Strike_Price)
# K_0_2 = next_term_option[(next_term_option['Strike_Price'].astype(float) - F2 < 1)].Difference == next_term_option[(next_term_option['Strike_Price'].astype(float) - F2 < 1)].Difference.min()
# K_0_2 = float(next_term_option[(next_term_option['Strike_Price'].astype(float) - F2 < 1)][K_0_2].Strike_Price)

# near_option_data_call = near_option_data[near_option_data['Option_Type'] == 'C']
# near_option_data_put = near_option_data[near_option_data['Option_Type'] == 'P']
# next_option_data_call = next_option_data[next_option_data['Option_Type'] == 'C']
# next_option_data_put = next_option_data[next_option_data['Option_Type'] == 'P']

# near_option_data_call['Strike_Price_Diff'] = near_option_data_call['Strike_Price'].astype(float).diff()
# near_option_data_put['Strike_Price_Diff'] = near_option_data_put['Strike_Price'].astype(float).diff()
# next_option_data_call['Strike_Price_Diff'] = next_option_data_call['Strike_Price'].astype(float).diff()
# next_option_data_put['Strike_Price_Diff'] = next_option_data_put['Strike_Price'].astype(float).diff()


# underlying = float(underlying[underlying.index == target_date].values[0])


# near_call = cutoff(near_option_data_call, underlying)
# near_put = cutoff(near_option_data_put, underlying)
# next_call = cutoff(next_option_data_call, underlying)
# next_put = cutoff(next_option_data_put, underlying)
# near_call['Contribution_by_Strike'] = (2.5/(near_call['Strike_Price'].astype(float).pow(2))) * math.exp(rates[0] * T[0]) * near_call['TDD_CLSPRC']
# near_put['Contribution_by_Strike'] = (2.5/(near_put['Strike_Price'].astype(float).pow(2))) * math.exp(rates[0] * T[0]) * near_put['TDD_CLSPRC']
# next_call['Contribution_by_Strike'] = (2.5/(next_call['Strike_Price'].astype(float).pow(2))) * math.exp(rates[1] * T[1]) * next_call['TDD_CLSPRC']
# next_put['Contribution_by_Strike'] = (2.5/(next_put['Strike_Price'].astype(float).pow(2))) * math.exp(rates[1] * T[1]) * next_put['TDD_CLSPRC']
# near = pd.concat([near_call, near_put])
# next = pd.concat([next_call, next_put])
# sigmasquared_1 = (2/T[0])*near['Contribution_by_Strike'].sum() - (1/T[0])*((F1/K_0_1)-1)**2
# sigmasquared_2 = (2/T[1])*next['Contribution_by_Strike'].sum() - (1/T[1])*((F2/K_0_2)-1)**2
# N30 = 60*24*5
# N365 = 60*24*365
# WVKOSPI = 100 * np.sqrt((T[0]*sigmasquared_1*((Nt[1]-N30)/(Nt[1]-Nt[0]))+T[1]*sigmasquared_2*((N30-Nt[0])/(Nt[1]-Nt[0])))*(N365/N30))

# print(WVKOSPI)