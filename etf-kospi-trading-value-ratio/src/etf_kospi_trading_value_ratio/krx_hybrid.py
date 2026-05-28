from __future__ import annotations

from pathlib import Path
import csv
import json

from .calculator import compute_daily_ratio
from .config import KrxRawConfig
from .models import (
    DailyRatioResult,
    DailySnapshot,
    EtfHoldingRecord,
    EtfMasterRecord,
    EtfTradingRecord,
    MarketTradingRecord,
    StockMasterRecord,
)
from .providers.krx_raw import _build_request_url, _extract_output_rows, _fetch_json
from .storage import save_result


def _to_float(value: object) -> float:
    if value is None:
        return 0.0
    if isinstance(value, (int, float)):
        return float(value)
    text = str(value).strip().replace(",", "")
    return float(text) if text else 0.0


def _normalize_text(value: object) -> str:
    return str(value).strip()


def _load_holdings_rows(path: str | Path) -> list[dict[str, object]]:
    file_path = Path(path)
    suffix = file_path.suffix.lower()

    if suffix == ".json":
        payload = json.loads(file_path.read_text(encoding="utf-8"))
        if not isinstance(payload, list):
            raise ValueError("Canonical holdings JSON must be a list.")
        return [dict(row) for row in payload if isinstance(row, dict)]

    if suffix == ".csv":
        rows: list[dict[str, object]] = []
        with file_path.open("r", encoding="utf-8-sig", newline="") as handle:
            reader = csv.DictReader(handle)
            for row in reader:
                rows.append(dict(row))
        return rows

    raise ValueError(f"Unsupported holdings file type: {file_path}")


def _resolve_holdings_rows(
    holdings_rows: list[dict[str, object]],
    *,
    etf_name_to_code: dict[str, str],
) -> list[EtfHoldingRecord]:
    results: list[EtfHoldingRecord] = []
    missing_names: set[str] = set()

    lowered_name_to_code = {
        key.casefold(): value for key, value in etf_name_to_code.items()
    }

    for row in holdings_rows:
        etf_code = _normalize_text(row.get("etf_code", ""))
        etf_name = _normalize_text(row.get("etf_name", ""))
        stock_code = _normalize_text(row.get("stock_code", ""))
        weight = _to_float(row.get("weight"))

        if not etf_code:
            if etf_name:
                etf_code = etf_name_to_code.get(etf_name) or lowered_name_to_code.get(
                    etf_name.casefold(), ""
                )
            if not etf_code:
                missing_names.add(etf_name or "<blank>")
                continue

        if not stock_code:
            raise ValueError("Each holdings row must include stock_code.")

        results.append(
            EtfHoldingRecord(
                etf_code=etf_code,
                stock_code=stock_code,
                weight=weight,
            )
        )

    if missing_names:
        sample = ", ".join(sorted(missing_names)[:5])
        raise ValueError(
            "Some holdings rows could not be resolved to live KRX ETF codes by etf_name. "
            f"Examples: {sample}"
        )

    return results


def _pick_first(row: dict[str, object], keys: list[str]) -> str:
    for key in keys:
        value = row.get(key)
        if value is not None and str(value).strip():
            return str(value).strip()
    return ""


def _fetch_rows(url: str | None, *, date: str, config: KrxRawConfig) -> list[dict[str, object]]:
    if not url:
        raise ValueError("Required KRX endpoint URL is missing.")

    payload = _fetch_json(
        _build_request_url(url, date=date),
        config.auth_key,
    )
    return _extract_output_rows(payload, config.output_block)


def build_snapshot_from_krx_rows(
    *,
    date: str,
    stock_master_rows: list[dict[str, object]],
    stock_trading_rows: list[dict[str, object]],
    etf_trading_rows: list[dict[str, object]],
    holdings: list[EtfHoldingRecord],
) -> DailySnapshot:
    stocks = [
        StockMasterRecord(
            stock_code=_pick_first(row, ["ISU_SRT_CD", "ISU_CD"]),
            market=_pick_first(row, ["MKT_TP_NM", "MKT_NM", "MKT_TP"]).upper(),
        )
        for row in stock_master_rows
        if _pick_first(row, ["ISU_SRT_CD", "ISU_CD"])
    ]

    etfs: list[EtfMasterRecord] = []
    etf_trading: list[EtfTradingRecord] = []
    for row in etf_trading_rows:
        etf_code = _pick_first(row, ["ISU_SRT_CD", "ISU_CD"])
        if not etf_code:
            continue
        etf_name = _pick_first(row, ["ISU_NM", "ISU_ABBRV", "ISU_ENG_NM"]) or etf_code
        etfs.append(EtfMasterRecord(etf_code=etf_code, etf_name=etf_name))
        etf_trading.append(
            EtfTradingRecord(
                etf_code=etf_code,
                trading_value=_to_float(row.get("ACC_TRDVAL")),
            )
        )

    denominator = sum(_to_float(row.get("ACC_TRDVAL")) for row in stock_trading_rows)
    market_trading = [MarketTradingRecord(market="KOSPI", trading_value=denominator)]

    return DailySnapshot(
        date=date,
        stocks=stocks,
        etfs=etfs,
        holdings=holdings,
        etf_trading=etf_trading,
        market_trading=market_trading,
    )


