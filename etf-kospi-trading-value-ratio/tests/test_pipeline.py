from __future__ import annotations

from datetime import date
from pathlib import Path
import os
import sqlite3
import sys
import unittest
import uuid


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))


from etf_kospi_trading_value_ratio.calculator import (  # noqa: E402
    RULE_ANY_KOSPI_CONSTITUENT,
    RULE_MIN_KOSPI_WEIGHT_SUM,
)
from etf_kospi_trading_value_ratio.models import EtfHoldingRecord  # noqa: E402
from etf_kospi_trading_value_ratio.pipeline import (  # noqa: E402
    compute_from_files,
    compute_from_raw_dir,
    compute_from_snapshot_file,
)
from etf_kospi_trading_value_ratio.krx_hybrid import (  # noqa: E402
    build_snapshot_from_krx_rows,
    _resolve_holdings_rows,
)
from etf_kospi_trading_value_ratio.etf_theme_trading import (  # noqa: E402
    summarize_etf_theme_trading_from_rows,
)
from etf_kospi_trading_value_ratio.kospi_related_etf import (  # noqa: E402
    _iter_weekdays,
    summarize_kospi_related_etf_ratio_from_rows,
)


class PipelineTest(unittest.TestCase):
    def test_compute_from_snapshot_uses_any_kospi_constituent_rule(self) -> None:
        snapshot_path = ROOT / "tests" / "fixtures" / "sample_snapshot.json"

        result = compute_from_snapshot_file(
            snapshot_path=snapshot_path,
            rule=RULE_ANY_KOSPI_CONSTITUENT,
            min_kospi_weight_sum=0.0,
        )

        self.assertEqual(result.eligible_etf_count, 2)
        self.assertAlmostEqual(result.numerator, 1700.0)
        self.assertAlmostEqual(result.denominator, 10000.0)
        self.assertAlmostEqual(result.ratio or 0.0, 0.17)

    def test_compute_from_files_and_persist_strict_rule(self) -> None:
        fixtures = ROOT / "tests" / "fixtures"
        tmp_dir = ROOT / "tests" / "_tmp"
        tmp_dir.mkdir(parents=True, exist_ok=True)
        db_path = tmp_dir / f"project-{uuid.uuid4().hex}.db"

        try:
            result = compute_from_files(
                date="20260427",
                stock_master_path=fixtures / "stock_master.csv",
                etf_master_path=fixtures / "etf_master.csv",
                holdings_path=fixtures / "holdings.csv",
                etf_trading_path=fixtures / "etf_trading.csv",
                market_trading_path=fixtures / "market_trading.csv",
                mapping_path=fixtures / "mapping.json",
                db_path=db_path,
                rule=RULE_MIN_KOSPI_WEIGHT_SUM,
                min_kospi_weight_sum=0.10,
            )

            self.assertEqual(result.eligible_etf_count, 1)
            self.assertAlmostEqual(result.numerator, 1000.0)
            self.assertAlmostEqual(result.denominator, 10000.0)
            self.assertAlmostEqual(result.ratio or 0.0, 0.10)

            with sqlite3.connect(db_path) as conn:
                row = conn.execute(
                    """
                    SELECT eligible_etf_count, numerator, denominator, ratio
                    FROM daily_ratio_results
                    WHERE date = ? AND rule = ? AND min_kospi_weight_sum = ?
                    """,
                    ("20260427", RULE_MIN_KOSPI_WEIGHT_SUM, 0.10),
                ).fetchone()
                self.assertIsNotNone(row)
                self.assertEqual(row[0], 1)
                self.assertAlmostEqual(row[1], 1000.0)
                self.assertAlmostEqual(row[2], 10000.0)
                self.assertAlmostEqual(row[3], 0.10)
        finally:
            if db_path.exists():
                try:
                    os.remove(db_path)
                except PermissionError:
                    pass

    def test_compute_from_raw_dir(self) -> None:
        fixtures = ROOT / "tests" / "fixtures"
        raw_dir = fixtures / "raw_snapshot"
        mapping_path = fixtures / "raw_mapping.json"

        result = compute_from_raw_dir(
            date="20260427",
            raw_dir=raw_dir,
            raw_mapping_path=mapping_path,
            rule=RULE_ANY_KOSPI_CONSTITUENT,
            min_kospi_weight_sum=0.0,
        )

        self.assertEqual(result.eligible_etf_count, 2)
        self.assertAlmostEqual(result.numerator, 1700.0)
        self.assertAlmostEqual(result.denominator, 10000.0)
        self.assertAlmostEqual(result.ratio or 0.0, 0.17)

    def test_build_snapshot_from_krx_rows(self) -> None:
        stock_master_rows = [
            {"ISU_SRT_CD": "005930", "MKT_TP_NM": "KOSPI"},
            {"ISU_SRT_CD": "035420", "MKT_TP_NM": "KOSPI"},
            {"ISU_SRT_CD": "357780", "MKT_TP_NM": "KOSDAQ"},
        ]
        stock_trading_rows = [
            {"ISU_SRT_CD": "005930", "ACC_TRDVAL": "6000.0"},
            {"ISU_SRT_CD": "035420", "ACC_TRDVAL": "4000.0"},
        ]
        etf_trading_rows = [
            {"ISU_SRT_CD": "A001", "ISU_NM": "ETF A", "ACC_TRDVAL": "1000.0"},
            {"ISU_SRT_CD": "B001", "ISU_NM": "ETF B", "ACC_TRDVAL": "300.0"},
            {"ISU_SRT_CD": "C001", "ISU_NM": "ETF C", "ACC_TRDVAL": "700.0"},
        ]
        holdings = [
            EtfHoldingRecord(etf_code="A001", stock_code="005930", weight=0.20),
            EtfHoldingRecord(etf_code="A001", stock_code="357780", weight=0.10),
            EtfHoldingRecord(etf_code="B001", stock_code="357780", weight=0.70),
            EtfHoldingRecord(etf_code="C001", stock_code="035420", weight=0.05),
        ]

        result_snapshot = build_snapshot_from_krx_rows(
            date="20260427",
            stock_master_rows=stock_master_rows,
            stock_trading_rows=stock_trading_rows,
            etf_trading_rows=etf_trading_rows,
            holdings=holdings,
        )

        self.assertEqual(result_snapshot.date, "20260427")
        self.assertEqual(len(result_snapshot.stocks), 3)
        self.assertEqual(len(result_snapshot.etfs), 3)
        self.assertAlmostEqual(result_snapshot.market_trading[0].trading_value, 10000.0)

    def test_resolve_holdings_rows_by_etf_name(self) -> None:
        raw_rows = [
            {"etf_name": "ETF A", "stock_code": "005930", "weight": "0.2"},
            {"etf_name": "ETF C", "stock_code": "035420", "weight": "0.05"},
        ]
        holdings = _resolve_holdings_rows(
            raw_rows,
            etf_name_to_code={"ETF A": "A001", "ETF C": "C001"},
        )

        self.assertEqual(len(holdings), 2)
        self.assertEqual(holdings[0].etf_code, "A001")
        self.assertEqual(holdings[1].etf_code, "C001")

    def test_summarize_etf_theme_trading_from_rows(self) -> None:
        rows = [
            {
                "ISU_SRT_CD": "001",
                "ISU_NM": "TIGER 미국S&P500",
                "IDX_IND_NM": "S&P 500",
                "ACC_TRDVAL": "1000",
            },
            {
                "ISU_SRT_CD": "002",
                "ISU_NM": "KODEX 국채선물",
                "IDX_IND_NM": "채권",
                "ACC_TRDVAL": "500",
            },
            {
                "ISU_SRT_CD": "003",
                "ISU_NM": "TIGER 리츠부동산인프라",
                "IDX_IND_NM": "REIT",
                "ACC_TRDVAL": "250",
            },
            {
                "ISU_SRT_CD": "004",
                "ISU_NM": "KODEX 200",
                "IDX_IND_NM": "코스피 200",
                "ACC_TRDVAL": "300",
            },
        ]

        summary = summarize_etf_theme_trading_from_rows(
            date="20260427",
            etf_trading_rows=rows,
        )

        self.assertEqual(summary.selected_etf_count, 3)
        self.assertAlmostEqual(summary.selected_total_trading_value, 1750.0)
        self.assertAlmostEqual(summary.category_totals["us_equity"], 1000.0)
        self.assertAlmostEqual(summary.category_totals["foreign_equity"], 0.0)
        self.assertAlmostEqual(summary.category_totals["bond"], 500.0)
        self.assertAlmostEqual(summary.category_totals["reits"], 250.0)
        self.assertAlmostEqual(summary.subcategory_totals["us_equity"], 1000.0)
        self.assertAlmostEqual(summary.subcategory_totals["domestic_bond"], 500.0)
        self.assertAlmostEqual(summary.subcategory_totals["domestic_reits"], 250.0)

    def test_summarize_kospi_related_etf_ratio_from_rows(self) -> None:
        stock_rows = [
            {"MKT_NM": "KOSPI", "ACC_TRDVAL": "10000"},
            {"MKT_NM": "KOSDAQ", "ACC_TRDVAL": "2000"},
        ]
        etf_rows = [
            {
                "ISU_SRT_CD": "100",
                "ISU_NM": "KODEX 200",
                "IDX_IND_NM": "코스피 200",
                "ACC_TRDVAL": "500",
            },
            {
                "ISU_SRT_CD": "101",
                "ISU_NM": "TIGER 미국S&P500",
                "IDX_IND_NM": "S&P 500",
                "ACC_TRDVAL": "700",
            },
            {
                "ISU_SRT_CD": "102",
                "ISU_NM": "KODEX 국채선물",
                "IDX_IND_NM": "채권",
                "ACC_TRDVAL": "300",
            },
            {
                "ISU_SRT_CD": "103",
                "ISU_NM": "KODEX 코스닥150",
                "IDX_IND_NM": "코스닥 150",
                "ACC_TRDVAL": "200",
            },
            {
                "ISU_SRT_CD": "104",
                "ISU_NM": "KODEX 반도체",
                "IDX_IND_NM": "KRX 반도체",
                "ACC_TRDVAL": "400",
            },
        ]

        summary = summarize_kospi_related_etf_ratio_from_rows(
            date="20260427",
            stock_trading_rows=stock_rows,
            etf_trading_rows=etf_rows,
        )

        self.assertEqual(summary.selected_etf_count, 2)
        self.assertAlmostEqual(summary.selected_total_trading_value, 900.0)
        self.assertAlmostEqual(summary.kospi_trading_value, 10000.0)
        self.assertAlmostEqual(summary.ratio, 0.09)

    def test_iter_weekdays_skips_weekends(self) -> None:
        dates = [
            item.strftime("%Y%m%d")
            for item in _iter_weekdays(
                date(2026, 4, 24),
                date(2026, 4, 28),
            )
        ]
        self.assertEqual(dates, ["20260424", "20260427", "20260428"])


if __name__ == "__main__":
    unittest.main()
