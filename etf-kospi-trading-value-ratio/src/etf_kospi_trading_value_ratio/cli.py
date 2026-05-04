from __future__ import annotations

import argparse
import json
from pathlib import Path

from .calculator import RULE_ANY_KOSPI_CONSTITUENT, RULE_MIN_KOSPI_WEIGHT_SUM
from .config import load_krx_raw_config
from .etf_theme_trading import (
    DEFAULT_SELECTED_CATEGORIES,
    compute_live_etf_theme_trading,
    export_etf_theme_trading_summary,
)
from .kospi_related_etf import (
    compute_live_kospi_related_etf_ratio,
    export_kospi_related_etf_ratio,
    export_kospi_related_etf_ratio_history,
)
from .krx_hybrid import compute_from_krx_plus_holdings, export_live_etf_catalog
from .pipeline import (
    compute_from_files,
    compute_from_raw_dir,
    compute_from_snapshot_file,
)
from .providers.krx_raw import KrxUnauthorizedError, collect_raw_payloads, verify_auth_key
from .storage import init_db


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="etf-kospi-trading-value-ratio",
        description="Compute daily KOSPI-included ETF trading value ratios.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    init_db_parser = subparsers.add_parser("init-db", help="Initialize a SQLite database.")
    init_db_parser.add_argument("--db", required=True, help="SQLite database path.")

    snapshot_parser = subparsers.add_parser(
        "compute-from-snapshot",
        help="Compute the ratio from a normalized JSON snapshot.",
    )
    snapshot_parser.add_argument("--snapshot", required=True, help="Snapshot JSON path.")
    snapshot_parser.add_argument("--db", help="Optional SQLite database path.")
    snapshot_parser.add_argument(
        "--rule",
        default=RULE_ANY_KOSPI_CONSTITUENT,
        choices=[RULE_ANY_KOSPI_CONSTITUENT, RULE_MIN_KOSPI_WEIGHT_SUM],
        help="ETF inclusion rule.",
    )
    snapshot_parser.add_argument(
        "--min-kospi-weight-sum",
        default=0.0,
        type=float,
        help="Threshold used when rule=min_kospi_weight_sum.",
    )

    files_parser = subparsers.add_parser(
        "compute-from-files",
        help="Compute the ratio from exported CSV or JSON files.",
    )
    files_parser.add_argument("--date", required=True, help="Business date in YYYYMMDD.")
    files_parser.add_argument("--stock-master", required=True, help="Stock master file.")
    files_parser.add_argument("--etf-master", required=True, help="ETF master file.")
    files_parser.add_argument("--holdings", required=True, help="ETF holdings file.")
    files_parser.add_argument("--etf-trading", required=True, help="ETF trading file.")
    files_parser.add_argument(
        "--market-trading",
        required=True,
        help="Market trading summary file.",
    )
    files_parser.add_argument("--mapping", required=True, help="Mapping JSON path.")
    files_parser.add_argument("--db", help="Optional SQLite database path.")
    files_parser.add_argument(
        "--rule",
        default=RULE_ANY_KOSPI_CONSTITUENT,
        choices=[RULE_ANY_KOSPI_CONSTITUENT, RULE_MIN_KOSPI_WEIGHT_SUM],
        help="ETF inclusion rule.",
    )
    files_parser.add_argument(
        "--min-kospi-weight-sum",
        default=0.0,
        type=float,
        help="Threshold used when rule=min_kospi_weight_sum.",
    )

    raw_parser = subparsers.add_parser(
        "collect-raw-krx",
        help="Download raw KRX JSON payloads to disk.",
    )
    raw_parser.add_argument("--date", required=True, help="Business date in YYYYMMDD.")
    raw_parser.add_argument("--output-dir", required=True, help="Output directory.")
    raw_parser.add_argument("--env-file", help="Optional env file path.")

    verify_parser = subparsers.add_parser(
        "verify-krx-key",
        help="Verify the KRX auth key against a known raw endpoint.",
    )
    verify_parser.add_argument("--date", required=True, help="Business date in YYYYMMDD.")
    verify_parser.add_argument("--env-file", help="Optional env file path.")

    raw_compute_parser = subparsers.add_parser(
        "compute-from-raw-krx",
        help="Compute the ratio from collected raw KRX JSON payloads.",
    )
    raw_compute_parser.add_argument("--date", required=True, help="Business date in YYYYMMDD.")
    raw_compute_parser.add_argument("--raw-dir", required=True, help="Raw payload directory.")
    raw_compute_parser.add_argument(
        "--raw-mapping",
        required=True,
        help="Raw KRX normalization mapping JSON path.",
    )
    raw_compute_parser.add_argument("--db", help="Optional SQLite database path.")
    raw_compute_parser.add_argument(
        "--rule",
        default=RULE_ANY_KOSPI_CONSTITUENT,
        choices=[RULE_ANY_KOSPI_CONSTITUENT, RULE_MIN_KOSPI_WEIGHT_SUM],
        help="ETF inclusion rule.",
    )
    raw_compute_parser.add_argument(
        "--min-kospi-weight-sum",
        default=0.0,
        type=float,
        help="Threshold used when rule=min_kospi_weight_sum.",
    )

    collect_compute_parser = subparsers.add_parser(
        "collect-and-compute-raw-krx",
        help="Collect raw KRX payloads with the API key, then compute the ratio.",
    )
    collect_compute_parser.add_argument("--date", required=True, help="Business date in YYYYMMDD.")
    collect_compute_parser.add_argument("--output-dir", required=True, help="Raw output directory.")
    collect_compute_parser.add_argument(
        "--raw-mapping",
        required=True,
        help="Raw KRX normalization mapping JSON path.",
    )
    collect_compute_parser.add_argument("--env-file", help="Optional env file path.")
    collect_compute_parser.add_argument("--db", help="Optional SQLite database path.")
    collect_compute_parser.add_argument(
        "--rule",
        default=RULE_ANY_KOSPI_CONSTITUENT,
        choices=[RULE_ANY_KOSPI_CONSTITUENT, RULE_MIN_KOSPI_WEIGHT_SUM],
        help="ETF inclusion rule.",
    )
    collect_compute_parser.add_argument(
        "--min-kospi-weight-sum",
        default=0.0,
        type=float,
        help="Threshold used when rule=min_kospi_weight_sum.",
    )

    hybrid_parser = subparsers.add_parser(
        "compute-from-krx-plus-holdings",
        help="Use KRX API for stock master, KOSPI trading, ETF trading, and a local holdings file for composition.",
    )
    hybrid_parser.add_argument("--date", required=True, help="Business date in YYYYMMDD.")
    hybrid_parser.add_argument(
        "--holdings",
        required=True,
        help="Holdings CSV or JSON with stock_code, weight, and either etf_code or etf_name.",
    )
    hybrid_parser.add_argument("--env-file", help="Optional env file path.")
    hybrid_parser.add_argument("--db", help="Optional SQLite database path.")
    hybrid_parser.add_argument(
        "--rule",
        default=RULE_ANY_KOSPI_CONSTITUENT,
        choices=[RULE_ANY_KOSPI_CONSTITUENT, RULE_MIN_KOSPI_WEIGHT_SUM],
        help="ETF inclusion rule.",
    )
    hybrid_parser.add_argument(
        "--min-kospi-weight-sum",
        default=0.0,
        type=float,
        help="Threshold used when rule=min_kospi_weight_sum.",
    )

    catalog_parser = subparsers.add_parser(
        "export-krx-etf-catalog",
        help="Export the live KRX ETF code/name catalog for a given date.",
    )
    catalog_parser.add_argument("--date", required=True, help="Business date in YYYYMMDD.")
    catalog_parser.add_argument("--output", required=True, help="CSV or JSON output path.")
    catalog_parser.add_argument("--env-file", help="Optional env file path.")

    theme_parser = subparsers.add_parser(
        "compute-krx-etf-theme-trading",
        help="Classify live KRX ETF trading rows into broad themes and sum trading values.",
    )
    theme_parser.add_argument("--date", required=True, help="Business date in YYYYMMDD.")
    theme_parser.add_argument(
        "--categories",
        default=",".join(DEFAULT_SELECTED_CATEGORIES),
        help="Comma-separated categories. Defaults to us_equity,foreign_equity,bond,reits.",
    )
    theme_parser.add_argument("--env-file", help="Optional env file path.")
    theme_parser.add_argument("--output", help="Optional JSON output path.")

    kospi_related_parser = subparsers.add_parser(
        "compute-krx-kospi-related-etf-ratio",
        help="Sum KOSPI-related ETF trading value and compare it against KOSPI trading value.",
    )
    kospi_related_parser.add_argument("--date", required=True, help="Business date in YYYYMMDD.")
    kospi_related_parser.add_argument("--env-file", help="Optional env file path.")
    kospi_related_parser.add_argument("--output", help="Optional JSON output path.")

    kospi_related_history_parser = subparsers.add_parser(
        "compute-krx-kospi-related-etf-ratio-history",
        help="Export historical daily KOSPI-related ETF trading value ratio data.",
    )
    kospi_related_history_parser.add_argument(
        "--start-date",
        default="20100104",
        help="History start date in YYYYMMDD. Defaults to 20100104.",
    )
    kospi_related_history_parser.add_argument(
        "--end-date",
        default="20260427",
        help="History end date in YYYYMMDD. Defaults to 20260427.",
    )
    kospi_related_history_parser.add_argument("--env-file", help="Optional env file path.")
    kospi_related_history_parser.add_argument(
        "--output",
        required=True,
        help="CSV or JSON output path.",
    )

    return parser


