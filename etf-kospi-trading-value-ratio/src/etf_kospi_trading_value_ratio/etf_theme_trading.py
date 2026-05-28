from __future__ import annotations

from pathlib import Path
import json

from .config import KrxRawConfig
from .models import EtfThemeTradingDetail, EtfThemeTradingSummary
from .providers.krx_raw import _extract_output_rows, _fetch_json


DEFAULT_SELECTED_CATEGORIES = [
    "us_equity",
    "foreign_equity",
    "bond",
    "reits",
]


BROAD_TO_SUBCATEGORY: dict[str, list[str]] = {
    "us_equity": ["us_equity"],
    "foreign_equity": [
        "china_equity",
        "japan_equity",
        "india_equity",
        "taiwan_equity",
        "europe_equity",
        "global_equity",
        "other_foreign_equity",
    ],
    "bond": [
        "domestic_bond",
        "foreign_bond",
        "mixed_bond",
    ],
    "reits": [
        "domestic_reits",
        "foreign_reits",
    ],
}


SUBCATEGORY_RULES: dict[str, dict[str, list[str]]] = {
    "us_equity": {
        "include": ["미국", "S&P", "나스닥", "NASDAQ", "다우", "DOW", "러셀", "RUSSELL", "NYSE", "필라델피아"],
        "exclude": ["채권", "국채", "미국채", "리츠", "REIT", "머니마켓", "CD금리", "전단채", "회사채"],
    },
    "china_equity": {
        "include": ["중국", "차이나", "CSI", "HANG SENG", "항셍", "홍콩"],
        "exclude": ["채권", "리츠", "REIT"],
    },
    "japan_equity": {
        "include": ["일본", "NIKKEI", "TOPIX", "엔화"],
        "exclude": ["채권", "국채", "리츠", "REIT"],
    },
    "india_equity": {
        "include": ["인도", "NIFTY", "SENSEX"],
        "exclude": ["채권", "리츠", "REIT"],
    },
    "taiwan_equity": {
        "include": ["대만", "TAIWAN", "TSMC"],
        "exclude": ["채권", "리츠", "REIT"],
    },
    "europe_equity": {
        "include": ["유럽", "EURO", "STOXX", "독일", "프랑스", "영국"],
        "exclude": ["채권", "리츠", "REIT"],
    },
    "global_equity": {
        "include": ["글로벌", "해외", "WORLD", "월드", "선진국", "신흥국", "MSCI", "아시아", "브라질", "베트남"],
        "exclude": ["채권", "리츠", "REIT", "미국채", "국채"],
    },
    "other_foreign_equity": {
        "include": ["해외주식", "해외주", "해외증시"],
        "exclude": ["채권", "리츠", "REIT"],
    },
    "domestic_bond": {
        "include": ["채권", "국채", "회사채", "통안", "전단채", "특수채", "CD금리", "머니마켓", "단기금융채", "국공채"],
        "exclude": ["미국채", "해외", "글로벌", "월드", "WORLD"],
    },
    "foreign_bond": {
        "include": ["미국채", "채권", "국채", "해외채권", "글로벌채권"],
        "exclude": ["리츠", "REIT"],
    },
    "mixed_bond": {
        "include": ["채권혼합", "혼합50", "혼합", "멀티에셋", "TDF", "타겟데이트"],
        "exclude": [],
    },
    "domestic_reits": {
        "include": ["리츠", "REIT"],
        "exclude": ["미국", "해외", "글로벌", "월드", "WORLD"],
    },
    "foreign_reits": {
        "include": ["리츠", "REIT"],
        "exclude": [],
    },
}


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
]

