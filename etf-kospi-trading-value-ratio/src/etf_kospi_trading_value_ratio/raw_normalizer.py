from __future__ import annotations

from pathlib import Path
import json

from .models import (
    DailySnapshot,
    EtfHoldingRecord,
    EtfMasterRecord,
    EtfTradingRecord,
    MarketTradingRecord,
    StockMasterRecord,
)


def _read_json(path: str | Path) -> object:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def _get_by_path(payload: object, dotted_path: str | None) -> object:
    if dotted_path in (None, "", "$"):
        return payload

    current = payload
    for segment in dotted_path.split("."):
        if isinstance(current, dict):
            current = current.get(segment)
        else:
            return []
    return current


def _ensure_list(value: object) -> list[dict[str, object]]:
    if isinstance(value, list):
        return [row for row in value if isinstance(row, dict)]
    return []


def _to_float(value: object) -> float:
    if value is None:
        return 0.0
    if isinstance(value, (float, int)):
        return float(value)
    text = str(value).strip().replace(",", "")
    return float(text) if text else 0.0


def _normalize_market(value: object) -> str:
    return str(value).strip().upper()


def _load_mapping(path: str | Path) -> dict[str, dict[str, object]]:
    payload = _read_json(path)
    if not isinstance(payload, dict):
        raise ValueError("Raw mapping must be a JSON object.")
    return payload


def _extract_rows(
    payload: object,
    entry_mapping: dict[str, object],
) -> list[dict[str, object]]:
    list_path = entry_mapping.get("list_path")
    rows = _ensure_list(_get_by_path(payload, str(list_path) if list_path is not None else None))
    defaults = entry_mapping.get("defaults", {})

    normalized: list[dict[str, object]] = []
    for row in rows:
        item = dict(defaults) if isinstance(defaults, dict) else {}
        item.update(row)
        normalized.append(item)
    return normalized


def load_snapshot_from_raw_dir(
    *,
    date: str,
    raw_dir: str | Path,
    mapping_path: str | Path,
) -> DailySnapshot:
    raw_path = Path(raw_dir)
    mapping = _load_mapping(mapping_path)

    stock_payload = _read_json(raw_path / "stock_master.json")
    etf_payload = _read_json(raw_path / "etf_master.json")
    holdings_payload = _read_json(raw_path / "etf_holdings.json")
    etf_trading_payload = _read_json(raw_path / "etf_trading.json")
    market_trading_payload = _read_json(raw_path / "market_summary.json")

    stock_rows = _extract_rows(stock_payload, mapping["stock_master"])
    etf_rows = _extract_rows(etf_payload, mapping["etf_master"])
    holding_rows = _extract_rows(holdings_payload, mapping["holdings"])
    etf_trading_rows = _extract_rows(etf_trading_payload, mapping["etf_trading"])
    market_trading_rows = _extract_rows(market_trading_payload, mapping["market_trading"])

    stock_fields = mapping["stock_master"]["fields"]
    etf_fields = mapping["etf_master"]["fields"]
    holding_fields = mapping["holdings"]["fields"]
    etf_trading_fields = mapping["etf_trading"]["fields"]
    market_trading_fields = mapping["market_trading"]["fields"]

    return DailySnapshot(
        date=str(date),
        stocks=[
            StockMasterRecord(
                stock_code=str(row[stock_fields["stock_code"]]).strip(),
                market=_normalize_market(row[stock_fields["market"]]),
            )
            for row in stock_rows
        ],
        etfs=[
            EtfMasterRecord(
                etf_code=str(row[etf_fields["etf_code"]]).strip(),
                etf_name=str(row[etf_fields["etf_name"]]).strip(),
            )
            for row in etf_rows
        ],
        holdings=[
            EtfHoldingRecord(
                etf_code=str(row[holding_fields["etf_code"]]).strip(),
                stock_code=str(row[holding_fields["stock_code"]]).strip(),
                weight=_to_float(row[holding_fields["weight"]]),
            )
            for row in holding_rows
        ],
        etf_trading=[
            EtfTradingRecord(
                etf_code=str(row[etf_trading_fields["etf_code"]]).strip(),
                trading_value=_to_float(row[etf_trading_fields["trading_value"]]),
            )
            for row in etf_trading_rows
        ],
        market_trading=[
            MarketTradingRecord(
                market=_normalize_market(row[market_trading_fields["market"]]),
                trading_value=_to_float(row[market_trading_fields["trading_value"]]),
            )
            for row in market_trading_rows
        ],
    )
