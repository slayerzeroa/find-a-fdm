from __future__ import annotations

from datetime import date as date_cls, datetime, timedelta
from pathlib import Path
import csv
import json
import time

import requests

from .config import KrxRawConfig
from .models import KospiRelatedEtfDetail, KospiRelatedEtfRatioSummary
from .providers.krx_raw import _extract_output_rows, _fetch_json


FOREIGN_HINTS = [
    "미국",
    "해외",
    "글로벌",
    "중국",
    "차이나",
    "일본",
    "인도",
    "대만",
    "유럽",
    "WORLD",
    "월드",
    "MSCI",
    "브라질",
    "베트남",
    "선진국",
    "신흥국",
    "ASIA",
    "ASEAN",
    "HANG SENG",
    "NIFTY",
    "S&P",
    "NASDAQ",
    "DOW",
    "RUSSELL",
    "NIKKEI",
    "TOPIX",
    "EURO",
    "STOXX",
    "NYSE",
    "BYD",
    "샤오미",
    "XIAOMI",
    "TESLA",
    "테슬라",
    "NVIDIA",
    "엔비디아",
    "PALANTIR",
    "팔란티어",
    "BROADCOM",
    "브로드컴",
    "TSMC",
    "ALIBABA",
    "알리바바",
]

KOSDAQ_HINTS = [
    "코스닥",
    "KOSDAQ",
]

BOND_HINTS = [
    "채권",
    "국채",
    "회사채",
    "통안",
    "머니마켓",
    "MMF",
    "CD금리",
    "전단채",
    "특수채",
    "미국채",
    "국공채",
    "채권혼합",
    "단기금융채",
    "AAA",
    "AA-",
]

REIT_HINTS = [
    "리츠",
    "REIT",
]

COMMODITY_HINTS = [
    "금",
    "골드",
    "금현물",
    "은",
    "원유",
    "에너지",
    "천연가스",
    "구리",
    "농산물",
    "원자재",
    "탄소",
    "배출권",
    "메타버스원자재",
]

ALLOCATION_HINTS = [
    "TDF",
    "TARGET-DATE",
    "TARGET DATE",
    "MULTI ASSET",
    "멀티에셋",
    "자산배분",
    "밸런스",
]

DOMESTIC_EQUITY_HINTS = [
    "코스피",
    "KOSPI",
    "코리아",
    "KOREA",
    "KRX",
    "200",
    "밸류업",
    "배당",
    "고배당",
    "반도체",
    "조선",
    "방산",
    "은행",
    "바이오",
    "화장품",
    "2차전지",
    "배터리",
    "전력",
    "증권",
    "자동차",
    "중소형",
    "대형주",
    "성장주",
    "가치주",
    "KPOP",
    "K-",
    "K반도체",
    "K수출",
    "K휴머노이드",
    "K소버린",
    "그룹주",
    "지주",
    "엔터",
    "게임",
    "플랫폼",
    "인터넷",
    "우주항공",
    "소부장",
    "전력설비",
]


def _to_float(value: object) -> float:
    if value is None:
        return 0.0
    if isinstance(value, (int, float)):
        return float(value)
    text = str(value).strip().replace(",", "")
    return float(text) if text else 0.0


def _has_any(text: str, keywords: list[str]) -> bool:
    upper = text.upper()
    return any(keyword.upper() in upper for keyword in keywords)


def _pick_first(row: dict[str, object], keys: list[str]) -> str:
    for key in keys:
        value = row.get(key)
        if value is not None and str(value).strip():
            return str(value).strip()
    return ""


def classify_kospi_related_etf(*, etf_name: str, index_name: str) -> tuple[bool, str]:
    text = f"{etf_name} {index_name}"

    if _has_any(text, BOND_HINTS):
        return False, "excluded_bond"
    if _has_any(text, REIT_HINTS):
        return False, "excluded_reit"
    if _has_any(text, COMMODITY_HINTS):
        return False, "excluded_commodity"
    if _has_any(text, ALLOCATION_HINTS):
        return False, "excluded_allocation"
    if _has_any(text, FOREIGN_HINTS):
        return False, "excluded_foreign"
    if _has_any(text, KOSDAQ_HINTS):
        return False, "excluded_kosdaq"

    if _has_any(text, DOMESTIC_EQUITY_HINTS):
        return True, "domestic_equity_keyword"

    return False, "excluded_ambiguous"


