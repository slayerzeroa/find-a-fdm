# # import datetime
# # import time

# # import os
# # import json
# # from tracemalloc import start

# # from arrow import get
# # import requests
# # import pandas as pd
# # import numpy as np
# # from dotenv import load_dotenv

# # from data.db import update_stock_options_daily_data


# # #### 환경변수 세팅
# # load_dotenv(dotenv_path='C:/Users/slaye/VscodeProjects/find-a-fdm/2024-2/ydm/env/.env')
# # APP_KEY = os.getenv("APP_KEY")
# # APP_SECRET = os.getenv("APP_SECRET")
# # KRX_API = os.getenv("KRX_API")  


# # def get_stock_list(market:str='KOSPI', date:str=(datetime.datetime.now())):
# #     '''
# #     market에 따른 종목코드 리스트 반환
# #     '''
# #     ## 근데 왜 당일 데이터가 안나오지?
# #     if market == 'KOSPI' or market == 'kospi' or market == '코스피':
# #         market_code = 'stk'
# #     elif market == 'KOSDAQ' or market == 'kosdaq' or market == '코스닥':
# #         market_code = 'ksq'
# #     else:
# #         return 'Invalid market code'
        
# #     headers = {
# #         'AUTH_KEY': KRX_API 
# #     }

# #     url = f'http://data-dbg.krx.co.kr/svc/apis/sto/{market_code}_isu_base_info?basDd={date}'

# #     response = requests.get(url=url, headers=headers)
# #     res_json = response.json()['OutBlock_1']
# #     res_df = pd.DataFrame(res_json)

# #     stock_list = res_df['ISU_SRT_CD'].tolist()

# #     return stock_list



# # def get_option_data(date:str=(datetime.datetime.now())):
# #     '''
# #     파생상품시장의 주식옵션 중 기초자산이 유가증권시장에 속하는 주식옵션의 거래정보 제공
# #     '''
# #     headers = {
# #         'AUTH_KEY': KRX_API
# #     }

# #     url = f'http://data-dbg.krx.co.kr/svc/apis/drv/eqsop_bydd_trd?basDd={date}'

# #     response = requests.get(url=url, headers=headers)
# #     res_json = response.json()['OutBlock_1']
# #     res_df = pd.DataFrame(res_json)

# #     return res_df




# # start_date = "20100415"


# # while start_date != "20241006":
# #     data = get_option_data(date=start_date)

# #     if data.empty:
# #         print(f"{start_date}에 해당하는 데이터가 없습니다.")
# #         pass
# #     else:
# #         print(f"{start_date}에 해당하는 데이터 업데이트 중...")
# #         update_stock_options_daily_data(data)
    
# #     start_date = get(start_date).shift(days=1).format("YYYYMMDD")

# #     time.sleep(4)


# import pandas as pd
# from data.api import *
# from data.db import *
# from data.helpful_functions import *


# pd.set_option('display.max_columns', None)

# result_df = pd.DataFrame()

# basDd = "20241007"

# for i in range(1, 10):
#     try:
#         option_df = get_index_option_from_krx(basDd=basDd, include_fundamental=True)
#         result_df = pd.concat([result_df, option_df])
#         basDd = get(basDd).shift(days=1).format("YYYYMMDD")
#     except:
#         print(f"{basDd}에 해당하는 데이터가 없습니다.")
#         basDd = get(basDd).shift(days=1).format("YYYYMMDD")


# test_df = cal_greeks(result_df)

# # print(test_df)


# print(test_df.iloc[230:239, :])


from click import option
from matplotlib.pyplot import hist
import data.api as api
import data.data as data
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from QuantLib import Date, SouthKorea
import math



# option_df = api.get_index_option_from_krx(basDd='20241101', include_fundamental=True)

# option_df.to_csv('option_data.csv', index=False)


## 옵션 만기가 세번째 금요일이니
## 해당 월의 세번째 금요일을 찾아주는 함수
def get_third_friday(year: int, month: int):
    # The 15th is the lowest third Friday can be
    third_friday = 15 + (4 - datetime(year, month, 15).weekday()) % 7
    return datetime(year, month, third_friday)