def fetch_live_etf_catalog(
    *,
    date: str,
    config: KrxRawConfig,
) -> list[dict[str, object]]:
    if not config.has_auth_key:
        raise ValueError("KRX auth key not found. Set KRX_API or KRX_AUTH_KEY.")
    if not config.etf_trading_url:
        raise ValueError(
            "KRX_ETF_TRADING_URL is required. Set it to your approved ETF daily trading endpoint."
        )

    rows = _fetch_rows(config.etf_trading_url, date=date, config=config)
    catalog: list[dict[str, object]] = []
    for row in rows:
        code = _pick_first(row, ["ISU_SRT_CD", "ISU_CD"])
        name = _pick_first(row, ["ISU_NM", "ISU_ABBRV", "ISU_ENG_NM"])
        if not code:
            continue
        catalog.append(
            {
                "date": date,
                "etf_code": code,
                "etf_name": name or code,
            }
        )
    return catalog


def export_live_etf_catalog(
    *,
    date: str,
    config: KrxRawConfig,
    output_path: str | Path,
) -> Path:
    catalog = fetch_live_etf_catalog(date=date, config=config)
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)

    if output.suffix.lower() == ".json":
        output.write_text(
            json.dumps(catalog, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        return output

    with output.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["date", "etf_code", "etf_name"])
        writer.writeheader()
        writer.writerows(catalog)
    return output


def compute_from_krx_plus_holdings(
    *,
    date: str,
    holdings_path: str | Path,
    config: KrxRawConfig,
    db_path: str | Path | None = None,
    rule: str,
    min_kospi_weight_sum: float,
) -> DailyRatioResult:
    if not config.has_auth_key:
        raise ValueError("KRX auth key not found. Set KRX_API or KRX_AUTH_KEY.")
    if not config.etf_trading_url:
        raise ValueError(
            "KRX_ETF_TRADING_URL is required. Set it to your approved ETF daily trading endpoint."
        )

    stock_master_rows = _fetch_rows(config.stock_master_url, date=date, config=config)
    stock_trading_rows = _fetch_rows(config.stock_trading_url, date=date, config=config)
    etf_trading_rows = _fetch_rows(config.etf_trading_url, date=date, config=config)
    holdings_rows = _load_holdings_rows(holdings_path)
    etf_name_to_code = {
        _pick_first(row, ["ISU_NM", "ISU_ABBRV", "ISU_ENG_NM"]): _pick_first(
            row, ["ISU_SRT_CD", "ISU_CD"]
        )
        for row in etf_trading_rows
        if _pick_first(row, ["ISU_SRT_CD", "ISU_CD"])
    }
    holdings = _resolve_holdings_rows(holdings_rows, etf_name_to_code=etf_name_to_code)

    holdings_etf_codes = {row.etf_code for row in holdings}
    live_etf_codes = {
        _pick_first(row, ["ISU_SRT_CD", "ISU_CD"])
        for row in etf_trading_rows
        if _pick_first(row, ["ISU_SRT_CD", "ISU_CD"])
    }
    matched_etf_codes = holdings_etf_codes & live_etf_codes

    if holdings and not matched_etf_codes:
        raise ValueError(
            "The holdings file ETF codes do not match any live KRX ETF trading codes for the selected date. "
            "Use a holdings file with real ETF short codes such as ISU_SRT_CD from KRX."
        )

    snapshot = build_snapshot_from_krx_rows(
        date=date,
        stock_master_rows=stock_master_rows,
        stock_trading_rows=stock_trading_rows,
        etf_trading_rows=etf_trading_rows,
        holdings=holdings,
    )

    result = compute_daily_ratio(
        snapshot,
        rule=rule,
        min_kospi_weight_sum=min_kospi_weight_sum,
    )
    if db_path is not None:
        save_result(db_path, result)
    return result
