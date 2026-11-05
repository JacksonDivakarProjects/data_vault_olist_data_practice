# Olist Data Vault (DuckDB)

Data Vault 2.0 practice project built on the [Olist Brazilian e-commerce dataset](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce), using DuckDB and Jupyter notebooks.

## Layers

| Folder | Layer | Notebooks |
|---|---|---|
| `notebooks/01_staging` | Staging | `stg_landing`, `stg_prep` |
| `notebooks/02_raw_vault` | Raw Data Vault (hubs, links, satellites) | `raw_vault` |
| `notebooks/03_business_vault` | Business Vault | `bv_bridge`, `bv_enrichment`, `bv_pit` |
| `notebooks/04_information_mart` | Information Mart (dimensions, facts) | `im_dim`, `im_fact` |

## Project structure

```
data/raw/         Source Olist CSV files
data/warehouse/   Generated DuckDB file (git-ignored)
notebooks/        Pipeline notebooks, numbered in execution order
orchestrator.py   Runs all notebooks in order
```

## Setup and run

```bash
python -m venv .venv
.venv\Scripts\activate        # Windows
pip install -r requirements.txt

python orchestrator.py            # run the full pipeline
python orchestrator.py --no-save  # run without writing outputs back into notebooks
```

Notebooks locate the project root automatically, so they can also be run one by one from Jupyter in the numbered order.
