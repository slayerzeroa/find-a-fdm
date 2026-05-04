import pandas as pd
from module import wvkospi, wvkosdaq, db
import datetime
import time
import schedule
from sqlalchemy import create_engine, text


ENGINE = create_engine(
    f"mysql+pymysql://{db.user}:{db.password}@{db.host}:{db.db_port}/{db.db_name}?charset=utf8mb4"
)


def _to_nullable_float(value):
    if value is None:
        return None
    try:
        if pd.isna(value):
            return None
    except Exception:
        pass
    try:
        return float(value)
    except Exception:
        return None


def upsert_wvkospi_row(row: dict):
    query = text(
        """
        INSERT INTO wvkospi (BAS_DD, KOSPI, WVKOSPI, VKOSPI)
        VALUES (:bas_dd, :kospi, :wvkospi, :vkospi)
        ON DUPLICATE KEY UPDATE
            KOSPI = COALESCE(VALUES(KOSPI), KOSPI),
            WVKOSPI = COALESCE(VALUES(WVKOSPI), WVKOSPI),
            VKOSPI = COALESCE(VALUES(VKOSPI), VKOSPI)
        """
    )
    with ENGINE.begin() as conn:
        conn.execute(
            query,
            {
                "bas_dd": row["BAS_DD"],
                "kospi": row["KOSPI"],
                "wvkospi": row["WVKOSPI"],
                "vkospi": row["VKOSPI"],
            },
        )


def upsert_wvkosdaq_row(row: dict):
    query = text(
        """
        INSERT INTO wvkosdaq (BAS_DD, KOSDAQ, WVKOSDAQ, VKOSDAQ)
        VALUES (:bas_dd, :kosdaq, :wvkosdaq, :vkosdaq)
        ON DUPLICATE KEY UPDATE
            KOSDAQ = COALESCE(VALUES(KOSDAQ), KOSDAQ),
            WVKOSDAQ = COALESCE(VALUES(WVKOSDAQ), WVKOSDAQ),
            VKOSDAQ = COALESCE(VALUES(VKOSDAQ), VKOSDAQ)
        """
    )
    with ENGINE.begin() as conn:
        conn.execute(
            query,
            {
                "bas_dd": row["BAS_DD"],
                "kosdaq": row["KOSDAQ"],
                "wvkosdaq": row["WVKOSDAQ"],
                "vkosdaq": row["VKOSDAQ"],
            },
        )


def collect_kospi_row(t: datetime.date):
    row = {
        "BAS_DD": t.strftime("%Y%m%d"),
        "KOSPI": None,
        "WVKOSPI": None,
        "VKOSPI": None,
    }

    try:
        underlying = (
            wvkospi.finance_api
            .get_kospi_df(t.strftime("%Y%m%d"), t.strftime("%Y%m%d"))["CLSPRC_IDX"]
            .astype(float)
            .values[0]
        )
        row["KOSPI"] = _to_nullable_float(underlying)
    except Exception as e:
        print(f"[KOSPI] {t} KOSPI 수집 실패: {e}")

    try:
        row["VKOSPI"] = _to_nullable_float(wvkospi.get_vkospi(t))
    except Exception as e:
        print(f"[KOSPI] {t} VKOSPI 수집 실패: {e}")

    try:
        rate_target_date, rate = wvkospi.get_latest_interest_rate_df(
            t - datetime.timedelta(days=1), lookback_days=14
        )
        if row["KOSPI"] is not None:
            row["WVKOSPI"] = _to_nullable_float(
                wvkospi.cal_wvkospi(
                    t,
                    row["KOSPI"],
                    rate,
                    rate_target_date=rate_target_date,
                )
            )
    except Exception as e:
        print(f"[KOSPI] {t} WVKOSPI 계산 실패: {e}")

    return row


def collect_kosdaq_row(t: datetime.date):
    row = {
        "BAS_DD": t.strftime("%Y%m%d"),
        "KOSDAQ": None,
        "WVKOSDAQ": None,
        "VKOSDAQ": None,
    }

    try:
        underlying = (
            wvkosdaq.finance_api
            .get_kosdaq_df(t.strftime("%Y%m%d"), t.strftime("%Y%m%d"))["CLSPRC_IDX"]
            .astype(float)
            .values[0]
        )
        row["KOSDAQ"] = _to_nullable_float(underlying)
    except Exception as e:
        print(f"[KOSDAQ] {t} KOSDAQ 수집 실패: {e}")

    try:
        row["VKOSDAQ"] = _to_nullable_float(wvkosdaq.get_vkosdaq(t))
    except Exception as e:
        print(f"[KOSDAQ] {t} VKOSDAQ 수집 실패: {e}")

    try:
        rate_target_date, rate = wvkosdaq.get_latest_interest_rate_df(
            t - datetime.timedelta(days=1), lookback_days=14
        )
        if row["KOSDAQ"] is not None:
            row["WVKOSDAQ"] = _to_nullable_float(
                wvkosdaq.cal_wvkosdaq(
                    t,
                    row["KOSDAQ"],
                    rate,
                    rate_target_date=rate_target_date,
                )
            )
    except Exception as e:
        print(f"[KOSDAQ] {t} WVKOSDAQ 계산 실패: {e}")

    return row


def main(kospi=True, kosdaq=True):
    # 현재 날짜/시간
    now = datetime.datetime.now()

    # 기본: KRX 데이터는 D-1 기준일 사용
    t = (now - datetime.timedelta(days=3)).date()

    # KOSPI: t-1 하루만 처리, 일부 결측이어도 가능한 값만 upsert
    if kospi:
        row_kospi = collect_kospi_row(t)
        if all(
            row_kospi[key] is None
            for key in ["KOSPI", "WVKOSPI", "VKOSPI"]
        ):
            print(f"[KOSPI] {t} skip (KOSPI/WVKOSPI/VKOSPI 모두 None)")
        else:
            upsert_wvkospi_row(row_kospi)
            print(pd.DataFrame([row_kospi]))
            print(f"[KOSPI] {t} upsert 완료")

    # KOSDAQ: t-1 하루만 처리, 일부 결측이어도 가능한 값만 upsert
    if kosdaq:
        row_kosdaq = collect_kosdaq_row(t)
        if all(
            row_kosdaq[key] is None
            for key in ["KOSDAQ", "WVKOSDAQ", "VKOSDAQ"]
        ):
            print(f"[KOSDAQ] {t} skip (KOSDAQ/WVKOSDAQ/VKOSDAQ 모두 None)")
        else:
            upsert_wvkosdaq_row(row_kosdaq)
            print(pd.DataFrame([row_kosdaq]))
            print(f"[KOSDAQ] {t} upsert 완료")


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

main(kospi=True, kosdaq=True)

# # 매일 08:00에 실행 (주석/시간 맞춰서 사용)
# schedule.every().day.at("08:00").do(run_main_with_retries)
#
# while True:
#     schedule.run_pending()
#     time.sleep(1)
