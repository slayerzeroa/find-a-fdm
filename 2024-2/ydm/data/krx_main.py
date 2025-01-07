
'''
옵션 그릭스 직접 계산
'''
import api as api
import helpful_functions as hf
import db as db
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from QuantLib import Date, SouthKorea

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




# target_date = '20190101'


# while target_date <= '20250107':
#     try:
#     krx_index_option_df = api.get_index_option_from_krx(basDd=target_date, include_fundamental=True)
#     rf = float(api.get_interest_df(start=target_date, end=target_date)['콜금리'])

#     fundamental_price = float(api.get_fundamental_info(krx_index_option_df['BAS_DD'].values[0])['CLSPRC_IDX'])
#     krx_index_option_df['FUNDAMENTAL'] = fundamental_price
#     krx_index_option_df['EXPIRATION_DATE'] = krx_index_option_df['EXPIRATION_DATE'].astype(str)
#     krx_index_option_df['BAS_DD'] = krx_index_option_df['BAS_DD'].astype(str)
#     krx_index_option_df['REMAINING_DAYS'] = krx_index_option_df.apply(lambda x: get_business_days(x['BAS_DD'], x['EXPIRATION_DATE']), axis=1)
#     krx_index_option_df['STRIKE_PRICE'] = krx_index_option_df['ISU_NM'].apply(lambda x: x.split(' ')[-1])
#     krx_index_option_df['STRIKE_PRICE'] = krx_index_option_df['STRIKE_PRICE'].astype(float)
#     krx_index_option_df['NXTDD_BAS_PRC'] = krx_index_option_df['NXTDD_BAS_PRC'].astype(float)
#     krx_index_option_df['IMP_VOLT'] = krx_index_option_df['IMP_VOLT'].astype(float)
#     krx_index_option_df['REMAINING_DAYS'] = krx_index_option_df['REMAINING_DAYS'].astype(float)

#     working_day = 252
#     krx_index_option_df['DELTA'] = krx_index_option_df.apply(lambda x: hf.get_delta(x['FUNDAMENTAL'], x['STRIKE_PRICE'], x['REMAINING_DAYS']/working_day, rf/working_day, x['IMP_VOLT']/100, option_type=x['RGHT_TP_NM']), axis=1)
#     krx_index_option_df['GAMMA'] = krx_index_option_df.apply(lambda x: hf.get_gamma(x['FUNDAMENTAL'], x['STRIKE_PRICE'], x['REMAINING_DAYS']/working_day, rf/working_day, x['IMP_VOLT']/100), axis=1)

#     cols_to_fix = ['TDD_CLSPRC', 'CMPPREVDD_PRC', 'TDD_OPNPRC', 'TDD_HGPRC', 'TDD_LWPRC']
#     for col in cols_to_fix:
#         # '-' 를 np.nan 으로 치환
#         krx_index_option_df[col] = krx_index_option_df[col].replace('-', np.nan)
#         # float로 변환 (에러 발생 시 NaN으로 처리)
#         krx_index_option_df[col] = pd.to_numeric(krx_index_option_df[col], errors='coerce')

#     db.update_krx_index_option(krx_index_option_df)
#     target_date += 1

#     except:
#         target_date+=1
    

#     print('현재 진행:', target_date)



'''
KRX 옵션 데이터 로딩
'''

start_date_str = '20200101'
end_date_str = '20250107'

rf_df = api.get_interest_df(start=start_date_str, end=end_date_str)
rf_df.index = rf_df.index.astype(str)

# 문자열을 datetime 객체로 변환
start_date = datetime.strptime(start_date_str, '%Y%m%d')
end_date   = datetime.strptime(end_date_str, '%Y%m%d')

current_date = start_date