def summarize_kospi_related_etf_ratio_from_rows(
    *,
    date: str,
    stock_trading_rows: list[dict[str, object]],
    etf_trading_rows: list[dict[str, object]],
) -> KospiRelatedEtfRatioSummary:
    kospi_trading_value = sum(
        _to_float(row.get("ACC_TRDVAL"))
        for row in stock_trading_rows
        if str(row.get("MKT_NM") or "").strip().upper() == "KOSPI"
    )
    if kospi_trading_value <= 0:
        raise ValueError("Market trading value for market 'KOSPI' must be positive.")

    details: list[KospiRelatedEtfDetail] = []
    for row in etf_trading_rows:
        etf_code = _pick_first(row, ["ISU_SRT_CD", "ISU_CD"])
        etf_name = _pick_first(row, ["ISU_NM", "ISU_ABBRV", "ISU_ENG_NM"]) or etf_code
        index_name = _pick_first(row, ["IDX_IND_NM"])
        included, reason = classify_kospi_related_etf(
            etf_name=etf_name,
            index_name=index_name,
        )
        if not included:
            continue
        details.append(
            KospiRelatedEtfDetail(
                etf_code=etf_code,
                etf_name=etf_name,
                index_name=index_name,
                trading_value=_to_float(row.get("ACC_TRDVAL")),
                include_reason=reason,
            )
        )

    selected_total_trading_value = sum(item.trading_value for item in details)
    ratio = selected_total_trading_value / kospi_trading_value

    return KospiRelatedEtfRatioSummary(
        date=date,
        selected_etf_count=len(details),
        selected_total_trading_value=selected_total_trading_value,
        kospi_trading_value=kospi_trading_value,
        ratio=ratio,
        details=details,
    )


def compute_live_kospi_related_etf_ratio(
    *,
    date: str,
    config: KrxRawConfig,
) -> KospiRelatedEtfRatioSummary:
    if not config.has_auth_key:
        raise ValueError("KRX auth key not found. Set KRX_API or KRX_AUTH_KEY.")
    if not config.stock_trading_url:
        raise ValueError("KRX_STOCK_TRADING_URL is required.")
    if not config.etf_trading_url:
        raise ValueError("KRX_ETF_TRADING_URL is required.")

    stock_payload = _fetch_json(
        f"{config.stock_trading_url}?basDd={date}",
        config.auth_key,
    )
    etf_payload = _fetch_json(
        f"{config.etf_trading_url}?basDd={date}",
        config.auth_key,
    )
    stock_rows = _extract_output_rows(stock_payload, config.output_block)
    etf_rows = _extract_output_rows(etf_payload, config.output_block)
    return summarize_kospi_related_etf_ratio_from_rows(
        date=date,
        stock_trading_rows=stock_rows,
        etf_trading_rows=etf_rows,
    )


