import json
import sqlite3
from pathlib import Path

from scripts.import_html_data_to_sqlite import import_sources, load_json_sources, main


def write_json(path: Path, content: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(content, ensure_ascii=False), encoding="utf-8")


def test_import_stages_source_documents_and_records_idempotently(tmp_path: Path):
    data_dir = tmp_path / "HTML" / "data"
    write_json(
        data_dir / "catalog_manifest.json",
        {
            "groups": [
                {
                    "classification": "synthetic_demo",
                    "entries": [
                        {"file": "module_04_pets.json", "arrayPath": "demoData"}
                    ],
                },
                {
                    "classification": "generated_catalog",
                    "entries": [
                        {
                            "file": "nutrition_catalog_4000.json",
                            "arrayPath": "products",
                            "derived": True,
                        }
                    ],
                },
            ]
        },
    )
    write_json(
        data_dir / "module_04_pets.json",
        {
            "moduleId": "module_04_pets",
            "demoData": [
                {"animalId": "PET-001", "name": "Sample"},
                {"animalId": "PET-002", "name": "Sample 2"},
            ],
        },
    )
    write_json(
        data_dir / "nutrition_catalog_4000.json",
        {"products": [{"product_code": "NUT-001", "name": "Reference"}]},
    )
    database_path = tmp_path / "transfer.sqlite"
    sources = load_json_sources(data_dir)

    assert len(sources) == 2
    assert sum(source["record_count"] for source in sources) == 3
    assert import_sources(database_path, sources) == 3
    assert import_sources(database_path, sources) == 3

    with sqlite3.connect(database_path) as connection:
        assert connection.execute("SELECT COUNT(*) FROM html_data_sources").fetchone()[0] == 2
        assert connection.execute("SELECT COUNT(*) FROM html_data_records").fetchone()[0] == 3
        assert connection.execute(
            "SELECT COUNT(*) FROM html_data_records WHERE is_synthetic = 1"
        ).fetchone()[0] == 3
        assert connection.execute(
            "SELECT is_derived, classification FROM html_data_sources "
            "WHERE source_file = 'nutrition_catalog_4000.json'"
        ).fetchone() == (1, "generated_catalog")
        assert connection.execute(
            """
            SELECT json_extract(record_json, '$.animalId')
            FROM html_data_records
            WHERE source_file = 'module_04_pets.json' AND row_number = 0
            """
        ).fetchone()[0] == "PET-001"


def test_reimport_replaces_changed_rows_for_one_source_only(tmp_path: Path):
    data_dir = tmp_path / "data"
    source_path = data_dir / "module_10_customers.json"
    other_path = data_dir / "module_04_pets.json"
    write_json(source_path, {"demoData": [{"customerId": "CUS-001"}]})
    write_json(other_path, {"demoData": [{"animalId": "PET-001"}]})
    database_path = tmp_path / "transfer.sqlite"
    import_sources(database_path, load_json_sources(data_dir))

    write_json(
        source_path,
        {"demoData": [{"customerId": "CUS-002"}, {"customerId": "CUS-003"}]},
    )
    import_sources(database_path, load_json_sources(data_dir))

    with sqlite3.connect(database_path) as connection:
        customer_rows = connection.execute(
            """
            SELECT json_extract(record_json, '$.customerId')
            FROM html_data_records
            WHERE source_file = 'module_10_customers.json'
            ORDER BY row_number
            """
        ).fetchall()
        assert customer_rows == [("CUS-002",), ("CUS-003",)]
        assert connection.execute(
            "SELECT COUNT(*) FROM html_data_records "
            "WHERE source_file = 'module_04_pets.json'"
        ).fetchone()[0] == 1


def test_load_sources_rejects_mixed_object_arrays_before_import(tmp_path: Path):
    data_dir = tmp_path / "data"
    write_json(data_dir / "valid.json", {"items": [{"id": 1}]})
    write_json(data_dir / "invalid.json", {"items": [{"id": 2}, "bad row"]})

    try:
        load_json_sources(data_dir)
    except ValueError as error:
        assert "Mixed object/non-object array" in str(error)
    else:
        raise AssertionError("Malformed record array must be rejected.")


def test_import_cannot_overwrite_a_json_source(tmp_path: Path):
    data_dir = tmp_path / "data"
    source_path = data_dir / "module_04_pets.json"
    write_json(source_path, {"demoData": [{"id": "PET-001"}]})
    sources = load_json_sources(data_dir)

    try:
        import_sources(source_path, sources)
    except ValueError as error:
        assert "cannot overwrite a source JSON file" in str(error)
    else:
        raise AssertionError("SQLite output must not overwrite a JSON input.")


def test_cli_imports_to_unicode_database_path(tmp_path: Path, capsys):
    data_dir = tmp_path / "nguồn dữ liệu"
    write_json(
        data_dir / "catalog_manifest.json",
        {
            "groups": [
                {
                    "classification": "synthetic_demo",
                    "entries": [{"file": "module_04_pets.json"}],
                }
            ]
        },
    )
    write_json(data_dir / "module_04_pets.json", {"demoData": [{"id": "PET-001"}]})
    database_path = tmp_path / "cơ sở dữ liệu.sqlite"

    result = main([
        "--data-dir",
        str(data_dir),
        "--database",
        str(database_path),
        "--apply",
    ])

    assert result == 0
    assert "Imported 1 source documents and 1 records" in capsys.readouterr().out
    assert database_path.is_file()


def test_shared_manifest_covers_all_project_html_json_sources():
    project_root = Path(__file__).resolve().parents[1]
    data_dir = project_root / "HTML" / "data"
    sources = load_json_sources(data_dir)
    manifest = json.loads((data_dir / "catalog_manifest.json").read_text(encoding="utf-8"))
    listed_files = {
        entry["file"]
        for group in manifest["groups"]
        for entry in group["entries"]
    }
    source_files = {Path(source["source_file"]).name for source in sources}

    assert len(listed_files) == 26
    assert listed_files == source_files
    classifications = {
        Path(source["source_file"]).name: source["classification"]
        for source in sources
    }
    assert classifications["product_spec_fields.json"] == "unverified"
    assert classifications["pet_product_specs.json"] == "unverified"
    assert classifications["pet_food_brands_global.json"] == "unverified"
    assert all(
        classification != "unverified"
        for filename, classification in classifications.items()
        if filename not in {
            "product_spec_fields.json",
            "pet_product_specs.json",
            "pet_food_brands_global.json",
        }
    )
