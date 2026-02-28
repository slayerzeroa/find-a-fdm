import pandas as pd
from module import wvkospi, wvkosdaq, db
import datetime
import time
import schedule
from sqlalchemy import create_engine, text


KOSDAQ_BACKFILL_START = datetime.date(2025, 10, 28)


def upsert_vkosdaq(df_vkosdaq: pd.DataFrame):
    engine = create_engine(
        f"mysql+pymysql://{db.user}:{db.password}@{db.host}:{db.db_port}/{db.db_name}?charset=utf8mb4"
    )
    query = text(
        """
        INSERT INTO wvkosdaq (BAS_DD, VKOSDAQ)
        VALUES (:bas_dd, :vkosdaq)
        ON DUPLICATE KEY UPDATE
            VKOSDAQ = VALUES(VKOSDAQ)
        """
    )
    with engine.begin() as conn:
        for _, row in df_vkosdaq.iterrows():
            conn.execute(
                query,
                {
                    "bas_dd": str(row["BAS_DD"]),
                    "vkosdaq": float(row["VKOSDAQ"]),
                },
            )


def main(kospi=True, kosdaq=True):
    # 현재 날짜/시간
    now = datetime.datetime.now()

    # 기본: KRX 데이터는 D-1 기준일 사용
    t = (now - datetime.timedelta(days=1)).date()

    # KOSPI
    if kospi:
        underlying_kospi, target_kospi, vkospi = wvkospi.get_wvkospi(t=t)
        df_kospi = pd.DataFrame({
            "BAS_DD": [t.strftime("%Y%m%d")],
            "KOSPI": [underlying_kospi],
            "WVKOSPI": [target_kospi],
            "VKOSPI": [vkospi],
        })
        db.update_wvkospi(df_kospi)
        print(df_kospi)
        print(f"[KOSPI] {t} 업데이트 완료")

    # KOSDAQ: 2025-10-28부터 백필
    if kosdaq:
        current = KOSDAQ_BACKFILL_START
        while current <= t:
            try:
                _, vkosdaq = wvkosdaq.get_wvkosdaq(t=current)
                df_vkosdaq = pd.DataFrame({
                    "BAS_DD": [current.strftime("%Y%m%d")],
                    "VKOSDAQ": [vkosdaq],
                })
                upsert_vkosdaq(df_vkosdaq)
                print(df_vkosdaq)
                print(f"[VKOSDAQ] {current} 업데이트 완료")
            except Exception as e:
                print(f"[VKOSDAQ] {current} 수집 실패: {e}")
            current += datetime.timedelta(days=1)


def run_main_with_retries(max_retries=5, retry_delay=60):
    """
    main()을 실행하되, 실패 시 일정 횟수 재시도.
    그래도 실패하면 스크립트를 죽이지 않고 에러 로그만 남김.
    """
    for attempt in range(1, max_retries + 1):
        try:
            main(kospi=False, kosdaq=True)
            return
        except Exception as e:
            print(f"[{attempt}/{max_retries}] 알 수 없는 오류 발생: {e}")
            if attempt < max_retries:
                print(f"{retry_delay}초 후 재시도합니다.")
                time.sleep(retry_delay)
            else:
                print("모든 재시도에 실패했습니다. 다음 스케줄까지 대기합니다.")


print("main.py is executed.")

main(kospi=False, kosdaq=True)

# # 매일 08:00에 실행 (주석/시간 맞춰서 사용)
# schedule.every().day.at("08:00").do(run_main_with_retries)
#
# while True:
#     schedule.run_pending()
#     time.sleep(1)