def export_kospi_related_etf_ratio(
    *,
    date: str,
    config: KrxRawConfig,
    output_path: str | Path,
) -> Path:
    summary = compute_live_kospi_related_etf_ratio(date=date, config=config)
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps(summary.to_dict(), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return output


def _iter_weekdays(start_date: date_cls, end_date: date_cls):
    current = start_date
    while current <= end_date:
        if current.weekday() < 5:
            yield current
        current += timedelta(days=1)


def _parse_date(value: str) -> date_cls:
    return datetime.strptime(value, "%Y%m%d").date()


def _fetch_rows_with_retry(
    *,
    url: str,
    auth_key: str,
    output_block: str,
    attempts: int = 6,
) -> list[dict[str, object]]:
    last_error: Exception | None = None
    for attempt in range(1, attempts + 1):
        try:
            payload = _fetch_json(url, auth_key)
            return _extract_output_rows(payload, output_block)
        except requests.exceptions.RequestException as exc:
            last_error = exc
            if attempt == attempts:
                break
            time.sleep(min(attempt, 5))

    if last_error is not None:
        raise last_error
    return []


def compute_live_kospi_related_etf_ratio_history(
    *,
    start_date: str,
    end_date: str,
    config: KrxRawConfig,
) -> list[dict[str, object]]:
    if not config.has_auth_key:
        raise ValueError("KRX auth key not found. Set KRX_API or KRX_AUTH_KEY.")
    if not config.stock_trading_url:
        raise ValueError("KRX_STOCK_TRADING_URL is required.")
    if not config.etf_trading_url:
        raise ValueError("KRX_ETF_TRADING_URL is required.")

    start = _parse_date(start_date)
    end = _parse_date(end_date)
    if start > end:
        raise ValueError("start_date must be less than or equal to end_date.")

    rows: list[dict[str, object]] = []
    for day in _iter_weekdays(start, end):
        bas_dd = day.strftime("%Y%m%d")
        stock_rows = _fetch_rows_with_retry(
            url=f"{config.stock_trading_url}?basDd={bas_dd}",
            auth_key=config.auth_key,
            output_block=config.output_block,
        )
        etf_rows = _fetch_rows_with_retry(
            url=f"{config.etf_trading_url}?basDd={bas_dd}",
            auth_key=config.auth_key,
            output_block=config.output_block,
        )

        # Skip holidays / non-trading weekdays.
        if not stock_rows or not etf_rows:
            continue

        summary = summarize_kospi_related_etf_ratio_from_rows(
            date=bas_dd,
            stock_trading_rows=stock_rows,
            etf_trading_rows=etf_rows,
        )
        rows.append(
            {
                "date": summary.date,
                "selected_etf_count": summary.selected_etf_count,
                "selected_total_trading_value": summary.selected_total_trading_value,
                "kospi_trading_value": summary.kospi_trading_value,
                "ratio": summary.ratio,
            }
        )

    return rows


def export_kospi_related_etf_ratio_history(
    *,
    start_date: str,
    end_date: str,
    config: KrxRawConfig,
    output_path: str | Path,
    history_rows: list[dict[str, object]] | None = None,
) -> Path:
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)

    if output.suffix.lower() == ".json":
        rows = history_rows
        if rows is None:
            rows = compute_live_kospi_related_etf_ratio_history(
                start_date=start_date,
                end_date=end_date,
                config=config,
            )
        output.write_text(
            json.dumps(rows, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        return output

    fieldnames = [
        "date",
        "selected_etf_count",
        "selected_total_trading_value",
        "kospi_trading_value",
        "ratio",
    ]

    existing_dates: set[str] = set()
    if output.exists():
        with output.open("r", encoding="utf-8-sig", newline="") as handle:
            reader = csv.DictReader(handle)
            for row in reader:
                existing_date = str(row.get("date", "")).strip()
                if existing_date:
                    existing_dates.add(existing_date)

    write_header = not output.exists() or output.stat().st_size == 0
    with output.open("a", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        if write_header:
            writer.writeheader()

        if history_rows is not None:
            for row in history_rows:
                if row["date"] in existing_dates:
                    continue
                writer.writerow(row)
                handle.flush()
            return output

        start = _parse_date(start_date)
        end = _parse_date(end_date)
        if start > end:
            raise ValueError("start_date must be less than or equal to end_date.")

        for day in _iter_weekdays(start, end):
            bas_dd = day.strftime("%Y%m%d")
            if bas_dd in existing_dates:
                continue

            stock_rows = _fetch_rows_with_retry(
                url=f"{config.stock_trading_url}?basDd={bas_dd}",
                auth_key=config.auth_key,
                output_block=config.output_block,
            )
            etf_rows = _fetch_rows_with_retry(
                url=f"{config.etf_trading_url}?basDd={bas_dd}",
                auth_key=config.auth_key,
                output_block=config.output_block,
            )
            if not stock_rows or not etf_rows:
                continue

            summary = summarize_kospi_related_etf_ratio_from_rows(
                date=bas_dd,
                stock_trading_rows=stock_rows,
                etf_trading_rows=etf_rows,
            )
            writer.writerow(
                {
                    "date": summary.date,
                    "selected_etf_count": summary.selected_etf_count,
                    "selected_total_trading_value": summary.selected_total_trading_value,
                    "kospi_trading_value": summary.kospi_trading_value,
                    "ratio": summary.ratio,
                }
            )
            handle.flush()

    return output