COVERED_CALL_HINTS = [
    "커버드콜",
    "COVEREDCALL",
    "COVERED CALL",
    "BUYWRITE",
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


def _match_subcategories(*, etf_name: str, index_name: str) -> list[str]:
    text = f"{etf_name} {index_name}"
    matched: list[str] = []

    for subcategory, rule in SUBCATEGORY_RULES.items():
        include_ok = _has_any(text, rule["include"])
        exclude_hit = _has_any(text, rule["exclude"])
        if include_ok and not exclude_hit:
            matched.append(subcategory)

    if "foreign_reits" in matched and not _has_any(text, FOREIGN_HINTS):
        matched.remove("foreign_reits")
    if "foreign_bond" in matched and not _has_any(text, FOREIGN_HINTS + ["미국채"]):
        matched.remove("foreign_bond")
    if "mixed_bond" in matched and "bond" not in text.upper() and not _has_any(
        text, ["혼합", "TDF", "타겟데이트", "채권혼합"]
    ):
        matched.remove("mixed_bond")

    return matched


def _subcategory_to_categories(subcategories: list[str]) -> list[str]:
    matched_categories: list[str] = []
    sub_set = set(subcategories)
    for category, children in BROAD_TO_SUBCATEGORY.items():
        if any(child in sub_set for child in children):
            matched_categories.append(category)
    return matched_categories


def _derive_region(subcategories: list[str]) -> str:
    ordered = [
        "us_equity",
        "china_equity",
        "japan_equity",
        "india_equity",
        "taiwan_equity",
        "europe_equity",
        "global_equity",
        "other_foreign_equity",
        "foreign_bond",
        "foreign_reits",
        "domestic_bond",
        "domestic_reits",
    ]
    for item in ordered:
        if item in subcategories:
            if item.startswith("us_"):
                return "us"
            if item.startswith("china_"):
                return "china"
            if item.startswith("japan_"):
                return "japan"
            if item.startswith("india_"):
                return "india"
            if item.startswith("taiwan_"):
                return "taiwan"
            if item.startswith("europe_"):
                return "europe"
            if item.startswith("global_"):
                return "global"
            if item.startswith("other_foreign_"):
                return "other_foreign"
            if item.startswith("foreign_"):
                return "foreign"
            if item.startswith("domestic_"):
                return "domestic"
    return "unknown"


def _derive_asset_family(subcategories: list[str]) -> str:
    if any(item.endswith("reits") for item in subcategories):
        return "reits"
    if any("bond" in item for item in subcategories):
        if "mixed_bond" in subcategories:
            return "mixed_bond"
        return "bond"
    if any(item.endswith("equity") for item in subcategories):
        return "equity"
    return "other"


def summarize_etf_theme_trading_from_rows(
    *,
    date: str,
    etf_trading_rows: list[dict[str, object]],
    selected_categories: list[str] | None = None,
) -> EtfThemeTradingSummary:
    categories = selected_categories or list(DEFAULT_SELECTED_CATEGORIES)
    category_totals = {category: 0.0 for category in categories}
    selected_subcategories = [
        subcategory
        for category in categories
        for subcategory in BROAD_TO_SUBCATEGORY.get(category, [])
    ]
    subcategory_totals = {subcategory: 0.0 for subcategory in selected_subcategories}
    details: list[EtfThemeTradingDetail] = []
    total_etf_trading_value = 0.0

    for row in etf_trading_rows:
        etf_code = str(row.get("ISU_SRT_CD") or row.get("ISU_CD") or "").strip()
        etf_name = str(row.get("ISU_NM") or row.get("ISU_ABBRV") or etf_code).strip()
        index_name = str(row.get("IDX_IND_NM") or "").strip()
        trading_value = _to_float(row.get("ACC_TRDVAL"))
        total_etf_trading_value += trading_value

        matched_subcategories = [
            subcategory
            for subcategory in _match_subcategories(etf_name=etf_name, index_name=index_name)
            if subcategory in subcategory_totals
        ]
        matched_categories = [
            category
            for category in _subcategory_to_categories(matched_subcategories)
            if category in categories
        ]
        if not matched_categories:
            continue

        details.append(
            EtfThemeTradingDetail(
                etf_code=etf_code,
                etf_name=etf_name,
                index_name=index_name,
                trading_value=trading_value,
                region=_derive_region(matched_subcategories),
                asset_family=_derive_asset_family(matched_subcategories),
                is_covered_call=_has_any(f"{etf_name} {index_name}", COVERED_CALL_HINTS),
                matched_categories=matched_categories,
                matched_subcategories=matched_subcategories,
            )
        )
        for category in matched_categories:
            category_totals[category] += trading_value
        for subcategory in matched_subcategories:
            subcategory_totals[subcategory] += trading_value

    selected_total_trading_value = sum(item.trading_value for item in details)

    return EtfThemeTradingSummary(
        date=date,
        selected_categories=categories,
        selected_etf_count=len(details),
        selected_total_trading_value=selected_total_trading_value,
        total_etf_count=len(etf_trading_rows),
        total_etf_trading_value=total_etf_trading_value,
        category_totals=category_totals,
        subcategory_totals=subcategory_totals,
        details=details,
    )


def compute_live_etf_theme_trading(
    *,
    date: str,
    config: KrxRawConfig,
    selected_categories: list[str] | None = None,
) -> EtfThemeTradingSummary:
    if not config.has_auth_key:
        raise ValueError("KRX auth key not found. Set KRX_API or KRX_AUTH_KEY.")
    if not config.etf_trading_url:
        raise ValueError(
            "KRX_ETF_TRADING_URL is required. Set it to your approved ETF daily trading endpoint."
        )

    payload = _fetch_json(
        f"{config.etf_trading_url}?basDd={date}",
        config.auth_key,
    )
    rows = _extract_output_rows(payload, config.output_block)
    return summarize_etf_theme_trading_from_rows(
        date=date,
        etf_trading_rows=rows,
        selected_categories=selected_categories,
    )


def export_etf_theme_trading_summary(
    *,
    date: str,
    config: KrxRawConfig,
    output_path: str | Path,
    selected_categories: list[str] | None = None,
) -> Path:
    summary = compute_live_etf_theme_trading(
        date=date,
        config=config,
        selected_categories=selected_categories,
    )
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps(summary.to_dict(), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return output
