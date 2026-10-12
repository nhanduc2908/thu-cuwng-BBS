"""Export public product and combo data from the local PetCare SQLite database."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import sqlite3
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.storefront_catalog import build_storefront_catalog


def default_database_path() -> Path:
    if os.environ.get("LOCALAPPDATA"):
        data_root = Path(os.environ["LOCALAPPDATA"])
    else:
        data_root = Path.home() / "AppData" / "Local"
    return data_root / "PetStoreManagement" / "pet_store.db"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--database",
        type=Path,
        default=default_database_path(),
        help="PetCare SQLite file (defaults to the current user's application database).",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=ROOT / "HTML" / "Web bán hàng" / "data" / "store_catalog.json",
        help="Storefront JSON snapshot destination.",
    )
    args = parser.parse_args()
    database_path = args.database.expanduser().resolve()
    output_path = args.output.expanduser().resolve()
    if not database_path.is_file():
        parser.error(f"PetCare database does not exist: {database_path}")
    output_path.parent.mkdir(parents=True, exist_ok=True)

    connection = sqlite3.connect(f"{database_path.as_uri()}?mode=ro", uri=True)
    connection.row_factory = sqlite3.Row
    try:
        catalog = build_storefront_catalog(connection, source_type="sqlite_snapshot")
    except sqlite3.Error as error:
        parser.error(f"Could not read catalog from {database_path}: {error}")
    finally:
        connection.close()

    output_path.write_text(
        json.dumps(catalog, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    summary = catalog["summary"]
    printable_path = str(output_path).encode("ascii", "backslashreplace").decode("ascii")
    print(
        f"Synced {summary['productCount']} products and "
        f"{summary['comboCount']} combos to {printable_path}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
