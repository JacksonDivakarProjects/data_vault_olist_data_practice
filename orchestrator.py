import time
from pathlib import Path
import nbformat
from nbclient import NotebookClient

# Root project directory
BASE_DIR = Path(
    r"C:\Users\JacksonDivakarRajasi\OneDrive - JMAN Group Ltd\Documents\Python Folder\DuckDB Environment\Olist Eccomerce DuckDB"
)

# Exact relative paths based on your folder structure in execution order
NOTEBOOK_PIPELINE = [
    "Staging Layer/stg__landing.ipynb",
    "Staging Layer/stg__prep.ipynb",
    "Raw Data Vault/raw_vault_nb.ipynb",
    "Business Vault/business_vault_bridge.ipynb",
    "Business Vault/business_vault_enrichment_nb.ipynb",
    "Business Vault/business_vault_pit_nb.ipynb",
    "Information Mart/Dimension Tables/information_mart_dim.ipynb",
    "Information Mart/Fact Tables/information_mart_fact.ipynb",
]


def run_notebook_pipeline(base_dir: Path, notebook_paths: list[str]) -> None:
    pipeline_start = time.perf_counter()
    print("Starting Olist Data Vault Notebook Pipeline...\n" + "=" * 60)

    for idx, rel_path in enumerate(notebook_paths, start=1):
        nb_path = base_dir / rel_path
        if not nb_path.exists():
            raise FileNotFoundError(f"Notebook not found: {nb_path}")

        print(f"[{idx}/{len(notebook_paths)}] Running: {rel_path} ...")
        step_start = time.perf_counter()

        # 1. Read the notebook
        with open(nb_path, "r", encoding="utf-8") as f:
            nb = nbformat.read(f, as_version=4)

        # 2. Append a temporary cell to close the DuckDB connection and release the file lock
        close_cell = nbformat.v4.new_code_cell(
            "if 'con' in locals():\n    con.close()"
        )
        nb.cells.append(close_cell)

        try:
            # 3. Execute the notebook in its directory
            client = NotebookClient(
                nb,
                timeout=600,
                resources={"metadata": {"path": str(nb_path.parent)}},
            )
            client.execute()
        finally:
            # 4. Remove the temporary close cell before saving back to disk
            nb.cells.pop()

        # 5. Save the executed outputs back into the .ipynb file
        with open(nb_path, "w", encoding="utf-8") as f:
            nbformat.write(nb, f)

        elapsed = time.perf_counter() - step_start
        print(f"    -> Completed in {elapsed:.2f}s\n")

    total_elapsed = time.perf_counter() - pipeline_start
    print("=" * 60)
    print(f"All {len(notebook_paths)} notebooks executed successfully in {total_elapsed:.2f}s!")


if __name__ == "__main__":
    run_notebook_pipeline(BASE_DIR, NOTEBOOK_PIPELINE)