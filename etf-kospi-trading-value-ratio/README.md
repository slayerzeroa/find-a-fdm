# ETF KOSPI Trading Value Ratio

This project computes a daily ratio:

`sum(trading value of ETFs that include KOSPI stocks) / KOSPI market trading value`

The first MVP is intentionally KRX-first.

- KRX is the primary source of truth for end-of-day market data.
- The project supports both official CSV exports and authenticated raw KRX HTTP collection.
- The raw KRX path uses the same `AUTH_KEY` header pattern already used elsewhere in this repository.

## Metric definition

The project supports two inclusion rules:

1. `any_kospi_constituent`
   An ETF is included when it holds at least one KOSPI-listed stock.
2. `min_kospi_weight_sum`
   An ETF is included when the sum of KOSPI stock weights is above a threshold.

Both values are stored so you can compare the loose and strict interpretations later.

## Recommended KRX workflow

Export the following daily datasets from KRX and place them in a local input folder:

1. KOSPI stock master
2. ETF master
3. ETF holdings or PDF holdings export
4. ETF daily trading value
5. KOSPI market trading value

Then map the exported column names to this project's canonical schema using a JSON mapping file.

## Direct KRX API key flow

If you already have a KRX API key, set it in `.env` as `KRX_API=<your key>`.

This project now supports:

1. `verify-krx-key`
   Checks that the key works against a known raw endpoint.
2. `collect-raw-krx`
   Downloads raw KRX JSON payloads using the key.
3. `compute-from-raw-krx`
   Normalizes collected raw JSON and computes the ratio.
4. `collect-and-compute-raw-krx`
   Runs collection and computation in one command.
5. `compute-from-krx-plus-holdings`
   Uses KRX API for the daily market data and a local ETF holdings file for composition.
6. `export-krx-etf-catalog`
   Exports the live KRX ETF code/name list for a selected date.
7. `compute-krx-etf-theme-trading`
   Sums trading value for broad KRX ETF themes such as US, foreign equity, bonds, and REITs.

The raw KRX endpoints still vary by account and screen. For that reason, `.env` keeps endpoint URLs configurable.

### Important KRX approval note

KRX OPEN API requires two separate steps:

1. issue an auth key
2. apply for each API service you want to call

If `verify-krx-key` returns `401 Unauthorized`, that usually means the key exists but the target service has not been approved yet.

For this project, the minimum likely approvals are:

- `유가증권 종목기본정보`
- `ETF 일별매매정보`
- `유가증권 일별매매정보`

Also note that the public KRX OPEN API service list clearly exposes `ETF 일별매매정보`, but does not clearly expose an ETF holdings/PDF constituent API in the same catalog. In practice, that means ETF holdings may still need to come from KRX export data or another source unless your account has a separate approved/internal endpoint for holdings.

## Canonical fields

The pipeline normalizes all inputs into the following shapes:

- `stock_master`: `stock_code`, `market`
- `etf_master`: `etf_code`, `etf_name`
- `holdings`: `etf_code`, `stock_code`, `weight`
- `etf_trading`: `etf_code`, `trading_value`
- `market_trading`: `market`, `trading_value`

## Quick start

Initialize a SQLite database:

```bash
python main.py init-db --db output/project.db
```

Run from the sample snapshot:

```bash
python main.py compute-from-snapshot ^
  --snapshot tests/fixtures/sample_snapshot.json ^
  --db output/project.db
```

Verify your KRX key:

```bash
python main.py verify-krx-key ^
  --date 20260427 ^
  --env-file .env
```

Collect raw KRX payloads with the API key:

```bash
python main.py collect-raw-krx ^
  --date 20260427 ^
  --output-dir raw ^
  --env-file .env
```

Compute from collected raw KRX JSON:

```bash
python main.py compute-from-raw-krx ^
  --date 20260427 ^
  --raw-dir raw/20260427 ^
  --raw-mapping tests/fixtures/raw_mapping.json ^
  --db output/project.db
```

Run the full KRX API key flow in one step:

```bash
python main.py collect-and-compute-raw-krx ^
  --date 20260427 ^
  --output-dir raw ^
  --raw-mapping tests/fixtures/raw_mapping.json ^
  --env-file .env ^
  --db output/project.db
```

Run the practical hybrid flow:

```bash
python main.py compute-from-krx-plus-holdings ^
  --date 20260427 ^
  --holdings tests/fixtures/holdings.csv ^
  --env-file .env ^
  --db output/project.db
```

This command assumes:

- `KRX_STOCK_MASTER_URL` is approved
- `KRX_STOCK_TRADING_URL` is approved
- `KRX_ETF_TRADING_URL` is approved and points to your ETF daily trading endpoint
- ETF holdings come from a local canonical file instead of a KRX holdings API

The holdings file may contain either:

- `etf_code`, `stock_code`, `weight`
- `etf_name`, `stock_code`, `weight`

If only `etf_name` is present, the project resolves it against the live KRX ETF name list for the selected date.

Export the live ETF catalog first:

```bash
python main.py export-krx-etf-catalog ^
  --date 20260427 ^
  --output output/krx_etf_catalog_20260427.csv
```