while current_date <= end_date:
    try:
        # 현재 날짜를 YYYYMMDD 문자열로 다시 변환
        target_date_str = current_date.strftime('%Y%m%d')

        # 1) 데이터 불러오기
        krx_index_option_df = api.get_index_option_from_krx(
            basDd=target_date_str,
            include_fundamental=True
        )

        rf = float(rf_df[(rf_df.index == target_date_str)]['콜금리'])  # 무위험 이자율

        fundamental_price = float(api.get_fundamental_info(krx_index_option_df['BAS_DD'].values[0])['CLSPRC_IDX'])
        krx_index_option_df['FUNDAMENTAL'] = fundamental_price
        krx_index_option_df['EXPIRATION_DATE'] = krx_index_option_df['EXPIRATION_DATE'].astype(str)
        krx_index_option_df['BAS_DD'] = krx_index_option_df['BAS_DD'].astype(str)
        krx_index_option_df['REMAINING_DAYS'] = krx_index_option_df.apply(lambda x: get_business_days(x['BAS_DD'], x['EXPIRATION_DATE']), axis=1)
        krx_index_option_df['STRIKE_PRICE'] = krx_index_option_df['ISU_NM'].apply(lambda x: x.split(' ')[-1])
        krx_index_option_df['STRIKE_PRICE'] = krx_index_option_df['STRIKE_PRICE'].astype(float)
        krx_index_option_df['NXTDD_BAS_PRC'] = krx_index_option_df['NXTDD_BAS_PRC'].astype(float)
        krx_index_option_df['IMP_VOLT'] = krx_index_option_df['IMP_VOLT'].astype(float)
        krx_index_option_df['REMAINING_DAYS'] = krx_index_option_df['REMAINING_DAYS'].astype(float)

        working_day = 252
        krx_index_option_df['DELTA'] = krx_index_option_df.apply(lambda x: hf.get_delta(x['FUNDAMENTAL'], x['STRIKE_PRICE'], x['REMAINING_DAYS']/working_day, rf/working_day, x['IMP_VOLT']/100, option_type=x['RGHT_TP_NM']), axis=1)
        krx_index_option_df['GAMMA'] = krx_index_option_df.apply(lambda x: hf.get_gamma(x['FUNDAMENTAL'], x['STRIKE_PRICE'], x['REMAINING_DAYS']/working_day, rf/working_day, x['IMP_VOLT']/100), axis=1)

        cols_to_fix = ['TDD_CLSPRC', 'CMPPREVDD_PRC', 'TDD_OPNPRC', 'TDD_HGPRC', 'TDD_LWPRC']
        for col in cols_to_fix:
            # '-' 를 np.nan 으로 치환
            krx_index_option_df[col] = krx_index_option_df[col].replace('-', np.nan)
            # float로 변환 (에러 발생 시 NaN으로 처리)
            krx_index_option_df[col] = pd.to_numeric(krx_index_option_df[col], errors='coerce')

        db.update_krx_index_option(krx_index_option_df)
        print(f"KOSPI 200 옵션 DB 저장 완료: {current_date}")

        net_gex, pc_gex = hf.cal_gamma_exposure_krx(krx_index_option_df)

        krx_gamma_exposure_df = pd.DataFrame()
        krx_gamma_exposure_df['DATE'] = [target_date_str]
        krx_gamma_exposure_df['NET_GEX'] = [net_gex]
        krx_gamma_exposure_df['PC_GEX'] = [pc_gex]

        db.update_krx_gamma_exposure(krx_gamma_exposure_df)
        print(f"KOSPI 200 옵션 GEX, DB 저장 완료: {current_date}")

    except Exception as e:
        print(f"[오류 발생 - {target_date_str}] {e}")

    finally:
        # 날짜를 하루 증가
        current_date += timedelta(days=1)
        print('현재 진행:', current_date.strftime('%Y-%m-%d'))

# # start_date_str = '20200101'
# # end_date_str = '20250107'

# target_date_str = '20200102'

# # 1) 데이터 불러오기
# krx_index_option_df = api.get_index_option_from_krx(
#     basDd=target_date_str,
#     include_fundamental=True
# )

# rf_df = api.get_interest_df(start=target_date_str, end=target_date_str)
# rf = float(rf_df['콜금리'])  # 무위험 이자율

# fundamental_price = float(api.get_fundamental_info(krx_index_option_df['BAS_DD'].values[0])['CLSPRC_IDX'])
# krx_index_option_df['FUNDAMENTAL'] = fundamental_price
# krx_index_option_df['EXPIRATION_DATE'] = krx_index_option_df['EXPIRATION_DATE'].astype(str)
# krx_index_option_df['BAS_DD'] = krx_index_option_df['BAS_DD'].astype(str)
# krx_index_option_df['REMAINING_DAYS'] = krx_index_option_df.apply(lambda x: get_business_days(x['BAS_DD'], x['EXPIRATION_DATE']), axis=1)
# krx_index_option_df['STRIKE_PRICE'] = krx_index_option_df['ISU_NM'].apply(lambda x: x.split(' ')[-1])
# krx_index_option_df['STRIKE_PRICE'] = krx_index_option_df['STRIKE_PRICE'].astype(float)
# krx_index_option_df['NXTDD_BAS_PRC'] = krx_index_option_df['NXTDD_BAS_PRC'].astype(float)
# krx_index_option_df['IMP_VOLT'] = krx_index_option_df['IMP_VOLT'].astype(float)
# krx_index_option_df['REMAINING_DAYS'] = krx_index_option_df['REMAINING_DAYS'].astype(float)

# working_day = 252
# krx_index_option_df['DELTA'] = krx_index_option_df.apply(lambda x: hf.get_delta(x['FUNDAMENTAL'], x['STRIKE_PRICE'], x['REMAINING_DAYS']/working_day, rf/working_day, x['IMP_VOLT']/100, option_type=x['RGHT_TP_NM']), axis=1)
# krx_index_option_df['GAMMA'] = krx_index_option_df.apply(lambda x: hf.get_gamma(x['FUNDAMENTAL'], x['STRIKE_PRICE'], x['REMAINING_DAYS']/working_day, rf/working_day, x['IMP_VOLT']/100), axis=1)

# cols_to_fix = ['TDD_CLSPRC', 'CMPPREVDD_PRC', 'TDD_OPNPRC', 'TDD_HGPRC', 'TDD_LWPRC']
# for col in cols_to_fix:
#     # '-' 를 np.nan 으로 치환
#     krx_index_option_df[col] = krx_index_option_df[col].replace('-', np.nan)
#     # float로 변환 (에러 발생 시 NaN으로 처리)
#     krx_index_option_df[col] = pd.to_numeric(krx_index_option_df[col], errors='coerce')

# db.update_krx_index_option(krx_index_option_df)
# print(f"KOSPI 200 옵션 DB 저장 완료: {target_date_str}")

# net_gex, pc_gex = hf.cal_gamma_exposure_krx(krx_index_option_df)

# krx_gamma_exposure_df = pd.DataFrame()
# krx_gamma_exposure_df['DATE'] = [datetime.datetime.now().strftime("%Y%m%d")]
# krx_gamma_exposure_df['NET_GEX'] = [net_gex]
# krx_gamma_exposure_df['PC_GEX'] = [pc_gex]

# db.update_krx_gamma_exposure(krx_gamma_exposure_df)
# print(f"KOSPI 200 옵션 GEX, DB 저장 완료: {target_date_str}")