## 만기일까지 남은 일수를 계산해주는 함수
def get_remaining_days(from_date: str, to_date: str):
    year = int(to_date[:4])
    month = int(to_date[4:6])
    third_friday = get_third_friday(year, month)
    today = datetime.strptime(from_date, '%Y%m%d')
    remaining_days = (third_friday - today).days
    return remaining_days


def get_business_days(from_date: str, to_date: str):
    # 날짜 문자열을 datetime 객체로 변환
    from_date = datetime.strptime(from_date, '%Y%m%d')

    year = int(to_date[:4])
    month = int(to_date[4:6])
    third_friday = get_third_friday(year, month)
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
            date_str = datetime(current_date.year(), current_date.month(), current_date.dayOfMonth()).strftime('%Y%m%d')
            business_days.append(date_str)
        current_date = current_date + 1  # 하루 증가

    return len(business_days)



option_df = pd.read_csv('option_data.csv')

fundamental_price = float(api.get_fundamental_info(option_df['BAS_DD'].values[0])['CLSPRC_IDX'])
# fundamental_price = float(api.get_fundamental_info('20241104')['OPNPRC_IDX'])
option_df['FUNDAMENTAL'] = fundamental_price
option_df['EXPIRATION_DATE'] = option_df['EXPIRATION_DATE'].astype(str)
option_df['BAS_DD'] = option_df['BAS_DD'].astype(str)
option_df['REMAINING_DAYS'] = option_df.apply(lambda x: get_business_days(x['BAS_DD'], x['EXPIRATION_DATE']), axis=1)
option_df['STRIKE_PRICE'] = option_df['ISU_NM'].apply(lambda x: x.split(' ')[-1])
option_df['STRIKE_PRICE'] = option_df['STRIKE_PRICE'].astype(float)
# pd.set_option('display.max_columns', None)

option_df['NXTDD_BAS_PRC'] = option_df['NXTDD_BAS_PRC'].astype(float)
option_df['IMP_VOLT'] = option_df['IMP_VOLT'].astype(float)
option_df['REMAINING_DAYS'] = option_df['REMAINING_DAYS'].astype(float)

working_day = 252
option_df['DELTA'] = option_df.apply(lambda x: data.get_delta(x['FUNDAMENTAL'], x['STRIKE_PRICE'], x['REMAINING_DAYS']/working_day, 0.03/working_day, x['IMP_VOLT']/100, option_type=x['RGHT_TP_NM']), axis=1)
option_df['GAMMA'] = option_df.apply(lambda x: data.get_gamma(x['FUNDAMENTAL'], x['STRIKE_PRICE'], x['REMAINING_DAYS']/working_day, 0.03/working_day, x['IMP_VOLT']/100), axis=1)

test_call_df = pd.read_csv('2024-2/ydm/data/kospi_call_option.csv')
test_put_df = pd.read_csv('2024-2/ydm/data/kospi_put_option.csv')

test_df = pd.concat([test_call_df, test_put_df])


ttest_df = test_df[['단축코드', 'delta', 'gamma']]

ooption_df = option_df[['ISU_CD', 'DELTA', 'GAMMA']]

ttest_df = ttest_df.sort_values(by='단축코드')
ooption_df = ooption_df.sort_values(by='ISU_CD')


from arrow import get
pd.set_option('display.max_columns', None)

result_df = pd.DataFrame()

basDd = "20241030"

for i in range(1, 4):
    try:
        option_df = api.get_index_option_from_krx(basDd=basDd, include_fundamental=True)
        result_df = pd.concat([result_df, option_df])
        basDd = get(basDd).shift(days=1).format("YYYYMMDD")
    except:
        print(f"{basDd}에 해당하는 데이터가 없습니다.")
        basDd = get(basDd).shift(days=1).format("YYYYMMDD")


print(result_df)


test_df = api.cal_greeks(result_df)

test_df = test_df[test_df['BAS_DD'] == '20241101']

test_df = test_df[['ISU_CD', 'DELTA', 'GAMMA']]

print('Target Data')
print(ttest_df.iloc[230:239, :])

print('Using BSM')
print(ooption_df.iloc[230:239, :])

print('Using Discrete Difference')
print(test_df.iloc[230:239, :])