from __future__ import annotations

from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class StockMasterRecord:
    stock_code: str
    market: str


@dataclass(frozen=True)
class EtfMasterRecord:
    etf_code: str
    etf_name: str


@dataclass(frozen=True)
class EtfHoldingRecord:
    etf_code: str
    stock_code: str
    weight: float


@dataclass(frozen=True)
class EtfTradingRecord:
    etf_code: str
    trading_value: float


@dataclass(frozen=True)
class MarketTradingRecord:
    market: str
    trading_value: float


@dataclass(frozen=True)
class DailySnapshot:
    date: str
    stocks: list[StockMasterRecord]
    etfs: list[EtfMasterRecord]
    holdings: list[EtfHoldingRecord]
    etf_trading: list[EtfTradingRecord]
    market_trading: list[MarketTradingRecord]


@dataclass(frozen=True)
class EtfInclusionDetail:
    etf_code: str
    etf_name: str
    kospi_holding_count: int
    kospi_weight_sum: float
    trading_value: float
    included: bool

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True)
class DailyRatioResult:
    date: str
    rule: str
    min_kospi_weight_sum: float
    eligible_etf_count: int
    numerator: float
    denominator: float
    ratio: float | None
    details: list[EtfInclusionDetail]

    def to_dict(self) -> dict[str, object]:
        payload = asdict(self)
        payload["details"] = [item.to_dict() for item in self.details]
        return payload


@dataclass(frozen=True)
class EtfThemeTradingDetail:
    etf_code: str
    etf_name: str
    index_name: str
    trading_value: float
    region: str
    asset_family: str
    is_covered_call: bool
    matched_categories: list[str]
    matched_subcategories: list[str]

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True)
class EtfThemeTradingSummary:
    date: str
    selected_categories: list[str]
    selected_etf_count: int
    selected_total_trading_value: float
    total_etf_count: int
    total_etf_trading_value: float
    category_totals: dict[str, float]
    subcategory_totals: dict[str, float]
    details: list[EtfThemeTradingDetail]

    def to_dict(self) -> dict[str, object]:
        payload = asdict(self)
        payload["details"] = [item.to_dict() for item in self.details]
        return payload


@dataclass(frozen=True)
class KospiRelatedEtfDetail:
    etf_code: str
    etf_name: str
    index_name: str
    trading_value: float
    include_reason: str

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True)
class KospiRelatedEtfRatioSummary:
    date: str
    selected_etf_count: int
    selected_total_trading_value: float
    kospi_trading_value: float
    ratio: float
    details: list[KospiRelatedEtfDetail]

    def to_dict(self) -> dict[str, object]:
        payload = asdict(self)
        payload["details"] = [item.to_dict() for item in self.details]
        return payload
