"""Validate and import HTML JSON datasets into non-operational SQLite staging tables."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sqlite3
import sys
from typing import Any, Iterator


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DATA_DIR = PROJECT_ROOT / "HTML" / "data"
MANIFEST_NAME = "catalog_manifest.json"


def _reject_nonstandard_constant(value: str) -> None:
    raise ValueError(f"JSON contains unsupported numeric value: {value}")


def _record_arrays(
    value: Any, path: str = "$"
) -> Iterator[tuple[str, list[dict[str, Any]]]]:
    if isinstance(value, dict):
        for key, child in value.items():
            yield from _record_arrays(child, f"{path}.{key}")
    elif isinstance(value, list):
        if value and all(isinstance(row, dict) for row in value):
            yield path, value
        elif any(isinstance(row, dict) for row in value):
            raise ValueError(f"Mixed object/non-object array at {path}.")


def _manifest_entries(data_dir: Path) -> dict[str, dict[str, Any]]:
    manifest_path = data_dir / MANIFEST_NAME
    if not manifest_path.is_file():
        return {}
    payload = json.loads(
        manifest_path.read_text(encoding="utf-8"),
        parse_constant=_reject_nonstandard_constant,
    )
    if not isinstance(payload, dict) or not isinstance(payload.get("groups"), list):
        raise ValueError(f"{MANIFEST_NAME} must define a groups array.")
    entries: dict[str, dict[str, Any]] = {}
    for group in payload["groups"]:
        if not isinstance(group, dict) or not isinstance(group.get("entries"), list):
            raise ValueError(f"{MANIFEST_NAME} contains an invalid group.")
        classification = group.get("classification", "unverified")
        if classification not in {
            "synthetic_demo",
            "generated_catalog",
            "unverified",
        }:
            raise ValueError(f"{MANIFEST_NAME} contains an invalid classification.")
        for entry in group["entries"]:
            if not isinstance(entry, dict):
                raise ValueError(f"{MANIFEST_NAME} contains an invalid dataset entry.")
            filename = entry.get("file")
            if (
                not isinstance(filename, str)
                or Path(filename).name != filename
                or not filename.lower().endswith(".json")
                or filename == MANIFEST_NAME
            ):
                raise ValueError(f"{MANIFEST_NAME} contains an invalid JSON filename.")
            if filename in entries:
                raise ValueError(f"{MANIFEST_NAME} repeats dataset {filename}.")
            entries[filename] = {
                **entry,
                "classification": classification,
                "is_derived": int(bool(entry.get("derived", False))),
            }
    return entries


def _record_key(record: dict[str, Any]) -> str | None:
    for field in ("id", "code", "product_code", "item_code", "animal_code", "name"):
        value = record.get(field)
        if value is not None and str(value).strip():
            return str(value).strip()[:300]
    return None


def load_json_sources(data_dir: Path) -> list[dict[str, Any]]:
    resolved_dir = data_dir.resolve()
    if not resolved_dir.is_dir():
        raise FileNotFoundError(f"Data directory does not exist: {resolved_dir}")

    manifest = _manifest_entries(resolved_dir)
    sources: list[dict[str, Any]] = []
    for path in sorted(resolved_dir.rglob("*.json")):
        if path == resolved_dir / MANIFEST_NAME:
            continue
        relative_path = path.relative_to(resolved_dir).as_posix()
        manifest_entry = manifest.get(relative_path, {})
        raw_json = path.read_text(encoding="utf-8")
        document = json.loads(raw_json, parse_constant=_reject_nonstandard_constant)
        if not isinstance(document, (dict, list)):
            raise ValueError(f"{relative_path} must contain a JSON object or array.")

        arrays = [
            {
                "array_path": array_path,
                "records": records,
            }
            for array_path, records in _record_arrays(document)
        ]
        classification = manifest_entry.get("classification", "unverified")
        sources.append({
            "source_file": relative_path,
            "source_path": path.resolve(),
            "label": manifest_entry.get("label", path.name),
            "array_path": manifest_entry.get("arrayPath"),
            "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
            "size_bytes": path.stat().st_size,
            "classification": classification,
            "is_synthetic": (
                1
                if classification in {"synthetic_demo", "generated_catalog"}
                else None
            ),
            "is_derived": manifest_entry.get("is_derived", 0),
            "document_json": raw_json,
            "arrays": arrays,
            "record_count": sum(len(array["records"]) for array in arrays),
        })

    if not sources:
        raise ValueError(f"No JSON files found under {resolved_dir}.")
    return sources


def _create_staging_schema(connection: sqlite3.Connection) -> None:
    connection.executescript(
        """
        CREATE TABLE IF NOT EXISTS html_data_sources (
            source_file TEXT PRIMARY KEY,
            sha256 TEXT NOT NULL,
            size_bytes INTEGER NOT NULL CHECK (size_bytes >= 0),
            classification TEXT NOT NULL CHECK (
                classification IN ('synthetic_demo', 'generated_catalog', 'unverified')
            ),
            is_synthetic INTEGER CHECK (is_synthetic IN (0, 1)),
            is_derived INTEGER NOT NULL CHECK (is_derived IN (0, 1)),
            record_count INTEGER NOT NULL CHECK (record_count >= 0),
            imported_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            document_json TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS html_data_records (
            source_file TEXT NOT NULL
                REFERENCES html_data_sources(source_file) ON DELETE CASCADE,
            array_path TEXT NOT NULL,
            row_number INTEGER NOT NULL CHECK (row_number >= 0),
            record_key TEXT,
            classification TEXT NOT NULL CHECK (
                classification IN ('synthetic_demo', 'generated_catalog', 'unverified')
            ),
            is_synthetic INTEGER CHECK (is_synthetic IN (0, 1)),
            is_derived INTEGER NOT NULL CHECK (is_derived IN (0, 1)),
            record_json TEXT NOT NULL,
            PRIMARY KEY (source_file, array_path, row_number)
        );

        CREATE INDEX IF NOT EXISTS idx_html_data_records_lookup
            ON html_data_records(source_file, array_path, record_key);
        CREATE INDEX IF NOT EXISTS idx_html_data_records_classification
            ON html_data_records(classification, is_derived);
        """
    )


def import_sources(database_path: Path, sources: list[dict[str, Any]]) -> int:
    resolved_database = database_path.resolve()
    if any(
        source.get("source_path") == resolved_database
        for source in sources
    ):
        raise ValueError("SQLite destination cannot overwrite a source JSON file.")
    database_path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(database_path)
    connection.execute("PRAGMA foreign_keys = ON")
    try:
        with connection:
            _create_staging_schema(connection)
            for source in sources:
                connection.execute(
                    """
                    INSERT INTO html_data_sources (
                        source_file, sha256, size_bytes, classification,
                        is_synthetic, is_derived, record_count, imported_at,
                        document_json
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP, ?)
                    ON CONFLICT(source_file) DO UPDATE SET
                        sha256 = excluded.sha256,
                        size_bytes = excluded.size_bytes,
                        classification = excluded.classification,
                        is_synthetic = excluded.is_synthetic,
                        is_derived = excluded.is_derived,
                        record_count = excluded.record_count,
                        imported_at = CURRENT_TIMESTAMP,
                        document_json = excluded.document_json
                    """,
                    (
                        source["source_file"],
                        source["sha256"],
                        source["size_bytes"],
                        source["classification"],
                        source["is_synthetic"],
                        source["is_derived"],
                        source["record_count"],
                        source["document_json"],
                    ),
                )
                connection.execute(
                    "DELETE FROM html_data_records WHERE source_file = ?",
                    (source["source_file"],),
                )
                for array in source["arrays"]:
                    connection.executemany(
                        """
                        INSERT INTO html_data_records (
                            source_file, array_path, row_number, record_key,
                            classification, is_synthetic, is_derived, record_json
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                        """,
                        [
                            (
                                source["source_file"],
                                array["array_path"],
                                row_number,
                                _record_key(record),
                                source["classification"],
                                source["is_synthetic"],
                                source["is_derived"],
                                json.dumps(record, ensure_ascii=False, separators=(",", ":")),
                            )
                            for row_number, record in enumerate(array["records"])
                        ],
                    )
        return sum(source["record_count"] for source in sources)
    finally:
        connection.close()


def _arguments(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Validate HTML/data JSON files and stage them in SQLite without "
            "writing to operational customer, pet, inventory, or order tables."
        )
    )
    parser.add_argument(
        "--data-dir",
        type=Path,
        default=DEFAULT_DATA_DIR,
        help=f"JSON source directory (default: {DEFAULT_DATA_DIR})",
    )
    parser.add_argument(
        "--database",
        type=Path,
        required=True,
        help="SQLite destination file. Existing database content is preserved.",
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Commit the import; otherwise validate and print a preview only.",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="backslashreplace")
    arguments = _arguments(argv)
    try:
        sources = load_json_sources(arguments.data_dir)
        print(f"Validated {len(sources)} JSON files.")
        for source in sources:
            print(
                f"{source['source_file']}: {source['record_count']} records; "
                f"{source['classification']}; "
                f"{'derived/overlapping' if source['is_derived'] else 'source'}; "
                f"sha256={source['sha256'][:12]}"
            )
        total_records = sum(source["record_count"] for source in sources)
        if not arguments.apply:
            print(
                f"Preview only: {total_records} records validated. "
                "Pass --apply to write staging tables."
            )
            return 0

        imported = import_sources(arguments.database, sources)
        print(
            f"Imported {len(sources)} source documents and {imported} records "
            f"into {arguments.database.resolve()} (staging only)."
        )
        return 0
    except (OSError, ValueError, json.JSONDecodeError, sqlite3.Error) as error:
        print(f"Import failed: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
