from __future__ import annotations

from pathlib import Path
from urllib.parse import urlencode, urlparse, urlunparse, parse_qsl
import json

import requests

from ..config import KrxRawConfig


class KrxUnauthorizedError(RuntimeError):
    """Raised when the KRX API key is present but not authorized for the service."""


def _extract_output_rows(payload: object, output_block: str) -> list[dict[str, object]]:
    if isinstance(payload, dict):
        rows = payload.get(output_block, [])
        if isinstance(rows, list):
            return [row for row in rows if isinstance(row, dict)]
    if isinstance(payload, list):
        return [row for row in payload if isinstance(row, dict)]
    return []


def _append_query(url: str, params: dict[str, str]) -> str:
    parsed = urlparse(url)
    query = dict(parse_qsl(parsed.query, keep_blank_values=True))
    query.update(params)
    return urlunparse(parsed._replace(query=urlencode(query)))


def _build_request_url(url: str, *, date: str, etf_code: str | None = None) -> str:
    if url.startswith("http://data-dbg.krx.co.kr/"):
        url = "https://" + url[len("http://"):]
    if "{date}" in url or "{etf_code}" in url:
        return url.format(date=date, etf_code=etf_code or "")
    return _append_query(url, {"basDd": date})


def _fetch_json(url: str, auth_key: str | None) -> dict[str, object]:
    headers = {
        "Accept": "application/json",
        "User-Agent": "python-requests/krx-client",
    }
    if auth_key:
        headers["AUTH_KEY"] = auth_key

    response = requests.get(url, headers=headers, timeout=30)
    if response.status_code == 401:
        raise KrxUnauthorizedError(
            "KRX returned 401 Unauthorized. The auth key is being sent, but this API "
            "service likely has not been separately approved in KRX OPEN API usage settings."
        )
    response.raise_for_status()
    return response.json()


def verify_auth_key(*, date: str, config: KrxRawConfig) -> dict[str, object]:
    if not config.has_auth_key:
        raise ValueError("KRX auth key not found. Set KRX_API or KRX_AUTH_KEY.")
    if not config.stock_master_url:
        raise ValueError("KRX_STOCK_MASTER_URL is required to verify the auth key.")

    payload = _fetch_json(_build_request_url(config.stock_master_url, date=date), config.auth_key)
    rows = _extract_output_rows(payload, config.output_block)
    return {
        "date": date,
        "has_auth_key": True,
        "stock_master_url": config.stock_master_url,
        "row_count": len(rows),
        "note": (
            "HTTP 200 from the real endpoint confirms the auth key is accepted. "
            "If row_count is 0, the selected date may not have published data yet."
        ),
    }


def collect_raw_payloads(
    *,
    date: str,
    output_dir: str | Path,
    config: KrxRawConfig,
) -> list[Path]:
    if not config.has_auth_key:
        raise ValueError("KRX auth key not found. Set KRX_API or KRX_AUTH_KEY.")

    endpoints = {
        "stock_master": config.stock_master_url,
        "etf_master": config.etf_master_url,
        "etf_trading": config.etf_trading_url,
        "market_summary": config.market_summary_url,
    }

    missing = [name for name, url in endpoints.items() if not url]
    if missing or not config.etf_holdings_url:
        raise ValueError(
            "Missing endpoint URLs for raw KRX collection: "
            + ", ".join(sorted(missing + (["etf_holdings"] if not config.etf_holdings_url else [])))
        )

    date_dir = Path(output_dir) / date
    date_dir.mkdir(parents=True, exist_ok=True)

    saved_files: list[Path] = []
    etf_master_payload: dict[str, object] | None = None
    for name, endpoint_url in endpoints.items():
        request_url = _build_request_url(endpoint_url, date=date)
        payload = _fetch_json(request_url, config.auth_key)

        output_path = date_dir / f"{name}.json"
        output_path.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        saved_files.append(output_path)
        if name == "etf_master":
            etf_master_payload = payload

    if etf_master_payload is None:
        raise ValueError("ETF master payload was not collected.")

    etf_rows = _extract_output_rows(etf_master_payload, config.output_block)
    etf_codes = [
        str(row.get(config.etf_master_code_field, "")).strip()
        for row in etf_rows
        if str(row.get(config.etf_master_code_field, "")).strip()
    ]

    combined_holding_rows: list[dict[str, object]] = []
    for etf_code in etf_codes:
        request_url = _build_request_url(
            config.etf_holdings_url,
            date=date,
            etf_code=etf_code,
        )
        payload = _fetch_json(request_url, config.auth_key)
        rows = _extract_output_rows(payload, config.output_block)
        for row in rows:
            if config.etf_holdings_etf_code_field not in row:
                row[config.etf_holdings_etf_code_field] = etf_code
            combined_holding_rows.append(row)

    holdings_payload = {config.output_block: combined_holding_rows}
    holdings_path = date_dir / "etf_holdings.json"
    holdings_path.write_text(
        json.dumps(holdings_payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    saved_files.append(holdings_path)

    return saved_files
