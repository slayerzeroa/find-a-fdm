import pandas as pd
from module import wvkospi, wvkosdaq, db
import datetime
import time
import schedule


def main(kospi=True, kosdaq=True):
    # 현재 날짜/시간
    now = datetime.datetime.now()

    # 기본: KRX 데이터는 D-1 기준일 사용
    t = (now - datetime.timedelta(days=1)).date()

    # # 월요일이면 금요일 데이터 기준(D-3)
    # if now.weekday() == 0:
    #     t = (now - datetime.timedelta(days=3)).date()

    # KOSPI
    if kospi:
        underlying_kospi, target_kospi, vkospi = wvkospi.get_wvkospi(t=t)
        df_kospi = pd.DataFrame({
            'BAS_DD': [t.strftime('%Y%m%d')],
            'KOSPI': [underlying_kospi],
            'WVKOSPI': [target_kospi],
            'VKOSPI': [vkospi]
        })
        db.update_wvkospi(df_kospi)
        print(f"[KOSPI] {t} 업데이트 완료")

    # KOSDAQ
    if kosdaq:
        underlying_kosdaq, target_kosdaq = wvkosdaq.get_wvkosdaq(t=t)
        df_kosdaq = pd.DataFrame({
            'BAS_DD': [t.strftime('%Y%m%d')],
            'KOSDAQ': [underlying_kosdaq],
            'WVKOSDAQ': [target_kosdaq]
        })
        db.update_wvkosdaq(df_kosdaq)
        print(f"[KOSDAQ] {t} 업데이트 완료")


def run_main_with_retries(max_retries=5, retry_delay=60):
    """
    main()을 실행하되, 실패 시 일정 횟수 재시도.
    그래도 실패하면 스크립트를 죽이지 않고 에러 로그만 남김.
    """
    for attempt in range(1, max_retries + 1):
        try:
            main(kospi=True, kosdaq=True)   # 여기서 둘 다 실행
            return
        except Exception as e:
            print(f"[{attempt}/{max_retries}] 알 수 없는 오류 발생: {e}")
            if attempt < max_retries:
                print(f"{retry_delay}초 후 재시도합니다.")
                time.sleep(retry_delay)
            else:
                print("모든 재시도에 실패했습니다. 다음 스케줄까지 대기합니다.")


print("main.py is executed.")

# 매일 08:00에 실행 (주석/시간 맞춰서 사용)
schedule.every().day.at("08:00").do(run_main_with_retries)

while True:
    schedule.run_pending()
    time.sleep(1)
