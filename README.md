# QuBTC: public quantum-risk warnings and Bitcoin holders' precaution

Analysis code for the study *Public warnings elicit little precaution against Bitcoin's quantum vulnerability* (Yulin Liu, Quantum Economics AI Lab).

The study asks whether public warnings about quantum attacks on Bitcoin's signatures led holders of exposed keys to move their coins to keys whose public keys have not been revealed. It uses the full Bitcoin ledger from the genesis block to 22 September 2026 (block 968,201), six dated quantum-risk events (2024–2026), randomization inference against placebo dates, and the Randstorm wallet-vulnerability disclosure (2023) as a positive control.

**Data**: Harvard Dataverse, [doi:10.7910/DVN/THUHEB](https://doi.org/10.7910/DVN/THUHEB). The dataset holds the inputs that cannot be regenerated (event list, frozen Wikipedia and Google Trends series, exchange addresses, hand-audited labels), the analysis tables used for estimation, and every estimate behind the figures and tables. Its README documents each table.

## Repository layout

```
notebooks/   00–40: data pipeline and analysis (Google Colab + BigQuery); 90: export to Dataverse
figures/     make_main_figures.py (Figures 1–4), make_sm_figures.py (Figures S1–S7)
requirements.txt
CITATION.cff, LICENSE
```

## Three ways to reproduce

### 1. Figures from the published estimates (minutes, no cloud account)

```bash
pip install -r requirements.txt
# download and unpack the Dataverse dataset, e.g. into ./dataverse (it contains results/ and data/)
QUBTC_DATA=dataverse QUBTC_FIGS=figs python figures/make_main_figures.py
QUBTC_DATA=dataverse QUBTC_FIGS=figs python figures/make_sm_figures.py
```

### 2. Estimates from the published analysis tables (under US$1)

Notebooks 20 and 20b read only tables in `data/analysis/` of the dataset. Load the published tables into a BigQuery dataset named `qbtc_raw` in your own project, keeping the table names:

```bash
bq mk --dataset --location=US YOUR_PROJECT:qbtc_raw
for f in dataverse/data/analysis/*.parquet dataverse/data/inputs/*.parquet; do
  bq load --source_format=PARQUET YOUR_PROJECT:qbtc_raw.$(basename "$f" .parquet) "$f"
done
```

Then open the notebook in Colab, set `PROJECT_ID` in the first cell and run it. Notebook 20 reproduces the pooled effect +0.0000818 (exposed − control, key-weighted, y1 strict, day +30); 20b, 22 and 22b check that they reproduce it to within 1e-8.

The estimation steps of 21 (step 3) and 23 (steps 1 and 6) also need only published tables (`panel_rs2`, `panel_rs2_ext`, `events_rs`, `placebo_days_rs`, `panel_event`, `placebo_draws_strict`, attention tables). Their first cell, however, checks that the full pipeline exists; remove that check and skip the table-building steps.

### 3. Full rebuild from the public ledger

Run the notebooks in order in Google Colab with a Google Cloud project that has billing enabled. Each notebook starts with a configuration cell (`PROJECT_ID`, dataset `qbtc_raw`, location `US`); every query is dry-run first and stops above a per-query limit (`MAX_USD_PER_QUERY`, default US$5) until `CONFIRM = True` is set. In the notebooks that build tables, tables are written with `CREATE OR REPLACE TABLE` and an existing table is skipped unless `FORCE_REBUILD = True`. Jobs run on the BigQuery server and continue if the Colab runtime disconnects; job IDs are saved to `jobs.json`. To resume, re-run the configuration and helper cells, then the reconnect cell near the end of the notebook.

| Notebook | What it builds | Approx. cost (list price) |
|---|---|---|
| `00_bigquery_healthcheck` | Freshness, gaps, field checks, cost estimates, block reconciliation | < $1 |
| `01_build_utxo_life` | `utxo_life` (every output with creation and spend), `address_stats`, `supply_by_type` | ~$20 |
| `02_exposure_snapshot` | `address_key` (address → key), `key_exposure` (first revelation of each public key), `holder_snapshot` (balances at t−1 of each event) | ~$3 |
| `03_events_attention` | `events`, attention indices (Wikipedia, GDELT, Google Trends), placebo dates and draws | < $1 |
| `02b_placebo_snapshots` | `holder_snapshot_placebo` (run after 03) | ~$5 |
| `04_flow_tagging` | Exchange labels, positive-control snapshots, outflow destinations y0–y3 per key and day | ~$13 |
| `04b_custodial_migration` | Coinbase on-chain migration of 2025-11-22: custodial keys, confound, re-drawn placebo pools | < $0.1 |
| `04c_large_mover_audit` | Key-days with ≥ 1,000 BTC outflows; merges hand-audited institutional keys into the exclusions | < $0.5 |
| `05_panel` | `panel_keys`, `panel_key_flows`, `panel_hazard`, `panel_event`, `panel_cem_strata` | ~$1.5 |
| `20_estimation` | Event effects, randomization inference, joint Google × BIP-361 estimate, hazard models, equivalence tests | < $0.1 |
| `20b_attention_subsets` | High- vs low-attention events; calendar-time placebo data | < $0.1 |
| `21_randstorm_pc` | Randstorm positive control: uncompressed vs compressed public keys, 2012-04 to 2014-03 | ~$5 |
| `22_y1_audit` | One-hop tracing of "y1 strict" outflows; stricter outcome definitions | ~$3 |
| `22b_randstorm_strict` | Randstorm under the stricter outcome definitions | ~$1.5 |
| `23_randstorm_local_pool` | Randstorm with a same-period placebo pool (2022–2024); 10-10 notification date | ~$13 |
| `30_exposure_segments` | Who holds the exposed coins: migrated, moved, active, indeterminate, behaviorally unreachable | ~$6 |
| `40_migration_bottleneck` | Block-space needed to migrate, fees, remaining exposure under scenarios | ~$4 |
| `90_dataverse_upload` | Exports the published tables to Parquet and uploads them to Harvard Dataverse (documentation of how the dataset was made) | free |

The full rebuild costs roughly US$70 in query charges at on-demand list prices (the first 1 TiB of queries per month is free) and stores about 1.4 TB in BigQuery (about US$28 per month of active storage; if you mind the monthly storage cost, this table can be deleted afterwards).

**Inputs that change over time.** To reproduce the published numbers exactly rather than with re-pulled sources:

- **Wikipedia and Google Trends** (03): load `wiki_frozen` and `gtrends_frozen` from `data/inputs/` into `qbtc_raw` before running 03, and keep `FREEZE_REFRESH = False`. Google Trends re-samples on every pull.
- **Exchange addresses** (04): copy `supplementary/Data_S1_exchange_addresses.csv` into the Colab working directory as `exchange_addresses_manual.csv`; it is merged with whatever the exchange pages still serve.
- **Large-transfer labels** (04c): copy `supplementary/Data_S2_large_movers_labeled.csv` into the Colab working directory as `large_movers_labeled.csv`.
- **Patoshi blocks** (30): downloaded from GitHub (`bensig/patoshi-addresses`); the block heights used are in `data/inputs/patoshi_blocks.parquet`.
- **Freeze date**: `FREEZE_DATE = "2026-09-22"`. The public BigQuery tables keep growing; spends after the freeze date are treated as unspent, so later data do not change the results, but the snapshot dates and coverage checks assume this date.

## Definitions used throughout

- **Key**: the public key or script controlling one or more addresses (P2PK, P2PKH and P2WPKH of the same public key are merged).
- **Groups**: `L` legacy keys whose public key is visible on chain; `T` Taproot keys; `C` hash-type keys whose public key has not been revealed (control).
- **Risk set**: keys with ≥ 0.01 BTC on the day before the event and an incoming transfer in the previous 365 days, excluding exchanges, services and custodial keys.
- **Main outcome, y1 strict**: share of a key's balance sent within 30 days to a never-seen hash-type address that then stays unspent for 30 days.
- **Inference**: event effect = CEM-matched exposed − control difference minus a local linear baseline fitted on placebo dates; p-values and intervals from leave-one-out placebo residuals.

## Figures

| Figure | Script | Inputs (in the dataset) |
|---|---|---|
| 1 | `make_main_figures.py` | `data/analysis/attention_daily.parquet`, `results/out40/q3_uneconomic_by_cls_type.csv` |
| 2 | `make_main_figures.py` | `results/est_20_effects.csv.gz`, `est_20_pooled.csv`, `out20b/est_20b_subsets.csv`, `est_21_pooled.csv`, `out23/est_23_pc.csv`, `pubform_by_month.csv` |
| 3 | `make_main_figures.py` | `results/out30/q2_segments.csv`, `q2_sensitivity.csv`, `out40/q3_stock_by_cls.csv` |
| 4 | `make_main_figures.py` | `results/out40/q3_throughput.csv`, `q3_remaining_curve.csv` |
| S1–S3 | `make_sm_figures.py` | `results/est_20_paths.csv.gz`, `out20b/est_20b_levels.csv`, `est_20_effects.csv.gz`, `est_20_pooled.csv` |
| S4 | `make_sm_figures.py` | `results/out30/q2_bridge.csv` |
| S5 | `make_sm_figures.py` | `results/out40/q3_fees.csv` |
| S6 | `make_sm_figures.py` | `results/out20b/est_20b_calendar.csv` |
| S7 | `make_sm_figures.py` | `results/out23/est_23_calendar_uc.csv`, `est_23_notice_path.csv` |

## Requirements

Python 3.10+. The notebooks were run on Google Colab, which provides `google-cloud-bigquery`, pandas, NumPy, SciPy and Matplotlib; notebook 03 also needs `pytrends`, and notebook 90 installs `dvuploader`. See `requirements.txt` for running locally.

## License and citation

Code: MIT License. Data: see the Dataverse dataset (CC BY 4.0). Please cite the article and the dataset; `CITATION.cff` gives the software citation.

Contact: Yulin Liu, yulin@quantecon.ai