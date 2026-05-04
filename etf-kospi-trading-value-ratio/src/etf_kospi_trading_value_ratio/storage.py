from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
import sqlite3

from .models import DailyRatioResult


RESULTS_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS daily_ratio_results (
    date TEXT NOT NULL,
    rule TEXT NOT NULL,
    min_kospi_weight_sum REAL NOT NULL,
    eligible_etf_count INTEGER NOT NULL,
    numerator REAL NOT NULL,
    denominator REAL NOT NULL,
    ratio REAL,
    created_at TEXT NOT NULL,
    PRIMARY KEY (date, rule, min_kospi_weight_sum)
)
"""


DETAILS_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS daily_ratio_etf_details (
    date TEXT NOT NULL,
    rule TEXT NOT NULL,
    min_kospi_weight_sum REAL NOT NULL,
    etf_code TEXT NOT NULL,
    etf_name TEXT NOT NULL,
    kospi_holding_count INTEGER NOT NULL,
    kospi_weight_sum REAL NOT NULL,
    trading_value REAL NOT NULL,
    included INTEGER NOT NULL,
    PRIMARY KEY (date, rule, min_kospi_weight_sum, etf_code)
)
"""


def init_db(db_path: str | Path) -> None:
    db_file = Path(db_path)
    db_file.parent.mkdir(parents=True, exist_ok=True)

    with sqlite3.connect(db_file) as conn:
        conn.execute(RESULTS_TABLE_SQL)
        conn.execute(DETAILS_TABLE_SQL)
        conn.commit()


def save_result(db_path: str | Path, result: DailyRatioResult) -> None:
    init_db(db_path)
    created_at = datetime.now(timezone.utc).isoformat()

    with sqlite3.connect(db_path) as conn:
        conn.execute(
            """
            INSERT INTO daily_ratio_results (
                date,
                rule,
                min_kospi_weight_sum,
                eligible_etf_count,
                numerator,
                denominator,
                ratio,
                created_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(date, rule, min_kospi_weight_sum) DO UPDATE SET
                eligible_etf_count = excluded.eligible_etf_count,
                numerator = excluded.numerator,
                denominator = excluded.denominator,
                ratio = excluded.ratio,
                created_at = excluded.created_at
            """,
            (
                result.date,
                result.rule,
                result.min_kospi_weight_sum,
                result.eligible_etf_count,
                result.numerator,
                result.denominator,
                result.ratio,
                created_at,
            ),
        )

        for detail in result.details:
            conn.execute(
                """
                INSERT INTO daily_ratio_etf_details (
                    date,
                    rule,
                    min_kospi_weight_sum,
                    etf_code,
                    etf_name,
                    kospi_holding_count,
                    kospi_weight_sum,
                    trading_value,
                    included
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(date, rule, min_kospi_weight_sum, etf_code) DO UPDATE SET
                    etf_name = excluded.etf_name,
                    kospi_holding_count = excluded.kospi_holding_count,
                    kospi_weight_sum = excluded.kospi_weight_sum,
                    trading_value = excluded.trading_value,
                    included = excluded.included
                """,
                (
                    result.date,
                    result.rule,
                    result.min_kospi_weight_sum,
                    detail.etf_code,
                    detail.etf_name,
                    detail.kospi_holding_count,
                    detail.kospi_weight_sum,
                    detail.trading_value,
                    1 if detail.included else 0,
                ),
            )

        conn.commit()
