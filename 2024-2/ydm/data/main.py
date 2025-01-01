from json import load
import api
import db

import pandas as pd

import time
import datetime
import schedule

import data
import requests  # 예: 네트워크 관련 예외 처리를 위해


def main():
    TOKEN = api.get_access_token()

    # 오늘이 working day인지 확인
    business_day_flag = api.check_business_day(TOKEN)
    if business_day_flag == 'Y':
        start = time.time()
        print("main start")
        kospi_call, kospi_put = api.get_index_option_dataframe(TOKEN)
        print("update index options...")

        db.update_index_options(kospi_call)
        db.update_index_options(kospi_put)
        
        print(time.time()-start)
        print("done!")

        print("update gamma exposure...")
        option_data = db.load_index_options(datetime.datetime.now().strftime("%Y%m%d"))
        net_gex, pc_gex = data.cal_gamma_exposure(option_data)

        df = pd.DataFrame()
        df['DATE'] = [datetime.datetime.now().strftime("%Y%m%d")]
        df['NET_GEX'] = [net_gex]
        df['PC_GEX'] = [pc_gex]

        db.update_gamma_exposure(df)
        print("done!")

    else:
        print("Today is not a business day.")




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
schedule.every().day.at("20:00").do(run_main_with_retries)
while True:
    schedule.run_pending()
    time.sleep(1)



# # main()
# if __name__ == '__main__':
#     while True:
#         schedule.run_pending()
#         time.sleep(1)