def main() -> int:
    parser = _build_parser()
    args = parser.parse_args()

    try:
        if args.command == "init-db":
            init_db(args.db)
            print(json.dumps({"db": args.db, "status": "initialized"}, indent=2))
            return 0

        if args.command == "compute-from-snapshot":
            result = compute_from_snapshot_file(
                snapshot_path=args.snapshot,
                db_path=args.db,
                rule=args.rule,
                min_kospi_weight_sum=args.min_kospi_weight_sum,
            )
            print(json.dumps(result.to_dict(), indent=2, ensure_ascii=False))
            return 0

        if args.command == "compute-from-files":
            result = compute_from_files(
                date=args.date,
                stock_master_path=args.stock_master,
                etf_master_path=args.etf_master,
                holdings_path=args.holdings,
                etf_trading_path=args.etf_trading,
                market_trading_path=args.market_trading,
                mapping_path=args.mapping,
                db_path=args.db,
                rule=args.rule,
                min_kospi_weight_sum=args.min_kospi_weight_sum,
            )
            print(json.dumps(result.to_dict(), indent=2, ensure_ascii=False))
            return 0

        if args.command == "collect-raw-krx":
            config = load_krx_raw_config(args.env_file)
            files = collect_raw_payloads(
                date=args.date,
                output_dir=args.output_dir,
                config=config,
            )
            print(
                json.dumps(
                    {"saved_files": [str(path) for path in files]},
                    indent=2,
                    ensure_ascii=False,
                )
            )
            return 0

        if args.command == "verify-krx-key":
            config = load_krx_raw_config(args.env_file)
            result = verify_auth_key(date=args.date, config=config)
            print(json.dumps(result, indent=2, ensure_ascii=False))
            return 0

        if args.command == "compute-from-raw-krx":
            result = compute_from_raw_dir(
                date=args.date,
                raw_dir=args.raw_dir,
                raw_mapping_path=args.raw_mapping,
                db_path=args.db,
                rule=args.rule,
                min_kospi_weight_sum=args.min_kospi_weight_sum,
            )
            print(json.dumps(result.to_dict(), indent=2, ensure_ascii=False))
            return 0

        if args.command == "collect-and-compute-raw-krx":
            config = load_krx_raw_config(args.env_file)
            collect_raw_payloads(
                date=args.date,
                output_dir=args.output_dir,
                config=config,
            )
            result = compute_from_raw_dir(
                date=args.date,
                raw_dir=f"{args.output_dir}/{args.date}",
                raw_mapping_path=args.raw_mapping,
                db_path=args.db,
                rule=args.rule,
                min_kospi_weight_sum=args.min_kospi_weight_sum,
            )
            print(json.dumps(result.to_dict(), indent=2, ensure_ascii=False))
            return 0

        if args.command == "compute-from-krx-plus-holdings":
            config = load_krx_raw_config(args.env_file)
            result = compute_from_krx_plus_holdings(
                date=args.date,
                holdings_path=args.holdings,
                config=config,
                db_path=args.db,
                rule=args.rule,
                min_kospi_weight_sum=args.min_kospi_weight_sum,
            )
            print(json.dumps(result.to_dict(), indent=2, ensure_ascii=False))
            return 0

        if args.command == "export-krx-etf-catalog":
            config = load_krx_raw_config(args.env_file)
            output = export_live_etf_catalog(
                date=args.date,
                config=config,
                output_path=args.output,
            )
            print(
                json.dumps(
                    {
                        "date": args.date,
                        "output": str(Path(output)),
                    },
                    indent=2,
                    ensure_ascii=False,
                )
            )
            return 0

        if args.command == "compute-krx-etf-theme-trading":
            config = load_krx_raw_config(args.env_file)
            categories = [
                item.strip() for item in args.categories.split(",") if item.strip()
            ]
            summary = compute_live_etf_theme_trading(
                date=args.date,
                config=config,
                selected_categories=categories,
            )
            if args.output:
                output = export_etf_theme_trading_summary(
                    date=args.date,
                    config=config,
                    output_path=args.output,
                    selected_categories=categories,
                )
                print(
                    json.dumps(
                        {
                            "date": args.date,
                            "output": str(Path(output)),
                            "selected_total_trading_value": summary.selected_total_trading_value,
                            "selected_etf_count": summary.selected_etf_count,
                        },
                        indent=2,
                        ensure_ascii=False,
                    )
                )
            else:
                print(json.dumps(summary.to_dict(), indent=2, ensure_ascii=False))
            return 0

        if args.command == "compute-krx-kospi-related-etf-ratio":
            config = load_krx_raw_config(args.env_file)
            summary = compute_live_kospi_related_etf_ratio(
                date=args.date,
                config=config,
            )
            if args.output:
                output = export_kospi_related_etf_ratio(
                    date=args.date,
                    config=config,
                    output_path=args.output,
                )
                print(
                    json.dumps(
                        {
                            "date": args.date,
                            "output": str(Path(output)),
                            "selected_total_trading_value": summary.selected_total_trading_value,
                            "kospi_trading_value": summary.kospi_trading_value,
                            "ratio": summary.ratio,
                            "selected_etf_count": summary.selected_etf_count,
                        },
                        indent=2,
                        ensure_ascii=False,
                    )
                )
            else:
                print(json.dumps(summary.to_dict(), indent=2, ensure_ascii=False))
            return 0

        if args.command == "compute-krx-kospi-related-etf-ratio-history":
            config = load_krx_raw_config(args.env_file)
            output = export_kospi_related_etf_ratio_history(
                start_date=args.start_date,
                end_date=args.end_date,
                config=config,
                output_path=args.output,
            )
            if str(output).lower().endswith(".csv"):
                with Path(output).open("r", encoding="utf-8-sig", newline="") as handle:
                    row_count = max(sum(1 for _ in handle) - 1, 0)
            else:
                row_count = len(json.loads(Path(output).read_text(encoding="utf-8")))
            print(
                json.dumps(
                    {
                        "start_date": args.start_date,
                        "end_date": args.end_date,
                        "output": str(Path(output)),
                        "row_count": row_count,
                    },
                    indent=2,
                    ensure_ascii=False,
                )
            )
            return 0

        parser.error(f"Unknown command: {args.command}")
        return 2
    except KrxUnauthorizedError as exc:
        print(
            json.dumps(
                {
                    "error": "krx_unauthorized",
                    "message": str(exc),
                },
                indent=2,
                ensure_ascii=False,
            )
        )
        return 1
    except Exception as exc:
        print(
            json.dumps(
                {
                    "error": type(exc).__name__,
                    "message": str(exc),
                },
                indent=2,
                ensure_ascii=False,
            )
        )
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
