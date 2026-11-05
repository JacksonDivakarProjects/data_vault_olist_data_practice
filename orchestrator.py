"""Run the Olist Data Vault notebook pipeline end to end, in layer order."""

import argparse
import logging
import time
from pathlib import Path

import nbformat
from nbclient import NotebookClient

PROJECT_ROOT = Path(__file__).resolve().parent
NOTEBOOK_DIR = PROJECT_ROOT / "notebooks"

# Execution order: staging -> raw vault -> business vault -> information mart
NOTEBOOK_PIPELINE = [
    "01_staging/stg_landing.ipynb",
    "01_staging/stg_prep.ipynb",
    "02_raw_vault/raw_vault.ipynb",
    "03_business_vault/bv_bridge.ipynb",
    "03_business_vault/bv_enrichment.ipynb",
    "03_business_vault/bv_pit.ipynb",
    "04_information_mart/im_dim.ipynb",
    "04_information_mart/im_fact.ipynb",
]

CLOSE_CONNECTION_SOURCE = "if 'con' in locals():\n    con.close()"

log = logging.getLogger("orchestrator")


def run_notebook(nb_path: Path, timeout: int, save_outputs: bool) -> None:
    """Execute one notebook in its own directory, releasing the DuckDB lock afterwards."""
    with nb_path.open("r", encoding="utf-8") as f:
        nb = nbformat.read(f, as_version=4)

    # Temporary final cell: close the DuckDB connection so the next notebook can open the file
    nb.cells.append(nbformat.v4.new_code_cell(CLOSE_CONNECTION_SOURCE))
    try:
        NotebookClient(
            nb,
            timeout=timeout,
            resources={"metadata": {"path": str(nb_path.parent)}},
        ).execute()
    finally:
        nb.cells.pop()

    if save_outputs:
        with nb_path.open("w", encoding="utf-8") as f:
            nbformat.write(nb, f)


def run_pipeline(notebooks: list[str], timeout: int = 600, save_outputs: bool = True) -> None:
    paths = [NOTEBOOK_DIR / rel for rel in notebooks]
    missing = [p for p in paths if not p.exists()]
    if missing:
        raise FileNotFoundError(f"Notebooks not found: {', '.join(map(str, missing))}")

    start = time.perf_counter()
    log.info("Starting Olist Data Vault pipeline (%d notebooks)", len(paths))
    for idx, (rel, path) in enumerate(zip(notebooks, paths), start=1):
        step_start = time.perf_counter()
        log.info("[%d/%d] Running %s", idx, len(paths), rel)
        run_notebook(path, timeout, save_outputs)
        log.info("    completed in %.2fs", time.perf_counter() - step_start)
    log.info("All %d notebooks executed in %.2fs", len(paths), time.perf_counter() - start)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--timeout", type=int, default=600, help="per-cell timeout in seconds")
    parser.add_argument(
        "--no-save", action="store_true", help="do not write executed outputs back to the notebooks"
    )
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    run_pipeline(NOTEBOOK_PIPELINE, timeout=args.timeout, save_outputs=not args.no_save)


if __name__ == "__main__":
    main()
