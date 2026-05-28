from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import os


DEFAULT_STOCK_MASTER_URL = "https://data-dbg.krx.co.kr/svc/apis/sto/stk_isu_base_info"
DEFAULT_STOCK_TRADING_URL = "https://data-dbg.krx.co.kr/svc/apis/sto/stk_bydd_trd"


def _parse_env_file(env_file: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    if not env_file.exists():
        return values

    for raw_line in env_file.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue

        key, value = line.split("=", 1)
        values[key.strip()] = value.strip().strip('"').strip("'")

    return values


def _read_setting(name: str, env_values: dict[str, str]) -> str | None:
    if name in os.environ:
        return os.environ[name]
    return env_values.get(name)


def _collect_env_values(env_file: str | Path | None) -> dict[str, str]:
    values: dict[str, str] = {}

    candidate_paths: list[Path] = []
    if env_file:
        candidate_paths.append(Path(env_file))
    else:
        candidate_paths.extend(
            [
                Path(".env"),
                Path("env/.env"),
                Path("../env/.env"),
            ]
        )

    for path in candidate_paths:
        try:
            resolved = path.resolve(strict=False)
        except Exception:
            resolved = path

        parsed = _parse_env_file(resolved)
        for key, value in parsed.items():
            if key not in values:
                values[key] = value

    return values


@dataclass(frozen=True)
class KrxRawConfig:
    auth_key: str | None
    output_block: str
    etf_master_code_field: str
    etf_holdings_etf_code_field: str
    stock_master_url: str | None
    stock_trading_url: str | None
    etf_master_url: str | None
    etf_holdings_url: str | None
    etf_trading_url: str | None
    market_summary_url: str | None

    @property
    def has_auth_key(self) -> bool:
        return bool(self.auth_key and self.auth_key.strip())


def load_krx_raw_config(env_file: str | Path | None = None) -> KrxRawConfig:
    file_values = _collect_env_values(env_file)
    auth_key = (
        _read_setting("KRX_API", file_values)
        or _read_setting("KRX_AUTH_KEY", file_values)
        or _read_setting("AUTH_KEY", file_values)
    )
    return KrxRawConfig(
        auth_key=auth_key,
        output_block=_read_setting("KRX_OUTPUT_BLOCK", file_values) or "OutBlock_1",
        etf_master_code_field=_read_setting("KRX_ETF_MASTER_CODE_FIELD", file_values)
        or "ISU_SRT_CD",
        etf_holdings_etf_code_field=_read_setting(
            "KRX_ETF_HOLDINGS_ETF_CODE_FIELD", file_values
        )
        or "ETF_CODE",
        stock_master_url=_read_setting("KRX_STOCK_MASTER_URL", file_values)
        or DEFAULT_STOCK_MASTER_URL,
        stock_trading_url=_read_setting("KRX_STOCK_TRADING_URL", file_values)
        or DEFAULT_STOCK_TRADING_URL,
        etf_master_url=_read_setting("KRX_ETF_MASTER_URL", file_values),
        etf_holdings_url=_read_setting("KRX_ETF_HOLDINGS_URL", file_values),
        etf_trading_url=_read_setting("KRX_ETF_TRADING_URL", file_values),
        market_summary_url=_read_setting("KRX_MARKET_SUMMARY_URL", file_values),
    )
