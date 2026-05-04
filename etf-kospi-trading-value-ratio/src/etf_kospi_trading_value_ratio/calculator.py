from __future__ import annotations

from collections import defaultdict

from .models import DailyRatioResult, DailySnapshot, EtfInclusionDetail


RULE_ANY_KOSPI_CONSTITUENT = "any_kospi_constituent"
RULE_MIN_KOSPI_WEIGHT_SUM = "min_kospi_weight_sum"
SUPPORTED_RULES = {
    RULE_ANY_KOSPI_CONSTITUENT,
    RULE_MIN_KOSPI_WEIGHT_SUM,
}


def _should_include(
    *,
    rule: str,
    kospi_holding_count: int,
    kospi_weight_sum: float,
    min_kospi_weight_sum: float,
) -> bool:
    if rule == RULE_ANY_KOSPI_CONSTITUENT:
        return kospi_holding_count > 0
    if rule == RULE_MIN_KOSPI_WEIGHT_SUM:
        return kospi_weight_sum > min_kospi_weight_sum
    raise ValueError(f"Unsupported rule: {rule}")


def compute_daily_ratio(
    snapshot: DailySnapshot,
    *,
    rule: str = RULE_ANY_KOSPI_CONSTITUENT,
    min_kospi_weight_sum: float = 0.0,
    target_market: str = "KOSPI",
) -> DailyRatioResult:
    if rule not in SUPPORTED_RULES:
        raise ValueError(
            f"Unsupported rule '{rule}'. Expected one of: {sorted(SUPPORTED_RULES)}"
        )

    normalized_market = target_market.strip().upper()
    kospi_stocks = {
        record.stock_code
        for record in snapshot.stocks
        if record.market.strip().upper() == normalized_market
    }

    etf_name_by_code = {record.etf_code: record.etf_name for record in snapshot.etfs}
    trading_by_etf: dict[str, float] = defaultdict(float)
    for row in snapshot.etf_trading:
        trading_by_etf[row.etf_code] += row.trading_value

    holding_count_by_etf: dict[str, int] = defaultdict(int)
    kospi_weight_by_etf: dict[str, float] = defaultdict(float)
    for row in snapshot.holdings:
        if row.stock_code not in kospi_stocks:
            continue
        holding_count_by_etf[row.etf_code] += 1
        kospi_weight_by_etf[row.etf_code] += row.weight

    denominator = sum(
        row.trading_value
        for row in snapshot.market_trading
        if row.market.strip().upper() == normalized_market
    )
    if denominator <= 0:
        raise ValueError(
            f"Market trading value for market '{normalized_market}' must be positive."
        )

    all_etf_codes = set(etf_name_by_code) | set(trading_by_etf) | set(holding_count_by_etf)
    details: list[EtfInclusionDetail] = []

    for etf_code in sorted(all_etf_codes):
        kospi_holding_count = holding_count_by_etf.get(etf_code, 0)
        kospi_weight_sum = kospi_weight_by_etf.get(etf_code, 0.0)
        trading_value = trading_by_etf.get(etf_code, 0.0)
        included = _should_include(
            rule=rule,
            kospi_holding_count=kospi_holding_count,
            kospi_weight_sum=kospi_weight_sum,
            min_kospi_weight_sum=min_kospi_weight_sum,
        )
        details.append(
            EtfInclusionDetail(
                etf_code=etf_code,
                etf_name=etf_name_by_code.get(etf_code, etf_code),
                kospi_holding_count=kospi_holding_count,
                kospi_weight_sum=kospi_weight_sum,
                trading_value=trading_value,
                included=included,
            )
        )

    numerator = sum(item.trading_value for item in details if item.included)
    ratio = numerator / denominator

    return DailyRatioResult(
        date=snapshot.date,
        rule=rule,
        min_kospi_weight_sum=min_kospi_weight_sum,
        eligible_etf_count=sum(1 for item in details if item.included),
        numerator=numerator,
        denominator=denominator,
        ratio=ratio,
        details=details,
    )
