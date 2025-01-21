from module import api as api
from module import db as db
import pandas as pd
import numpy as np
from json import load
import time
import datetime
import schedule
import requests  # 예: 네트워크 관련 예외 처리를 위해

'''
매일 업데이트
'''



def main():
    today = datetime.datetime.today() - datetime.timedelta(days=1)
    start_date = today - datetime.timedelta(days=7)
    today_str = today.strftime("%Y%m%d")
    start_str =start_date.strftime("%Y%m%d")

    rf_df = api.get_interest_df(start=start_str, end=today_str)
    rf_df.index = rf_df.index.astype(str)

    # 1) 데이터 불러오기
    rf = float(rf_df[(rf_df.index == today_str)]['콜금리'])  # 무위험 이자율
    krx_index_option_df = api.get_index_option_from_krx(
        basDd=today_str,
        include_fundamental=True,
        rf=rf
    )

    db.update_krx_index_option(krx_index_option_df)
    print(f"KOSPI 200 옵션 DB 저장 완료: {today_str}")

    krx_index_option_df = db.load_krx_index_options(today_str)
    net_gex, pc_gex = api.cal_gamma_exposure_krx(krx_index_option_df)
    market_cap = api.get_index_market_cap(today_str)

    net_gex = float(net_gex / market_cap)

    krx_gamma_exposure_df = pd.DataFrame()
    krx_gamma_exposure_df['DATE'] = [today_str]
    krx_gamma_exposure_df['NET_GEX'] = [net_gex]
    krx_gamma_exposure_df['PC_GEX'] = [pc_gex]

    db.update_krx_gamma_exposure(krx_gamma_exposure_df)
    print(f"KOSPI 200 옵션 GEX, DB 저장 완료: {today_str}")



def run_main_with_retries(max_retries=5, retry_delay=60):
    """
    main()을 실행하되, 실패 시 일정 횟수 재시도.
    그래도 실패하면 스크립트를 죽이지 않고 에러 로그만 남김.
    """
    for attempt in range(1, max_retries + 1):
        try:
            main()
            return  # main() 성공 시 즉시 함수 종료
        except Exception as e:
            print(f"[{attempt}/{max_retries}] 알 수 없는 오류 발생: {e}")
            if attempt < max_retries:
                print(f"{retry_delay}초 후 재시도합니다.")
                time.sleep(retry_delay)
            else:
                print("모든 재시도에 실패했습니다. 다음 스케줄까지 대기합니다.")


print("main.py is executed.")
schedule.every().day.at("16:00").do(run_main_with_retries)
while True:
    schedule.run_pending()
    time.sleep(1)



# '''
# KRX 옵션 데이터 로딩
# '''

# start_date_str = '20250116'
# end_date_str = '20250120'


# rf_df = api.get_interest_df(start=start_date_str, end=end_date_str)
# rf_df.index = rf_df.index.astype(str)

# # 문자열을 datetime 객체로 변환
# start_date = datetime.datetime.strptime(start_date_str, '%Y%m%d')
# end_date   = datetime.datetime.strptime(end_date_str, '%Y%m%d')

# current_date = start_date

# while current_date <= end_date:
#     try:
#         # 현재 날짜를 YYYYMMDD 문자열로 다시 변환
#         target_date_str = current_date.strftime('%Y%m%d')

#         # 1) 데이터 불러오기
#         rf = float(rf_df[(rf_df.index == target_date_str)]['콜금리'])  # 무위험 이자율
#         krx_index_option_df = api.get_index_option_from_krx(
#             basDd=target_date_str,
#             include_fundamental=True,
#             rf=rf
#         )

#         db.update_krx_index_option(krx_index_option_df)
#         print(f"KOSPI 200 옵션 DB 저장 완료: {current_date}")

#         krx_index_option_df = db.load_krx_index_options(target_date_str)
#         net_gex, pc_gex = api.cal_gamma_exposure_krx(krx_index_option_df)
#         market_cap = api.get_index_market_cap(target_date_str)

#         net_gex = float(net_gex / market_cap)

#         krx_gamma_exposure_df = pd.DataFrame()
#         krx_gamma_exposure_df['DATE'] = [target_date_str]
#         krx_gamma_exposure_df['NET_GEX'] = [net_gex]
#         krx_gamma_exposure_df['PC_GEX'] = [pc_gex]

#         db.update_krx_gamma_exposure(krx_gamma_exposure_df)
#         print(f"KOSPI 200 옵션 GEX, DB 저장 완료: {current_date}")

#     except Exception as e:
#         print(f"[오류 발생 - {target_date_str}] {e}")

#     finally:
#         # 날짜를 하루 증가
#         current_date += datetime.timedelta(days=1)
#         print('현재 진행:', current_date.strftime('%Y-%m-%d'))
