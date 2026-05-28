from __future__ import annotations

from pathlib import Path
import csv
import json

from .models import (
    DailySnapshot,
    EtfHoldingRecord,
    EtfMasterRecord,
    EtfTradingRecord,
    MarketTradingRecord,
    StockMasterRecord,
)


ENCODING_CANDIDATES = ("utf-8-sig", "cp949", "utf-8")


def _read_text(path: Path) -> str:
    last_error: UnicodeDecodeError | None = None
    for encoding in ENCODING_CANDIDATES:
        try:
            return path.read_text(encoding=encoding)
        except UnicodeDecodeError as exc:
            last_error = exc
    if last_error is not None:
        raise last_error
    raise ValueError(f"Unable to read file: {path}")


def _load_rows(path: str | Path) -> list[dict[str, object]]:
    file_path = Path(path)
    suffix = file_path.suffix.lower()

    if suffix == ".json":
        payload = json.loads(_read_text(file_path))
        if not isinstance(payload, list):
            raise ValueError(f"JSON payload must be a list: {file_path}")
        return payload

    if suffix == ".csv":
        rows: list[dict[str, object]] = []
        text = _read_text(file_path)
        reader = csv.DictReader(text.splitlines())
        for row in reader:
            rows.append(dict(row))
        return rows

    raise ValueError(f"Unsupported file type: {file_path}")


def _load_mapping(path: str | Path) -> dict[str, dict[str, str]]:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("Mapping file must be a JSON object.")
    return payload


def _to_float(value: object) -> float:
    if value is None:
        return 0.0
    if isinstance(value, (int, float)):
        return float(value)

    text = str(value).strip().replace(",", "")
    if text == "":
        return 0.0
    return float(text)


def _normalize_market(value: object) -> str:
    return str(value).strip().upper()


def load_snapshot_json(path: str | Path) -> DailySnapshot:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))

    return DailySnapshot(
        date=str(payload["date"]),
        stocks=[
            StockMasterRecord(
                stock_code=str(item["stock_code"]).strip(),
                market=_normalize_market(item["market"]),
            )
            for item in payload.get("stocks", [])
        ],
        etfs=[
            EtfMasterRecord(
                etf_code=str(item["etf_code"]).strip(),
                etf_name=str(item["etf_name"]).strip(),
            )
            for item in payload.get("etfs", [])
        ],
        holdings=[
            EtfHoldingRecord(
                etf_code=str(item["etf_code"]).strip(),
                stock_code=str(item["stock_code"]).strip(),
                weight=_to_float(item["weight"]),
            )
            for item in payload.get("holdings", [])
        ],
        etf_trading=[
            EtfTradingRecord(
                etf_code=str(item["etf_code"]).strip(),
                trading_value=_to_float(item["trading_value"]),
            )
            for item in payload.get("etf_trading", [])
        ],
        market_trading=[
            MarketTradingRecord(
                market=_normalize_market(item["market"]),
                trading_value=_to_float(item["trading_value"]),
            )
            for item in payload.get("market_trading", [])
        ],
    )


def load_snapshot_from_files(
    *,
    date: str,
    stock_master_path: str | Path,
    etf_master_path: str | Path,
    holdings_path: str | Path,
    etf_trading_path: str | Path,
    market_trading_path: str | Path,
    mapping_path: str | Path,
) -> DailySnapshot:
    mapping = _load_mapping(mapping_path)

    stock_rows = _load_rows(stock_master_path)
    etf_rows = _load_rows(etf_master_path)
    holding_rows = _load_rows(holdings_path)
    etf_trading_rows = _load_rows(etf_trading_path)
    market_trading_rows = _load_rows(market_trading_path)

    stock_map = mapping["stock_master"]
    etf_map = mapping["etf_master"]
    holding_map = mapping["holdings"]
    etf_trading_map = mapping["etf_trading"]
    market_trading_map = mapping["market_trading"]

    return DailySnapshot(
        date=str(date),
        stocks=[
            StockMasterRecord(
                stock_code=str(row[stock_map["stock_code"]]).strip(),
                market=_normalize_market(row[stock_map["market"]]),
            )
            for row in stock_rows
        ],
        etfs=[
            EtfMasterRecord(
                etf_code=str(row[etf_map["etf_code"]]).strip(),
                etf_name=str(row[etf_map["etf_name"]]).strip(),
            )
            for row in etf_rows
        ],
        holdings=[
            EtfHoldingRecord(
                etf_code=str(row[holding_map["etf_code"]]).strip(),
                stock_code=str(row[holding_map["stock_code"]]).strip(),
                weight=_to_float(row[holding_map["weight"]]),
            )
            for row in holding_rows
        ],
        etf_trading=[
            EtfTradingRecord(
                etf_code=str(row[etf_trading_map["etf_code"]]).strip(),
                trading_value=_to_float(row[etf_trading_map["trading_value"]]),
            )
            for row in etf_trading_rows
        ],
        market_trading=[
            MarketTradingRecord(
                market=_normalize_market(row[market_trading_map["market"]]),
                trading_value=_to_float(row[market_trading_map["trading_value"]]),
            )
            for row in market_trading_rows
        ],
    )