Run the simplified theme-based trading-value flow:

```bash
python main.py compute-krx-etf-theme-trading ^
  --date 20260427 ^
  --output output/krx_etf_theme_trading_20260427.json
```

Default categories:

- `us_equity`
- `foreign_equity`
- `bond`
- `reits`

Internally these are refined into more specific subcategories such as:

- `china_equity`, `japan_equity`, `india_equity`, `taiwan_equity`, `global_equity`
- `domestic_bond`, `foreign_bond`, `mixed_bond`
- `domestic_reits`, `foreign_reits`

You can override them:

```bash
python main.py compute-krx-etf-theme-trading ^
  --date 20260427 ^
  --categories us_equity,bond,reits
```

Run from CSV files:

```bash
python main.py compute-from-files ^
  --date 20260427 ^
  --stock-master tests/fixtures/stock_master.csv ^
  --etf-master tests/fixtures/etf_master.csv ^
  --holdings tests/fixtures/holdings.csv ^
  --etf-trading tests/fixtures/etf_trading.csv ^
  --market-trading tests/fixtures/market_trading.csv ^
  --mapping tests/fixtures/mapping.json ^
  --db output/project.db
```

Run the stricter rule:

```bash
python main.py compute-from-files ^
  --date 20260427 ^
  --stock-master tests/fixtures/stock_master.csv ^
  --etf-master tests/fixtures/etf_master.csv ^
  --holdings tests/fixtures/holdings.csv ^
  --etf-trading tests/fixtures/etf_trading.csv ^
  --market-trading tests/fixtures/market_trading.csv ^
  --mapping tests/fixtures/mapping.json ^
  --db output/project.db ^
  --rule min_kospi_weight_sum ^
  --min-kospi-weight-sum 0.10
```

## Mapping file format

Example:

```json
{
  "stock_master": {
    "stock_code": "code",
    "market": "market"
  },
  "etf_master": {
    "etf_code": "code",
    "etf_name": "name"
  },
  "holdings": {
    "etf_code": "etf_code",
    "stock_code": "stock_code",
    "weight": "weight"
  },
  "etf_trading": {
    "etf_code": "etf_code",
    "trading_value": "trading_value"
  },
  "market_trading": {
    "market": "market",
    "trading_value": "trading_value"
  }
}
```

## Optional raw KRX collection

If you already have a KRX auth key and concrete raw endpoint URLs, fill `.env` from `.env.example` and run:

```bash
python main.py collect-raw-krx ^
  --date 20260427 ^
  --output-dir raw ^
  --env-file .env
```

This command saves raw JSON payloads only. It does not assume field names for normalization.

### Raw mapping file

`compute-from-raw-krx` expects a mapping that tells the project where rows live in each JSON payload and which raw field names map to canonical fields.

See [tests/fixtures/raw_mapping.json](C:\Users\slaye\VscodeProjects\find-a-fdm\etf-kospi-trading-value-ratio\tests\fixtures\raw_mapping.json) for a working example.

## Output tables

The SQLite database contains:

- `daily_ratio_results`
- `daily_ratio_etf_details`

## Official references

- KRX Data Marketplace: https://data.krx.co.kr/contents/MDC/MAIN/main/index.cmd
- KRX market data terms: https://data.krx.co.kr/contents/MDC/INFO/informationController/MDCINFO003.cmd
- KIS Open API catalog: https://apiportal.koreainvestment.com/apiservice
- Kiwoom REST API guide: https://openapi.kiwoom.com/guide/apiguide

## Notes

- This MVP is end-of-day oriented.
- For near-real-time expansion, keep holdings from KRX and replace or supplement ETF trading values with a brokerage API such as KIS.
- `KRX_STOCK_MASTER_URL=https://data-dbg.krx.co.kr/svc/apis/sto/stk_isu_base_info` is taken from the existing repository code and verified live.
- `KRX_STOCK_TRADING_URL=https://data-dbg.krx.co.kr/svc/apis/sto/stk_bydd_trd` maps to the official `유가증권 일별매매정보` service.
- `KRX_ETF_TRADING_URL=https://data-dbg.krx.co.kr/svc/apis/etp/etf_bydd_trd` maps to the official `ETF 일별매매정보` service.
- Other raw KRX endpoint URLs may differ by screen or account. Keep those values configurable in `.env` and verify them in your environment.
- KRX Data Marketplace HTML confirms that `PDF(Portfolio Deposit File)` exists under both the ETF branch (`screen-no=13108`) and the 상장형 수익증권 branch (`screen-no=13408`). The publicly reachable direct JSP we traced is the 상장형 수익증권 branch (`MDCSTAT407/408/409`), while the ETF-only direct JSP route is still not obvious from the public menu HTML alone.
- The theme-based flow uses ETF `ISU_NM` and `IDX_IND_NM` keyword heuristics, so it is intentionally approximate. It is useful as a practical interim metric when a full holdings-based definition is too expensive to maintain.
- Broad category totals are de-duplicated at the category level, but `subcategory_totals` may overlap when one ETF is both a bond and a mixed asset product, for example.
