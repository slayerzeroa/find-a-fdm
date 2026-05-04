from __future__ import annotations

from pathlib import Path

from .calculator import compute_daily_ratio
from .importers import load_snapshot_from_files, load_snapshot_json
from .models import DailyRatioResult
from .raw_normalizer import load_snapshot_from_raw_dir
from .storage import save_result


def compute_from_snapshot_file(
    *,
    snapshot_path: str | Path,
    db_path: str | Path | None = None,
    rule: str,
    min_kospi_weight_sum: float,
) -> DailyRatioResult:
    snapshot = load_snapshot_json(snapshot_path)
    result = compute_daily_ratio(
        snapshot,
        rule=rule,
        min_kospi_weight_sum=min_kospi_weight_sum,
    )
    if db_path is not None:
        save_result(db_path, result)
    return result


def compute_from_files(
    *,
    date: str,
    stock_master_path: str | Path,
    etf_master_path: str | Path,
    holdings_path: str | Path,
    etf_trading_path: str | Path,
    market_trading_path: str | Path,
    mapping_path: str | Path,
    db_path: str | Path | None = None,
    rule: str,
    min_kospi_weight_sum: float,
) -> DailyRatioResult:
    snapshot = load_snapshot_from_files(
        date=date,
        stock_master_path=stock_master_path,
        etf_master_path=etf_master_path,
        holdings_path=holdings_path,
        etf_trading_path=etf_trading_path,
        market_trading_path=market_trading_path,
        mapping_path=mapping_path,
    )
    result = compute_daily_ratio(
        snapshot,
        rule=rule,
        min_kospi_weight_sum=min_kospi_weight_sum,
    )
    if db_path is not None:
        save_result(db_path, result)
    return result


def compute_from_raw_dir(
    *,
    date: str,
    raw_dir: str | Path,
    raw_mapping_path: str | Path,
    db_path: str | Path | None = None,
    rule: str,
    min_kospi_weight_sum: float,
) -> DailyRatioResult:
    snapshot = load_snapshot_from_raw_dir(
        date=date,
        raw_dir=raw_dir,
        mapping_path=raw_mapping_path,
    )
    result = compute_daily_ratio(
        snapshot,
        rule=rule,
        min_kospi_weight_sum=min_kospi_weight_sum,
    )
    if db_path is not None:
        save_result(db_path, result)
    return result
